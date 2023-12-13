#!/usr/bin/env python3

import argparse
import os
import sys
from dataclasses import dataclass

# 現在のファイルの絶対パスを取得
current_file_path = os.path.abspath(__file__)

# ルートディレクトリまでのパスを取得（例：2階層上がルートディレクトリの場合）
root_directory = os.path.dirname(os.path.dirname(current_file_path))

# Pythonの実行パスにルートディレクトリを追加
if root_directory not in sys.path:
    sys.path.append(root_directory)


from apps.lib.content_size_optimizer import ContentSizeOptimizer  # noqa: E402
from apps.lib.dependency_analyzer.main import DependencyAnalyzer  # noqa: E402
from apps.lib.file_content_collector import FileContentCollector  # noqa: E402
from apps.lib.outputs import copy_to_clipboard, print_result  # noqa: E402
from apps.lib.path_tree import PathTree  # noqa: E402
from apps.lib.utils import print_colored  # noqa: E402

default_depth = 999
default_max_char = 999_999_999
default_max_token = 25_000


@dataclass
class MainArgs:
    root_path: str
    target_paths: list[str] | None
    scope_paths: list[str] | None
    ignore_paths: list[str] | None
    depth: int | None
    no_comment: bool | None
    max_char: int | None
    max_token: int | None


def main(
    root_path: str,
    target_paths: list[str] | None = None,
    scope_paths: list[str] | None = None,
    ignore_paths: list[str] | None = None,
    depth: int = default_depth,
    no_comment: bool = False,
    max_char: int = default_max_char,
    max_token: int = default_max_token,
) -> list[str]:
    """指定されたファイルのパスのファイルの内容を取得する

    Args:
        root_path (str): 起点となるファイルのパス
        module_paths (List[str], optional): 起点となるファイルのパスからの相対パスのリスト. Defaults to [].
        depth (int, optional): 起点となるファイルのパスからの相対パスのリスト. Defaults to sys.maxsize.
        no_comment (bool, optional): コメントを除去するかどうか. Defaults to False.
        max_chara (int, optional): ファイルの内容を取得する際のチャンクサイズ. Defaults to sys.maxsize.
        ignores (List[str], optional): 除外するファイルのパスのリスト. Defaults to [].

    Returns:
        List[str]: 指定されたファイルのパスのファイルの内容のリスト
    """
    if target_paths is None:
        target_paths = []
    if scope_paths is None:
        scope_paths = []
    if ignore_paths is None:
        ignore_paths = []

    # ファイルの依存関係を解析
    dependency_analyzer = DependencyAnalyzer.factory(
        root_path=root_path,
        start_relative_paths=target_paths,
        scope_relative_paths=scope_paths,
        ignore_relative_paths=ignore_paths,
        depth=depth
    )
    dependency_file_paths: list[str] = dependency_analyzer.analyze()

    # 取得したファイルのパスをツリー構造で表示
    path_tree = PathTree(dependency_file_paths, root_path=root_path)
    path_tree.print_tree_map()

    # ファイルの内容を取得
    file_content_collector = FileContentCollector(
        dependency_file_paths,
        root_path,
        no_docstring=no_comment
    )
    contents = file_content_collector.collect()

    # ディレクトリ構成図をコンテンツの先頭に追加する
    path_tree_content = path_tree.get_tree_map()
    contents.insert(0, path_tree_content)

    # 取得したコンテンツをトークン数で調整する
    optimizer = ContentSizeOptimizer(
        contents,
        max_char=max_char,
        max_token=max_token
    )
    optimized_contents = optimizer.optimize_contents()
    return optimized_contents


