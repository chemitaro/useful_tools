import importlib
import importlib.util  # 追加
import inspect

from apps.lib.utils import path_to_module, print_colored


class ClassCollector:
    """
    指定されたファイルパスからクラスを収集するクラス。
    """

    file_paths: list[str]
    classes: list[type]

    def __init__(self, file_paths: list[str]):
        """
        ClassCollectorのコンストラクタ。

        :param file_paths: クラスを収集するPythonファイルのパスのリスト。
        """
        self.file_paths = file_paths
        self.classes = []

    def execute(self) -> list[type]:
        """
        指定されたファイルパスからクラスを収集し、リストとして返す。

        :return: 収集されたクラスのリスト。
        """
        for file_path in self.file_paths:
            module_name = path_to_module(file_path)
            module = self._import_module(module_name, file_path)
            self._extract_classes(module)
        return self.classes

    # 取得したクラスの一覧を出力する
    def print_classes(self):
        """
        収集されたクラスの一覧を出力する。
        """
        print_colored(("\n== Class List ==\n", "green"))
        for cls in self.classes:
            print_colored(f"{cls}")

    def _import_module(self, module_name: str, file_path: str):
        """
        ファイルパスからモジュールをインポートする。

        :param module_name: モジュール名。
        :param file_path: Pythonファイルのパス。
        :return: インポートされたモジュール。
        """
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _extract_classes(self, module):
        """
        モジュールからクラスを抽出し、クラスリストに追加する。

        :param module: クラスを抽出する対象のモジュール。
        """
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__ == module.__name__:
                self.classes.append(obj)
