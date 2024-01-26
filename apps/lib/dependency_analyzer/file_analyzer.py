import ast
import importlib.util
import os
import pkgutil
import re
from abc import ABC, abstractmethod

from apps.lib.utils import (make_absolute_path, make_relative_path,
                            read_file_content)


class FileAnalyzerIF(ABC):
    """ファイル解析クラスのインターフェース"""
    root_path: str
    all_file_paths: list[str]

    def __init__(
        self,
        root_path: str,
        all_file_paths: list[str]
    ):
        self.root_path = root_path
        self.all_file_paths = all_file_paths

    # 解析する
    @abstractmethod
    def analyze(self, target_path: str) -> list[str]:
        raise NotImplementedError


def extract_module_names_from_imports(file_content: str) -> list[str]:
    """ファイルの内容からモジュールパスを抽出する

    Args:
        file_content (str): ファイルの内容

    Returns:
        list[str]: モジュールパスのリスト
    """
    # インポートおよびエクスポート文を検索するための正規表現パターン
    pattern = r"(?:import .* from|export .* from) ['\"](@?[^'\"]+)['\"]"

    # 正規表現を用いてインポートおよびエクスポート文を検索
    matches: list[str] = re.findall(pattern, file_content)

    # matchesの中身が全て文字列で無い場合は例外を発生させる
    if not all(isinstance(match, str) for match in matches):
        raise ValueError('matches の中身が全て文字列である必要があります')

    # アットマークを除去してリストに追加
    paths = [match.lstrip('@/') for match in matches if match.startswith('@/')]

    return paths


class FileAnalyzerJs(FileAnalyzerIF):
    """JavaScript 用のファイル解析クラス"""

    def analyze(self, target_path: str) -> list[str]:
        """指定されたファイルの内容から、そのファイルが依存しているファイルのパスを抽出する"""
        file_content = read_file_content(target_path)
        module_names = extract_module_names_from_imports(file_content)
        # モジュール名をファイルパスに変換
        file_paths = []
        for module_name in module_names:
            file_path = self.convert_module_name_to_file_path(module_name)
            if type(file_path) is str:
                file_paths.append(file_path)
        return file_paths

    def convert_module_name_to_file_path(self, module_name: str) -> str | None:
        """指定されたモジュール名にマッチするファイルパスを探す

        Args:
            module_name (str): モジュール名

        Returns:
            str: マッチしたファイルパス
        """
        extensions = ['.js', '.json', '.jsx', '.ts', '.tsx']

        # ルートディレクトリとモジュールのパスを組み合わせて拡張子のないパスを生成
        base_path = make_absolute_path(self.root_path, module_name)

        # 指定されたすべての拡張子に対してチェック
        for ext in extensions:
            potential_path = f"{base_path}{ext}"
            if potential_path in self.all_file_paths:
                return potential_path

        # マッチするものが見つからない場合は None を返す
        return None


def is_package(module_name: str) -> bool:
    """
    指定されたモジュールがパッケージであるかどうかを返します。

    Args:
        module_name (str): モジュール名。

    Returns:
        bool: パッケージであるかどうかを示すブール値。
    """
    try:
        spec = importlib.util.find_spec(module_name)
    except (AttributeError, ModuleNotFoundError):
        return False
    return spec is not None and spec.submodule_search_locations is not None


def get_modules_in_package(package_name: str) -> list[str]:
    """
    指定されたパッケージに含まれるモジュールの名前のリストを返します。

    Args:
        package_name (str): パッケージ名。

    Returns:
        List[str]: パッケージに含まれるモジュールの名前のリスト。
    """
    return [name for _, name, _ in pkgutil.iter_modules([package_name])]


class FileAnalyzerPy(FileAnalyzerIF):
    """Python 用のファイル解析クラス"""

    def analyze(self, target_path: str) -> list[str]:
        """
        指定されたPythonファイルのインポートを解析し、インポートされたモジュールのファイルの相対パスのリストを返します。

        Args:
            root_path (str): 依存関係を解析する起点のPythonファイルのパス。
            relative_path (str): 依存関係を解析するPythonファイルのパス。

        Returns:
            List[str]: インポートされたモジュールのファイルの相対パスのリスト。
        """
        # ファイルの内容を読み込む
        code = read_file_content(target_path)
        # コードをASTで解析する
        tree = ast.parse(code)

        # AST内のすべてのImportFromノードを検索する
        imports: list[ast.ImportFrom] = [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]

        result_module_names = []

        # モジュール名を取得する
        for node in imports:
            import_class_and_func_names = []
            module_name: str = node.module or ''

            # インポートされたクラスや関数の名前を取得する
            for alias in node.names:
                import_class_and_func_names.append(alias.name)

            # 相対インポートの場合は、絶対インポートに変換する *相対インポートは未対応
            if node.level > 0:
                base_path = target_path
                for _ in range(node.level):
                    base_path = os.path.dirname(base_path)

                # パッケージ名を取得する
                package_relative_path = make_relative_path(self.root_path, base_path)
                package_name = package_relative_path.replace('/', '.')
                # モジュール名を結合する
                module_name = f"{package_name}.{module_name}"

            # モジュール名がパッケージであるの場合は、パッケージに含まれるモジュールの内、直接importしているクラスや関数を含むモジュールを取得する
            if is_package(module_name):
                modules = get_modules_in_package(module_name)
                for module in modules:
                    result_module_names.append(f"{package_name}.{module}")
                continue

            result_module_names.append(module_name)  # モジュール名を追加する

        # モジュール名をファイルの絶対パスに変換する
        collected_paths = []
        for module_name in result_module_names:
            path = self.convert_module_name_to_file_path(module_name)
            if path:
                collected_paths.append(path)
        return collected_paths

    # モジュール名をファイルの絶対パスに変換するメソッド
    def convert_module_name_to_file_path(self, module_name: str) -> str | None:
        """指定されたモジュール名にマッチするファイルパスを探す

        Args:
            module_name (str): モジュール名

        Returns:
            str: マッチしたファイルパス
        """
        relative_path = module_name.replace(".", "/") + ".py"
        absolute_path = make_absolute_path(self.root_path, relative_path)
        if absolute_path in self.all_file_paths:
            return absolute_path
        return None


class FileAnalyzerUnknown(FileAnalyzerIF):
    """不明なファイル用のファイル解析クラス"""
    def analyze(self, target_path: str) -> list[str]:
        return []
