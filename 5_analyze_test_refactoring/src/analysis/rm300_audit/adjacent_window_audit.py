"""Adjacent-commit co-occurrence audit (minor revision, Comment 3-10).

For every commit with a manually confirmed test refactoring, check whether
RefactoringMiner 3.0.0 detects a general-purpose refactoring in a test file
(a) in the same commit, (b) in the three preceding commits, and (c) in the
three following commits on the same branch. As a baseline, it applies the
same check to a random three-commit window of the same repository.

Differences to run_all_commits.py / multi_commit_cooccurrence.py:
  * full (non-partial) clones, so RM never sees missing blobs;
  * one worker per repository, so no two RM runs share a working tree;
  * following commits and a random baseline window are added.

Definitions
  preceding  first-parent ancestors sha^, sha^^, sha^^^ (as in the paper).
  following  walk forward from sha: next = the descendant whose first parent
             is the current commit; if the current commit was merged as a
             second parent, the merge commit is taken. Searched on
             origin/HEAD first, then on all remote branches.
  baseline   for each test-refactoring commit, one anchor drawn uniformly
             (seed = sha) from the non-merge first-parent commits of
             origin/HEAD within +-365 days, excluding the 7-commit
             neighbourhood of the commit; window = the anchor's three
             first-parent ancestors (same shape as "preceding").
  test file  rm_runner.is_test_path (same rule as the published 88/158).

Usage (env as in rm_runner: RM300_WORK, RM300_BIN):
    python adjacent_window_audit.py --workers 16 [--exclude sha1,sha2,...]
Outputs (in RM300_WORK): adjacent_windows.csv, adjacent_summary.txt
"""
import argparse
import csv
import json
import os
import random
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = Path(os.environ.get("RM300_WORK", HERE / "work"))
RM_BIN = Path(os.environ.get("RM300_BIN", WORK / "RefactoringMiner-3.0.0/bin/RefactoringMiner"))
CANONICAL = Path(os.environ.get(
    "CANONICAL_CSV",
    HERE.parent / "rq3/1_analyze_testsmell_diff/file_level_wide.csv"))
REPOS = WORK / "repos_full"
JSONS = WORK / "json_full"
LOGS = WORK / "log_full"
for d in (REPOS, JSONS, LOGS):
    d.mkdir(parents=True, exist_ok=True)

K = 3
TEST_PATH_HINTS = ("/src/test/", "/tests/", "/test/")


def is_test_path(p):
    pl = (p or "").lower()
    if any(h in pl for h in TEST_PATH_HINTS):
        return True
    return (p or "").endswith(("Test.java", "Tests.java", "IT.java", "ITCase.java"))


def git(repo, *args, timeout=600):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       text=True, timeout=timeout)
    return r.stdout if r.returncode == 0 else ""


def base_commits(exclude):
    out = {}
    for r in csv.DictReader(open(CANONICAL, encoding="utf-8-sig")):
        parts = r["commit_url"].strip().split("/")
        owner, repo, sha = parts[3], parts[4], parts[6]
        if sha not in exclude:
            out[sha] = (owner, repo, r["commit_url"].strip())
    return out


def ensure_clone(owner, repo, log):
    d = REPOS / f"{owner}__{repo}"
    if not (d / ".git").is_dir():
        # RM's -c mode opens <dir>/.git, so use a normal (but unchecked-out) clone
        with open(log, "ab") as lf:
            subprocess.run(["git", "clone", "--no-checkout", "--no-tags",
                            f"https://github.com/{owner}/{repo}.git", str(d)],
                           stdout=lf, stderr=lf, timeout=7200)
    return d


def ensure_commit(d, sha):
    if not git(d, "cat-file", "-t", sha).strip():
        git(d, "fetch", "--no-tags", "origin", sha, timeout=1800)
    return bool(git(d, "cat-file", "-t", sha).strip())


def head_ref(d):
    for ref in ("refs/remotes/origin/HEAD", "HEAD"):
        if git(d, "rev-parse", "--verify", "-q", ref).strip():
            return ref
    return "HEAD"


def preceding(d, sha):
    out = git(d, "rev-list", "--first-parent", "-n", str(K), f"{sha}^")
    return [l for l in out.split() if l]


def following(d, sha):
    for tip in [head_ref(d), "--remotes"]:
        rng = ["--remotes"] if tip == "--remotes" else [tip]
        out = git(d, "rev-list", "--ancestry-path", "--parents", f"^{sha}", *rng, timeout=1800)
        if not out:
            continue
        parents = {}
        for line in out.splitlines():
            p = line.split()
            parents[p[0]] = p[1:]
        res, cur = [], sha
        for _ in range(K):
            first = [c for c, ps in parents.items() if ps and ps[0] == cur]
            if not first:
                first = [c for c, ps in parents.items() if cur in ps[1:]]
            if not first:
                break
            cur = sorted(first)[0]
            res.append(cur)
        if res:
            return res
    return []


