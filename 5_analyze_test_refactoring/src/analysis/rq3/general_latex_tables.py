import pandas as pd

# ファイルパス（必要に応じて修正）
change_summary_path = "detailed_visualization/detailed_change_analysis_file.csv"
outlier_summary_path = "detailed_visualization/outlier_analysis_file.csv"
significant_path = "refactoring_smell_relationship/best_refactorings_file.csv"
effectiveness_path = "detailed_visualization/refactoring_effectiveness_file.csv"

def to_latex_table(df, caption, label, columns, floatfmt=None):
    latex = "\\begin{table}[htbp]\n\\centering\n"
    latex += f"\\caption{{{caption}}}\n"
    latex += f"\\label{{{label}}}\n"
    latex += df.to_latex(index=False, columns=columns, float_format=floatfmt, escape=False)
    latex += "\\end{table}\n"
    return latex

# 1. 全体サマリ表
change_df = pd.read_csv(change_summary_path)
change_df["Improved_pct"] = (change_df["improved"] / change_df["total"] * 100).round(1)
change_df["Degraded_pct"] = (change_df["degraded"] / change_df["total"] * 100).round(1)
change_df["Unchanged_pct"] = (change_df["unchanged"] / change_df["total"] * 100).round(1)
summary_cols = ["test_smell", "improved", "Improved_pct", "degraded", "Degraded_pct", "unchanged", "Unchanged_pct", "total"]
print(to_latex_table(change_df, "Test smell changes after refactoring (file level)", "tab:test-smell-change-summary", summary_cols))

# 2. 外れ値サマリ表
outlier_df = pd.read_csv(outlier_summary_path)
outlier_df["outlier_percentage"] = outlier_df["outlier_percentage"].round(1)
outlier_cols = ["test_smell", "outlier_count", "outlier_percentage", "max_outlier", "min_outlier"]
print(to_latex_table(outlier_df, "Outlier summary for each test smell (file level)", "tab:outlier-summary", outlier_cols))

# 3. 有意な改善・悪化の組み合わせ表
sig_df = pd.read_csv(significant_path)
sig_cols = ["test_smell", "refactoring_type", "improvement_rate", "effect_size", "p_value", "significant"]
sig_df = sig_df[sig_df["significant"] == True]
print(to_latex_table(sig_df, "Statistically significant test smell improvements", "tab:significant-improvements", sig_cols, floatfmt="%.3f"))

# 4. リファクタリングタイプ×テストスメルの効果表（抜粋例）
eff_df = pd.read_csv(effectiveness_path)
eff_cols = ["refactoring_type", "test_smell", "improvement_rate", "effect_size", "p_value", "sample_size", "significant"]
print(to_latex_table(eff_df, "Effectiveness of refactoring types for test smell reduction", "tab:refactoring-type-effect", eff_cols, floatfmt="%.3f"))