if __name__ == "__main__":
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(
        description="""
        This tool analyzes the dependencies of Python programs, displays all the code in those files, and also copies them to the clipboard.
        It is also possible to omit document comments by adding options.
        Assuming a character limit, you can also split the copy to the clipboard by a specified number of characters.
        """
    )
    parser.add_argument(
        'target_path',
        nargs='*',
        help='Path of the Python file from which to parse dependencies, multiple paths can be specified'
    )
    parser.add_argument(
        '-r',
        '--root_path',
        type=str,
        help='Specify the root path of the project'
    )
    parser.add_argument(
        '-s',
        '--scope_paths',
        nargs='*',
        help='Specify paths of files to scope, multiple files can be specified'
    )
    parser.add_argument(
        '-i',
        '--ignore_paths',
        nargs='*',
        help='Specify paths of files to ignore, multiple files can be specified'
    )
    parser.add_argument(
        '-d',
        '--depth',
        type=int,
        help='Specify depth of dependency analysis'
    )
    parser.add_argument(
        '-nc',
        '--no_comment',
        action='store_true',
        help='Omit document comments'
    )
    parser.add_argument(
        '-mt',
        '--max_token',
        type=int,
        help='Split by a specified number of tokens when copying to the clipboard'
    )
    parser.add_argument(
        '-mc',
        '--max_char',
        type=int,
        help='Split by a specified number of characters when copying to the clipboard'
    )
    args = parser.parse_args()

    # コマンドライン引数をMainArgsに変換
    main_args: MainArgs = MainArgs(
        root_path=args.root_path or os.getcwd(),
        target_paths=args.target_path,
        scope_paths=args.scope_paths,
        ignore_paths=args.ignore_paths,
        depth=args.depth,
        no_comment=args.no_comment,
        max_char=args.max_char,
        max_token=args.max_token
    )

    # 不足している引数がある場合は、input()で入力を求める
    if not main_args.target_paths:
        print_colored('\n依存関係を解析するファイルのパスを入力してください。', (" default: None", "grey"))
        input_data = input('target_path: ')
        if input_data:
            main_args.target_paths = input_data.split(' ')

    if not main_args.scope_paths:
        print_colored('\n探索範囲のファイルのパスを入力してください。', (" default: None", "grey"))
        input_data = input('scope_paths: ')
        if input_data:
            main_args.scope_paths = input_data.split(' ')

    if not main_args.ignore_paths:
        print_colored('\n無視するファイルのパスを入力してください。', (" default: None", "grey"))
        input_data = input('ignore_paths: ')
        if input_data:
            main_args.ignore_paths = input_data.split(' ')

    if main_args.target_paths and not main_args.depth:
        print_colored('\n依存関係を解析する深さを入力してください。', (" default: 999", "grey"))
        input_data = input('depth: ')
        if input_data:
            main_args.depth = int(input_data)

    if not main_args.no_comment:
        print_colored('\nコメントを除去しますか？("y" or "n")', (" default: n", "grey"))
        input_data = input('no_comment: ')
        if input_data == 'y':
            main_args.no_comment = True
        else:
            main_args.no_comment = False

    if not main_args.max_token:
        print_colored('\n分割するトークン数を入力してください。', (" default: 25,000", "grey"))
        input_data = input('max_token: ')
        if input_data:
            main_args.max_token = int(input_data)

    if not main_args.max_char:
        print_colored('\n分割する文字数を入力してください。', (" default: 999,999,999, Gemini: 30,000", "grey"))
        input_data = input('max_char: ')
        if input_data:
            main_args.max_char = int(input_data)

    # メイン処理
    chunked_content = main(
        main_args.root_path,
        target_paths=main_args.target_paths,
        scope_paths=main_args.scope_paths,
        ignore_paths=main_args.ignore_paths,
        depth=main_args.depth or default_depth,
        no_comment=main_args.no_comment or False,
        max_char=main_args.max_char or default_max_char,
        max_token=main_args.max_token or default_max_token
    )

    # 取得したコードと文字数やトークン数、chunkの数を表示する
    print_result(chunked_content, max_char=main_args.max_char, max_token=main_args.max_token)

    # chunked_content を順番にクリップボードにコピーする
    copy_to_clipboard(chunked_content)
