# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: inline command #117 (cwd rq3_recompute)).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/inline/inline_117_eager_lazy_commits_fix2.py).
from pathlib import Path as _P  # PATH (rebuild)
ROOT = _P(__file__).resolve().parent.parent  # PATH (rebuild): rq3_rebuild/
INTER = ROOT / "intermediate"  # PATH (rebuild): replaces scratch rq3_recompute/ and rq3_recompute/followup/
# Verbatim inline code from transcript command #117 (2026-10-12T02:14:11.811Z, tool_use toolu_01VQKsMbyg4XXCTuip7hLZbW),
# originally run as `python - <<'EOF'` with cwd = .../scratchpad/rq3_recompute
import pandas as pd
f=pd.read_csv(ROOT / "data_fix2/file_level_wide.csv",encoding="utf-8-sig")  # PATH (rebuild)
for s in ("Eager Test","Lazy Test"):
    b,a=f[f"{s}_before"],f[f"{s}_after"]
    d=pd.DataFrame({"u":f.commit_url.str.split("github.com/").str[1].str[:60],"meas":b.notna()&a.notna(),"both":b.isna()&a.isna(),
                    "one":b.notna()&a.isna(),"bpos":(b>0)&a.isna()})
    g=d.groupby("u").agg(meas=("meas","sum"),both=("both","sum"),one=("one","sum"),bpos=("bpos","sum"))
    print(s, "| commits:", len(g), "measured>=1:", int((g.meas>0).sum()), "| no measured but has one-side pair:", int(((g.meas==0)&(g.one>0)).sum()),
          "| of which before>0 known:", int(((g.meas==0)&(g.bpos>0)).sum()), "| one-side pairs in commits that also have measured pairs:", int(g[g.meas>0].one.sum()))
    print(g[(g.one>0)].to_string())
