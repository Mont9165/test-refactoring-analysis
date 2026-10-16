# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: rq3_recompute/followup/verify_flaws.py).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/rq3_recompute/followup/verify_flaws.py).
"""Verify (1) NaN structure of the file-level wide CSV and (2) one-sided annotations."""
import json
from collections import Counter
import numpy as np
import pandas as pd
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent / "intermediate"  # PATH (rebuild)

ANN = (__import__("pathlib").Path(__file__).resolve().parents[6] / "5_analyze_test_refactoring/src/results/annotation_result_2024-02-20.json")
D = HERE / "data_orig"  # PATH (rebuild)
f = pd.read_csv(f"{D}/file_level_wide.csv", encoding="utf-8-sig")
m = pd.read_csv(f"{D}/method_level_wide.csv", encoding="utf-8-sig")
ann = json.load(open(ANN, encoding="utf-8"))

# ---- alignment: sort by (url, original index) ----
order = sorted(range(len(ann)), key=lambda i: (ann[i]["url"], i))
ann_s = [ann[i] for i in order]
match = sum(a["url"] == u and a["type_name"] == t for a, u, t in zip(ann_s, f.commit_url, f.type_name))
print(f"alignment (url,type) matches: {match}/{len(f)}; wide CSV sorted by url: {list(f.commit_url) == sorted(f.commit_url)}")
# is the CSV order exactly the stable sort? check that within-url order of type names equals JSON original order
def side_has_elements(a, side):
    for k, v in (a["parameter_data"].get(side) or {}).items():
        for e in (v or {}).get("elements") or []:
            if e and isinstance(e, dict) and (e.get("location") or {}).get("path"):
                return True
    return False
def side_files(a, side):
    out = []
    for k, v in (a["parameter_data"].get(side) or {}).items():
        for e in (v or {}).get("elements") or []:
            if e and isinstance(e, dict) and (e.get("location") or {}).get("path"):
                out.append(e["location"]["path"])
    return out
f["has_before"] = [side_has_elements(a, "before") for a in ann_s]
f["has_after"] = [side_has_elements(a, "after") for a in ann_s]
f["before_files"] = [sorted({p.split("/")[-1] for p in side_files(a, "before")}) for a in ann_s]
f["after_files"] = [sorted({p.split("/")[-1] for p in side_files(a, "after")}) for a in ann_s]
f["sha7"] = f.commit_url.str.extract(r"/commit/([0-9a-f]{7})")[0]
f["repo"] = f.commit_url.str.extract(r"github.com/[^/]+/([^/]+)/commit")[0]
f["lam"] = f.type_name.eq("Lambdarize Method")
def cat(r):
    if r.has_before and r.has_after: return "both"
    if r.has_before: return "no-after"
    if r.has_after: return "no-before"
    return "neither"
f["sides"] = f.apply(cat, axis=1)
for scope, x in (("405 rows", f), ("403 rows (no Lambdarize)", f[~f.lam])):
    print(f"{scope}: side categories {dict(Counter(x.sides))}")
one = f[(~f.lam) & (f.sides != "both")]
print("\nOne-sided pairs (403 rows) by type:", dict(Counter(one.type_name)))
dmo = f[f.type_name == "Delete Mock Object"]
print("\nDelete Mock Object pairs:")
print(dmo[["repo", "sha7", "sides", "before_files", "after_files", "NumberOfMethods_before", "NumberOfMethods_after"]].to_string())
th = f[f.type_name == "Test Helper"]
print("\nTest Helper pairs:")
print(th[["repo", "sha7", "sides", "before_files", "after_files"]].to_string())
print("\nAll one-sided pairs:")
print(one[["repo", "sha7", "type_name", "sides", "NumberOfMethods_before", "NumberOfMethods_after"]].to_string())

# ---- NaN structure (file level) ----
sm = [c[:-7] for c in f.columns if c.endswith("_before") and c[:-7] + "_after" in f.columns]
print("\nfile-level NaN cells per smell (before/after) over 405 rows:")
nan_cols = {}
for s in sm:
    b, a = f[f"{s}_before"], f[f"{s}_after"]
    nb, na_ = int(b.isna().sum()), int(a.isna().sum())
    if nb or na_:
        both = int((b.isna() & a.isna()).sum()); ob = int((b.isna() & a.notna()).sum()); oa = int((b.notna() & a.isna()).sum())
        oa_pos = int((b.gt(0) & a.isna()).sum()); ob_pos = int((b.isna() & a.gt(0)).sum())
        nan_cols[s] = (nb, na_)
        print(f"  {s:28s} NaN before={nb:3d} after={na_:3d} | both={both:3d} only-after-NaN={oa:2d} (before>0: {oa_pos}) only-before-NaN={ob:2d} (after>0: {ob_pos})")
allnan = f[[f"{s}_{w}" for s in sm for w in ("before", "after")]].isna().all(axis=1)
print("rows with ALL smell cells NaN:", int(allnan.sum()), f[allnan][["repo", "sha7", "type_name", "sides"]].to_string())
# rows where every smell before is NaN, or every after
allb = f[[f"{s}_before" for s in sm]].isna().all(axis=1); alla = f[[f"{s}_after" for s in sm]].isna().all(axis=1)
print("rows all-before-NaN:", int(allb.sum()), " all-after-NaN:", int(alla.sum()))
# Eager/Lazy: count pairs with NaN on both sides, for 403 rows
x = f[~f.lam]
for s in ("Eager Test", "Lazy Test"):
    b, a = x[f"{s}_before"], x[f"{s}_after"]
    print(f"[403] {s}: both NaN={int((b.isna()&a.isna()).sum())}, before>0&after NaN={int((b.gt(0)&a.isna()).sum())}, before NaN&after>0={int((b.isna()&a.gt(0)).sum())}, measured both={int((b.notna()&a.notna()).sum())}")
print("method-level NaN cells:", int(m.isna().sum().sum()))
f.drop(columns=[c for c in f.columns if c.endswith(("_before", "_after", "_diff"))]).to_pickle(HERE / "flags_405.pkl")
