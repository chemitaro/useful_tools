import re
from apps.lib.enums import ProgramType
from apps.lib.utils import read_file_content, make_relative_path


def remove_py_docstring(content):
    """
    指定されたPythonコードからドキュメントコメントを削除します。

    Args:
        content (str): ドキュメントコメントを削除するPythonコード。

    Returns:
        str: ドキュメントコメントが削除されたPythonコード。
    """
    # ドキュメントコメントを削除する
    omit_content = re.sub(r'""".*?"""\n', '', content, flags=re.DOTALL)
    # '# 'から始めるコメントを削除する
    omit_content = re.sub(r'# .*?\n', '', omit_content)
    return omit_content


def remove_js_docstring(content):
    """
    指定されたJavaScriptコードからドキュメントコメントを削除します。

    Args:
        content (str): ドキュメントコメントを削除するJavaScriptコード。

    Returns:
        str: ドキュメントコメントが削除されたJavaScriptコード。
    """
    # ドキュメントコメントを削除する
    omit_content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # '// 'から始めるコメントを削除する
    omit_content = re.sub(r'// .*?\n', '', omit_content)
    return omit_content


class FileContentCollector:
    file_paths: list[str]
    root_path: str
    no_docstring: bool

    def __init__(self, file_paths: list[str], root_path: str, no_docstring: bool = False):
        self.file_paths = file_paths
        self.root_path = root_path
        self.no_docstring = no_docstring

    def collect(self) -> list[str]:
        """
        指定されたファイルパスのリストから、ファイルの内容を収集します。

        Returns:
            list[str]: ファイルの内容のリスト。
        """
        # ファイルの内容を収集する
        contents = []
        for file_path in self.file_paths:
            content = read_file_content(file_path)
            # ドキュメントコメントを削除する
            content = self.without_docstring(file_path, content)
            content = self.format_content(file_path, content)
            contents.append(content)
        return contents

    def format_content(self, file_path, content) -> str:
        """
        受け取ったコンテントを相対パス名```コンテントの内容```の形式に整形します。

        Args:
            content (str): 整形するファイルの内容。

        Returns:
            str: 整形されたファイルの内容。
        """
        relative_path = make_relative_path(self.root_path, file_path)
        formatted_content = f'{relative_path}\n```\n{content}\n```\n'
        return formatted_content

    # ドキュメントコメントを削除する
    def without_docstring(self, file_path, content):
        if self.no_docstring:
            program_type = ProgramType.get_program_type(file_path)
            if program_type == ProgramType.PYTHON:
                content = remove_py_docstring(content)
            elif program_type == ProgramType.JAVASCRIPT:
                content = remove_js_docstring(content)
        return content
