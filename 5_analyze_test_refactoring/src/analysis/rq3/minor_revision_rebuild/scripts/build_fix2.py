# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: rq3_recompute/followup2/build_fix2.py).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/rq3_recompute/followup2/build_fix2.py).
"""data_fix2: data_fix_mmask (method-level cells blanked where the file-level cell is NaN) minus the three
openjdk/lilliput 7f80683 instances, whose files tsDetect did not analyze (all file-level smells NaN, 0 test methods)."""
import csv, sys
from pathlib import Path
H = Path(__file__).resolve().parent.parent  # PATH (rebuild)
for lvl in ("file", "method"):
    text = (H / "intermediate/data_fix_mmask" / f"{lvl}_level_wide.csv").read_bytes().decode("utf-8-sig")  # PATH (rebuild)
    rows = list(csv.reader(text.splitlines())); hdr, body = rows[0], rows[1:]
    ui = hdr.index("commit_url")
    keep = [r for r in body if "/openjdk/lilliput/commit/7f80683" not in r[ui]]
    print(lvl, len(body), "->", len(keep), "rows;", len({r[ui] for r in keep}), "commits")
    with open(H / "data_fix2" / f"{lvl}_level_wide.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(hdr); w.writerows(keep)
