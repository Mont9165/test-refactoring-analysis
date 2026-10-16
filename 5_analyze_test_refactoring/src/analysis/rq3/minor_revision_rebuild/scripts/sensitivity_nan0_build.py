# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: inline command #123 part 1 (cwd rq3_recompute)).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/inline/inline_123_followup3_nan0_sensitivity_part1.py).
from pathlib import Path as _P  # PATH (rebuild)
ROOT = _P(__file__).resolve().parent.parent  # PATH (rebuild): rq3_rebuild/
INTER = ROOT / "intermediate"  # PATH (rebuild): replaces scratch rq3_recompute/ and rq3_recompute/followup/
# Verbatim inline code from transcript command #123 (2026-10-12T04:04:18.763Z, tool_use toolu_01FrgHWpPHuhbusD1xBm32BN),
# originally run as `python - <<'EOF'` with cwd = .../scratchpad/rq3_recompute
import pandas as pd
f=pd.read_csv(ROOT / "data_fix2/file_level_wide.csv",encoding="utf-8-sig")  # PATH (rebuild)
m=pd.read_csv(INTER / "data_fix/method_level_wide.csv",encoding="utf-8-sig")  # PATH (rebuild)
m=m[~m.commit_url.str.contains("/openjdk/lilliput/commit/7f80683")].reset_index(drop=True)
assert (f.commit_url.values==m.commit_url.values).all()
num=[c for c in f.columns if c not in ("commit_url","type_name")]
f[num]=f[num].fillna(0); m[num]=m[num].fillna(0)
f.to_csv(ROOT / "sensitivity_nan0/data_nan0/file_level_wide.csv",index=False,encoding="utf-8-sig"); m.to_csv(ROOT / "sensitivity_nan0/data_nan0/method_level_wide.csv",index=False,encoding="utf-8-sig")  # PATH (rebuild)
print(len(f), f.commit_url.nunique())
