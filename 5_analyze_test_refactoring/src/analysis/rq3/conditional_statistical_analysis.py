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
RESULTS_DIR = f"{BASE_DIR}/5_analyze_test_refactoring/src/analysis/rq3/conditional_analysis"

# Create output directory if it does not exist
os.makedirs(RESULTS_DIR, exist_ok=True)


def load_data():
    """Load the dataset from a CSV file."""
    file_level_path = f"{CSV_DIR}/file_level_wide.csv"
    method_level_path = f"{CSV_DIR}/method_level_wide.csv"
    file_df = pd.read_csv(file_level_path)
    method_df = pd.read_csv(method_level_path)
    return file_df, method_df


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


def analyze_changed_pairs_only(df, level):
    """
    Perform statistical analysis only on pairs that actually changed.
    """
    print(f"\n=== Conditional Statistical Analysis for {level} Level ===")
    
    results = []
    
    for test_smell in df["test_smell"].unique():
        subset = df[df["test_smell"] == test_smell]
        
        # Filter only changed pairs
        changed_pairs = subset[subset["after_value"] != subset["before_value"]]
        total_pairs = len(subset)
        changed_count = len(changed_pairs)
        
        print(f"\n{test_smell}:")
        print(f"  Total pairs: {total_pairs}")
        print(f"  Changed pairs: {changed_count} ({changed_count/total_pairs*100:.1f}%)")
        
        if changed_count < 5:
            print(f"  → Insufficient changes for statistical test")
            results.append({
                "test_smell": test_smell,
                "total_pairs": total_pairs,
                "changed_pairs": changed_count,
                "change_rate": changed_count/total_pairs*100,
                "test_performed": False,
                "reason": "Insufficient changes (<5)"
            })
            continue
        
        try:
            # Perform Wilcoxon test on changed pairs only
            stat, p_value = wilcoxon(changed_pairs["before_value"], changed_pairs["after_value"])
            
            # Calculate effect size (Cohen's d for paired samples)
            diff = changed_pairs["after_value"] - changed_pairs["before_value"]
            effect_size = np.mean(diff) / np.std(diff) if np.std(diff) > 0 else 0
            
            # Determine direction of change
            improvements = (changed_pairs["after_value"] < changed_pairs["before_value"]).sum()
            degradations = (changed_pairs["after_value"] > changed_pairs["before_value"]).sum()
            
            print(f"  → Wilcoxon test: stat={stat:.3f}, p={p_value:.4f}")
            print(f"  → Effect size: {effect_size:.3f}")
            print(f"  → Improvements: {improvements}, Degradations: {degradations}")
            
            results.append({
                "test_smell": test_smell,
                "total_pairs": total_pairs,
                "changed_pairs": changed_count,
                "change_rate": changed_count/total_pairs*100,
                "test_performed": True,
                "wilcoxon_stat": stat,
                "p_value": p_value,
                "effect_size": effect_size,
                "improvements": improvements,
                "degradations": degradations,
                "significant": p_value < 0.05,
                "improvement_dominant": improvements > degradations
            })
            
        except Exception as e:
            print(f"  → Error: {e}")
            results.append({
                "test_smell": test_smell,
                "total_pairs": total_pairs,
                "changed_pairs": changed_count,
                "change_rate": changed_count/total_pairs*100,
                "test_performed": False,
                "reason": str(e)
            })
    
    return pd.DataFrame(results)


