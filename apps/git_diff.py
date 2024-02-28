#!/usr/bin/env python3

import argparse
import os
import sys

# 現在のファイルの絶対パスを取得
current_file_path = os.path.abspath(__file__)

# ルートディレクトリまでのパスを取得（例：2階層上がルートディレクトリの場合）
root_directory = os.path.dirname(os.path.dirname(current_file_path))

# Pythonの実行パスにルートディレクトリを追加
if root_directory not in sys.path:
    sys.path.append(root_directory)


from apps.lib.git_operater import get_git_cached_diff  # noqa: E402
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


if __name__ == "__main__":
    # argparseのパーサーを作成
    parser = argparse.ArgumentParser(description="Gitの差分をコミットメッセージにコピーします。")
    # 'commit_message'という名前の引数を追加（フラグなしの位置引数）
    parser.add_argument("commit_message", nargs="?", help="コミットメッセージを指定します。")
    # 引数を解析
    args = parser.parse_args()

    # 'commit_message'引数が指定された場合、stage_diff_to_commit_clipboard関数を実行
    if args.commit_message:
        stage_diff_to_commit_clipboard()
