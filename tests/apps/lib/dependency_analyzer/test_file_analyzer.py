from apps.lib.dependency_analyzer.file_analyzer import extract_module_names_from_imports, FileAnalyzerJs


class TestExtractModuleNamesFromImports:
    file_contest = """
    'use server'

    import { postEmailLogin, EmailLoginRequestDto, ApiResponse } from '@/src/servers/shared/lib/handlers/postEmailLogin'
    import { revalidatePath, revalidateTag } from 'next/cache';
    import { ServerSessionStore } from '@/src/servers/shared/lib/ServerSessionStore'
    """

    def test_extract_module_names_from_imports(self):
        """ファイルの内容からモジュールパスを抽出することができることを確認する"""
        # モジュールパスを抽出
        module_paths = extract_module_names_from_imports(self.file_contest)
        print(module_paths)
        assert module_paths == [
            '/src/servers/shared/lib/handlers/postEmailLogin',
            '/src/servers/shared/lib/ServerSessionStore'
        ]


class TestFileAnalyzerJs:
    """FileAnalyzerJs のテスト"""

    # 初期化してインスタンスを生成できることを確認する
    def test_init(self):
        root_path = '/root/path'
        all_file_paths = ['/root/path/file1.js', '/root/path/file2.js']
        analyzer = FileAnalyzerJs(root_path, all_file_paths)
        assert type(analyzer) is FileAnalyzerJs
        assert analyzer.root_path == root_path
        assert analyzer.all_file_paths == all_file_paths
