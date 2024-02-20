from typing import Literal

from apps.lib.utils import make_relative_path


class FilePathFormatter:
    file_paths: list[str]
    root_path: str
    type: Literal["cursor", "path"]
    formatted_file_paths: list[str]

    def __init__(self, file_paths: list[str], root_path: str, type: Literal["cursor", "path"] = "cursor"):
        self.file_paths = file_paths
        self.root_path = root_path
        self.type = type

    def format(self) -> None:
        """
        指定されたファイルパスのリストを整形します。

        Returns:
            list[str]: 整形されたファイルパスのリスト。
        """
        # ファイルパスを初期化する
        self.formatted_file_paths = []

        # ファイルパスを整形する
        for file_path in self.file_paths:
            formatted_file_path = make_relative_path(self.root_path, file_path)
            if self.type == "cursor":
                formatted_file_path = f"@{formatted_file_path}"
            self.formatted_file_paths.append(formatted_file_path)

        # カーソルの場合は最後にコードベースを追加する
        if self.type == "cursor":
            self.formatted_file_paths.append("@Codebase\n")

    def join_formatted_file_paths(self) -> str:
        """
        整形されたファイルパスのリストを改行で結合します。

        Returns:
            str: 整形されたファイルパスのリスト。
        """
        return "\n".join(self.formatted_file_paths)

    def execute(self) -> str:
        """
        ファイルパスの整形と結合を実行し、結果を文字列で返します。

        Returns:
            str: 整形され、結合されたファイルパスの文字列。
        """
        self.format()
        joined_formatted_file_paths = self.join_formatted_file_paths()
        return joined_formatted_file_paths
