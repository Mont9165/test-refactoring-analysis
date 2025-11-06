import pandas as pd


def count_unique_repos(input_file):
    """
    CSVファイル内のユニークなリポジトリの数をカウントします。

    :param input_file: リポジトリデータを含む入力CSVファイルのパス。
    """
    try:
        # CSVファイルを読み込む
        df = pd.read_csv(input_file)

        # 'repository_name' 列のユニークな値の数を数える
        repo_count = df['repository_name'].nunique()

        print(f"ユニークなリポジトリの数: {repo_count}")

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {input_file}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


# ファイルパスをあなたの環境に合わせて変更してください
input_file = 'sampling_test_commits.csv'
count_unique_repos(input_file)


def main():
    input_file = '/app/2_sampling_test_refactor_commits/result/sampling_test_commits.csv'  # Replace with your input file path
    count_unique_repos(input_file)


if __name__ == "__main__":
    main()