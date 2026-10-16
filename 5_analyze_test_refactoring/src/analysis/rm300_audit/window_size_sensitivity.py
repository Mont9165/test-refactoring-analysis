import csv
from scipy.stats import wilcoxon, rankdata
import numpy as np
rows = [r for r in csv.DictReader(open('outputs/adjacent_windows_v2.csv'))
        if not r['sha'].startswith(('238654e', '33e64d6'))]
print('commits', len(rows))
def counts(s, k):
    v = [int(x) for x in s.split()][:k] if s.strip() else []
    return [max(x, 0) for x in v]          # RM failure (-1) -> 0
def rrb(d):
    d = np.array([x for x in d if x != 0], float)
    rk = rankdata(np.abs(d)); wp = rk[d > 0].sum(); wm = rk[d < 0].sum()
    return (wp - wm) / (wp + wm)
for k in (1, 2, 3):
    out = []
    for side, base in (('pre', 'base'), ('fol', 'base_fol')):
        hit = sum(any(c > 0 for c in counts(r[f'{side}_counts'], k)) for r in rows)
        withb = [r for r in rows if int(r[f'n_{base}'] or 0) > 0]
        bhit = sum(any(c > 0 for c in counts(r[f'{base}_counts'], k)) for r in withb)
        x = [sum(counts(r[f'{side}_counts'], k)) for r in withb]
        y = [sum(counts(r[f'{base}_counts'], k)) for r in withb]
        p = wilcoxon(x, y).pvalue
        out.append(f'{side}: {hit}/{len(rows)}={100*hit/len(rows):.1f}%  base {bhit}/{len(withb)}={100*bhit/len(withb):.1f}%  p={p:.4f} r={rrb(np.array(x)-np.array(y)):.2f}')
    print(f'k={k}:', ' | '.join(out))
