import importlib
import importlib.util  # 追加
import inspect
from types import ModuleType

from apps.lib.utils import make_relative_path, path_to_module, print_colored


class ClassCollector:
    """
    指定されたファイルパスからクラスを収集するクラス。
    """

    file_paths: list[str]
    root_path: str
    classes: list[type]

    def __init__(self, file_paths: list[str], root_path: str):
        """
        ClassCollectorのコンストラクタ。

        :param file_paths: クラスを収集するPythonファイルのパスのリスト。
        """
        self.file_paths = file_paths
        self.root_path = root_path
        self.classes = []

    def execute(self) -> list[type]:
        """
        指定されたファイルパスからクラスを収集し、リストとして返す。

        :return: 収集されたクラスのリスト。
        """
        for file_path in self.file_paths:
            # 相対パスに変換
            relative_path = make_relative_path(self.root_path, file_path)
            module_name = path_to_module(relative_path)
            module = self._import_module(module_name, file_path)
            self._extract_classes(module)
        return self.classes

    # 取得したクラスの一覧を出力する
    def print_classes(self) -> None:
        """
        収集されたクラスの一覧を出力する。
        """
        print_colored(("\n== Class List ==\n", "green"))
        for cls in self.classes:
            print_colored(f"{cls}")

    def _import_module(self, module_name: str, file_path: str) -> ModuleType:
        """
        ファイルパスからモジュールをインポートする。

        :param module_name: モジュール名。
        :param file_path: Pythonファイルのパス。
        :return: インポートされたモジュール。
        """
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            raise ImportError(f"Failed to import module: {module_name}")
        module = importlib.util.module_from_spec(spec)

        # モジュールを読み込む
        spec_loader = spec.loader
        if spec_loader is None:
            raise ImportError(f"Failed to import module: {module_name}")
        spec_loader.exec_module(module)
        return module

    def _extract_classes(self, module: ModuleType) -> None:
        """
        モジュールからクラスを抽出し、クラスリストに追加する。

        :param module: クラスを抽出する対象のモジュール。
        """
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__ == module.__name__:
                self.classes.append(obj)
