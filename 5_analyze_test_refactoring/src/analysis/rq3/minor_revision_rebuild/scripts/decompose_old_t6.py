# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: scratchpad/decompose_old_t6.py).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/decompose_old_t6.py).
"""Decompose the old Table-6 counting (all pair x smell cells, unmeasured -> 0) at the file level, 403 pairs."""
from pathlib import Path as _P  # PATH (rebuild)
ROOT = _P(__file__).resolve().parent.parent  # PATH (rebuild): rq3_rebuild/
INTER = ROOT / "intermediate"  # PATH (rebuild): replaces scratch rq3_recompute/ and rq3_recompute/followup/

import json, sys
import numpy as np, pandas as pd
R = None  # PATH (rebuild)
ANN = (__import__("pathlib").Path(__file__).resolve().parents[6] / "5_analyze_test_refactoring/src/results/annotation_result_2024-02-20.json")
f = pd.read_csv(INTER / "data_orig/file_level_wide.csv", encoding="utf-8-sig")  # PATH (rebuild)
ann = json.load(open(ANN, encoding="utf-8"))
order = sorted(range(len(ann)), key=lambda i: (ann[i]["url"], i))
ann_s = [ann[i] for i in order]
assert all(a["url"] == u and a["type_name"] == t for a, u, t in zip(ann_s, f.commit_url, f.type_name))
def has(a, side):
    for v in (a["parameter_data"].get(side) or {}).values():
        for e in (v or {}).get("elements") or []:
            if e and isinstance(e, dict) and (e.get("location") or {}).get("path"):
                return True
    return False
f["hb"] = [has(a, "before") for a in ann_s]; f["ha"] = [has(a, "after") for a in ann_s]
f = f[~f.type_name.eq("Lambdarize Method")].reset_index(drop=True)
SM = ["Assertion Roulette","Conditional Test Logic","Constructor Initialization","Default Test","Empty Test",
      "Exception Catching Throwing","General Fixture","Mystery Guest","Print Statement","Redundant Assertion",
      "Sensitive Equality","Sleepy Test","Eager Test","Lazy Test","Duplicate Assert","Unknown Test","IgnoredTest",
      "Resource Optimism","Magic Number Test"]
assert len(SM) == 19 and len(f) == 403
rows = []
for s in SM:
    b = f[f"{s}_before"].to_numpy(float); a = f[f"{s}_after"].to_numpy(float)
    ub = np.isnan(b) | ~f.hb.to_numpy() | f["Assertion Roulette_before"].isna().to_numpy(); ua = np.isnan(a) | ~f.ha.to_numpy() | f["Assertion Roulette_after"].isna().to_numpy()
    b0 = np.where(ub, 0, np.nan_to_num(b)); a0 = np.where(ua, 0, np.nan_to_num(a))
    meas = ~ub & ~ua
    for name, m in [("absent_0to0 (measured)", meas & (b0 == 0) & (a0 == 0)),
                    ("present_unchanged (measured)", meas & (b0 == a0) & (b0 > 0)),
                    ("improve (measured)", meas & (a0 < b0)), ("degrade (measured)", meas & (a0 > b0)),
                    ("unmeasured -> 0to0 (old: no change)", ~meas & (b0 == a0)),
                    ("unmeasured -> spurious improve", ~meas & (a0 < b0)),
                    ("unmeasured -> spurious degrade", ~meas & (a0 > b0))]:
        rows.append((s, name, int(m.sum())))
d = pd.DataFrame(rows, columns=["smell", "cat", "n"])
tot = d.groupby("cat").n.sum(); N = tot.sum()
print(f"cells = {N} (403 pairs x 19 smells)")
for k, v in tot.items():
    print(f"  {k:40s} {v:5d}  {100*v/N:5.1f}%")
oldnc = tot["absent_0to0 (measured)"] + tot["present_unchanged (measured)"] + tot["unmeasured -> 0to0 (old: no change)"]
print(f"old 'No Change' total {oldnc} = {100*oldnc/N:.1f}%")
print("spurious changes by smell:")
sp = d[d.cat.str.startswith("unmeasured -> spurious")].pivot(index="smell", columns="cat", values="n")
print(sp[sp.sum(axis=1) > 0].to_string())
meas_tot = N - tot[[c for c in tot.index if c.startswith("unmeasured")]].sum()
print(f"measured cells {meas_tot}; absent share among measured {100*tot['absent_0to0 (measured)']/meas_tot:.1f}%")
print("measured pairs per smell:", {s: int(d[(d.smell == s) & ~d.cat.str.startswith("unmeasured")].n.sum()) for s in ["Assertion Roulette", "Eager Test", "Lazy Test"]})
fx = pd.read_csv(ROOT / "data_fix2/file_level_wide.csv", encoding="utf-8-sig")  # PATH (rebuild)
print("data_fix2 rows", len(fx), "Eager both measured", int((fx["Eager Test_before"].notna() & fx["Eager Test_after"].notna()).sum()),
      "Lazy", int((fx["Lazy Test_before"].notna() & fx["Lazy Test_after"].notna()).sum()))
ms = d[~d.cat.str.startswith("unmeasured")].groupby("smell").n.sum()
print(ms[ms != 379].to_dict(), "sum", int(ms.sum()))
