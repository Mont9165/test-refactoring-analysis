"""B5 (Reviewer R3-14): Power analysis to justify the n>=5 threshold used
when running Wilcoxon signed-rank tests on test-smell pairs.

Two complementary computations are reported:
  (1) For each n in [3..30] and α=0.05 (two-tailed), what is the smallest
      attainable p-value (extreme rank configuration)? This is purely a
      property of the Wilcoxon statistic and tells us when the test can
      reject H0 *at all*.
  (2) Approximate post-hoc power vs sample size for medium (r=0.3) and
      large (r=0.5) effect sizes, using the t-test approximation
      (paired t-test gives a close upper bound on Wilcoxon's power).

Output: text summary printed to stdout + power_analysis.csv with the
        per-n table, suitable for citing in the response letter.

Usage:
    python power_analysis.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import wilcoxon, norm


def smallest_attainable_pvalue(n: int) -> float:
    """For Wilcoxon signed-rank with n nonzero pairs, the smallest two-tailed
    p-value occurs when all differences agree in sign (W = 0 or W = n(n+1)/2).
    """
    if n <= 0:
        return 1.0
    diffs_pos = [1.0] * n
    diffs_zero = [0.0] * n
    try:
        _, p = wilcoxon(diffs_pos, diffs_zero, alternative="two-sided",
                        zero_method="wilcox", correction=False, method="auto")
        return float(p)
    except Exception:
        return float("nan")


def paired_t_power_n_required(effect_size: float, alpha: float = 0.05,
                              power: float = 0.80) -> int:
    """Required n for paired t-test to reach `power` at given effect size.

    Closed form via normal approximation (Cohen 1988):
        n = ((z_{1-alpha/2} + z_{power}) / effect)^2
    """
    z_alpha = norm.ppf(1 - alpha / 2)
    z_power = norm.ppf(power)
    n = ((z_alpha + z_power) / effect_size) ** 2
    return max(2, math.ceil(n))


def paired_t_power(n: int, effect_size: float, alpha: float = 0.05) -> float:
    """Approximate power of a paired t-test (≥ Wilcoxon power)."""
    if n < 2:
        return 0.0
    z_alpha = norm.ppf(1 - alpha / 2)
    ncp = effect_size * math.sqrt(n)
    return 1.0 - norm.cdf(z_alpha - ncp) + norm.cdf(-z_alpha - ncp)


def main() -> int:
    here = Path(__file__).resolve().parent
    rows = []
    for n in range(3, 31):
        rows.append({
            "n": n,
            "min_attainable_p_two_tailed": smallest_attainable_pvalue(n),
            "power_at_r_0.30": paired_t_power(n, 0.30),
            "power_at_r_0.50": paired_t_power(n, 0.50),
            "power_at_r_0.80": paired_t_power(n, 0.80),
        })
    df = pd.DataFrame(rows)
    out_path = here / "power_analysis.csv"
    df.to_csv(out_path, index=False)
    print(f"[done] {out_path}\n")

    print("Wilcoxon signed-rank: smallest two-tailed p-value attainable per n")
    print("-" * 70)
    print(df[["n", "min_attainable_p_two_tailed"]].to_string(index=False))

    n5_p = df.loc[df["n"] == 5, "min_attainable_p_two_tailed"].iloc[0]
    n6_p = df.loc[df["n"] == 6, "min_attainable_p_two_tailed"].iloc[0]
    print()
    print(f"At n=5, the smallest two-tailed p-value Wilcoxon can produce is {n5_p:.4f}.")
    print(f"At n=6, it drops to {n6_p:.4f} — the first n at which the test can reject H0 at α=0.05 two-tailed.")

    print()
    print("Required n for paired t-test (≥ Wilcoxon) at α=0.05, power=0.80:")
    print(f"  small  effect r=0.20: n ≥ {paired_t_power_n_required(0.20)}")
    print(f"  medium effect r=0.30: n ≥ {paired_t_power_n_required(0.30)}")
    print(f"  large  effect r=0.50: n ≥ {paired_t_power_n_required(0.50)}")
    print(f"  v.large       r=0.80: n ≥ {paired_t_power_n_required(0.80)}")

    print()
    print("Power achievable at n=5 (paired t-test, two-tailed α=0.05):")
    for r in (0.30, 0.50, 0.80, 1.20):
        print(f"  r={r}: power ≈ {paired_t_power(5, r):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
