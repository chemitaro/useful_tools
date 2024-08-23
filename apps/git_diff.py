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


from import_collector import import_collect  # noqa: E402
from lib.clipboard_util import copy_chunks_to_clipboard, copy_to_clipboard  # noqa: E402
from lib.file_content_collector import FileContentCollector  # noqa: E402
from lib.git_operater import (  # noqa: E402
    get_diff_with_commit,
    get_file_diff_with_main_branch,
    get_git_cached_diff,
    get_git_path_diff,
    get_git_staged_paths,
)
from lib.utils import (  # noqa: E402
    make_absolute_path,
    make_relative_path,
    print_colored,
    truncate_string,
)


def stage_diff_to_commit_clipboard(*, current_path: str) -> None:
    """ステージングされた変更をコミットメッセージにコピーする"""
    # Gitの差分を取得
    git_diff = get_git_cached_diff()

    # 変更のあったファイルの絶対パスを取得
    staged_paths = get_git_staged_paths()
    file_content_collector = FileContentCollector(root_path=current_path, file_paths=staged_paths)
    file_contents = file_content_collector.collect()
    output_content = "\n".join(file_contents)

    # ファイルの内容の前後のメッセージのプロンプト
    file_contents_prefix = '変更後のファイル\n"""\n'
    file_contents_suffix = '\n"""\n\n'

    # メッセージの前後のプロンプト
    git_diff_prefix = 'Gitの差分\n"""\n'
    git_diff_suffix = '\n"""\n'

    # コミットメッセージを結合する
    commit_message = (
        file_contents_prefix + output_content + file_contents_suffix + git_diff_prefix + git_diff + git_diff_suffix
    )

    # Gitの差分をターミナルに出力
    print_colored(("\n== Git Diff ==\n", "green"))
    print(truncate_string(git_diff, 1000))

    # コミットメッセージをクリップボードにコピー
    copy_chunks_to_clipboard(commit_message)


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

        import_collection = import_collect(
            root_path=current_path, target_paths=[relative_path], output="code", with_prompt=True
        )
        joined_import_collection = "\n".join(import_collection)

        # ファイルのメインブランチとの差分を取得
        file_diff = get_file_diff_with_main_branch(path)

        review_prompt = f'{joined_import_collection}\n\n### レビュー対象のコードの差分\n"""\n{file_diff}\n"""\n\n##指示:\n 以下のファイルに対してコードレビューをお願いします: \n- 変更点の内容と評価を簡潔に箇条書きで報告してください\n- 問題点や改善すると良い点やについて詳細に詳しく解説してください。 \n\n### レビュー対象のファイルのパス\n@{relative_path}\n'

        print_colored((f"{path_index}/{total_files}"), (f" {relative_path}", "cyan"))
        # クリップボードにコピー
        copy_to_clipboard(review_prompt)
        # エンターキーが押されるまで待機する
        print_colored(("Press Enter to continue...", "grey"))
        input()


def diff_with_commit(*, commit_hash: str | None = None, current_path: str, paths: list[str] | None = None) -> None:
    """指定したコミットハッシュと現在の状態との差分を表示しクリップボードにコピーする"""
    # pathsが相対パスの場合は絶対パスに変換する処理
    if paths is not None:
        absolute_paths = []
        for path in paths:
            if not os.path.isabs(path):
                absolute_path = make_absolute_path(current_path, path)
                absolute_paths.append(absolute_path)
            else:
                absolute_paths.append(path)
    else:
        absolute_paths = None

    # 指定したコミットハッシュと現在の状態との差分を取得
    git_diff = get_diff_with_commit(commit_hash=commit_hash, paths=absolute_paths)

    # Gitの差分をターミナルに出力
    print_colored(("\n== Git Diff ==\n", "green"))
    print_colored((truncate_string(git_diff, 1000)))

    # Gitの差分をクリップボードにコピー
    prefix = f'以下のコミットハッシュと現在の状態との差分を表示します。\nコミットハッシュ: {commit_hash}\n"""\n'
    suffix = '\n"""\n'
    copy_chunks_to_clipboard(prefix + git_diff + suffix)


def stage_diff_to_clipboard(*, current_path: str) -> None:
    """ステージングされた変更をコミットメッセージにコピーする"""
    # Gitの差分を取得
    git_diff = get_git_cached_diff()

    # Gitの差分をターミナルに出力
    print_colored(("\n== Git Diff ==\n", "green"))
    print_colored((truncate_string(git_diff, 1000)))

    # Gitの差分をクリップボードにコピー
    prefix = '以下のステージングされた変更の差分を表示します。\n"""\n'
    suffix = '\n"""\n'
    copy_chunks_to_clipboard(prefix + git_diff + suffix)


def main() -> None:
    # argparseのパーサーを作成
    parser = argparse.ArgumentParser(
        description="Gitの差分を表示、コミットメッセージ作成、コードレビュー依頼を行います。"
    )
    # サブコマンドを追加
    subparsers = parser.add_subparsers(dest="command")

    # 'diff'サブコマンドを追加
    diff_parser = subparsers.add_parser("diff", help="指定したコミットと現在の状態との差分を表示します。")
    diff_parser.add_argument(
        "commit_hash", type=str, help="差分を取得するコミットのハッシュ値を指定します。", nargs="?", default=None
    )
    diff_parser.add_argument(
        "-p", "--paths", type=str, help="差分を取得するファイルやディレクトリのパスを指定します。", nargs="*"
    )

    # 'stage' サブコマンドを追加
    subparsers.add_parser("stage", help="ステージングされた変更の差分をクリップボードにコピーします。")

    # 'commit'サブコマンドを追加
    subparsers.add_parser("commit", help="ステージングされた変更をコミットメッセージにコピーします。")

    # 'review'サブコマンドを追加
    subparsers.add_parser("review", help="コードレビューを依頼するプロンプトを作成します。")

    # 引数を解析
    args = parser.parse_args()

    # 現在のワーキングディレクトリのパスを取得
    current_path = os.getcwd()

    # 'diff'サブコマンドが指定された場合、diff_with_commit関数を実行
    if args.command == "diff":
        diff_with_commit(commit_hash=args.commit_hash, current_path=current_path, paths=args.paths)

    # 'stage' サブコマンドが指定された場合、stage_diff_to_commit_clipboard関数を実行
    elif args.command == "stage":
        stage_diff_to_clipboard(current_path=current_path)

    # 'commit'サブコマンドが指定された場合、stage_diff_to_commit_clipboard関数を実行
    elif args.command == "commit":
        stage_diff_to_commit_clipboard(current_path=current_path)

    # 'review'サブコマンドが指定された場合、code_review_prompt_clipboard関数を実行
    elif args.command == "review":
        code_review_prompt_clipboard()

    # サブコマンドが指定されていない場合、ヘルプを表示
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
