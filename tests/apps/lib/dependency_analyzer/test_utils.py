from apps.lib.dependency_analyzer.utils import read_file_content
from .test_main import mock_path
import os


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
