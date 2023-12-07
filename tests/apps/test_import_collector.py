import os
from apps.import_collector import main
from apps.lib.utils import count_tokens


# テスト用のファイルとディレクトリとして、mock 以下を使用
relative_path = os.path.join(os.path.dirname(__file__), '..', 'mock')
mock_path = os.path.abspath(relative_path)


class TestMain:
    target_relative_paths = ["ts_mock/ts_mock_1.ts"]

    """メイン関数のテスト"""
    def test_import_collector(self):
        optimized_content = main(
            mock_path,
            self.target_relative_paths,
        )

        assert len(optimized_content) == 1
        assert type(optimized_content) is list

    def test_import_collector_with_max_token_200(self):
        optimized_contents = main(
            mock_path,
            self.target_relative_paths,
            max_token=200
        )

        assert len(optimized_contents) == 3
        assert type(optimized_contents) is list
        assert all([count_tokens(content) <= 200 for content in optimized_contents])
