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

py_mock_1 = 'py_mock_1'
print(py_mock_a_1)
print(py_mock_b_1)
