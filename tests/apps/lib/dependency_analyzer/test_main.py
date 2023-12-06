import os
from apps.lib.dependency_analyzer.main import get_all_file_paths


class TestGetAllFilePaths:
    # テスト用のファイルとディレクトリとして、mock 以下を使用
    root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'mock')

    def test_get_all_file_paths(self):
        # テスト用のディレクトリ以下のファイルパスを取得
        file_paths = get_all_file_paths(self.root_path)

        # テスト用のディレクトリ以下のファイルパスが取得できていることを確認
        assert len(file_paths) == 30
