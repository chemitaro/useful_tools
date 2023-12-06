import re
from abc import ABC, abstractmethod
from apps.lib.dependency_analyzer.utils import make_absolute_path, read_file_content


class FileAnalyzerIF(ABC):
    target_path: str
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
        extensions = ['.js', 'json', '.jsx', '.ts', '.tsx']

        # ルートディレクトリとモジュールのパスを組み合わせて拡張子のないパスを生成
        base_path = make_absolute_path(self.root_path, module_name)

        # 指定されたすべての拡張子に対してチェック
        for ext in extensions:
            potential_path = f"{base_path}{ext}"
            if potential_path in self.all_file_paths:
                return potential_path

        # マッチするものが見つからない場合は None を返す
        return None


class FileAnalyzerPy(FileAnalyzerIF):
    def analyze(self, target_path: str) -> list[str]:
        raise NotImplementedError()
