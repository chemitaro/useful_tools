import os

from apps.lib.dependency_analyzer.file_analyzer import (
    FileAnalyzerIF,
    FileAnalyzerJs,
    FileAnalyzerPy,
    FileAnalyzerUnknown,
)
from apps.lib.enums import ProgramType
from apps.lib.utils import make_absolute_path, make_relative_path, print_colored


def get_all_file_paths(
    root_path: str,
    scope_paths: list[str] | None = None,
    ignore_paths: list[str] | None = None,
    ignore_dirs: list[str] | None = None,
    extensions: tuple[str, ...] | None = None,
) -> list[str]:
    """指定したディレクトリ以下のファイルを再帰的に検索する

    Args:
        root_path (str): 検索を開始するディレクトリのパス
        extensions (tuple[str, ...]): 検索対象の拡張子
        ignore_dirs (list[str]): 無視するディレクトリ名のリスト

    Returns:
        list[str]: 検索結果のファイルパスのリスト
    """
    if scope_paths is None:
        scope_paths = []
    if ignore_paths is None:
        ignore_paths = []
    if ignore_dirs is None:
        ignore_dirs = [
            "__pycashe__",
            "node_modules",
            "cypress",
            "coverage",
            ".next",
            ".devcontainer",
            ".storybook",
            ".swc",
            ".vscode",
            "cypress",
        ]
    if extensions is None:
        extensions = (".py", ".js", ".json", ".jsx", ".ts", ".tsx")

    all_file_paths: list[str] = []
    for root, dirs, files in os.walk(root_path):
        # 無視するディレクトリをここで除外
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file.endswith(extensions):
                all_file_paths.append(os.path.join(root, file))

    if len(scope_paths) > 0:
        # scope_paths が相対パスの場合は絶対パスに変換する
        scope_paths = [make_absolute_path(root_path, p) for p in scope_paths]

        # 収集したファイルパスから探索範囲外のパスを除外する。
        all_file_paths = [p for p in all_file_paths if any([p.startswith(scope_path) for scope_path in scope_paths])]

    if len(ignore_paths) > 0:
        # ignore_paths が相対パスの場合は絶対パスに変換する
        ignore_paths = [make_absolute_path(root_path, p) for p in ignore_paths]

        # 収集したファイルパスから無視するパスを除外する。
        all_file_paths = [p for p in all_file_paths if not any([p.startswith(ignore_path) for ignore_path in ignore_paths])]

    return all_file_paths


def filter_paths(file_paths: list[str], ignore_paths: list[str]) -> list[str]:
    """指定したファイルパスのリストから、指定したパスを除外する

    Args:
        file_paths (list[str]): ファイルパスのリスト
        ignore_paths (list[str]): 除外するパスのリスト

    Returns:
        list[str]: 除外後のファイルパスのリスト
    """
    return [p for p in file_paths if p not in ignore_paths]


