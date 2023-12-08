from apps.lib.utils import read_file_content
from .dependency_analyzer.test_main import mock_path
import os


class TestMakeAbsolutePath:
    """make_absolute_path のテスト"""

    def test_make_absolute_path(self):
        """ルートパスと相対パスを組み合わせて絶対パスを生成できることを確認する"""
        root_path = '/Users/hogehoge/workspace/python/useful_tools/tests/mock'
        relative_path = 'ts_mock/ts_mock_b/ts_mock_b_1'
        absolute_path = os.path.join(root_path, relative_path)
        assert absolute_path == '/Users/hogehoge/workspace/python/useful_tools/tests/mock/ts_mock/ts_mock_b/ts_mock_b_1'


class TestReadFileContent:
    mock_file_path = os.path.join(mock_path, 'ts_mock', 'ts_mock_1.ts')

    def test_read_file_content(self):
        """ファイルの内容を読み込めることを確認する"""
        # ファイルの内容を読み込む
        file_content = read_file_content(self.mock_file_path)

        # ファイルの内容が読み込めていることを確認
        assert len(file_content) > 0
        assert type(file_content) is str
        assert file_content.startswith("import { ts_mock_a_1 } from '@/ts_mock/ts_mock_a/ts_mock_a_1'")
        assert file_content.endswith('\n')
