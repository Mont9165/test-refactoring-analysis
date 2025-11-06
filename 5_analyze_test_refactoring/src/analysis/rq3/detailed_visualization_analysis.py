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
RESULTS_DIR = f"{BASE_DIR}/5_analyze_test_refactoring/src/analysis/rq3/detailed_visualization"

# Create output directory if it does not exist
os.makedirs(RESULTS_DIR, exist_ok=True)

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_data():
    """Load the dataset from a CSV file."""
    file_level_path = f"{CSV_DIR}/file_level_wide.csv"
    method_level_path = f"{CSV_DIR}/method_level_wide.csv"
    file_df = pd.read_csv(file_level_path)
    method_df = pd.read_csv(method_level_path)
    return file_df, method_df

def preprocess_data(df):
    """Reshape data for analysis."""
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

def create_detailed_change_analysis(df, level):
    """Create detailed analysis of changes with outliers detection."""
    
    # 1. Overall change distribution
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f'Detailed Change Analysis - {level} Level', fontsize=16)
    
    # Change distribution
    change_counts = []
    for test_smell in df["test_smell"].unique():
        subset = df[df["test_smell"] == test_smell]
        improved = (subset["diff_value"] < 0).sum()
        degraded = (subset["diff_value"] > 0).sum()
        unchanged = (subset["diff_value"] == 0).sum()
        change_counts.append({
            "test_smell": test_smell,
            "improved": improved,
            "degraded": degraded,
            "unchanged": unchanged,
            "total": len(subset)
        })
    
    change_df = pd.DataFrame(change_counts)
    
    # Plot 1: Change distribution by test smell
    change_df_melted = change_df.melt(id_vars=["test_smell"], 
                                     value_vars=["improved", "degraded", "unchanged"],
                                     var_name="Change Type", value_name="Count")
    
    sns.barplot(data=change_df_melted, x="test_smell", y="Count", hue="Change Type", ax=axes[0,0])
    axes[0,0].set_title("Change Distribution by Test Smell")
    axes[0,0].tick_params(axis='x', rotation=45)
    axes[0,0].legend(title="Change Type")
    
    # Plot 2: Percentage of changes
    change_df["improved_pct"] = change_df["improved"] / change_df["total"] * 100
    change_df["degraded_pct"] = change_df["degraded"] / change_df["total"] * 100
    change_df["unchanged_pct"] = change_df["unchanged"] / change_df["total"] * 100
    
    change_pct_melted = change_df.melt(id_vars=["test_smell"], 
                                      value_vars=["improved_pct", "degraded_pct", "unchanged_pct"],
                                      var_name="Change Type", value_name="Percentage")
    
    sns.barplot(data=change_pct_melted, x="test_smell", y="Percentage", hue="Change Type", ax=axes[0,1])
    axes[0,1].set_title("Change Percentage by Test Smell")
    axes[0,1].tick_params(axis='x', rotation=45)
    axes[0,1].legend(title="Change Type")
    
    # Plot 3: Box plot of changes with outliers
    sns.boxplot(data=df, x="test_smell", y="diff_value", ax=axes[1,0])
    axes[1,0].set_title("Distribution of Changes (with Outliers)")
    axes[1,0].tick_params(axis='x', rotation=45)
    axes[1,0].axhline(y=0, color='red', linestyle='--', alpha=0.7)
    
    # Plot 4: Violin plot showing distribution shape
    sns.violinplot(data=df, x="test_smell", y="diff_value", ax=axes[1,1])
    axes[1,1].set_title("Distribution Shape of Changes")
    axes[1,1].tick_params(axis='x', rotation=45)
    axes[1,1].axhline(y=0, color='red', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/detailed_change_analysis_{level}.png", dpi=300, bbox_inches="tight")
    plt.close()
    
    return change_df

def create_outlier_analysis(df, level):
    """Analyze and visualize outliers in the data."""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f'Outlier Analysis - {level} Level', fontsize=16)
    
    # Calculate outliers for each test smell
    outlier_data = []
    for test_smell in df["test_smell"].unique():
        subset = df[df["test_smell"] == test_smell]
        Q1 = subset["diff_value"].quantile(0.25)
        Q3 = subset["diff_value"].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = subset[(subset["diff_value"] < lower_bound) | (subset["diff_value"] > upper_bound)]
        
        outlier_data.append({
            "test_smell": test_smell,
            "total_count": len(subset),
            "outlier_count": len(outliers),
            "outlier_percentage": len(outliers) / len(subset) * 100,
            "max_outlier": outliers["diff_value"].max() if len(outliers) > 0 else 0,
            "min_outlier": outliers["diff_value"].min() if len(outliers) > 0 else 0
        })
    
    outlier_df = pd.DataFrame(outlier_data)
    
    # Plot 1: Number of outliers by test smell
    sns.barplot(data=outlier_df, x="test_smell", y="outlier_count", ax=axes[0,0])
    axes[0,0].set_title("Number of Outliers by Test Smell")
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Plot 2: Percentage of outliers
    sns.barplot(data=outlier_df, x="test_smell", y="outlier_percentage", ax=axes[0,1])
    axes[0,1].set_title("Percentage of Outliers by Test Smell")
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # Plot 3: Scatter plot with outliers highlighted
    for test_smell in df["test_smell"].unique():
        subset = df[df["test_smell"] == test_smell]
        Q1 = subset["diff_value"].quantile(0.25)
        Q3 = subset["diff_value"].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        normal_data = subset[(subset["diff_value"] >= lower_bound) & (subset["diff_value"] <= upper_bound)]
        outlier_data = subset[(subset["diff_value"] < lower_bound) | (subset["diff_value"] > upper_bound)]
        
        if len(normal_data) > 0:
            axes[1,0].scatter([test_smell] * len(normal_data), normal_data["diff_value"], 
                             alpha=0.6, s=20, color='blue')
        if len(outlier_data) > 0:
            axes[1,0].scatter([test_smell] * len(outlier_data), outlier_data["diff_value"], 
                             alpha=0.8, s=30, color='red', marker='x')
    
    axes[1,0].set_title("Data Points with Outliers Highlighted")
    axes[1,0].tick_params(axis='x', rotation=45)
    axes[1,0].axhline(y=0, color='black', linestyle='--', alpha=0.7)
    
    # Plot 4: Distribution without outliers
    df_no_outliers = df.copy()
    for test_smell in df["test_smell"].unique():
        subset = df[df["test_smell"] == test_smell]
        Q1 = subset["diff_value"].quantile(0.25)
        Q3 = subset["diff_value"].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outlier_mask = (subset["diff_value"] < lower_bound) | (subset["diff_value"] > upper_bound)
        df_no_outliers.loc[subset[outlier_mask].index, "diff_value"] = np.nan
    
    sns.boxplot(data=df_no_outliers, x="test_smell", y="diff_value", ax=axes[1,1])
    axes[1,1].set_title("Distribution Without Outliers")
    axes[1,1].tick_params(axis='x', rotation=45)
    axes[1,1].axhline(y=0, color='red', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/outlier_analysis_{level}.png", dpi=300, bbox_inches="tight")
    plt.close()
    
    return outlier_df

def create_refactoring_type_heatmap(df, level):
    """Create detailed heatmap showing refactoring type effectiveness."""
    
    # Calculate effectiveness for each refactoring type and test smell combination
    effectiveness_data = []
    for refactoring_type in df["type_name"].unique():
        for test_smell in df["test_smell"].unique():
            subset = df[(df["type_name"] == refactoring_type) & (df["test_smell"] == test_smell)]
            
            if len(subset) >= 5:  # Only include combinations with sufficient data
                improved = (subset["diff_value"] < 0).sum()
                degraded = (subset["diff_value"] > 0).sum()
                unchanged = (subset["diff_value"] == 0).sum()
                total = len(subset)
                
                improvement_rate = improved / total * 100 if total > 0 else 0
                degradation_rate = degraded / total * 100 if total > 0 else 0
                
                # Calculate effect size if there are changes
                if improved + degraded > 0:
                    try:
                        stat, p_value = wilcoxon(subset["before_value"], subset["after_value"])
                        z = norm.ppf(1 - p_value / 2) * (-1 if stat < 0 else 1)
                        effect_size = z / np.sqrt(len(subset))
                    except:
                        effect_size = 0
                else:
                    effect_size = 0
                
                effectiveness_data.append({
                    "refactoring_type": refactoring_type,
                    "test_smell": test_smell,
                    "sample_size": total,
                    "improvement_rate": improvement_rate,
                    "degradation_rate": degradation_rate,
                    "effect_size": effect_size,
                    "significant": p_value <= 0.05 if 'p_value' in locals() else False
                })
    
    effectiveness_df = pd.DataFrame(effectiveness_data)
    
    # Create heatmaps
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle(f'Refactoring Type Effectiveness - {level} Level', fontsize=16)
    
    # Heatmap 1: Improvement Rate
    pivot_improvement = effectiveness_df.pivot(index="refactoring_type", columns="test_smell", values="improvement_rate")
    sns.heatmap(pivot_improvement, annot=True, fmt=".1f", cmap="Greens", ax=axes[0,0])
    axes[0,0].set_title("Improvement Rate (%)")
    
    # Heatmap 2: Effect Size
    pivot_effect = effectiveness_df.pivot(index="refactoring_type", columns="test_smell", values="effect_size")
    sns.heatmap(pivot_effect, annot=True, fmt=".3f", cmap="RdBu_r", center=0, ax=axes[0,1])
    axes[0,1].set_title("Effect Size")
    
    # Heatmap 3: Sample Size
    pivot_sample = effectiveness_df.pivot(index="refactoring_type", columns="test_smell", values="sample_size")
    sns.heatmap(pivot_sample, annot=True, fmt="d", cmap="Blues", ax=axes[1,0])
    axes[1,0].set_title("Sample Size")
    
    # Heatmap 4: Significance (1 for significant, 0 for not)
    pivot_sig = effectiveness_df.pivot(index="refactoring_type", columns="test_smell", values="significant")
    sns.heatmap(pivot_sig, annot=True, fmt="d", cmap="Reds", ax=axes[1,1])
    axes[1,1].set_title("Statistical Significance (1=Yes, 0=No)")
    
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/refactoring_effectiveness_heatmap_{level}.png", dpi=300, bbox_inches="tight")
    plt.close()
    
    return effectiveness_df

def create_statistical_power_analysis(df, level):
    """Analyze statistical power for different sample sizes."""
    
    power_data = []
    for test_smell in df["test_smell"].unique():
        subset = df[df["test_smell"] == test_smell]
        n = len(subset)
        
        if n >= 5:
            # Calculate effect size
            try:
                stat, p_value = wilcoxon(subset["before_value"], subset["after_value"])
                z = norm.ppf(1 - p_value / 2) * (-1 if stat < 0 else 1)
                effect_size = z / np.sqrt(n)
            except:
                effect_size = 0
                p_value = 1.0
            
            # Estimate power (simplified)
            if effect_size != 0:
                # Using Cohen's guidelines for power estimation
                if abs(effect_size) >= 0.8:
                    power_category = "High"
                elif abs(effect_size) >= 0.5:
                    power_category = "Medium"
                elif abs(effect_size) >= 0.2:
                    power_category = "Low"
                else:
                    power_category = "Very Low"
            else:
                power_category = "N/A"
            
            power_data.append({
                "test_smell": test_smell,
                "sample_size": n,
                "effect_size": effect_size,
                "p_value": p_value,
                "power_category": power_category,
                "significant": p_value <= 0.05
            })
    
    power_df = pd.DataFrame(power_data)
    
    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f'Statistical Power Analysis - {level} Level', fontsize=16)
    
    # Plot 1: Sample size vs effect size
    scatter = axes[0,0].scatter(power_df["sample_size"], power_df["effect_size"], 
                               c=power_df["p_value"], cmap="viridis", s=50, alpha=0.7)
    axes[0,0].set_xlabel("Sample Size")
    axes[0,0].set_ylabel("Effect Size")
    axes[0,0].set_title("Sample Size vs Effect Size")
    axes[0,0].axhline(y=0, color='red', linestyle='--', alpha=0.7)
    plt.colorbar(scatter, ax=axes[0,0], label="p-value")
    
    # Plot 2: Power categories
    power_counts = power_df["power_category"].value_counts()
    axes[0,1].pie(power_counts.values, labels=power_counts.index, autopct='%1.1f%%')
    axes[0,1].set_title("Distribution of Statistical Power")
    
    # Plot 3: Sample size distribution
    sns.histplot(data=power_df, x="sample_size", bins=20, ax=axes[1,0])
    axes[1,0].set_title("Distribution of Sample Sizes")
    axes[1,0].axvline(x=20, color='red', linestyle='--', label="Adequate (≥20)")
    axes[1,0].axvline(x=10, color='orange', linestyle='--', label="Small (≥10)")
    axes[1,0].legend()
    
    # Plot 4: Effect size distribution
    sns.histplot(data=power_df, x="effect_size", bins=20, ax=axes[1,1])
    axes[1,1].set_title("Distribution of Effect Sizes")
    axes[1,1].axvline(x=0.2, color='green', linestyle='--', label="Small (≥0.2)")
    axes[1,1].axvline(x=0.5, color='orange', linestyle='--', label="Medium (≥0.5)")
    axes[1,1].axvline(x=0.8, color='red', linestyle='--', label="Large (≥0.8)")
    axes[1,1].legend()
    
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/statistical_power_analysis_{level}.png", dpi=300, bbox_inches="tight")
    plt.close()
    
    return power_df

