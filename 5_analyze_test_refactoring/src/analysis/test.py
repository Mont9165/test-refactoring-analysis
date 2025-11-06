import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

# Vargha-Delaney効果量の算出関数
def vargha_delaney_effect(x, y):
    """
    2群間の Vargha-Delaney Â12 効果量を計算する関数。
    Â12 は、x のランダムなサンプルが y のランダムなサンプルより大きい確率を示す。
    """
    n1 = len(x)
    n2 = len(y)
    count = 0
    for xi in x:
        count += np.sum(xi > y) + 0.5 * np.sum(xi == y)
    A12 = count / (n1 * n2)
    return A12

def analyze_metrics(data):
    """
    与えられたデータ（DataFrame）において、"_before" で終わるカラムを探し、
    リファクタリング前後のペアデータに対して Wilcoxon 検定および Vargha-Delaney 効果量を算出する。
    結果は DataFrame で返す。
    """
    results = []
    for col in data.columns:
        if col.endswith('_before'):
            metric = col.replace('_before', '')
            after_col = metric + '_after'
            if after_col in data.columns:
                before = data[col].dropna()
                after = data[after_col].dropna()
                # インデックスが揃っている前提です。必要に応じてマージなどの前処理を追加してください。
                if len(before) > 0 and len(after) > 0 and len(before) == len(after):
                    try:
                        stat, p_value = wilcoxon(before, after)
                        effect = vargha_delaney_effect(before.values, after.values)
                        results.append({
                            'metric': metric,
                            'wilcoxon_stat': stat,
                            'p_value': p_value,
                            'A12': effect
                        })
                    except Exception as e:
                        print(f"Error processing metric {metric}: {e}")
    return pd.DataFrame(results)

def analyze_grouped_metrics(data):
    """
    'type_name' カラムが存在する場合、リファクタリング種類ごとにグループ分けして
    各グループでのテストスメル前後の変化を解析する。
    結果は DataFrame で返す。
    """
    if 'type_name' not in data.columns:
        print("データに 'type_name' カラムが存在しません。")
        return None

    results = []
    for ref_type, group in data.groupby('type_name'):
        for col in group.columns:
            if col.endswith('_before'):
                metric = col.replace('_before', '')
                after_col = metric + '_after'
                if after_col in group.columns:
                    before = group[col].dropna()
                    after = group[after_col].dropna()
                    if len(before) > 0 and len(after) > 0 and len(before) == len(after):
                        try:
                            stat, p_value = wilcoxon(before, after)
                            effect = vargha_delaney_effect(before.values, after.values)
                            results.append({
                                'type_name': ref_type,
                                'metric': metric,
                                'wilcoxon_stat': stat,
                                'p_value': p_value,
                                'A12': effect
                            })
                        except Exception as e:
                            print(f"Error processing metric {metric} for type_name {ref_type}: {e}")
    return pd.DataFrame(results)

def main():
    # CSVファイルのパス
    file_level_path = '/5_analyze_test_refactoring/src/analysis/rq3/smells_result/file_level_wide.csv'
    method_level_path = '/5_analyze_test_refactoring/src/analysis/rq3/smells_result/method_level_wide.csv'

    # ファイルレベルのデータ読み込みと解析
    file_level = pd.read_csv(file_level_path)
    print("【ファイルレベル】リファクタリング前後のテストスメル分析結果")
    file_results_df = analyze_metrics(file_level)
    print(file_results_df)

    print("【ファイルレベル】リファクタリング種類別（type_name）テストスメル分析結果")
    file_grouped_results_df = analyze_grouped_metrics(file_level)
    if file_grouped_results_df is not None:
        print(file_grouped_results_df)

    # メソッドレベルのデータ読み込みと解析
    method_level = pd.read_csv(method_level_path)
    print("【メソッドレベル】リファクタリング前後のテストスメル分析結果")
    method_results_df = analyze_metrics(method_level)
    print(method_results_df)

    print("【メソッドレベル】リファクタリング種類別（type_name）テストスメル分析結果")
    method_grouped_results_df = analyze_grouped_metrics(method_level)
    if method_grouped_results_df is not None:
        print(method_grouped_results_df)

if __name__ == '__main__':
    main()