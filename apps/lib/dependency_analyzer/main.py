import logging
import os

from apps.lib.dependency_analyzer.file_analyzer import (FileAnalyzerIF,
                                                        FileAnalyzerJs,
                                                        FileAnalyzerPy,
                                                        FileAnalyzerUnknown)
from apps.lib.enum import ProgramType
from apps.lib.utils import make_absolute_path, make_relative_path


def get_all_file_paths(
    root_path: str,
    scope_relative_paths: list[str] | None = None,
    ignore_relative_paths: list[str] | None = None,
    ignore_dirs: list[str] | None = None,
    extensions: tuple[str, ...] | None = None
) -> list[str]:
    """指定したディレクトリ以下のファイルを再帰的に検索する

    Args:
        root_path (str): 検索を開始するディレクトリのパス
        extensions (tuple[str, ...]): 検索対象の拡張子
        ignore_dirs (list[str]): 無視するディレクトリ名のリスト

    Returns:
        list[str]: 検索結果のファイルパスのリスト
    """
    if scope_relative_paths is None:
        scope_relative_paths = []
    if ignore_relative_paths is None:
        ignore_relative_paths = []
    if ignore_dirs is None:
        ignore_dirs = ['__pycashe__', 'node_modules', 'cypress', 'coverage', '.next', '.devcontainer', '.storybook', '.swc', '.vscode', 'cypress', ]
    if extensions is None:
        extensions = ('.py', '.js', '.json', '.jsx', '.ts', '.tsx')

    all_file_paths: list[str] = []
    for root, dirs, files in os.walk(root_path):
        # 無視するディレクトリをここで除外
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file.endswith(extensions):
                all_file_paths.append(os.path.join(root, file))

    if len(scope_relative_paths) > 0:
        # 探索範囲の相対パスを絶対パスに変換
        scope_absolute_paths = [os.path.join(root_path, p) for p in scope_relative_paths]
        # 収集したファイルパスのうち、探索範囲に含まれていないパスを除外する。
        all_file_paths = [p for p in all_file_paths if any([p.startswith(scope_path) for scope_path in scope_absolute_paths])]

    if len(ignore_relative_paths) > 0:
        # 無視する相対パスを絶対パスに変換
        ignore_absolute_paths = [os.path.join(root_path, p) for p in ignore_relative_paths]
        # 収集したファイルパスから無視するパスを除外する。
        all_file_paths = [p for p in all_file_paths if not any([p.startswith(ignore_path) for ignore_path in ignore_absolute_paths])]

    return all_file_paths


def filter_paths(
    file_paths: list[str],
    ignore_paths: list[str]
) -> list[str]:
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
    file_analyzer: FileAnalyzerIF
    depth: int = 9999
    current_depth: int = 0
    search_paths: list[list[str]]
    result_paths: list[str] = []

    def __init__(
        self,
        root_path: str,
        start_paths: list[str],
        all_file_paths: list[str],
        depth: int,
        file_analyzer: FileAnalyzerIF
    ) -> None:
        self.root_path = root_path
        self.start_paths = start_paths
        self.all_file_paths = all_file_paths
        self.depth = depth
        self.file_analyzer = file_analyzer

    # クラスのインスタンスを生成するメソッドを定義する
    @classmethod
    def factory(
        cls,
        root_path: str,
        start_relative_paths: list[str] | None = None,
        ignore_relative_paths: list[str] | None = None,
        depth: int = 9999
    ) -> 'DependencyAnalyzer':
        if start_relative_paths is None:
            start_relative_paths = []
        if ignore_relative_paths is None:
            ignore_relative_paths = []

        # 相対パスを絶対パスに変換
        start_paths = [make_absolute_path(root_path, p) for p in start_relative_paths]

        # 無視するパスを相対パスを絶対パスに変換
        ignore_paths = [make_absolute_path(root_path, p) for p in ignore_relative_paths]
        # ファイルパスを収集
        all_file_paths = get_all_file_paths(root_path)

        # 収集したファイルパスから無視するパスを除外
        all_file_paths = filter_paths(all_file_paths, ignore_paths)

        # ファイルのタイプを確認して、適切なファイル解析クラスを生成
        if len(start_paths):
            file_type = ProgramType.get_program_type(start_paths[0])
        else:
            file_type = ProgramType.UNKNOWN

        file_analyzer: FileAnalyzerIF
        if file_type == ProgramType.PYTHON:
            file_analyzer = FileAnalyzerPy(root_path, all_file_paths)
        elif file_type == ProgramType.JAVASCRIPT:
            file_analyzer = FileAnalyzerJs(root_path, all_file_paths)
        else:
            file_analyzer = FileAnalyzerUnknown(root_path, all_file_paths)

        # クラスのインスタンスを生成して返す
        return cls(root_path, start_paths, all_file_paths, depth, file_analyzer)

    def analyze(self) -> list[str]:
        """指定したファイルの依存関係を解析する"""
        # start_pathsが空の場合、全てのファイルのパスを返す
        if len(self.start_paths) == 0:
            return self.all_file_paths

        # 指定したファイルの依存関係を解析する
        self.search_paths: list[list[str]] = [self.start_paths]
        self.result_paths = []
        self.current_depth: int = 0  # 探索中の階層の深さを0で初期化
        logging.info('\n== Parsing module dependencies ==')
        # 指定された深さまで依存関係を解析する
        for _ in range(0, self.depth + 1):
            # 次に探索するファイルのパスを格納するリスト追加する
            self.search_paths.append([])
            # 現在の階層のログを出力する
            logging.info(f"\nDepth: {self.current_depth}")
            # 現在の階層のファイルのパスを取得する
            for path in self.search_paths[self.current_depth]:
                # 現在の階層のファイルのパスが探索済みのパスに含まれている場合、次のファイルのパスを探索する
                if path in self.result_paths:
                    continue
                if path not in self.all_file_paths:
                    continue

                logging.info(f"  {make_relative_path(self.root_path, path)}")
                # 現在の階層のファイルのパスを探索済みのパスの先頭に追加する
                self.result_paths.insert(0, path)
                # 現在の階層のファイルのパスから、依存関係を解析して、ファイルのパスを取得する。この時、絶対パスに変換する
                dependencies: list[str] = self.file_analyzer.analyze(path)
                # 現在の階層のファイルのパスの依存関係のうち、探索済みのファイルのパスに含まれていない、かつ、探索候補のファイルのパスに含まれている場合は、次の階層のファイルのパスに追加する
                for dependency in dependencies:
                    self.search_paths[self.current_depth + 1].append(dependency)
            self.current_depth += 1  # 次の階層に移動する
            # 次の階層のファイルのパスが存在しない場合、探索を終了する
            if len(self.search_paths[self.current_depth]) == 0:
                break

        return self.result_paths
