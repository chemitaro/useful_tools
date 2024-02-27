import subprocess


def get_git_cached_diff() -> str:
    """ステージングされた変更のgit diffを取得する

    Returns:
        str: git diffの出力
    """
    result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
    return result.stdout
