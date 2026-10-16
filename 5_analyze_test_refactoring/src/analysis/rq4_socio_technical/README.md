# Motivations for test refactorings (paper, Section 6.1)

This directory holds the data and scripts for the motivation analysis in
Section 6.1 of the paper (Table 9). The category definitions are in
[`CODEBOOK.md`](CODEBOOK.md).

## Files

| File | Contents |
|---|---|
| `enrich_with_pr_context.py` | Collects, for every (commit, refactoring type) pair in the RQ3 data, the full commit message and, if the commit belongs to a pull request, its title, description, comments and reviews (GitHub API through the `gh` CLI). Writes `socio_technical_annotation.csv`. |
| `auto_hint_triggers.py` | Adds keyword-based hints for the coders (`auto_hint_*` columns). Writes `socio_technical_annotation_with_hints.csv`. |
| `annotation_template.csv` | Empty coding sheet. |
| `motivation_coding_final.csv` | Final coding: one row per (commit, refactoring type) pair, with the context above, the labels of the two coders (`category_kosei`, `category_fujiwara`), the reconciled label (`final label`) and the coders' notes. |
| `compute_motivation_kappa.py` | Computes Cohen's kappa and the reconciled distribution. |

## Reproducing the paper's numbers

```bash
python compute_motivation_kappa.py
```

The CSV has 187 rows. The script drops the 2 rows of `Lambdarize Method`,
which the minor revision removed from the catalogue because it is a general
refactoring. This leaves 185 cases: the coders agreed in 176 of them (95.1%,
Cohen's kappa = 0.93), and the reconciled distribution matches Table 9
(`not_documented` 96 cases, 51.9%).
