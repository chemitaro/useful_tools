import subprocess


def get_git_cached_diff() -> str:
    """ステージングされた変更のgit diffを取得する

    Returns:
        str: git diffの出力
    """
    result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
    return result.stdout


def get_git_root_path() -> str:
    """Gitのルートディレクトリの絶対パスを取得する

    Returns:
        str: Gitのルートディレクトリの絶対パス
    """
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return result.stdout.strip()
