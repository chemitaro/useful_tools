import os

from apps.lib.file_content_collector import FileContentCollector


class TestFileContentCollector:
    """FileContentCollector のテスト"""

    # テスト用のファイルとディレクトリとして、mock 以下を使用
    relative_path = os.path.join(os.path.dirname(__file__), '..', '..', 'mock')
    mock_path = os.path.abspath(relative_path)

    file_paths = [
        os.path.join(mock_path, 'ts_mock/ts_mock_1.ts'),
        os.path.join(mock_path, 'ts_mock/ts_mock_a/ts_mock_a_1.ts'),
        os.path.join(mock_path, 'ts_mock/ts_mock_b/ts_mock_b_1.ts'),
        os.path.join(mock_path, 'ts_mock/ts_mock_a/ts_mock_a_a/ts_mock_a_a_1.ts'),
        os.path.join(mock_path, 'ts_mock/ts_mock_a/ts_mock_a_b/ts_mock_a_b_1.ts'),
        os.path.join(mock_path, 'ts_mock/ts_mock_b/ts_mock_b_a/ts_mock_b_a_1.ts'),
        os.path.join(mock_path, 'ts_mock/ts_mock_b/ts_mock_b_b/ts_mock_b_b_1.ts'),
    ]

    collector = FileContentCollector(
        file_paths, mock_path
    )

    def test_init(self):
        """初期化してインスタンスを生成できることを確認する"""
        assert type(self.collector) is FileContentCollector

    def test_collect(self):
        """ファイルの内容を収集できることを確認する"""
        # ファイルの内容を収集する
        contents = self.collector.collect()

        # ファイルの内容が収集できていることを確認
        assert len(contents) == 7
        assert all([type(content) is str for content in contents])
