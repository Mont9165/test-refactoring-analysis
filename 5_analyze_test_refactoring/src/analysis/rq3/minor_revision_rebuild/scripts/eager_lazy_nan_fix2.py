# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: inline command #116 (cwd rq3_recompute)).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/inline/inline_116_eager_lazy_nan_fix2.py).
from pathlib import Path as _P  # PATH (rebuild)
ROOT = _P(__file__).resolve().parent.parent  # PATH (rebuild): rq3_rebuild/
INTER = ROOT / "intermediate"  # PATH (rebuild): replaces scratch rq3_recompute/ and rq3_recompute/followup/
# Verbatim inline code from transcript command #116 (2026-10-12T02:13:27.228Z, tool_use toolu_01PBjRt5QffFK6faFzDdeh2E),
# originally run as `python - <<'EOF'` with cwd = .../scratchpad/rq3_recompute
import pandas as pd
f=pd.read_csv(ROOT / "data_fix2/file_level_wide.csv",encoding="utf-8-sig")  # PATH (rebuild)
m=pd.read_csv(INTER / "data_fix/method_level_wide.csv",encoding="utf-8-sig")   # unmasked method level (382)  # PATH (rebuild)
m=m[~m.commit_url.str.contains("/openjdk/lilliput/commit/7f80683")].reset_index(drop=True)
assert (f.commit_url.values==m.commit_url.values).all() and (f.type_name.values==m.type_name.values).all()
cols=[c for c in f.columns if c.endswith("_before") or c.endswith("_after")]
nan_cols=sorted({c.rsplit("_",1)[0] for c in cols if f[c].isna().any()})
print("file-level smells with NaN:", nan_cols)
for s in ("Eager Test","Lazy Test"):
    b,a=f[f"{s}_before"],f[f"{s}_after"]
    both=b.isna()&a.isna(); onlyb=b.isna()&a.notna(); onlya=b.notna()&a.isna(); meas=b.notna()&a.notna()
    print(f"{s}: measured {int(meas.sum())}, both NaN {int(both.sum())}, before-only NaN {int(onlyb.sum())} (after>0: {int((onlyb&(a>0)).sum())}), after-only NaN {int(onlya.sum())} (before>0: {int((onlya&(b>0)).sum())})")
    mb,ma=m[f"{s}_before"],m[f"{s}_after"]
    print(f"   method-level values on file-both-NaN rows: nonzero {int(((mb!=0)|(ma!=0))[both].sum())}; on one-side-NaN rows: nonzero {int(((mb!=0)|(ma!=0))[onlyb|onlya].sum())}")
    # commits whose Eager pairs are ALL one-side NaN (would drop out of the figure base under the new rule)
    g=pd.DataFrame({"u":f.commit_url,"ok":(meas|both)}).groupby("u").ok.any()
    print(f"   commits with no measured-or-both-NaN pair: {int((~g).sum())} of {len(g)}")