class DependencyAnalyzer:
    root_path: str
    start_paths: list[str]
    all_file_paths: list[str]
    depth: int = 9999
    current_depth: int = 0
    search_paths: list[list[str]]
    result_paths: list[str] = []
    log: list[str] = []

    def __init__(
        self,
        root_path: str,
        start_paths: list[str],
        all_file_paths: list[str],
        depth: int,
    ) -> None:
        self.root_path = root_path
        self.start_paths = start_paths
        self.all_file_paths = all_file_paths
        self.depth = depth

    # クラスのインスタンスを生成するメソッドを定義する
    @classmethod
    def factory(
        cls,
        root_path: str,
        start_relative_paths: list[str] | None = None,
        scope_relative_paths: list[str] | None = None,
        ignore_relative_paths: list[str] | None = None,
        depth: int | None = None,
    ) -> "DependencyAnalyzer":
        if start_relative_paths is None:
            start_relative_paths = []
        if scope_relative_paths is None:
            scope_relative_paths = []
        if ignore_relative_paths is None:
            ignore_relative_paths = []
        if depth is None:
            depth = 9999

        # 相対パスを絶対パスに変換
        start_paths = [make_absolute_path(root_path, p) for p in start_relative_paths]

        # 探索範囲のパスを相対パスを絶対パスに変換
        scope_paths = [make_absolute_path(root_path, p) for p in scope_relative_paths]

        # 無視するパスを相対パスを絶対パスに変換
        ignore_paths = [make_absolute_path(root_path, p) for p in ignore_relative_paths]
        # ファイルパスを収集
        all_file_paths = get_all_file_paths(root_path, scope_paths=scope_paths, ignore_paths=ignore_paths)

        # クラスのインスタンスを生成して返す
        return cls(root_path, start_paths, all_file_paths, depth)

    # 引数にファイルのパスを渡すことで、ファイルのプログラミング言語を判定し、適したファイル解析クラスを生成する
    def analyze(self) -> list[str]:
        """指定したファイルの依存関係を解析する"""
        self.log = []  # ログを初期化する

        # start_pathsが空の場合、全てのファイルのパスを返す
        if len(self.start_paths) == 0:
            return self.all_file_paths

        # depthが0の場合、start_pathsを返す
        if self.depth == 0:
            self.result_paths = self.start_paths
            return self.result_paths

        # 指定したファイルの依存関係を解析する
        self.search_paths: list[list[str]] = [self.start_paths]
        self.result_paths = []
        self.current_depth: int = 0  # 探索中の階層の深さを0で初期化

        message = "\n== Parsing module dependencies =="
        print_colored((message, "green"))

        # 指定された深さまで依存関係を解析する
        for _ in range(0, self.depth + 1):
            # 次に探索するファイルのパスを格納するリスト追加する
            self.search_paths.append([])
            # 現在の階層のログを出力する
            message = f"\nDepth: {self.current_depth}"
            print_colored((message, "cyan"))
            self.log.append(message)

            # 現在の階層のファイルのパスを取得する
            for path in self.search_paths[self.current_depth]:
                message = f"  {make_relative_path(self.root_path, path)}"
                print_colored(message)
                self.log.append(message)

                # 現在のファイルのパスが探索済みのパスに含まれている場合、次のファイルのパスを探索する
                if path in self.result_paths:
                    continue

                # 現在のファイルのパスと接頭部が一致して、かつ完全一致ではないパスのうち、未探索のファイルのパスがある場合、次の階層のファイルパスに追加する
                matched_paths = [p for p in self.all_file_paths if p.startswith(path) and p != path and p not in self.result_paths]
                for matched_path in matched_paths:
                    message = f"    + Contains: {make_relative_path(self.root_path, matched_path)}"
                    print_colored((message, "grey"))
                    self.log.append(message)

                    self.search_paths[self.current_depth + 1].append(matched_path)

                # 現在のファイルのパスが全てのファイルのパスに含まれていない場合、次のファイルのパスを探索する
                if path not in self.all_file_paths:
                    continue

                # 現在の階層のファイルのパスを探索済みのパスの先頭に追加する
                self.result_paths.insert(0, path)
                # 現在の階層のファイルのパスから、依存関係を解析して、ファイルのパスを取得する。この時、絶対パスに変換する
                file_analyzer: FileAnalyzerIF = self._get_file_analyzer(path)
                dependencies: list[str] = file_analyzer.analyze(path)
                # 現在の階層のファイルのパスの依存関係のうち、探索済みのファイルのパスに含まれていない、かつ、探索候補のファイルのパスに含まれている場合は、次の階層のファイルのパスに追加する
                for dependency in dependencies:
                    message = f"    + Depends: {make_relative_path(self.root_path, dependency)}"
                    print_colored((message, "grey"))
                    self.log.append(message)

                    self.search_paths[self.current_depth + 1].append(dependency)
            self.current_depth += 1  # 次の階層に移動する
            # 次の階層のファイルのパスが存在しない場合、探索を終了する
            if len(self.search_paths[self.current_depth]) == 0:
                break

        return self.result_paths

    def get_log(self) -> str:
        """ログを改行で接合して文字列にして返す"""
        # もしlogが空の場合、空文字""を返す
        if not self.log:
            return ""

        # logを改行で接合して文字列にして返す
        log = "\n".join(self.log)
        prefix = '\n### Parsing module dependencies\n"""'
        suffix = '\n"""\n'

        return prefix + log + suffix

    def _get_file_analyzer_py(self) -> FileAnalyzerPy:
        """FileAnalyzerPyクラスのインスタンスを返す"""
        if not hasattr(self, "_file_analyzer_py_instance"):
            self._file_analyzer_py_instance = FileAnalyzerPy(self.root_path, self.all_file_paths)
        return self._file_analyzer_py_instance

    def _get_file_analyzer_js(self) -> FileAnalyzerJs:
        """FileAnalyzerJsクラスのインスタンスを返す"""
        if not hasattr(self, "_file_analyzer_js_instance"):
            self._file_analyzer_js_instance = FileAnalyzerJs(self.root_path, self.all_file_paths)
        return self._file_analyzer_js_instance

    def _get_file_analyzer_unknown(self) -> FileAnalyzerUnknown:
        """FileAnalyzerUnknownクラスのインスタンスを返す"""
        if not hasattr(self, "_file_analyzer_unknown_instance"):
            self._file_analyzer_unknown_instance = FileAnalyzerUnknown(self.root_path, self.all_file_paths)
        return self._file_analyzer_unknown_instance

    # ファイルのタイプに応じたファイル解析クラスのインスタンスを返す
    def _get_file_analyzer(self, file_path: str) -> FileAnalyzerIF:
        """ファイルの拡張子に応じて、適切なファイル解析クラスのインスタンスを返す"""
        file_type = ProgramType.get_program_type(file_path)
        if file_type == ProgramType.PYTHON:
            return self._get_file_analyzer_py()
        elif file_type == ProgramType.JAVASCRIPT:
            return self._get_file_analyzer_js()
        else:
            return self._get_file_analyzer_unknown()
