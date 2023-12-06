import re
import os


def extract_module_paths_from_imports(file_content: str) -> list[str]:
    """ファイルの内容からモジュールパスを抽出する

    Args:
        file_content (str): ファイルの内容

    Returns:
        list[str]: モジュールパスのリスト
    """
    # インポート文を検索するための正規表現パターン
    import_pattern = r"import .* from ['\"](@?[^'\"]+)['\"]"

    # 正規表現を用いてインポート文を検索
    matches = re.findall(import_pattern, file_content)

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


def find_matching_file_path(
    root_dir: str,
    module_path: str,
    all_file_paths: list[str],
    extensions: list[str] | None = None
) -> str | None:
    """指定されたファイルパスのリストから、指定されたモジュールパスにマッチするものを探す

    Args:
        root_dir (str): ルートディレクトリのパス
        module_path (str): モジュールのパス
        all_file_paths (list[str]): ファイルパスのリスト
        extensions (list[str], optional): 拡張子のリスト. Defaults to ['.js', '.ts', '.tsx', '.jsx'].

    Returns:
        str: マッチしたファイルパス
    """
    if extensions is None:
        extensions = ['.ts', '.js', '.tsx', '.jsx']
    # ルートディレクトリとモジュールのパスを組み合わせて基本パスを生成
    base_path = os.path.join(root_dir, module_path)

    # 指定されたすべての拡張子に対してチェック
    for ext in extensions:
        potential_path = f"{base_path}{ext}"
        if potential_path in all_file_paths:
            return potential_path

    # マッチするものが見つからない場合は None を返す
    return None


# 使用例
# root_dir = "/path/to/root"
# module_path = "src/servers/shared/lib/handlers/postEmailLogin"
# file_paths = [
#     "/path/to/root/src/servers/shared/lib/handlers/postEmailLogin.js",
#     "/path/to/root/src/servers/shared/lib/handlers/postEmailLogin.ts",
#     # その他のファイルパス...
# ]
# extensions = ['.js', '.ts', '.tsx', '.jsx']

# matching_path = find_matching_file_path(root_dir, module_path, file_paths, extensions)
# print("matching_path")
# print(matching_path)


# ファイルのパスから、そのファイルが依存しているモジュールのパスを抽出して返す