def analyze_by_refactoring_type_changed(df, level):
    """
    Analyze changed pairs by refactoring type.
    """
    print(f"\n=== Conditional Analysis by Refactoring Type for {level} Level ===")
    
    results = []
    
    for type_name in df["type_name"].unique():
        type_data = df[df["type_name"] == type_name]
        
        # Filter changed pairs for this refactoring type
        changed_pairs = type_data[type_data["after_value"] != type_data["before_value"]]
        total_pairs = len(type_data)
        changed_count = len(changed_pairs)
        
        if changed_count < 5:
            continue
        
        print(f"\n{type_name}:")
        print(f"  Total pairs: {total_pairs}, Changed pairs: {changed_count} ({changed_count/total_pairs*100:.1f}%)")
        
        # Analyze by test smell within this type
        smell_results = []
        for test_smell in changed_pairs["test_smell"].unique():
            smell_data = changed_pairs[changed_pairs["test_smell"] == test_smell]
            if len(smell_data) < 3:  # Too few for meaningful analysis
                continue
                
            try:
                stat, p_value = wilcoxon(smell_data["before_value"], smell_data["after_value"])
                diff = smell_data["after_value"] - smell_data["before_value"]
                effect_size = np.mean(diff) / np.std(diff) if np.std(diff) > 0 else 0
                
                improvements = (smell_data["after_value"] < smell_data["before_value"]).sum()
                degradations = (smell_data["after_value"] > smell_data["before_value"]).sum()
                
                smell_results.append({
                    "test_smell": test_smell,
                    "changed_pairs": len(smell_data),
                    "wilcoxon_stat": stat,
                    "p_value": p_value,
                    "effect_size": effect_size,
                    "improvements": improvements,
                    "degradations": degradations,
                    "significant": p_value < 0.05
                })
                
            except Exception as e:
                continue
        
        if smell_results:
            results.append({
                "type_name": type_name,
                "total_pairs": total_pairs,
                "changed_pairs": changed_count,
                "change_rate": changed_count/total_pairs*100,
                "smell_results": smell_results
            })
    
    return results


def plot_conditional_results(results_df, level):
    """
    Create visualizations for conditional analysis results.
    """
    # Filter only tests that were performed
    performed_tests = results_df[results_df["test_performed"] == True]
    
    if len(performed_tests) == 0:
        print(f"No statistical tests were performed for {level} level")
        return
    
    # 1. P-values visualization
    plt.figure(figsize=(12, 6))
    test_smells = performed_tests["test_smell"]
    p_values = performed_tests["p_value"]
    colors = ['red' if p < 0.05 else 'blue' for p in p_values]
    
    plt.bar(test_smells, p_values, color=colors, alpha=0.7)
    plt.axhline(y=0.05, color='red', linestyle='--', label='Significance threshold (0.05)')
    plt.xlabel('Test Smells')
    plt.ylabel('p-value')
    plt.title(f'P-values for Changed Pairs Only ({level} Level)')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/conditional_p_values_{level}.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Effect sizes visualization
    plt.figure(figsize=(12, 6))
    effect_sizes = performed_tests["effect_size"]
    colors = ['red' if x < 0 else 'green' if x > 0 else 'gray' for x in effect_sizes]
    
    plt.bar(test_smells, effect_sizes, color=colors, alpha=0.7)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.xlabel('Test Smells')
    plt.ylabel('Effect Size (Cohen\'s d)')
    plt.title(f'Effect Sizes for Changed Pairs Only ({level} Level)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/conditional_effect_sizes_{level}.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Change rate vs effect size scatter plot
    plt.figure(figsize=(10, 6))
    change_rates = performed_tests["change_rate"]
    plt.scatter(change_rates, effect_sizes, c=colors, alpha=0.7, s=100)
    plt.xlabel('Change Rate (%)')
    plt.ylabel('Effect Size (Cohen\'s d)')
    plt.title(f'Change Rate vs Effect Size ({level} Level)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/change_rate_vs_effect_size_{level}.png", dpi=300, bbox_inches='tight')
    plt.close()


def main():
    """Main function to execute the conditional statistical analysis."""
    # Load data
    file_df_raw, method_df_raw = load_data()
    
    # Preprocess data
    file_df = preprocess_data(file_df_raw)
    method_df = preprocess_data(method_df_raw)
    
    # Analyze changed pairs only
    file_results = analyze_changed_pairs_only(file_df, "file")
    method_results = analyze_changed_pairs_only(method_df, "method")
    
    # Analyze by refactoring type
    file_by_type = analyze_by_refactoring_type_changed(file_df, "file")
    method_by_type = analyze_by_refactoring_type_changed(method_df, "method")
    
    # Create visualizations
    plot_conditional_results(file_results, "file")
    plot_conditional_results(method_results, "method")
    
    # Save results
    file_results.to_csv(f"{RESULTS_DIR}/conditional_results_file.csv", index=False)
    method_results.to_csv(f"{RESULTS_DIR}/conditional_results_method.csv", index=False)
    
    # Print summary
    print(f"\n=== Summary ===")
    print(f"File level: {len(file_results[file_results['test_performed'] == True])} tests performed")
    print(f"Method level: {len(method_results[method_results['test_performed'] == True])} tests performed")
    print(f"Results saved to: {RESULTS_DIR}")


if __name__ == "__main__":
    main() 