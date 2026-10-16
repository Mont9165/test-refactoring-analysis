# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: rq3_recompute/make_new_data.py).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/rq3_recompute/make_new_data.py).
"""Build the 403-row RQ3 tables: drop 'Lambdarize Method' rows and merge the five
exception-verification labels into 'Change Exception Verification'.
Uses the csv module so every other cell is copied byte-for-byte (formatting kept)."""
import csv, shutil, sys
from collections import Counter
from pathlib import Path

R = (__import__("pathlib").Path(__file__).resolve().parents[6] / "5_analyze_test_refactoring/src/analysis/rq3")
OUT = Path(__file__).resolve().parent.parent / "intermediate"  # PATH (rebuild)
SRC = {
    "file_level_wide.csv": R / "1_analyze_testsmell_diff/file_level_wide.csv",
    "method_level_wide.csv": R / "smells_result/method_level_wide.csv",   # identical content to 1_analyze_testsmell_diff/method_level_wide.csv
}
EXC = {'Replace try/catch with asserThrows', 'Replace annotation with assertThrow',
       'Replace try/catch with annotation', 'Replace assertThrow with try/catch',
       'Replace annotation with try/catch'}
NEW = "Change Exception Verification"

for name, src in SRC.items():
    shutil.copyfile(src, OUT / "data_orig" / name)
    raw = src.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    nl = "\r\n" if "\r\n" in text else "\n"
    rows = list(csv.reader(text.splitlines()))
    hdr, body = rows[0], rows[1:]
    ti = hdr.index("type_name"); ui = hdr.index("commit_url")
    kept = []
    for r in body:
        if r[ti] == "Lambdarize Method":
            continue
        if r[ti] in EXC:
            r = list(r); r[ti] = NEW
        kept.append(r)
    dst = OUT / "data_new" / name
    with open(dst, "w", encoding="utf-8-sig" if bom else "utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator=nl)
        w.writerow(hdr); w.writerows(kept)
    keys = Counter((r[ui], r[ti]) for r in kept)
    print(f"{name}: bom={bom} nl={nl!r} orig rows={len(body)} new rows={len(kept)} "
          f"commits={len({r[ui] for r in kept})} CEV rows={sum(r[ti]==NEW for r in kept)} "
          f"types={len({r[ti] for r in kept})} distinct (commit,type)={len(keys)}")
    cev = Counter(r[ui] for r in kept if r[ti] == NEW)
    print("   CEV per commit:", sorted(cev.values(), reverse=True), "commits:", len(cev))
