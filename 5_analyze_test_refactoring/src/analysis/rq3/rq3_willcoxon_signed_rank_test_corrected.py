import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy.stats import wilcoxon, norm
from statsmodels.stats.multitest import multipletests

# Directory settings
BASE_DIR = "/app"
CSV_DIR = f"{BASE_DIR}/5_analyze_test_refactoring/src/smells_result"
RESULTS_DIR = f"{BASE_DIR}/5_analyze_test_refactoring/src/analysis/rq3/statistical_analysis_corrected"

# Create output directory if it does not exist
os.makedirs(RESULTS_DIR, exist_ok=True)


def load_data():
    """Load the dataset from a CSV file."""
    file_level_path = f"{CSV_DIR}/file_level_wide.csv"
    method_level_path = f"{CSV_DIR}/method_level_wide.csv"
    file_df = pd.read_csv(file_level_path)
    method_df = pd.read_csv(method_level_path)
    return file_df, method_df


def calculate_effect_size_r(before, after):
    """
    Calculate effect size r for Wilcoxon signed-rank test using the correct formula.
    r = Z / sqrt(N) where Z is the standardized test statistic.
    """
    n = len(before)
    if n == 0:
        return 0.0
    
    # Calculate Wilcoxon statistic
    stat, p_value = wilcoxon(before, after)
    
    # Calculate Z statistic
    # For Wilcoxon signed-rank test: Z = (W - μ) / σ
    # where μ = n(n+1)/4 and σ = sqrt(n(n+1)(2n+1)/24)
    mu = n * (n + 1) / 4
    sigma = np.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    z = (stat - mu) / sigma
    
    # Effect size r
    r = z / np.sqrt(n)
    return r


def wilcoxon_signed_rank_test_corrected(df, level):
    """
    Perform Wilcoxon signed-rank test with correct effect size calculation.
    Include pairs with no change (0 difference) as valid samples.
    """
    results = []
    p_values = []
    
    for test_smell in df["test_smell"].unique():
        subset = df[df["test_smell"] == test_smell]
        before = subset["before_value"].values
        after = subset["after_value"].values
        n = len(subset)
        
        # Skip if sample size is too small
        if n < 5:
            print(f"Warning: Sample size too small for {test_smell} (n={n})")
            continue
        
        try:
            # Perform Wilcoxon test (including pairs with no change)
            stat, p_value = wilcoxon(before, after)
            
            # Calculate effect size
            effect_size_r = calculate_effect_size_r(before, after)
            
            # Count pairs with no change
            no_change_pairs = np.sum(before == after)
            
            results.append({
                "test_smell": test_smell,
                "sample_size": n,
                "no_change_pairs": no_change_pairs,
                "change_pairs": n - no_change_pairs,
                "Wilcoxon_stat": stat,
                "p_value": p_value,
                "effect_size_r": effect_size_r,
                "sample_size_adequate": n >= 20
            })
            p_values.append(p_value)
            
        except ValueError as e:
            print(f"Error in {test_smell}: {e}")
            continue
    
    # Multiple testing correction (separate for each level)
    if p_values:
        _, pvals_corrected, _, _ = multipletests(p_values, alpha=0.05, method='fdr_bh')
        for i, res in enumerate(results):
            res["p_value_corrected"] = pvals_corrected[i]
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(f"{RESULTS_DIR}/wilcoxon_test_results_{level}_corrected.csv", index=False)
    return results_df


def wilcoxon_by_type_corrected(df, level):
    """
    Perform Wilcoxon test by refactoring type with proper statistical handling.
    Include pairs with no change as valid samples.
    """
    results = []
    
    for type_name, group in df.groupby("type_name"):
        type_p_values = []
        type_results = []
        
        for test_smell in group["test_smell"].unique():
            subset = group[group["test_smell"] == test_smell]
            before = subset["before_value"].values
            after = subset["after_value"].values
            n = len(subset)
            
            # Skip if sample size is too small
            if n < 5:
                continue
                
            try:
                stat, p_value = wilcoxon(before, after)
                effect_size_r = calculate_effect_size_r(before, after)
                
                # Count pairs with no change
                no_change_pairs = np.sum(before == after)
                
                result = {
                    "type_name": type_name,
                    "test_smell": test_smell,
                    "sample_size": n,
                    "no_change_pairs": no_change_pairs,
                    "change_pairs": n - no_change_pairs,
                    "Wilcoxon_stat": stat,
                    "p_value": p_value,
                    "effect_size_r": effect_size_r
                }
                type_results.append(result)
                type_p_values.append(p_value)
                
            except Exception as e:
                print(f"Error processing {test_smell} for {type_name}: {e}")
                continue
        
        # Multiple testing correction within each refactoring type
        if type_p_values:
            _, pvals_corrected, _, _ = multipletests(type_p_values, alpha=0.05, method='fdr_bh')
            for i, res in enumerate(type_results):
                res["p_value_corrected"] = pvals_corrected[i]
        
        results.extend(type_results)
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(f"{RESULTS_DIR}/wilcoxon_by_type_{level}_corrected.csv", index=False)
    return results_df


