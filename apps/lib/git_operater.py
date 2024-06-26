import os
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
        list[str]: 変更のあったファイルの絶対パスのリスト
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


def get_git_staged_paths() -> list[str]:
    """ステージングされた変更のあるファイルの絶対パスをリストで取得する
    Returns:
        list[str]: ステージングされた変更のあるファイルの絶対パスのリスト
    """

    result = subprocess.run(["git", "diff", "--name-only", "--cached"], capture_output=True, text=True)
    relative_paths = result.stdout.split("\n")
    paths = []
    for relative_path in relative_paths:
        if relative_path:  # 空のパスを無視
            absolute_path = make_absolute_path(get_git_root_path(), relative_path)
            if os.path.isfile(absolute_path):  # パスがファイルを指している場合のみリストに追加
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


def get_diff_with_commit(commit_hash: str | None = None, paths: list[str] | None = None) -> str:
    """指定したコミットハッシュと現在の状態との差分を取得する。commit_hashがNoneの場合はワーキングステージ（最新のコミット）との差分を取得する。
    pathsにファイルやディレクトリのパスを指定することで、差分の表示されるファイルを制限できる。pathsがNoneの場合は、すべてのファイルの差分を取得する。

    Args:
        commit_hash (str | None): コミットのハッシュ値。Noneの場合はワーキングステージとの差分を取得。
        paths (list[str] | None): 差分を取得するファイルやディレクトリのパスのリスト。Noneの場合はすべてのファイルの差分を取得。

    Returns:
        str: 指定したコミットと現在の状態との差分
    """
    command = ["git", "diff"]
    if commit_hash is not None:
        command.append(commit_hash)
    if paths is not None:
        command.append("--")
        command.extend(paths)

    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

def get_git_commit_logs(count: int) -> str:
    """指定された件数のgitコミットログを取得するが、コミットメッセージのみを含むようにする

    Args:
        count (int): 取得するコミットの件数

    Returns:
        str: コミットログの出力
    """
    result = subprocess.run(["git", "log", f"--max-count={count}"], capture_output=True, text=True)
    return result.stdout
