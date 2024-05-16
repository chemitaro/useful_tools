import os

from apps.lib.dependency_analyzer.main import (DependencyAnalyzer,
                                               get_all_file_paths)

# テスト用のファイルとディレクトリとして、mock 以下を使用
relative_path: str = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'mock')
mock_path: str = os.path.abspath(relative_path)


class TestGetAllFilePaths:
    """get_all_file_paths のテスト"""

    def test_get_all_file_paths(self):
        # テスト用のディレクトリ以下のファイルパスを取得
        file_paths = get_all_file_paths(mock_path)

        # テスト用のディレクトリ以下のファイルパスが取得できていることを確認
        assert len(file_paths) == 33

    def test_scope_paths(self):
        """探索範囲を指定できることを確認する"""
        # テスト用のディレクトリ以下のファイルパスを取得
        file_paths = get_all_file_paths(mock_path, scope_paths=['ts_mock'])

        # テスト用のディレクトリ以下のファイルパスが取得できていることを確認
        assert len(file_paths) == 13
        # pathの戦闘が指定したディレクトリ(mock_path/ts_mock)以下であることを確認
        assert all([p.startswith(os.path.join(mock_path, 'ts_mock')) for p in file_paths])

    def test_ignore_paths(self):
        """無視するパスを指定できることを確認する"""
        # テスト用のディレクトリ以下のファイルパスを取得
        file_paths = get_all_file_paths(mock_path, ignore_paths=['ts_mock'])

        # テスト用のディレクトリ以下のファイルパスが取得できていることを確認
        assert len(file_paths) == 20
        # pathの戦闘が指定したディレクトリ(mock_path/ts_mock)以下でないことを確認
        assert all([not p.startswith(os.path.join(mock_path, 'ts_mock')) for p in file_paths])


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
        analyzer = DependencyAnalyzer.factory(
            mock_path,
            start_relative_paths=['ts_mock/ts_mock_1.ts']
        )
        result_paths = analyzer.analyze()

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
        assert isinstance(result_paths, list)
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
        assert isinstance(result_paths, list)
        assert len(result_paths) == 3
        assert os.path.join(mock_path, 'py_mock/py_mock_a/py_mock_a_2.py') in result_paths
        assert os.path.join(mock_path, 'py_mock/py_mock_a/py_mock_a_a/py_mock_a_a_2.py') in result_paths
        assert os.path.join(mock_path, 'py_mock/py_mock_a/py_mock_a_b/py_mock_a_b_2.py') in result_paths

    # depth が0の場合は、start_pathsがそのまま返ることを確認する。
    def test_depth_0(self):
        """depth が 0 の場合は、start_paths がそのまま返ることを確認する"""
        # 解析する
        analyzer = DependencyAnalyzer.factory(
            mock_path,
            ['py_mock/py_mock_1.py'],
            depth=1
        )
        result_paths = analyzer.analyze()

        # 解析結果を確認
        assert isinstance(result_paths, list)
        assert len(result_paths) == 1
        assert os.path.join(mock_path, 'py_mock/py_mock_1.py') in result_paths
