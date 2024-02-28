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


from apps.lib.file_path_formatter import FilePathFormatter  # noqa: E402
from apps.lib.git_operater import get_git_cached_diff, get_git_path_diff  # noqa: E402
from apps.lib.outputs import copy_to_clipboard, print_colored  # noqa: E402
from apps.lib.utils import truncate_string  # noqa: E402


def stage_diff_to_commit_clipboard() -> None:
    """ステージングされた変更をコミットメッセージにコピーする"""
    # Gitの差分を取得
    git_diff = get_git_cached_diff()

    # コミットメッセージを作成
    commit_message = (
        f'以下のGitの差分からコミットメッセージを作成してください。\n"""\n{git_diff}\n"""\n生成したコミットメッセージは ``` ``` で囲ってください。\n'
    )

    # Gitの差分をターミナルに出力
    print_colored(("\n== Git Diff ==\n", "green"))
    print(truncate_string(git_diff, 1000))

    # コミットメッセージをクリップボードにコピー
    copy_to_clipboard(commit_message)


# コードレビューを依頼するプロンプトを作成する関数
def code_review_prompt_clipboard(branch: str | None = None) -> None:
    """コードレビューを依頼するプロンプトを作成する"""
    # 現在の作業ディレクトリのパスを取得
    current_path = os.getcwd()

    # 変更のあったファイルの絶対パスを取得
    changed_file_paths = get_git_path_diff(branch)

    # 現在の作業ディレクトリとマッチするパスのみを保持
    changed_file_paths = [path for path in changed_file_paths if path.startswith(current_path)]

    # ファイルの相対パスをCursor用に整形
    path_formatter = FilePathFormatter(changed_file_paths, current_path, type="cursor")
    formatted_file_paths = path_formatter.format()

    # 変更のあったファイルの数をターミナルに出力
    total_files = len(formatted_file_paths)
    print_colored(("\n== Changed Files ==\n", "green"))
    print_colored(f"file count: {total_files}")

    # 変更のあったファイルの相対パスをターミナルに出力し、コードレビューを依頼するプロンプトをクリップボードにコピー
    path_index = 0
    for path in formatted_file_paths:
        path_index += 1
        total_files = len(formatted_file_paths)
        print_colored((f"{path_index}/{total_files}"), (f" {path}", "cyan"))
        review_prompt = f"以下のファイルに対してコードレビューをお願いします:\n{path}\n"
        # クリップボードにコピー
        pyperclip.copy(review_prompt)
        # エンターキーが押されるまで待機する
        print_colored(("Press Enter to continue...", "grey"))
        input()


if __name__ == "__main__":
    # argparseのパーサーを作成
    parser = argparse.ArgumentParser(description="Gitの差分をコミットメッセージにコピーまたはコードレビューを依頼します。")
    # 'action'という名前の引数を追加（フラグなしの位置引数）
    parser.add_argument("action", nargs="?", help="実行するアクションを指定します。('commit'または'review')")
    # 引数を解析
    args = parser.parse_args()

    # 'action'引数が'commit_message'の場合、stage_diff_to_commit_clipboard関数を実行
    if args.action == "commit":
        stage_diff_to_commit_clipboard()

    # 'action'引数が'review'の場合、code_review_prompt_clipboard関数を実行
    if args.action == "review":
        code_review_prompt_clipboard()

    # argparseのヘルプを表示
    if args.action not in ["commit", "review"]:
        parser.print_help()
        sys.exit(1)
