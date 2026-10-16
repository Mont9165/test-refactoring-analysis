import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io

# --- CSVデータの呼び出し部分 ---
# 通常は 'pd.read_csv("test_refactoring_counts.csv")' のようにファイルから読み込みますが、
# ここでは文字列として直接データを作成しています。
csv_data = """type_name,count
Change Assertion Type,123
Split Test Method,37
Prebuilt Fixture,35
Delegated Setup,32
Grouping Tests,23
Parameterized Test,23
Replace try/catch with annotation,14
Guard Assertion,10
Delete Mock Object,10
Implicit Setup,10
Verification Method,8
Test Helper,7
Await Event,6
Replace annotation with assertThrow,6
Inline Assertion,6
Custom Assertion,6
Tuning Resources,6
Replace Dependency with Test Double,6
"""

# 文字列データをCSVとして読み込み、DataFrameを作成します。
df = pd.read_csv("/Users/horikawa/Dev/Research-repo/InvestigatingTheImpactOfTestSpecificRefactoring/5_analyze_test_refactoring/src/analysis/rq1/output/test/test_refactoring_counts.csv")


# --- グラフの作成部分 ---

# データを 'count' 列の降順（大きい順）に並べ替えます。
df_sorted = df.sort_values('count', ascending=False).head(10)
# df_top10 = df.sort_values('count', ascending=False).head(10)

# グラフのサイズを指定します。
plt.figure(figsize=(10, 7))

# seabornを使って水平棒グラフを作成します。
# x軸に 'count'、y軸に 'type_name' を指定し、色合い（palette）も設定しています。
sns.barplot(x='count', y='type_name', data=df_sorted, palette='viridis')
plt.xticks(fontsize=16)
plt.yticks(fontsize=18)

# x軸とy軸のラベル、グラフのタイトルを設定します。
plt.xlabel('Count')
plt.ylabel('Type Name')
plt.title('Test Refactoring Counts (Seaborn)')

# ラベルがグラフ領域からはみ出ないようにレイアウトを調整します。
plt.tight_layout()

# グラフをPNGファイルとして保存します。
plt.savefig('test_refactoring_counts_seaborn.pdf', format='pdf', dpi=900)

print("グラフが 'test_refactoring_counts_seaborn.png' として保存されました。")