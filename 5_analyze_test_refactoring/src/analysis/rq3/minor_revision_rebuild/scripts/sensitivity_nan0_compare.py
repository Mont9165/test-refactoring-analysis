# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: inline command #123 part 2 (cwd rq3_recompute)).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/inline/inline_123_followup3_nan0_sensitivity_part2.py).
from pathlib import Path as _P  # PATH (rebuild)
ROOT = _P(__file__).resolve().parent.parent  # PATH (rebuild): rq3_rebuild/
INTER = ROOT / "intermediate"  # PATH (rebuild): replaces scratch rq3_recompute/ and rq3_recompute/followup/
# Verbatim inline code from transcript command #123 (2026-10-12T04:04:18.763Z, tool_use toolu_01FrgHWpPHuhbusD1xBm32BN),
# originally run as `python - <<'EOF'` with cwd = .../scratchpad/rq3_recompute
import pandas as pd
a=pd.read_csv(ROOT / "out_fix2/table7_all.csv"); b=pd.read_csv(ROOT / "sensitivity_nan0/out_nan0/table7_all.csv")  # PATH (rebuild)
m=a.merge(b,on=["level","smell"],suffixes=("_cur","_nan0"))
for _,x in m.iterrows():
    sa=x.q_cur<0.05; sb=x.q_nan0<0.05
    if sa or sb:
        if (sa!=sb) or x.smell in ("Eager Test","Lazy Test"):
            print(f"{x.level:5s} {x.smell:22s} current: n={x.n_cur:.0f} imp={x.imp_cur:.0f} deg={x.deg_cur:.0f} p={x.p_cur:.3g} q={x.q_cur:.3f} | NaN->0: n={x.n_nan0:.0f} imp={x.imp_nan0:.0f} deg={x.deg_nan0:.0f} p={x.p_nan0:.3g} q={x.q_nan0:.3f} r={x.r_nan0:+.2f}")
t8a=pd.read_csv(ROOT / "out_fix2/table8_all.csv"); t8b=pd.read_csv(ROOT / "sensitivity_nan0/out_nan0/table8_all.csv")  # PATH (rebuild)
k=["level","type","smell"]; mm=t8a.merge(t8b,on=k,how="outer",suffixes=("_cur","_nan0"))
ch=mm[((mm.q_cur<0.05)!=(mm.q_nan0<0.05))]
print("per-type significance changes:"); print(ch[k+["n_cur","imp_cur","q_cur","n_nan0","imp_nan0","q_nan0"]].to_string(index=False))