def analyze_data_quality(df, level):
    """
    Analyze data quality and potential issues.
    """
    print(f"\n=== Data Quality Analysis for {level} Level ===")
    
    # Check for missing values
    missing_before = df["before_value"].isna().sum()
    missing_after = df["after_value"].isna().sum()
    print(f"Missing values - before: {missing_before}, after: {missing_after}")
    
    # Check for zero variance
    zero_var_count = 0
    for test_smell in df["test_smell"].unique():
        subset = df[df["test_smell"] == test_smell]
        if subset["before_value"].var() == 0 and subset["after_value"].var() == 0:
            zero_var_count += 1
    print(f"Test smells with zero variance: {zero_var_count}")
    
    # Check sample sizes
    sample_sizes = df.groupby("test_smell").size()
    print(f"Sample size range: {sample_sizes.min()} - {sample_sizes.max()}")
    print(f"Test smells with n < 10: {(sample_sizes < 10).sum()}")


def preprocess_data(df):
    """
    Reshape data to ensure before/after values are paired for each commit, type, and test smell.
    """
    test_smell_columns = [col for col in df.columns if "_diff" in col]
    before_cols = [col.replace("_diff", "_before") for col in test_smell_columns]
    after_cols = [col.replace("_diff", "_after") for col in test_smell_columns]
    data = []
    for idx, row in df.iterrows():
        for smell, before_col, after_col in zip(test_smell_columns, before_cols, after_cols):
            data.append({
                "commit_url": row["commit_url"],
                "type_name": row["type_name"],
                "test_smell": smell.replace("_diff", ""),
                "before_value": row[before_col] if pd.notnull(row[before_col]) else 0,
                "after_value": row[after_col] if pd.notnull(row[after_col]) else 0,
                "diff_value": row[smell] if pd.notnull(row[smell]) else 0
            })
    return pd.DataFrame(data)


def analyze_raw_data_distribution(df, level):
    """
    Analyze the distribution of raw data to understand the sample size issue.
    """
    print(f"\n=== Raw Data Distribution Analysis for {level} Level ===")
    
    # Overall statistics
    total_commits = df["commit_url"].nunique()
    total_types = df["type_name"].nunique()
    total_smells = df["test_smell"].nunique()
    
    print(f"Total unique commits: {total_commits}")
    print(f"Total unique refactoring types: {total_types}")
    print(f"Total unique test smells: {total_smells}")
    
    # Analysis by type_name
    print(f"\nSample sizes by refactoring type:")
    type_counts = df.groupby("type_name").size()
    for type_name, count in type_counts.items():
        print(f"  {type_name}: {count} pairs")
    
    # Analysis of zero values and no change
    zero_before = (df["before_value"] == 0).sum()
    zero_after = (df["after_value"] == 0).sum()
    no_change = (df["before_value"] == df["after_value"]).sum()
    
    print(f"\nData quality:")
    print(f"  Zero values in before: {zero_before} ({zero_before/len(df)*100:.1f}%)")
    print(f"  Zero values in after: {zero_after} ({zero_after/len(df)*100:.1f}%)")
    print(f"  No change pairs: {no_change} ({no_change/len(df)*100:.1f}%)")
    
    # Analysis by test smell
    print(f"\nSample sizes by test smell:")
    smell_counts = df.groupby("test_smell").size()
    for smell, count in smell_counts.items():
        print(f"  {smell}: {count} pairs")


def main():
    """Main function with corrected statistical analysis."""
    # Load data
    file_df_raw, method_df_raw = load_data()
    
    # Preprocess data
    file_df = preprocess_data(file_df_raw)
    method_df = preprocess_data(method_df_raw)
    
    # Analyze raw data distribution
    analyze_raw_data_distribution(file_df, "file")
    analyze_raw_data_distribution(method_df, "method")
    
    # Analyze data quality
    analyze_data_quality(file_df, "file")
    analyze_data_quality(method_df, "method")
    
    # Perform corrected statistical analysis
    file_results = wilcoxon_signed_rank_test_corrected(file_df, "file")
    method_results = wilcoxon_signed_rank_test_corrected(method_df, "method")
    
    # Type-specific analysis
    file_by_type = wilcoxon_by_type_corrected(file_df, "file")
    method_by_type = wilcoxon_by_type_corrected(method_df, "method")
    
    print("\n=== Analysis Complete ===")
    print("Results saved to:", RESULTS_DIR)


if __name__ == "__main__":
    main() 