"""Shared runner: execute RefactoringMiner 3.0.0 on a commit and cache the JSON.

RefactoringMiner (JGit) cannot read blob:none partial clones -- it silently
returns empty output. We therefore clone with --filter=blob:none for speed but
materialize the blobs of both snapshots (sha^ and sha) via git CLI checkouts
before invoking RM.

Configuration via environment variables:
  RM300_WORK  work directory for clones/JSONs/logs
              (default: <this dir>/work)
  RM300_BIN   RefactoringMiner 3.0.0 launcher
              (default: <RM300_WORK>/RefactoringMiner-3.0.0/bin/RefactoringMiner)

Download RM 3.0.0:
  curl -sL -o rm300.zip https://github.com/tsantalis/RefactoringMiner/releases/download/3.0.0/RefactoringMiner-3.0.0.zip
  unzip rm300.zip -d "$RM300_WORK"
"""
import os
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = Path(os.environ.get("RM300_WORK", HERE / "work"))
RM_BIN = Path(os.environ.get("RM300_BIN", WORK / "RefactoringMiner-3.0.0/bin/RefactoringMiner"))
REPO_ROOT = HERE.parents[3]

REPOS = WORK / "repos"
JSONS = WORK / "json"
LOGS = WORK / "log"
for d in (REPOS, JSONS, LOGS):
    d.mkdir(parents=True, exist_ok=True)

URL_RE = re.compile(r"https://github\.com/([^/]+)/([^/]+)/commit/([0-9a-f]+)")

TEST_PATH_HINTS = ("/src/test/", "/tests/", "/test/")


def is_test_path(p: str) -> bool:
    pl = (p or "").lower()
    if any(h in pl for h in TEST_PATH_HINTS):
        return True
    return (p or "").endswith(("Test.java", "Tests.java", "IT.java", "ITCase.java"))


def sh(cmd, timeout=None, log=None, cwd=None):
    with open(log, "ab") if log else open(os.devnull, "wb") as lf:
        return subprocess.run(cmd, stdout=lf, stderr=lf, timeout=timeout, cwd=cwd).returncode


def process_commit(item):
    """item = (sha, (owner, repo)). Returns (sha, status)."""
    sha, (owner, repo) = item
    out_json = JSONS / f"{sha}.json"
    log = LOGS / f"{sha}.log"
    if out_json.exists() and out_json.stat().st_size > 0:
        return sha, "cached"
    repo_dir = REPOS / f"{owner}__{repo}"
    if not (repo_dir / ".git").is_dir():
        rc = sh(["git", "clone", "--filter=blob:none", "--no-tags",
                 f"https://github.com/{owner}/{repo}.git", str(repo_dir)], timeout=1800, log=log)
        if rc != 0:
            return sha, "clone_failed"
    sh(["git", "fetch", "origin", sha], timeout=600, log=log, cwd=str(repo_dir))
    # Materialize blobs of both snapshots (JGit cannot fetch them on demand).
    for ref in (f"{sha}^", sha):
        sh(["git", "-c", "advice.detachedHead=false", "checkout", "-f", ref],
           timeout=1800, log=log, cwd=str(repo_dir))
    try:
        rc = sh([str(RM_BIN), "-c", str(repo_dir), sha, "-json", str(out_json)],
                timeout=900, log=log)
    except subprocess.TimeoutExpired:
        return sha, "rm_timeout"
    return sha, ("ok" if rc == 0 and out_json.exists() else "rm_failed")