def baseline_window(d, sha):
    ts = git(d, "show", "-s", "--format=%ct", sha).strip()
    if not ts:
        return "", []
    t = datetime.fromtimestamp(int(ts))
    lo, hi = t - timedelta(days=365), t + timedelta(days=365)
    out = git(d, "rev-list", "--first-parent", "--no-merges",
              f"--since={lo:%Y-%m-%d}", f"--until={hi:%Y-%m-%d}", head_ref(d), timeout=1800)
    cands = [c for c in out.split() if c]
    near = set([sha] + preceding(d, sha) + following(d, sha))
    cands = [c for c in cands if c not in near]
    if not cands:
        return "", []
    anchor = random.Random(sha).choice(sorted(cands))
    return anchor, preceding(d, anchor)


def rm_count(d, sha, log):
    """Number of RM general refactorings touching a test file; -1 on failure."""
    js = JSONS / f"{sha}.json"
    if not (js.exists() and js.stat().st_size > 0):
        try:
            with open(log, "ab") as lf:
                subprocess.run([str(RM_BIN), "-c", str(d), sha, "-json", str(js)],
                               stdout=lf, stderr=lf, timeout=1200)
        except subprocess.TimeoutExpired:
            return -1
        if not (js.exists() and js.stat().st_size > 0):
            return -1
    try:
        data = json.loads(js.read_text())
    except Exception:
        return -1
    n = 0
    for c in data.get("commits", []):
        for ref in c.get("refactorings", []) or []:
            paths = {loc.get("filePath") for side in ("leftSideLocations", "rightSideLocations")
                     for loc in (ref.get(side) or [])}
            if any(is_test_path(p) for p in paths if p):
                n += 1
    return n


def process_repo(owner, repo, items):
    log = LOGS / f"{owner}__{repo}.log"
    d = ensure_clone(owner, repo, log)
    rows = []
    for sha, url in items:
        if not ensure_commit(d, sha):
            rows.append({"commit_url": url, "sha": sha, "same": -1, "n_pre": 0, "pre_counts": "",
                         "pre_hit": 0, "n_fol": 0, "fol_counts": "", "fol_hit": 0,
                         "baseline_anchor": "", "n_base": 0, "base_counts": "", "base_hit": 0,
                         "rm_failures": 1})
            continue
        pre, fol = preceding(d, sha), following(d, sha)
        anchor, base = baseline_window(d, sha)
        cnt = lambda shas: [rm_count(d, s, log) for s in shas]
        same, cp, cf, cb = rm_count(d, sha, log), cnt(pre), cnt(fol), cnt(base)
        hit = lambda cs: int(any(c > 0 for c in cs))
        rows.append({
            "commit_url": url, "sha": sha, "same": same,
            "n_pre": len(pre), "pre_counts": " ".join(map(str, cp)), "pre_hit": hit(cp),
            "n_fol": len(fol), "fol_counts": " ".join(map(str, cf)), "fol_hit": hit(cf),
            "baseline_anchor": anchor, "n_base": len(base),
            "base_counts": " ".join(map(str, cb)), "base_hit": hit(cb),
            "rm_failures": sum(c < 0 for c in [same] + cp + cf + cb),
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--exclude", default="", help="comma-separated SHAs to drop")
    args = ap.parse_args()
    exclude = {s for s in args.exclude.split(",") if s}
    commits = base_commits(exclude)
    by_repo = {}
    for sha, (owner, repo, url) in commits.items():
        by_repo.setdefault((owner, repo), []).append((sha, url))
    print(f"[plan] {len(commits)} commits in {len(by_repo)} repos", flush=True)
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(process_repo, o, r, it): (o, r) for (o, r), it in by_repo.items()}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                rows += f.result()
            except Exception as e:
                print(f"[error] {futs[f]}: {e}", flush=True)
            print(f"[{i}/{len(futs)}] {futs[f][0]}/{futs[f][1]} done", flush=True)
    rows.sort(key=lambda r: r["commit_url"])
    with open(WORK / "adjacent_windows.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    n = len(rows)
    s = lambda k: sum(r[k] for r in rows)
    either = sum(r["pre_hit"] or r["fol_hit"] for r in rows)
    lines = [
        f"commits: {n}",
        f"same commit: {sum(r['same'] > 0 for r in rows)}",
        f"preceding window hit: {s('pre_hit')} ({100*s('pre_hit')/n:.1f}%)",
        f"following window hit: {s('fol_hit')} ({100*s('fol_hit')/n:.1f}%)",
        f"either window hit: {either} ({100*either/n:.1f}%)",
        f"baseline window hit: {s('base_hit')} of {sum(r['n_base'] > 0 for r in rows)} with a baseline",
        f"windows shorter than {K}: pre {sum(r['n_pre'] < K for r in rows)}, "
        f"fol {sum(r['n_fol'] < K for r in rows)}, base {sum(r['n_base'] < K for r in rows)}",
        f"rows with RM failures: {sum(r['rm_failures'] > 0 for r in rows)}",
    ]
    (WORK / "adjacent_summary.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
