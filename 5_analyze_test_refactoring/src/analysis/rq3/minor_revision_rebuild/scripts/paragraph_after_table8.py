# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: rq3_recompute/scripts/paragraph_after_table8.py).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/rq3_recompute/scripts/paragraph_after_table8.py).
"""Reproduce/update the paragraph after Table 8 (Sec. 5.3.3) and Sec. 7.1:
per-type file-level effects from new_types_effect_sizes.py output, BH over the
file-level family (rows with valid p and n>=6), q<0.05.
Usage: python paragraph_after_table8.py <effect_sizes_dir> <data_dir>"""
import sys
import pandas as pd
from statsmodels.stats.multitest import multipletests
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300)
es_dir, data_dir = sys.argv[1], sys.argv[2]

def family(level, nfloor=6):
    d = pd.read_csv(f"{es_dir}/new_types_effect_sizes_{level}.csv")
    x = d[d.p_value.notna() & (d.n >= nfloor)].copy()
    x["q"] = multipletests(x.p_value, method="fdr_bh")[1]
    return x

for level in ("file", "method"):
    fam = family(level)
    print(f"\n######## {level}-level BH family: m={len(fam)} tests (valid p, n>=6)")
    sig = fam[fam.q < 0.05]
    for t, g in sig.groupby("refactoring_type"):
        red = g[(g.A12 > 0.5) & (g.smell != "NumberOfMethods")]
        inc = g[g.A12 < 0.5]
        rng = f"[{red.A12.min():.3f}, {red.A12.max():.3f}]" if len(red) else "-"
        print(f"  {t:30s} n={int(g.n.max()):3d} #sig={len(g):2d} lower-count smells (non-NOM)={len(red):2d} A12 {rng}; "
              f"higher-count: {list(inc.smell)}; NOM: " +
              (", ".join(f"A12={r.A12:.3f} median_diff={r.median_diff:g} q={r.q:.3g}" for r in g[g.smell == 'NumberOfMethods'].itertuples()) or "n.s."))
    for t in ("Change Exception Verification", "Replace try/catch with annotation", "Delete Mock Object", "Grouping Tests"):
        g = fam[fam.refactoring_type == t].sort_values("p_value")
        if len(g):
            print(f"\n  -- {t} ({level}) all tested rows:")
            print(g[["smell", "n", "improved", "degraded", "unchanged", "p_value", "q", "A12", "median_diff"]].to_string(index=False))

# instance-level detail for the merged type
EXC_NEW = "Change Exception Verification"
for level in ("file", "method"):
    df = pd.read_csv(f"{data_dir}/{level}_level_wide.csv", encoding="utf-8-sig")
    g = df[df.type_name == EXC_NEW]
    if g.empty:
        continue
    b, a = g["Exception Catching Throwing_before"], g["Exception Catching Throwing_after"]
    ok = b.notna() & a.notna()
    print(f"\n[{level}] CEV x Exception Catching Throwing: rows={len(g)}, complete pairs={int(ok.sum())}, "
          f"NaN before={int(b.isna().sum())} after={int(a.isna().sum())}")
    bb, aa = b.fillna(0), a.fillna(0)
    print(f"   NaN->0 : reduced={int((aa<bb).sum())}  removed to zero (before>0 & after==0)={int(((bb>0)&(aa==0)).sum())}  "
          f"increased={int((aa>bb).sum())}  unchanged={int((aa==bb).sum())}  (present before: {int((bb>0).sum())})")
    print(f"   NaN-drop: reduced={int((a[ok]<b[ok]).sum())}  removed to zero={int(((b[ok]>0)&(a[ok]==0)).sum())}  "
          f"increased={int((a[ok]>b[ok]).sum())}  unchanged={int((a[ok]==b[ok]).sum())}")
    # by commit
    gg = g.assign(before=bb, after=aa, sha=g.commit_url.str.extract(r"github.com/([^/]+/[^/]+)/commit/([0-9a-f]{7})").agg("/".join, axis=1))
    print(gg.groupby("sha").apply(lambda x: pd.Series(dict(rows=len(x), reduced=int((x.after<x.before).sum()), increased=int((x.after>x.before).sum()),
          unchanged=int((x.after==x.before).sum()), before_sum=x.before.sum(), after_sum=x.after.sum()))).to_string())
