"""NEW (written for the rebuild, not recovered from the transcript): recompute the paper's verified RQ3
numbers from data_fix2/ + out_fix2/ + intermediate/ and compare them with the expected values.
Run after run_all.sh."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INTER = ROOT / "intermediate"
D2, O2 = ROOT / "data_fix2", ROOT / "out_fix2"
ANN = (__import__("pathlib").Path(__file__).resolve().parents[6] / "5_analyze_test_refactoring/src/results/annotation_result_2024-02-20.json")
EX = {"NumberOfMethods", "Verbose Test", "Dependent Test"}

rows = []
def chk(item, expected, got, ok=None):
    if ok is None:
        ok = str(expected) == str(got)
    rows.append((item, str(expected), str(got), "OK" if ok else "DIFF"))

f = pd.read_csv(D2 / "file_level_wide.csv", encoding="utf-8-sig")
m = pd.read_csv(D2 / "method_level_wide.csv", encoding="utf-8-sig")
chk("file level: instances / commits", "379 / 145", f"{len(f)} / {f.commit_url.nunique()}")
chk("refactoring level: instances / commits", "379 / 145", f"{len(m)} / {m.commit_url.nunique()}")

# exclusions: 403 -> 382 (one-sided) -> 379 (lilliput 7f80683)
new403 = pd.read_csv(INTER / "data_new/file_level_wide.csv", encoding="utf-8-sig")
fix = pd.read_csv(INTER / "data_fix/file_level_wide.csv", encoding="utf-8-sig")
lil = int(fix.commit_url.str.contains("/openjdk/lilliput/commit/7f80683").sum())
chk("excluded = one-sided + lilliput 7f80683", "24 = 21 + 3", f"{len(new403) - len(f)} = {len(new403) - len(fix)} + {lil}")
smc = [c for c in fix.columns if c.endswith(("_before", "_after")) and not c.startswith(("NumberOfMethods", "Empty Test"))]
lr = fix[fix.commit_url.str.contains("/openjdk/lilliput/commit/7f80683")]
chk("lilliput rows: all tsDetect smell cells NaN (excl. NOM/Empty Test)", True, bool(lr[smc].isna().all().all()))

ok = f["Eager Test_before"].notna() & f["Eager Test_after"].notna()
okl = f["Lazy Test_before"].notna() & f["Lazy Test_after"].notna()
chk("Eager Test measured: instances / commits", "139 / 63", f"{int(ok.sum())} / {f[ok].commit_url.nunique()}")
chk("Lazy Test measured: instances / commits", "139 / 63", f"{int(okl.sum())} / {f[okl].commit_url.nunique()}")

# Table 6 (same formula as table6_prevalence_fix2.py)
def t6(df):
    sm = [c[:-7] for c in df.columns if c.endswith("_before") and c[:-7] not in EX]
    ab = nc = imp = deg = 0
    for s in sm:
        b, a = df[f"{s}_before"], df[f"{s}_after"]; k = b.notna() & a.notna(); b, a = b[k], a[k]
        ab += int(((b == 0) & (a == 0)).sum()); nc += int(((b == a) & (b > 0)).sum())
        imp += int((a < b).sum()); deg += int((a > b).sum())
    t = ab + nc + imp + deg; p = nc + imp + deg
    return t, ab, nc, imp, deg, p
for lvl, df, e4, ep in (("File", f, "71.0/17.1/6.9/5.0", "59.0/23.9/17.1"), ("Refactoring", m, "82.4/10.7/4.3/2.7", "60.4/24.4/15.3")):
    t, ab, nc, imp, deg, p = t6(df)
    chk(f"Table 6 {lvl}: NotPresent/NoChange/Imp/Deg %", e4, f"{100*ab/t:.1f}/{100*nc/t:.1f}/{100*imp/t:.1f}/{100*deg/t:.1f}")
    chk(f"Table 6 {lvl} present-only: unchanged/imp/deg %", ep, f"{100*nc/p:.1f}/{100*imp/p:.1f}/{100*deg/p:.1f}")
    rows.append((f"   (cells {lvl})", "", f"total={t} 0/0={ab} nochange={nc} imp={imp} deg={deg} present-base={p}", "info"))

# Spearman pairs (contradictory_smells.py output)
al = pd.read_csv(O2 / "contradictory_smells_file_all.csv")
def pair(a_, b_):
    return al[((al.smell_a == a_) & (al.smell_b == b_)) | ((al.smell_a == b_) & (al.smell_b == a_))].iloc[0]
r = pair("Conditional Test Logic", "Duplicate Assert")
chk("Spearman CTL vs DA: rho / p / n", "-0.62 / ~1.7e-41 / 379", f"{r.spearman_rho:.2f} / {r.p_value:.2e} / {r.n_paired_commits}",
    ok=round(r.spearman_rho, 2) == -0.62 and abs(r.p_value / 1.7e-41 - 1) < 0.05 and r.n_paired_commits == 379)
r = pair("Duplicate Assert", "Mystery Guest")
chk("Spearman DA vs MG: rho / p", "-0.39 / ~3.3e-15", f"{r.spearman_rho:.2f} / {r.p_value:.2e}",
    ok=round(r.spearman_rho, 2) == -0.39 and abs(r.p_value / 3.3e-15 - 1) < 0.05)

# 403-row file-level cell decomposition (decompose_old_t6.py logic: unmeasured = NaN, one-sided annotation side,
# or lilliput row [Assertion Roulette NaN]); then split the 824 unmeasured 0->0 cells by which side was unmeasured
fo = pd.read_csv(INTER / "data_orig/file_level_wide.csv", encoding="utf-8-sig")
ann = json.load(open(ANN, encoding="utf-8"))
order = sorted(range(len(ann)), key=lambda i: (ann[i]["url"], i)); ann_s = [ann[i] for i in order]
assert all(a["url"] == u and a["type_name"] == t for a, u, t in zip(ann_s, fo.commit_url, fo.type_name))
def has(a, side):
    for v in (a["parameter_data"].get(side) or {}).values():
        for e in (v or {}).get("elements") or []:
            if e and isinstance(e, dict) and (e.get("location") or {}).get("path"):
                return True
    return False
fo["hb"] = [has(a, "before") for a in ann_s]; fo["ha"] = [has(a, "after") for a in ann_s]
fo = fo[~fo.type_name.eq("Lambdarize Method")].reset_index(drop=True)
SM = [c[:-7] for c in fo.columns if c.endswith("_before") and c[:-7] not in EX]
nana = nan0 = zna = zz = 0
for s in SM:
    b = fo[f"{s}_before"].to_numpy(float); a = fo[f"{s}_after"].to_numpy(float)
    ub = np.isnan(b) | ~fo.hb.to_numpy() | fo["Assertion Roulette_before"].isna().to_numpy()
    ua = np.isnan(a) | ~fo.ha.to_numpy() | fo["Assertion Roulette_after"].isna().to_numpy()
    b0 = np.where(ub, 0, np.nan_to_num(b)); a0 = np.where(ua, 0, np.nan_to_num(a))
    same0 = (b0 == a0) & ~(~ub & ~ua)
    nana += int((same0 & ub & ua).sum()); nan0 += int((same0 & ub & ~ua).sum()); zna += int((same0 & ~ub & ua).sum())
    zz += int((~ub & ~ua & (b0 == 0) & (a0 == 0)).sum())
chk("unmeasured 0->0 cells = NA/NA + NA/0 + 0/NA [side unmeasured if NaN, no annotation, or AR NaN on that side = decompose_old_t6 rule]",
    "824 = 580 + 177 + 67", f"{nana + nan0 + zna} = {nana} + {nan0} + {zna}")
# variant: the AR-NaN rule replaced by "row belongs to openjdk/lilliput 7f80683" (both sides unmeasured). The only cell
# that differs is camunda 5831979 Add Conditional Annotation x Empty Test (no-before pair; after-side Empty Test = 0
# while every other after-side smell is NaN).
lilrow = fo.commit_url.str.contains("/openjdk/lilliput/commit/7f80683").to_numpy()
nana = nan0 = zna = 0
for s in SM:
    b = fo[f"{s}_before"].to_numpy(float); a = fo[f"{s}_after"].to_numpy(float)
    ub = np.isnan(b) | ~fo.hb.to_numpy() | lilrow
    ua = np.isnan(a) | ~fo.ha.to_numpy() | lilrow
    b0 = np.where(ub, 0, np.nan_to_num(b)); a0 = np.where(ua, 0, np.nan_to_num(a))
    same0 = (b0 == a0) & ~(~ub & ~ua)
    nana += int((same0 & ub & ua).sum()); nan0 += int((same0 & ub & ~ua).sum()); zna += int((same0 & ~ub & ua).sum())
chk("  same split, lilliput-row rule instead of AR-NaN rule", "824 = 580 + 177 + 67", f"{nana + nan0 + zna} = {nana} + {nan0} + {zna}")
chk("measured 0/0 cells (403 pairs; = Not Present cells of data_fix2 file level)", "4771", f"{zz}")

# Mystery Guest increases (file level, data_fix2)
mg = f[f["Mystery Guest_after"] > f["Mystery Guest_before"]]
by = mg.commit_url.str.split("/").str[4].value_counts().to_dict()
chk("Mystery Guest increases (file level) by project", "23 = errai 22 + fluent-http 1", f"{len(mg)} = " + " + ".join(f"{k} {v}" for k, v in by.items()))

w = max(len(r[0]) for r in rows)
for it, e, g, s in rows:
    print(f"{s:4s}  {it:{w}s}  expected: {e:28s}  got: {g}")
