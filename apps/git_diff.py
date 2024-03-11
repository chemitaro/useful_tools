#!/usr/bin/env python3

import argparse
import os
import sys

import pyperclip

# 現在のファイルの絶対パスを取得
current_file_path = os.path.abspath(__file__)

# ルートディレクトリまでのパスを取得（例：2階層上がルートディレクトリの場合）
root_directory = os.path.dirname(os.path.dirname(current_file_path))

# Pythonの実行パスにルートディレクトリを追加
if root_directory not in sys.path:
    sys.path.append(root_directory)


from apps.import_collector import import_collect  # noqa: E402
from apps.lib.git_operater import (  # noqa: E402
    get_diff_with_commit,  # 追加されたインポート
    get_file_diff_with_main_branch,
    get_git_cached_diff,
    get_git_path_diff,
)
from apps.lib.outputs import copy_to_clipboard, print_colored  # noqa: E402
from apps.lib.utils import make_relative_path, truncate_string  # noqa: E402


def stage_diff_to_commit_clipboard() -> None:
    """ステージングされた変更をコミットメッセージにコピーする"""
    # Gitの差分を取得
    git_diff = get_git_cached_diff()
    # メッセージの接頭部
    commit_message_prefix = '''以下のGitの差分からコミットメッセージを作成してください。
    """
    '''
    # メッセージの接尾部
    commit_message_suffix = '''
    """
    コミットメッセージは内容の概要と修正点を箇条書きで生成してください。
    生成したコミットメッセージは ``` ``` で囲ってください。
    言語は日本語です。

    記入例
    ```
    {修正点の説明}

    - {修正内容の詳細 1つ目}
    - {修正内容の詳細 2つ目}
    - {修正内容の詳細 nつ目}
    ```

    それではGitコミットメッセージを作成してください。
    '''
    # コミットメッセージを結合する
    commit_message = commit_message_prefix + git_diff + commit_message_suffix

    # Gitの差分をターミナルに出力
    print_colored(("\n== Git Diff ==\n", "green"))
    print(truncate_string(git_diff, 1000))

    # コミットメッセージをクリップボードにコピー
    copy_to_clipboard(commit_message)


def code_review_prompt_clipboard(branch: str | None = None) -> None:
    """コードレビューを依頼するプロンプトを作成する"""
    # 現在の作業ディレクトリのパスを取得
    current_path = os.getcwd()

    # 変更のあったファイルの絶対パスを取得
    changed_file_paths = get_git_path_diff(branch)

    # 現在の作業ディレクトリとマッチするパスのみを保持
    changed_file_paths = [path for path in changed_file_paths if path.startswith(current_path)]

    # 変更のあったファイルの数をターミナルに出力
    total_files = len(changed_file_paths)
    print_colored(("\n== Changed Files ==\n", "green"))
    print_colored(f"file count: {total_files}")

    # 変更のあったファイルの相対パスをターミナルに出力し、コードレビューを依頼するプロンプトをクリップボードにコピー
    path_index = 0
    for path in changed_file_paths:
        path_index += 1
        total_files = len(changed_file_paths)
        # 絶対パスを相対パスに変換
        relative_path = make_relative_path(current_path, path)

        import_collection = import_collect(root_path=current_path, target_paths=[relative_path], output="path", with_prompt=True)
        joined_import_collection = "\n".join(import_collection)

        # ファイルのメインブランチとの差分を取得
        file_diff = get_file_diff_with_main_branch(path)

        review_prompt = f'{joined_import_collection}\n\n### レビュー対象のコードの差分\n"""\n{file_diff}\n"""\n\n##指示:\n 以下のファイルに対してコードレビューをお願いします: \n- 変更点の内容と評価を簡潔に箇条書きで報告してください\n- 問題点や改善すると良い点やについて詳細に詳しく解説してください。 \n\n### レビュー対象のファイルのパス\n@{relative_path}\n'

        print_colored((f"{path_index}/{total_files}"), (f" {relative_path}", "cyan"))
        # クリップボードにコピー
        pyperclip.copy(review_prompt)
        # エンターキーが押されるまで待機する
        print_colored(("Press Enter to continue...", "grey"))
        input()


def diff_with_commit(commit_hash: str) -> None:
    """指定したコミットハッシュと現在の状態との差分を表示しクリップボードにコピーする"""
    # 指定したコミットハッシュと現在の状態との差分を取得
    git_diff = get_diff_with_commit(commit_hash)

    # Gitの差分をターミナルに出力
    print_colored(("\n== Git Diff ==\n", "green"))
    print(truncate_string(git_diff, 1000))

    # Gitの差分をクリップボードにコピー
    copy_to_clipboard(git_diff)


if __name__ == "__main__":
    # argparseのパーサーを作成
    parser = argparse.ArgumentParser(description="Gitの差分を表示、コミットメッセージ作成、コードレビュー依頼を行います。")
    # サブコマンドを追加
    subparsers = parser.add_subparsers(dest="command")

    # 'diff'サブコマンドを追加
    diff_parser = subparsers.add_parser("diff", help="指定したコミットと現在の状態との差分を表示します。")
    diff_parser.add_argument("commit_hash", type=str, help="差分を取得するコミットのハッシュ値を指定します。")

    # 'commit'サブコマンドを追加
    commit_parser = subparsers.add_parser("commit", help="ステージングされた変更をコミットメッセージにコピーします。")

    # 'review'サブコマンドを追加
    review_parser = subparsers.add_parser("review", help="コードレビューを依頼するプロンプトを作成します。")

    # 引数を解析
    args = parser.parse_args()

    # 'diff'サブコマンドが指定された場合、diff_with_commit関数を実行
    if args.command == "diff":
        diff_with_commit(args.commit_hash)

    # 'commit'サブコマンドが指定された場合、stage_diff_to_commit_clipboard関数を実行
    elif args.command == "commit":
        stage_diff_to_commit_clipboard()

    # 'review'サブコマンドが指定された場合、code_review_prompt_clipboard関数を実行
    elif args.command == "review":
        code_review_prompt_clipboard()

    # サブコマンドが指定されていない場合、ヘルプを表示
    else:
        parser.print_help()
