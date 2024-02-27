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


from apps.lib.git_diff import get_git_cached_diff
from apps.lib.outputs import copy_to_clipboard, print_colored


def create_commit_message(git_diff: str) -> str:
    """Gitの差分からコミットメッセージを作成する

    Args:
        git_diff (str): Gitの差分の文字列

    Returns:
        str: 作成されたコミットメッセージ
    """
    # ここでgit_diffを解析し、コミットメッセージを作成するロジックを実装する
    # 例: コミットメッセージのテンプレートを使用する
    commit_message = (
        f'以下のGitの差分からコミットメッセージを作成してください。\n"""\n{git_diff}\n"""\n生成したコミットメッセージは ``` ``` で囲ってください。\n'
    )
    return commit_message


if __name__ == "__main__":
    # Gitの差分を取得
    git_diff = get_git_cached_diff()

    git_diff_lines = git_diff.split("\n")
    git_diff_preview = "\n".join(git_diff_lines[:10])

    # コミットメッセージを作成
    commit_message = create_commit_message(git_diff_preview)

    # Gitの差分をターミナルに出力
    print_colored(("\n== Git Diff ==\n", "green"))
    print(git_diff)

    # コミットメッセージをクリップボードにコピー
    copy_to_clipboard(commit_message)
