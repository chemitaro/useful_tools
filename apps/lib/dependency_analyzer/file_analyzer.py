import ast
import importlib.util
import logging
import os
import pkgutil
import re
from abc import ABC, abstractmethod

from apps.lib.utils import make_absolute_path, read_file_content


class FileAnalyzerIF(ABC):
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
    # インポート文を検索するための正規表現パターン
    import_pattern = r"import .* from ['\"](@?[^'\"]+)['\"]"

    # 正規表現を用いてインポート文を検索
    matches: list[str] = re.findall(import_pattern, file_content)

    # matchesの中身が全て文字列で無い場合は例外を発生させる
    if not all(isinstance(match, str) for match in matches):
        raise ValueError('matches の中身が全て文字列である必要があります')

    # アットマークを除去してリストに追加
    paths = [match.lstrip('@') for match in matches if match.startswith('@')]

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
        logging.debug(f'self.root_path: {self.root_path}')
        logging.debug(f'☆base_path: {base_path}')

        # 指定されたすべての拡張子に対してチェック
        for ext in extensions:
            potential_path = f"{base_path}{ext}"
            logging.debug(f'potential_path: {potential_path}')
            if potential_path in self.all_file_paths:
                logging.debug(f"マッチしたファイルパス: {potential_path}")
                return potential_path

        # マッチするものが見つからない場合は None を返す
        logging.debug(f"マッチするファイルパスが見つかりませんでした: {base_path}")
        return None


def is_package(module_name):
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

            # 相対インポートの場合は、絶対インポートに変換する
            if node.level > 0:
                base_dir = os.path.dirname(target_path)
                for _ in range(node.level - 1):
                    base_dir = os.path.dirname(base_dir)

                # パッケージ名を取得する
                package_name = os.path.basename(base_dir)
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
            relative_path = module_name.replace(".", "/") + ".py"
            absolute_path = make_absolute_path(self.root_path, relative_path)
            if absolute_path in self.all_file_paths:
                collected_paths.append(absolute_path)
        return collected_paths