def main():
    """Main function to execute the detailed analysis."""
    print("Loading data...")
    file_df, method_df = load_data()
    
    print("Preprocessing data...")
    file_melted_df = preprocess_data(file_df)
    method_melted_df = preprocess_data(method_df)
    
    print("Creating detailed change analysis...")
    file_change_df = create_detailed_change_analysis(file_melted_df, "file")
    method_change_df = create_detailed_change_analysis(method_melted_df, "refactoring")
    
    print("Creating outlier analysis...")
    file_outlier_df = create_outlier_analysis(file_melted_df, "file")
    method_outlier_df = create_outlier_analysis(method_melted_df, "refactoring")
    
    print("Creating refactoring effectiveness heatmaps...")
    file_effectiveness_df = create_refactoring_type_heatmap(file_melted_df, "file")
    method_effectiveness_df = create_refactoring_type_heatmap(method_melted_df, "refactoring")
    
    print("Creating statistical power analysis...")
    file_power_df = create_statistical_power_analysis(file_melted_df, "file")
    method_power_df = create_statistical_power_analysis(method_melted_df, "refactoring")
    
    # Save detailed results
    file_change_df.to_csv(f"{RESULTS_DIR}/detailed_change_analysis_file.csv", index=False)
    method_change_df.to_csv(f"{RESULTS_DIR}/detailed_change_analysis_refactoring.csv", index=False)
    file_outlier_df.to_csv(f"{RESULTS_DIR}/outlier_analysis_file.csv", index=False)
    method_outlier_df.to_csv(f"{RESULTS_DIR}/outlier_analysis_refactoring.csv", index=False)
    file_effectiveness_df.to_csv(f"{RESULTS_DIR}/refactoring_effectiveness_file.csv", index=False)
    method_effectiveness_df.to_csv(f"{RESULTS_DIR}/refactoring_effectiveness_refactoring.csv", index=False)
    file_power_df.to_csv(f"{RESULTS_DIR}/statistical_power_analysis_file.csv", index=False)
    method_power_df.to_csv(f"{RESULTS_DIR}/statistical_power_analysis_refactoring.csv", index=False)
    
    print("Analysis complete! Results saved to:", RESULTS_DIR)

if __name__ == "__main__":
    main() 