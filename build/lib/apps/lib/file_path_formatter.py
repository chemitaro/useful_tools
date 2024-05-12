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

    def format(self) -> list[str]:
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
                formatted_file_path = f"@{formatted_file_path}\n"
            self.formatted_file_paths.append(formatted_file_path)

        return self.formatted_file_paths
