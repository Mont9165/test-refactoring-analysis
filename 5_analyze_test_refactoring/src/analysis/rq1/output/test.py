# ファイルパスを指定
file_a_path = 'complete_commits.txt'  # 処理済みデータ
file_b_path = 'yotei.txt'  # 処理予定データ

# ファイルAの内容をセットに読み込む（重複を無視しつつ高速検索可能）
with open(file_a_path, 'r', encoding='utf-8') as file_a:
    processed = set(line.strip() for line in file_a if line.strip())

# ファイルBの各行と照合して、Aに含まれない行だけ出力
with open(file_b_path, 'r', encoding='utf-8') as file_b:
    unprocessed = [line.strip() for line in file_b if line.strip() and line.strip() not in processed]

# 結果の表示
for line in unprocessed:
    print(line)
