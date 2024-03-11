import subprocess

from apps.lib.utils import make_absolute_path


def get_git_cached_diff() -> str:
    """ステージングされた変更のgit diffを取得する

    Returns:
        str: git diffの出力
    """
    result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
    return result.stdout


def get_git_path_diff(branch_name: str | None = None) -> list[str]:
    """指定したブランチと現在のブランチの変更のあっファイルの絶対パスをリストで取得する

    Args:
        branch_name (str): 比較するブランチ名

    Returns:
        list[str]: ファイルの絶対パスのリスト
    """
    if branch_name is None:
        branch_name = get_main_branch_name()

    result = subprocess.run(["git", "diff", "--name-only", branch_name], capture_output=True, text=True)
    relative_paths = result.stdout.split("\n")

    paths = []
    for relative_path in relative_paths:
        absolute_path = make_absolute_path(get_git_root_path(), relative_path)
        paths.append(absolute_path)

    return paths


def get_git_root_path() -> str:
    """Gitのルートディレクトリの絶対パスを取得する

    Returns:
        str: Gitのルートディレクトリの絶対パス
    """
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return result.stdout.strip()


def get_main_branch_name() -> str:
    """Gitリモートのメインブランチの名称を取得する

    Returns:
        str: メインブランチの名称
    """
    # Gitリモートのメインブランチの名称を取得するコマンドを実行
    result = subprocess.run(["git", "remote", "show", "origin"], capture_output=True, text=True)
    # コマンドの出力からメインブランチの名称を抽出
    for line in result.stdout.split("\n"):
        if "HEAD branch" in line:
            main_branch_name = line.split(": ")[1]
            break
    else:
        # メインブランチの名称が見つからない場合は例外を発生させる
        raise Exception("メインブランチの名称が見つかりませんでした。")
    return main_branch_name


def get_file_diff_with_main_branch(file_path: str) -> str:
    """メインブランチと指定したファイルの差分を取得する

    Args:
        file_path (str): 差分を取得するファイルの絶対パス

    Returns:
        str: 指定したファイルの差分
    """
    main_branch_name = get_main_branch_name()
    result = subprocess.run(["git", "diff", main_branch_name, "--", file_path], capture_output=True, text=True)
    return result.stdout


def get_diff_with_commit(commit_hash: str) -> str:
    """指定したコミットハッシュと現在の状態との差分を取得する

    Args:
        commit_hash (str): コミットのハッシュ値

    Returns:
        str: 指定したコミットと現在の状態との差分
    """
    result = subprocess.run(["git", "diff", commit_hash], capture_output=True, text=True)
    return result.stdout
