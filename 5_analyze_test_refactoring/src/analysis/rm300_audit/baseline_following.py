"""Add the following-window baseline: for each test-refactoring commit, take the
same random anchor already drawn for the preceding-window baseline and count
general refactorings in test files in the anchor's three following commits."""
import csv, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, '.')
import adjacent_window_audit as A

rows = list(csv.DictReader(open(A.WORK / "adjacent_windows.csv")))
by_repo = {}
for r in rows:
    parts = r["commit_url"].split("/")
    by_repo.setdefault((parts[3], parts[4]), []).append(r)

def work(owner, repo, rs):
    log = A.LOGS / f"{owner}__{repo}.log"
    d = A.REPOS / f"{owner}__{repo}"
    out = []
    for r in rs:
        anc = r["baseline_anchor"]
        if not anc:
            out.append((r["sha"], 0, "")); continue
        fol = A.following(d, anc)
        cs = [A.rm_count(d, s, log) for s in fol]
        out.append((r["sha"], len(fol), " ".join(map(str, cs))))
    return out

res = {}
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = [ex.submit(work, o, rp, rs) for (o, rp), rs in by_repo.items()]
    for i, f in enumerate(as_completed(futs), 1):
        for sha, n, cs in f.result():
            res[sha] = (n, cs)
        print(f"[{i}/{len(futs)}]", flush=True)
for r in rows:
    n, cs = res.get(r["sha"], (0, ""))
    r["n_base_fol"] = n; r["base_fol_counts"] = cs
    vals = [int(x) for x in cs.split()] if cs else []
    r["base_fol_hit"] = int(any(v > 0 for v in vals))
with open(A.WORK / "adjacent_windows_v2.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("done")
