import importlib
import importlib.util  # 追加
import inspect
from typing import List, Type


class ClassCollector:
    """
    指定されたファイルパスからクラスを収集するクラス。
    """

    def __init__(self, file_paths: List[str]):
        """
        ClassCollectorのコンストラクタ。

        :param file_paths: クラスを収集するPythonファイルのパスのリスト。
        """
        self.file_paths = file_paths
        self.classes = []

    def execute(self) -> List[Type]:
        """
        指定されたファイルパスからクラスを収集し、リストとして返す。

        :return: 収集されたクラスのリスト。
        """
        for file_path in self.file_paths:
            module_name = self._get_module_name(file_path)
            module = self._import_module(module_name, file_path)
            self._extract_classes(module)
        return self.classes

    def _get_module_name(self, file_path: str) -> str:
        """
        ファイルパスからモジュール名を生成する。

        :param file_path: Pythonファイルのパス。
        :return: 生成されたモジュール名。
        """
        return file_path.replace("/", ".").replace(".py", "")

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
