from apps.lib.dependency_analyzer.file_analyzer_js import extract_module_names_from_imports


class TestExtractModuleNamesFromImports:
    file_contest = """
    'use server'

    import { postEmailLogin, EmailLoginRequestDto, ApiResponse } from '@/src/servers/shared/lib/handlers/postEmailLogin'
    import { revalidatePath, revalidateTag } from 'next/cache'
    import { ServerSessionStore } from '@/src/servers/shared/lib/ServerSessionStore'
    """

    def test_extract_module_names_from_imports(self):
        # モジュールパスを抽出
        module_paths = extract_module_names_from_imports(self.file_contest)
        print(module_paths)
        assert module_paths == [
            '/src/servers/shared/lib/handlers/postEmailLogin',
            '/src/servers/shared/lib/ServerSessionStore'
        ]
