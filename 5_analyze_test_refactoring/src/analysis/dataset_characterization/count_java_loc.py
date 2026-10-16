"""Count Java SLOC per project for the manual-inspection sample.

For each project named in the annotation data, shallow-clones the current
default branch, runs `scc --by-file` on .java files, classifies test files
(path contains a test/tests/testing/androidTest/it directory segment, or the
file name matches *Test(s).java / *TestCase.java / *IT.java), appends one CSV
row, and deletes the clone. Resume-friendly: reruns skip projects already
counted without error.

Output: java_loc_per_project.csv next to this script.
Requires: git, scc (https://github.com/boyter/scc).
"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ANN_CSV = REPO / "4_manual_inspection/src/refactoring_data_2025-02-19.csv"
OUT_CSV = HERE / "java_loc_per_project.csv"
CLONE_ROOT = HERE / "clones"
WORKERS = 4

TEST_DIR_RE = re.compile(r"(^|/)(test|tests|testing|androidTest|it)(/|$)", re.I)
TEST_FILE_RE = re.compile(r"(Test[s]?|TestCase|IT)\.java$")

FIELDS = ["full_name", "java_files", "java_code", "java_lines",
          "test_files", "test_code", "error"]

write_lock = Lock()


def load_projects() -> list[str]:
    projs = set()
    with open(ANN_CSV) as f:
        for r in csv.DictReader(f):
            m = re.search(r"github\.com/([^/]+/[^/]+)", r["url"])
            if m:
                projs.add(m.group(1))
    return sorted(projs)


def is_test_file(rel_path: str) -> bool:
    return bool(TEST_DIR_RE.search(os.path.dirname(rel_path)) or
                TEST_FILE_RE.search(os.path.basename(rel_path)))


def process(name: str) -> dict:
    row = {c: "" for c in FIELDS}
    row["full_name"] = name
    dest = CLONE_ROOT / name.replace("/", "__")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--single-branch", "--quiet",
             f"https://github.com/{name}.git", str(dest)],
            check=True, capture_output=True, timeout=1200,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
        out = subprocess.run(
            ["scc", "--by-file", "--format", "json", "--include-ext", "java",
             "--no-cocomo", str(dest)],
            check=True, capture_output=True, timeout=600, text=True,
        ).stdout
        data = json.loads(out)
        files = []
        for lang in data:
            if lang.get("Name") == "Java":
                files = lang.get("Files", [])
        n_files = n_code = n_lines = t_files = t_code = 0
        prefix = str(dest) + "/"
        for fobj in files:
            rel = fobj["Location"].removeprefix(prefix)
            n_files += 1
            n_code += fobj["Code"]
            n_lines += fobj["Lines"]
            if is_test_file(rel):
                t_files += 1
                t_code += fobj["Code"]
        row.update(java_files=n_files, java_code=n_code, java_lines=n_lines,
                   test_files=t_files, test_code=t_code)
    except subprocess.CalledProcessError as e:
        row["error"] = (e.stderr or b"").decode(errors="ignore")[:200] or "failed"
    except Exception as e:
        row["error"] = f"{type(e).__name__}: {e}"[:200]
    finally:
        shutil.rmtree(dest, ignore_errors=True)
    with write_lock:
        with open(OUT_CSV, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writerow(row)
        print(f"done {name} err={row['error'][:60]}", flush=True)
    return row


def main() -> int:
    CLONE_ROOT.mkdir(exist_ok=True)
    done = set()
    if OUT_CSV.exists():
        with open(OUT_CSV) as f:
            done = {r["full_name"] for r in csv.DictReader(f) if not r["error"]}
    else:
        with open(OUT_CSV, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()

    todo = [p for p in load_projects() if p not in done]
    print(f"{len(todo)} projects to process ({len(done)} already done)", flush=True)
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(process, todo))
    print("ALL DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
