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


from apps.lib.content_size_optimizer import ContentSizeOptimizer  # noqa: E402
from apps.lib.dependency_analyzer.main import DependencyAnalyzer  # noqa: E402
from apps.lib.file_content_collector import FileContentCollector  # noqa: E402
from apps.lib.outputs import copy_to_clipboard, print_result  # noqa: E402


def main(
    root_path: str,
    target_paths: list[str] | None = None,
    depth: int = 999,
    no_comment: bool = False,
    max_char: int = 999_999_999,
    max_token: int = 120_000,
    scope_paths: list[str] | None = None,
    ignore_paths: list[str] | None = None
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

    # 引数の検証
    if type(root_path) is not str:
        raise TypeError('root_path must be str')
    if type(target_paths) is not list:
        raise TypeError('module_paths must be list')
    if type(depth) is not int:
        raise TypeError('depth must be int')
    # depthは0以上の整数でなければならない
    if depth < 0:
        raise ValueError('depth must be positive')
    if type(no_comment) is not bool:
        raise TypeError('no_comment must be bool')
    if type(max_char) is not int:
        raise TypeError('max_chara must be int')
    if max_char < 1:
        raise ValueError('max_chara must be positive')
    if type(max_token) is not int:
        raise TypeError('max_token must be int')
    if max_token < 1:
        raise ValueError('max_token must be positive')
    if type(scope_paths) is not list:
        raise TypeError('scopes must be list')
    if type(ignore_paths) is not list:
        raise TypeError('ignores must be list')

    # ファイルの依存関係を解析
    dependency_analyzer = DependencyAnalyzer.factory(
        root_path=root_path,
        start_relative_paths=target_paths,
        scope_relative_paths=scope_paths,
        ignore_relative_paths=ignore_paths,
        depth=depth
    )
    dependency_file_paths: list[str] = dependency_analyzer.analyze()

    # ファイルの内容を取得
    file_content_collector = FileContentCollector(
        dependency_file_paths,
        root_path,
        no_docstring=no_comment
    )
    contents = file_content_collector.collect()

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
        default=[],
        help='Path of the Python file from which to parse dependencies, multiple paths can be specified'
    )
    parser.add_argument(
        '-d',
        '--depth',
        type=int,
        default=999,
        help='Specify depth of dependency analysis'
    )
    parser.add_argument(
        '-nc',
        '--no-comment',
        action='store_true',
        help='Omit document comments'
    )
    parser.add_argument(
        '-mc',
        '--max_char',
        type=int,
        default=999_999_999,
        help='Split by a specified number of characters when copying to the clipboard'
    )
    parser.add_argument(
        '-mt',
        '--max_token',
        type=int,
        default=120_000,
        help='Split by a specified number of tokens when copying to the clipboard'
    )
    parser.add_argument(
        '-s',
        '--scope',
        nargs='*',
        default=[],
        help='Specify paths of files to scope, multiple files can be specified'
    )
    parser.add_argument(
        '-i',
        '--ignore',
        nargs='*',
        default=[],
        help='Specify paths of files to ignore, multiple files can be specified'
    )
    args = parser.parse_args()

    root_dir = os.getcwd()

    # メイン処理
    chunked_content = main(
        root_dir,
        target_paths=args.target_path,
        depth=args.depth,
        no_comment=args.no_comment,
        max_char=args.max_char,
        max_token=args.max_token,
        scope_paths=args.scope,
        ignore_paths=args.ignore
    )

    # 取得したコードと文字数やトークン数、chunkの数を表示する
    print_result(chunked_content, max_char=args.max_char, max_token=args.max_token)

    # chunked_content を順番にクリップボードにコピーする
    copy_to_clipboard(chunked_content)
