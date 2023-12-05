import os


def collect_files_recursively(directory: str, extensions: tuple[str, ...]) -> list[str]:
    """指定したディレクトリ以下のファイルを再帰的に検索する"""
    paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extensions):
                paths.append(os.path.join(root, file))
    return paths


directory_to_search = "/Users/iwasawayuuta/workspace/product/taikyohiyou_project/taikyohiyou_webui/src"
extensions = ('.ts', '.tsx', '.js', '.jsx')

# ファイルのパスを検索
file_paths = collect_files_recursively(directory_to_search, extensions)

# 結果の配列を表示
print(file_paths)
