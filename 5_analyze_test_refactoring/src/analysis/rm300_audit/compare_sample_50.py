"""Step 2: sensitivity-sample statistics (Section 4.3.2 of the paper).

Reproduces:
  - Cohen's kappa = 0.81 and reconciled precision 0.88 (44/50) on the
    50-detection stratified sample (two independent raters);
  - the bridge sentence: 43 of the 50 detections are reproduced identically
    by RefactoringMiner 3.0.0, with precision unchanged at 0.88 (38/43);
  - the pool size: 1,756 test-file detections under 3.0.0 (via
    rq1/rm_sensitivity/sample_rm_detections.py over the step-1 JSONs).

Inputs: the validated sample (manual_validation_sample_linked.csv) and the
two rater files at the repository root
("test-refactoring-precision - manual_validation_sample_{kan,kosei}.csv").
"""
import csv
import json
import math
import re
from collections import Counter

from rm_runner import REPO_ROOT, JSONS

SENS = REPO_ROOT / "5_analyze_test_refactoring/src/analysis/rq1/rm_sensitivity"
URL_RE = re.compile(r"https://github\.com/[^/]+/[^/]+/commit/([0-9a-f]+)")


def key(row):
    return (URL_RE.match(row["commit_url"]).group(1), row["rm_description"].strip())


def load_rater(path):
    """The rater CSVs carry the human judgement in the `label` column (TRUE/FALSE)."""
    d = {}
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        m = URL_RE.match((r.get("commit_url") or r.get("url") or "").strip())
        if m:
            d[(m.group(1), r["rm_description"].strip())] = str(r.get("label") or r.get("is_correct") or "").strip()
    return d


def kappa(pairs):
    agree = sum(1 for a, b in pairs if a == b) / len(pairs)
    ca = Counter(a for a, _ in pairs)
    cb = Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / len(pairs) ** 2
    return (agree - pe) / (1 - pe), agree


def wilson(c, n, z=1.96):
    p = c / n
    lo = (p + z * z / (2 * n) - z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)) / (1 + z * z / n)
    hi = (p + z * z / (2 * n) + z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)) / (1 + z * z / n)
    return lo, hi


def main():
    rows = list(csv.DictReader(open(SENS / "manual_validation_sample_linked.csv", encoding="utf-8-sig")))
    ra = load_rater(REPO_ROOT / "test-refactoring-precision - manual_validation_sample_kan.csv")
    rb = load_rater(REPO_ROOT / "test-refactoring-precision - manual_validation_sample_kosei.csv")

    pairs = [(ra[key(r)], rb[key(r)]) for r in rows]
    k, agree = kappa(pairs)
    correct = sum(1 for r in rows if str(r["is_correct"]).strip() in ("1", "Y", "y", "TRUE", "True"))
    lo, hi = wilson(correct, len(rows))
    print(f"full sample: n={len(rows)}, agreement={agree:.3f}, kappa={k:.2f}, "
          f"precision={correct}/{len(rows)}={correct/len(rows):.2f}, Wilson95=[{lo:.2f},{hi:.2f}]")

    # 3.0.0 reproduction: identical (type, description) present in the step-1 JSON.
    reproduced = []
    for r in rows:
        sha = URL_RE.match(r["commit_url"]).group(1)
        data = json.loads((JSONS / f"{sha}.json").read_text())
        dets = [d for c in data.get("commits", []) for d in c.get("refactorings", [])]
        if any(d.get("type") == r["rm_type"]
               and d.get("description", "").strip() == r["rm_description"].strip() for d in dets):
            reproduced.append(r)
    c43 = sum(1 for r in reproduced if str(r["is_correct"]).strip() in ("1", "Y", "y", "TRUE", "True"))
    print(f"reproduced identically by RM 3.0.0: {len(reproduced)}/{len(rows)}; "
          f"precision on that subset: {c43}/{len(reproduced)}={c43/len(reproduced):.2f}")


if __name__ == "__main__":
    main()
