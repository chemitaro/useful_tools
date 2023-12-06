import os
import enum
from abc import ABC, abstractmethod


def get_all_file_paths(
    root_path: str,
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
    if ignore_relative_paths is None:
        ignore_relative_paths = []
    if ignore_dirs is None:
        ignore_dirs = ['node_modules', 'cypress', 'coverage', '__pycashe__']
    if extensions is None:
        extensions = ('.py', '.js', '.jsx', '.ts', '.tsx')

    paths = []
    for root, dirs, files in os.walk(root_path):
        # 無視するディレクトリをここで除外
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file.endswith(extensions):
                paths.append(os.path.join(root, file))

    # 無視する相対パスを絶対パスに変換
    ignore_absolute_paths = [os.path.join(root_path, p) for p in ignore_relative_paths]

    # 収集したファイルパスから無視するパスを除外
    valid_paths = [p for p in paths if p not in ignore_absolute_paths]
    return valid_paths


def make_absolute_path(root_path: str, relative_path: str) -> str:
    """ルートパスと相対パスを組み合わせて絶対パスを生成する

    Args:
        root_path (str): ルートパス
        relative_path (str): 相対パス

    Returns:
        str: 絶対パス
    """
    return os.path.join(root_path, relative_path)


def make_relative_path(root_path: str, absolute_path: str) -> str:
    """ルートパスと絶対パスを組み合わせて相対パスを生成する

    Args:
        root_path (str): ルートパス
        absolute_path (str): 絶対パス

    Returns:
        str: 相対パス
    """
    return os.path.relpath(absolute_path, root_path)


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


def read_file_content(file_path: str) -> str:
    """指定したファイルの内容を読み込み、文字列として返す"""
    with open(file_path, 'r') as f:
        content = f.read()
    return content


class FileAnalyzerIF(ABC):
    file_path: str
    root_path: str
    all_file_paths: list[str]

    # 解析する
    @abstractmethod
    def analyze(self) -> list[str]:
        pass


class ProgramType(enum.Enum):
    PYTHON = ['.py']
    JAVASCRIPT = ['.js', '.jsx', '.ts', '.tsx']

    # 渡されたファイルのパスの拡張子からプログラムの種類を判定するメソッドを定義する
    @classmethod
    def get_program_type(cls, file_path: str) -> 'ProgramType':
        ext = os.path.splitext(file_path)[1]
        if ext in cls.PYTHON.value:
            return cls.PYTHON
        elif ext in cls.JAVASCRIPT.value:
            return cls.JAVASCRIPT
        else:
            raise ValueError('invalid file extension')


class DependencyAnalyzer:
    root_path: str
    start_paths: list[str]
    all_file_paths: list[str]
    depth: int = 9999
    result_paths: list[str] = []

    def __init__(
        self,
        root_path: str,
        start_paths: list[str],
        all_file_paths: list[str],
        depth: int
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
        start_relative_paths: list[str],
        ignore_relative_paths: list[str] | None = None,
        depth: int = 9999
    ) -> 'DependencyAnalyzer':
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

        # クラスのインスタンスを生成して返す
        return cls(root_path, start_paths, all_file_paths, depth)
