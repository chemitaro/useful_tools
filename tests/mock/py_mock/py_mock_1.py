import os
import sys

# 現在のファイルの絶対パスを取得
current_file_path = os.path.abspath(__file__)

# ルートディレクトリまでのパスを取得（例：2階層上がルートディレクトリの場合）
root_directory = os.path.dirname(os.path.dirname(current_file_path))

# Pythonの実行パスにルートディレクトリを追加
if root_directory not in sys.path:
    sys.path.append(root_directory)


from py_mock.py_mock_a.py_mock_a_1 import py_mock_a_1  # noqa: E402
from py_mock.py_mock_b.py_mock_b_1 import py_mock_b_1  # noqa: E402

py_mock_1 = "py_mock_1"
print(py_mock_a_1)
print(py_mock_b_1)


class Mock0:
    str_field: str

    def __init__(self, str_field: str):
        self.field = str_field

    def get_field(self) -> str:
        return self.str_field


class Mock1(Mock0):
    pass


class Mock2:
    num_field: int
    mock_object: Mock1

    def __init__(self, num_field: int, mock_object: Mock1):
        self.num_field = num_field
        self.mock_object = mock_object

    def get_field(self) -> str:
        return self.field

    def get_mock_field(self) -> str:
        return self.mock_object.get_field()


class Mock2Collection:
    mock_objects: list[Mock2]

    def __init__(self, mock_objects: list[Mock2]):
        self.mock_objects = mock_objects

    def get_mock_fields(self) -> list[str]:
        return [mock.get_mock_field() for mock in self.mock_objects]

    def get_num_fields(self) -> list[int]:
        return [mock.num_field for mock in self.mock_objects]
