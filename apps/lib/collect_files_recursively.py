import os


def collect_files_recursively(root_path: str, extensions: tuple[str, ...], ignore_dirs: list[str]) -> list[str]:
    """指定したディレクトリ以下のファイルを再帰的に検索する

    Args:
        root_path (str): 検索を開始するディレクトリのパス
        extensions (tuple[str, ...]): 検索対象の拡張子
        ignore_dirs (list[str]): 無視するディレクトリ名のリスト

    Returns:
        list[str]: 検索結果のファイルパスのリスト
    """
    paths = []
    for root, dirs, files in os.walk(root_path):
        # 無視するディレクトリをここで除外
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file.endswith(extensions):
                paths.append(os.path.join(root, file))
    return paths


directory_to_search = "/Users/iwasawayuuta/workspace/product/taikyohiyou_project/taikyohiyou_webui"
ignore_paths = ["src", "node_modules"]

extensions = ('.ts', '.tsx', '.js', '.jsx')

# ファイルのパスを検索
file_paths = collect_files_recursively(directory_to_search, extensions, ignore_paths)

# 結果の配列を表示
print(file_paths)
