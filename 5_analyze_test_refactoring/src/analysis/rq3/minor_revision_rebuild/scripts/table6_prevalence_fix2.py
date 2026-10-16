# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: inline command #94 (cwd rq3_recompute)).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/inline/inline_094_table6_prevalence_fix2.py).
from pathlib import Path as _P  # PATH (rebuild)
ROOT = _P(__file__).resolve().parent.parent  # PATH (rebuild): rq3_rebuild/
INTER = ROOT / "intermediate"  # PATH (rebuild): replaces scratch rq3_recompute/ and rq3_recompute/followup/
DIRS = {"followup/data_fix": INTER / "data_fix", "followup2/data_fix2": ROOT / "data_fix2"}  # PATH (rebuild)
# Verbatim inline code from transcript command #94 (2026-10-12T01:10:10.809Z, tool_use toolu_01N4AWMfvHsZqhFDvQd69a5m),
# originally run as `python - <<'EOF'` with cwd = .../scratchpad/rq3_recompute
import pandas as pd
EX={"NumberOfMethods","Verbose Test","Dependent Test"}
def t6(path):
    df=pd.read_csv(path,encoding="utf-8-sig")
    sm=[c[:-7] for c in df.columns if c.endswith("_before") and c[:-7] not in EX]
    ab=nc=imp=deg=0
    for s in sm:
        b,a=df[f"{s}_before"],df[f"{s}_after"]; ok=b.notna()&a.notna(); b,a=b[ok],a[ok]
        ab+=int(((b==0)&(a==0)).sum()); nc+=int(((b==a)&(b>0)).sum()); imp+=int((a<b).sum()); deg+=int((a>b).sum())
    t=ab+nc+imp+deg; p=nc+imp+deg
    return t,ab,nc,imp,deg,p
for d in ("followup/data_fix","followup2/data_fix2"):
    for lvl in ("file","method"):
        t,ab,nc,imp,deg,p=t6(DIRS[d] / f"{lvl}_level_wide.csv")  # PATH (rebuild)
        print(f"{d:22s} {lvl:6s} cells={t} | NotPresent {100*ab/t:.1f} NoChange {100*nc/t:.1f} Imp {100*imp/t:.1f} Deg {100*deg/t:.1f} | present-only ({p}): unchanged {100*nc/p:.1f} imp {100*imp/p:.1f} deg {100*deg/p:.1f}")
# prevalence at file level: commits with >=1 smell present before (both sides measured), 19 smells + all except NumberOfMethods
for d in ("followup/data_fix","followup2/data_fix2"):
    df=pd.read_csv(DIRS[d] / "file_level_wide.csv",encoding="utf-8-sig")  # PATH (rebuild)
    sm=[c[:-7] for c in df.columns if c.endswith("_before") and c[:-7]!="NumberOfMethods"]
    pres=pd.Series(False,index=df.index); meas=pd.Series(False,index=df.index)
    for s in sm:
        b,a=df[f"{s}_before"],df[f"{s}_after"]
        pres|=(b>0)&a.notna(); meas|=b.notna()&a.notna()
    g=df.assign(p=pres,m=meas).groupby("commit_url")[["p","m"]].any()
    print(d,"commits",len(g),"measured",int(g.m.sum()),"present-before",int(g.p.sum()), f"= {100*g.p.sum()/g.m.sum():.1f}% of measured")
