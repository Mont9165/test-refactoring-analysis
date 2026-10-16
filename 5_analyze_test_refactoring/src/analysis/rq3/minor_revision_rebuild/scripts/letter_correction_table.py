"""Rows of the correction table in the round-2 response letter (file level, 403 pairs x 19 smells).

A side of a cell counts as "not measured" when the annotation marks no code on
that side or the cell itself has no tsDetect value. Both sides of the three
openjdk/lilliput 7f80683 rows count as not measured, because tsDetect reported
no smell values for that commit. Unlike decompose_old_t6.py,
a missing Assertion Roulette value does not mark the whole side as unmeasured,
so camunda 5831979 (Add Conditional Annotation) x Empty Test, whose after value
is 0, falls into "not measured / 0" (580/177 instead of 581/176).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
ANN = (__import__("pathlib").Path(__file__).resolve().parents[6] / "5_analyze_test_refactoring/src/results/annotation_result_2024-02-20.json")
f = pd.read_csv(ROOT / "intermediate/data_orig/file_level_wide.csv", encoding="utf-8-sig")
ann = json.load(open(ANN, encoding="utf-8"))
ann_s = [ann[i] for i in sorted(range(len(ann)), key=lambda i: (ann[i]["url"], i))]
assert all(a["url"] == u and a["type_name"] == t for a, u, t in zip(ann_s, f.commit_url, f.type_name))


def has(a, side):
    for v in (a["parameter_data"].get(side) or {}).values():
        for e in (v or {}).get("elements") or []:
            if e and isinstance(e, dict) and (e.get("location") or {}).get("path"):
                return True
    return False


f["hb"] = [has(a, "before") for a in ann_s]
f["ha"] = [has(a, "after") for a in ann_s]
f = f[~f.type_name.eq("Lambdarize Method")].reset_index(drop=True)
SM = ["Assertion Roulette", "Conditional Test Logic", "Constructor Initialization", "Default Test", "Empty Test",
      "Exception Catching Throwing", "General Fixture", "Mystery Guest", "Print Statement", "Redundant Assertion",
      "Sensitive Equality", "Sleepy Test", "Eager Test", "Lazy Test", "Duplicate Assert", "Unknown Test", "IgnoredTest",
      "Resource Optimism", "Magic Number Test"]
assert len(SM) == 19 and len(f) == 403
lilliput = f.commit_url.str.contains("7f80683").to_numpy()
excluded_rows = ~(f.hb & f.ha).to_numpy() | lilliput
cnt = {}
for s in SM:
    b = f[f"{s}_before"].to_numpy(float)
    a = f[f"{s}_after"].to_numpy(float)
    ub = np.isnan(b) | ~f.hb.to_numpy() | lilliput
    ua = np.isnan(a) | ~f.ha.to_numpy() | lilliput
    for i in range(len(f)):
        lb = "not measured" if ub[i] else ("0" if b[i] == 0 else "1 or more")
        la = "not measured" if ua[i] else ("0" if a[i] == 0 else "1 or more")
        if excluded_rows[i] or ub[i] or ua[i]:
            key = (lb, la, "excluded")
        else:
            key = (lb, la, "kept")
        cnt[key] = cnt.get(key, 0) + 1
print("excluded instances:", int(excluded_rows.sum()))
for k in sorted(cnt):
    if k[2] == "excluded" or k[:2] == ("0", "0"):
        print(f"{k[0]:>13} | {k[1]:>13} | {k[2]:8} | {cnt[k]}")
print("excluded cells total:", sum(v for k, v in cnt.items() if k[2] == "excluded"))
