# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: rq3_recompute/followup/build_fixed.py).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/rq3_recompute/followup/build_fixed.py).
"""Build the corrected RQ3 tables:
  data_fix/        : 403-row CEV data minus the 21 one-sided pairs (=382), NaN cells kept as empty (missing)
  data_fix_mmask/  : same, plus method-level cells blanked where the file-level cell is NaN on either side
                     (sensitivity: unmeasured Eager/Lazy etc. at method level)
Row alignment: data_orig (405 rows) == annotation JSON sorted by (url, index) (verified 405/405)."""
import csv
from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent.parent / "intermediate"  # PATH (rebuild)
fl = pd.read_pickle(HERE / "flags_405.pkl")              # 405 rows, aligned with data_orig
keep405 = (~fl.lam) & (fl.sides == "both")             # drop Lambdarize + one-sided
EXC = {'Replace try/catch with asserThrows', 'Replace annotation with assertThrow', 'Replace try/catch with annotation',
       'Replace assertThrow with try/catch', 'Replace annotation with try/catch'}

def read(path):
    text = Path(path).read_bytes().decode("utf-8-sig")
    rows = list(csv.reader(text.splitlines()))
    return rows[0], rows[1:]

out = {}
for lvl in ("file", "method"):
    hdr, body = read(HERE / "data_orig" / f"{lvl}_level_wide.csv")  # PATH (rebuild)
    assert len(body) == len(fl)
    ti, ui = hdr.index("type_name"), hdr.index("commit_url")
    for r, (_, fr) in zip(body, fl.iterrows()):
        assert r[ui] == fr.commit_url and r[ti] == fr.type_name
    kept = []
    for r, k in zip(body, keep405):
        if not k:
            continue
        r = list(r)
        if r[ti] in EXC:
            r[ti] = "Change Exception Verification"
        kept.append(r)
    out[lvl] = (hdr, kept)

def write(d, lvl, hdr, rows):
    with open(HERE / d / f"{lvl}_level_wide.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(hdr); w.writerows(rows)

for lvl in ("file", "method"):
    write("data_fix", lvl, *out[lvl])
# sensitivity: propagate file-level NaN mask to method level
fh_, frows = out["file"]; mh, mrows = out["method"]
assert fh_ == mh
mm = []
blank = Counter()
for fr, mr in zip(frows, mrows):
    assert fr[0] == mr[0] and fr[1] == mr[1]
    mr = list(mr)
    for j, col in enumerate(mh):
        if col.endswith(("_before", "_after", "_diff")):
            base = col.rsplit("_", 1)[0]
            jb, ja = mh.index(base + "_before"), mh.index(base + "_after")
            if fr[jb] == "" or fr[ja] == "":
                mr[j] = ""
                if col.endswith("_before"): blank[base] += 1
    mm.append(mr)
write("data_fix_mmask", "file", fh_, frows)
write("data_fix_mmask", "method", mh, mm)
print("method-level cells blanked in sensitivity variant (per smell, pairs):", dict(blank))

# ---- summary ----
f = pd.read_csv(HERE / "data_fix/file_level_wide.csv", encoding="utf-8-sig")
new403 = pd.read_csv(HERE / "data_new/file_level_wide.csv", encoding="utf-8-sig")  # PATH (rebuild)
print("rows:", len(f), " commits:", f.commit_url.nunique(), " (403-row data commits:", new403.commit_url.nunique(), ")")
gone = sorted(set(new403.commit_url) - set(f.commit_url))
print("commits lost entirely (all pairs one-sided):", len(gone))
for u in gone:
    print("   ", u.split("github.com/")[1][:70], dict(Counter(new403[new403.commit_url == u].type_name)))
print("type counts after exclusion (changed ones):")
a, b = Counter(new403.type_name), Counter(f.type_name)
for t in sorted(a, key=lambda t: -a[t]):
    if a[t] != b.get(t, 0):
        print(f"    {t:30s} {a[t]} -> {b.get(t,0)}")
EX = {"NumberOfMethods", "Verbose Test", "Dependent Test"}
sm19 = [c[:-7] for c in f.columns if c.endswith("_before") and c[:-7] not in EX]
print("measured file-level pairs per smell (both sides non-NaN):")
for s in sm19:
    ok = f[f"{s}_before"].notna() & f[f"{s}_after"].notna()
    cm = f[ok].commit_url.nunique()
    print(f"    {s:28s} pairs {int(ok.sum())}/{len(f)}  commits {cm}/{f.commit_url.nunique()}")
