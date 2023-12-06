import re
import os
from apps.lib.dependency_analyzer.main import FileAnalyzerIF, make_absolute_path, make_relative_path, read_file_content


def extract_module_names_from_imports(file_content: str) -> list[str]:
    """ファイルの内容からモジュールパスを抽出する

    Args:
        file_content (str): ファイルの内容

    Returns:
        list[str]: モジュールパスのリスト
    """
    # インポート文を検索するための正規表現パターン
    import_pattern = r"import .* from ['\"](@?[^'\"]+)['\"]"

    # 正規表現を用いてインポート文を検索
    matches: list[str] = re.findall(import_pattern, file_content)

    # matchesの中身が全て文字列で無い場合は例外を発生させる
    if not all(isinstance(match, str) for match in matches):
        raise ValueError('matches の中身が全て文字列である必要があります')

    # アットマークを除去してリストに追加
    paths = [match.lstrip('@') for match in matches if match.startswith('@')]

    return paths


# ファイルの内容を読み込む（例）
# file_content = """
# 'use server'

# import { postEmailLogin, EmailLoginRequestDto, ApiResponse } from '@/src/servers/shared/lib/handlers/postEmailLogin'
# import { revalidatePath, revalidateTag } from 'next/cache'
# import { ServerSessionStore } from '@/src/servers/shared/lib/ServerSessionStore'


# /**
#  * メールアドレスとパスワードを使用して Management-API へログイン処理を行い、アクセストークンとリフレッシュトークンをcookieに保存する
#  */
# export async function emailLoginAction(EmailLoginRequestDto: EmailLoginRequestDto): Promise<ApiResponse> {
#   const response = await postEmailLogin(EmailLoginRequestDto)
#   if (response.statusCode === 200) {
#     // すべてのcacheを削除する
#     revalidatePath('/')
#     revalidateTag('management-api')

#     // ログインに成功した場合、アクセストークンとリフレッシュトークンをcookieに保存する
#     const sessionStore = ServerSessionStore.factoryNew()
#     sessionStore.setAccessToken(response.body.accessToken)
#     sessionStore.setRefreshToken(response.body.refreshToken)
#   }
#   return response
# }
# """

# # モジュールパスを抽出
# module_paths = extract_module_paths_from_imports(file_content)
# print(module_paths)



class FileAnalyzerJs(FileAnalyzerIF):
    def analyze(self, target_path: str) -> list[str]:
        return []  # TODO: 未実装

    def convert_module_name_to_file_path(self, module_name: str) -> str | None:
        """指定されたモジュール名にマッチするファイルパスを探す

        Args:
            module_name (str): モジュール名

        Returns:
            str: マッチしたファイルパス
        """
        extensions = ['.ts', '.js', '.tsx', '.jsx']

        # ルートディレクトリとモジュールのパスを組み合わせて拡張子のないパスを生成
        base_path = make_absolute_path(self.root_path, module_name)

        # 指定されたすべての拡張子に対してチェック
        for ext in extensions:
            potential_path = f"{base_path}{ext}"
            if potential_path in self.all_file_paths:
                return potential_path

        # マッチするものが見つからない場合は None を返す
        return None
