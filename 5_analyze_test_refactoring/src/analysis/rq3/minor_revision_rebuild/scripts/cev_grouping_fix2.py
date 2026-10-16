# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: inline command #104 (cwd rq3_recompute)).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/inline/inline_104_cev_grouping_fix2.py).
from pathlib import Path as _P  # PATH (rebuild)
ROOT = _P(__file__).resolve().parent.parent  # PATH (rebuild): rq3_rebuild/
INTER = ROOT / "intermediate"  # PATH (rebuild): replaces scratch rq3_recompute/ and rq3_recompute/followup/
# Verbatim inline code from transcript command #104 (2026-10-12T01:42:33.444Z, tool_use toolu_01K2BrUjYz7MwmMUPqEGJPHG),
# originally run as `python - <<'EOF'` with cwd = .../scratchpad/rq3_recompute
import pandas as pd
for lvl in ("method","file"):
    m=pd.read_csv(ROOT / f"data_fix2/{lvl}_level_wide.csv",encoding="utf-8-sig")  # PATH (rebuild)
    c=m[m.type_name=="Change Exception Verification"]
    b,a=c["Exception Catching Throwing_before"],c["Exception Catching Throwing_after"]
    ok=b.notna()&a.notna()
    print(lvl,"CEV n",int(ok.sum()),"improved",int((a<b).sum()),"removed to 0",int(((a==0)&(b>0)).sum()),"degraded",int((a>b).sum()),
          "| improved by commit:",c[a<b].commit_url.str.split("/").str[4].value_counts().to_dict())
g=pd.read_csv(ROOT / "data_fix2/file_level_wide.csv",encoding="utf-8-sig"); g=g[g.type_name=="Grouping Tests"]  # PATH (rebuild)
d=g.NumberOfMethods_after-g.NumberOfMethods_before
print("Grouping Tests n",len(g),"median dNOM",d.median())
