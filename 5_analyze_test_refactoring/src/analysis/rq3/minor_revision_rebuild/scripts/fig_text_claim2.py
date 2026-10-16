# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: rq3_recompute/followup2/fig_text_claim2.py).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/rq3_recompute/followup2/fig_text_claim2.py).
from pathlib import Path as _P  # PATH (rebuild)
ROOT = _P(__file__).resolve().parent.parent  # PATH (rebuild): rq3_rebuild/
INTER = ROOT / "intermediate"  # PATH (rebuild): replaces scratch rq3_recompute/ and rq3_recompute/followup/
import re
for level in ("file", "method"):
    rows, on = [], False
    for line in open(ROOT / "out_fix2/figures/regen_fix2_log.txt"):  # PATH (rebuild)
        if line.startswith("==="):
            on = f"=== {level} level" in line; continue
        m = re.match(r"^(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$", line) if on else None
        if m:
            s = m.group(1).strip(); pres, imp, deg, nc, ab, base = map(int, m.groups()[1:])
            rows.append((s, 100 * imp / base, 100 * deg / base, base))
    top_i = sorted(rows, key=lambda r: -r[1])[:5]; top_d = sorted(rows, key=lambda r: -r[2])[:5]
    rank = lambda s, key: 1 + sorted(rows, key=key).index(next(r for r in rows if r[0] == s))
    print(f"{level}: top improvement shares: " + ", ".join(f"{s} {i:.1f}%" for s, i, d, b in top_i))
    print(f"{level}: top degradation shares: " + ", ".join(f"{s} {d:.1f}%" for s, i, d, b in top_d))
    print(f"   Duplicate Assert improvement rank {rank('Duplicate Assert', lambda r: -r[1])}/{len(rows)}; "
          f"Mystery Guest degradation rank {rank('Mystery Guest', lambda r: -r[2])}/{len(rows)} ({next(r[2] for r in rows if r[0]=='Mystery Guest'):.1f}%)")
