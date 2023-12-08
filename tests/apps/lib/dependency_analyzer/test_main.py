import os

from apps.lib.dependency_analyzer.main import get_all_file_paths, DependencyAnalyzer

# テスト用のファイルとディレクトリとして、mock 以下を使用
relative_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'mock')
mock_path = os.path.abspath(relative_path)


class TestGetAllFilePaths:
    """get_all_file_paths のテスト"""

    def test_get_all_file_paths(self):
        # テスト用のディレクトリ以下のファイルパスを取得
        file_paths = get_all_file_paths(mock_path)

        # テスト用のディレクトリ以下のファイルパスが取得できていることを確認
        assert len(file_paths) == 33


class TestDependencyAnalyzer:
    """DependencyAnalyzer のテスト"""

    analyzer = DependencyAnalyzer.factory(
        mock_path,
        ['ts_mock/ts_mock_1.ts']
    )

    def test_init(self):
        """初期化してインスタンスを生成できることを確認する"""
        assert type(self.analyzer) is DependencyAnalyzer

    def test_ts_analyze(self):
        """TypeScript のファイルを解析できることを確認する"""
        # 解析する
        result_paths = self.analyzer.analyze()

        # 解析結果を確認
        assert len(result_paths) == 7
        assert os.path.join(mock_path, 'ts_mock/ts_mock_1.ts') in result_paths
        assert os.path.join(mock_path, 'ts_mock/ts_mock_a/ts_mock_a_1.ts') in result_paths
        assert os.path.join(mock_path, 'ts_mock/ts_mock_b/ts_mock_b_1.ts') in result_paths
        assert os.path.join(mock_path, 'ts_mock/ts_mock_a/ts_mock_a_a/ts_mock_a_a_1.ts') in result_paths
        assert os.path.join(mock_path, 'ts_mock/ts_mock_a/ts_mock_a_b/ts_mock_a_b_1.ts') in result_paths
        assert os.path.join(mock_path, 'ts_mock/ts_mock_b/ts_mock_b_a/ts_mock_b_a_1.ts') in result_paths
        assert os.path.join(mock_path, 'ts_mock/ts_mock_b/ts_mock_b_b/ts_mock_b_b_1.ts') in result_paths

    def test_py_analyze(self):
        """Python のファイルを解析できることを確認する"""
        # 解析する
        analyzer = DependencyAnalyzer.factory(
            mock_path,
            ['py_mock/py_mock_1.py']
        )
        result_paths = analyzer.analyze()

        # 解析結果を確認
        assert type(result_paths) is list
        assert len(result_paths) == 7
        assert os.path.join(mock_path, 'py_mock/py_mock_1.py') in result_paths
        assert os.path.join(mock_path, 'py_mock/py_mock_a/py_mock_a_1.py') in result_paths
        assert os.path.join(mock_path, 'py_mock/py_mock_b/py_mock_b_1.py') in result_paths
        assert os.path.join(mock_path, 'py_mock/py_mock_a/py_mock_a_a/py_mock_a_a_1.py') in result_paths
        assert os.path.join(mock_path, 'py_mock/py_mock_a/py_mock_a_b/py_mock_a_b_1.py') in result_paths
        assert os.path.join(mock_path, 'py_mock/py_mock_b/py_mock_b_a/py_mock_b_a_1.py') in result_paths
        assert os.path.join(mock_path, 'py_mock/py_mock_b/py_mock_b_b/py_mock_b_b_1.py') in result_paths

    def test_py_analyze_with_relative_import(self):
        """相対インポートを含む Python のファイルを解析できることを確認する"""
        # 解析する
        analyzer = DependencyAnalyzer.factory(
            mock_path,
            ['py_mock/py_mock_a/py_mock_a_2.py']
        )
        result_paths = analyzer.analyze()

        # 解析結果を確認
        assert type(result_paths) is list
        assert len(result_paths) == 3
        assert os.path.join(mock_path, 'py_mock/py_mock_a/py_mock_a_2.py') in result_paths
        assert os.path.join(mock_path, 'py_mock/py_mock_a/py_mock_a_a/py_mock_a_a_2.py') in result_paths
        assert os.path.join(mock_path, 'py_mock/py_mock_a/py_mock_a_b/py_mock_a_b_2.py') in result_paths
