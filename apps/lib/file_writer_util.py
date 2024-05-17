import os

from apps.lib.utils import print_colored


class FileWriter:
    """ファイルに書き出す"""

    file_path: str
    file_dir: str

    def __init__(self, file_name: str, file_dir: str, extension: str = "txt"):
        """ファイル名とファイルのディレクトリを指定する"""
        self.file_dir = os.path.expanduser(file_dir)
        self.file_path = os.path.join(self.file_dir, f"{file_name}.{extension}")

    def write(self, contents: list[str] | str) -> None:
        """ファイルに書き出す"""
        print_colored(("\n== Write to file ==\n", "green"))
        self.create_dir()
        if isinstance(contents, str):
            text = contents
        elif isinstance(contents, list) and all(isinstance(content, str) for content in contents):
            text = "\n".join(contents)
        else:
            # すべて文字列に変換して結合する
            text = "\n".join(str(content) for content in contents)

        with open(self.file_path, "w") as f:
            f.write(text)
        print_colored(("Saved to File: ", "green"), self.file_path)

    def create_dir(self) -> None:
        """ディレクトリが存在しない場合は作成する"""
        if not os.path.exists(self.file_dir):
            print_colored(("\nCreating New Directory: ", "green"), self.file_dir)
            os.makedirs(self.file_dir)
