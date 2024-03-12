#!/usr/bin/env python3

import argparse
import os
import sys
from dataclasses import dataclass
from typing import Literal, TypedDict, cast

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
from apps.lib.file_path_formatter import FilePathFormatter  # noqa: E402
from apps.lib.outputs import copy_to_clipboard, print_result  # noqa: E402
from apps.lib.path_tree import PathTree  # noqa: E402
from apps.lib.utils import format_number, print_colored  # noqa: E402

default_depth = 999
default_max_char = 999_999_999
default_max_token = 125_000
default_output = cast(Literal["code", "path"], "path")


class ModeConfig(TypedDict):
    output: Literal["code", "path"]
    no_comment: bool
    with_prompt: bool
    max_char: int
    max_token: int


default_configs: dict[Literal["cursor", "chatgpt", "claude"], ModeConfig] = {
    "cursor": {
        "output": cast(Literal["code", "path"], "path"),
        "no_comment": False,
        "with_prompt": True,
        "max_char": 999_999_999,
        "max_token": 125_000,
    },
    "chatgpt": {
        "output": cast(Literal["code", "path"], "code"),
        "no_comment": False,
        "with_prompt": True,
        "max_char": 999_999_999,
        "max_token": 125_000,
    },
    "claude": {
        "output": cast(Literal["code", "path"], "code"),
        "no_comment": False,
        "with_prompt": False,
        "max_char": 999_999_999,
        "max_token": 200_000,
    },
}

default_config: ModeConfig = default_configs["cursor"]


@dataclass
class MainArgs:
    root_path: str
    target_paths: list[str] | None
    scope_paths: list[str] | None
    ignore_paths: list[str] | None
    depth: int | None
    output: Literal["code", "path"] | None
    no_comment: bool | None
    with_prompt: bool | None
    max_char: int | None
    max_token: int | None
    mode: Literal["cursor", "chatgpt", "claude", None] | None


def import_collect(
    root_path: str,
    target_paths: list[str] | None = None,
    scope_paths: list[str] | None = None,
    ignore_paths: list[str] | None = None,
    depth: int = default_depth,
    output: Literal["code", "path"] = default_output,
    no_comment: bool = False,
    with_prompt: bool = False,
    max_char: int = default_max_char,
    max_token: int = default_max_token,
) -> list[str]:
    if target_paths is None:
        target_paths = []
    if scope_paths is None:
        scope_paths = []
    if ignore_paths is None:
        ignore_paths = []

    # ファイルの依存関係を解析
    dependency_analyzer = DependencyAnalyzer.factory(
        root_path=root_path, start_relative_paths=target_paths, scope_relative_paths=scope_paths, ignore_relative_paths=ignore_paths, depth=depth
    )
    dependency_file_paths: list[str] = dependency_analyzer.analyze()

    # 取得したファイルのパスをツリー構造で表示
    path_tree = PathTree(dependency_file_paths, root_path=root_path)
    path_tree.print_tree_map()

    # 出力形式が"code"の場合の処理
    if output == "code":
        # ファイルの内容を取得
        file_content_collector = FileContentCollector(dependency_file_paths, root_path, no_docstring=no_comment)
        contents = file_content_collector.collect()
    elif output == "path":
        # 出力形式が"path"の場合の処理
        file_path_formatter = FilePathFormatter(dependency_file_paths, root_path)
        contents = file_path_formatter.format()
    else:
        raise ValueError("output must be 'code' or 'path'")

    # ディレクトリ構成図をコンテンツの先頭に追加する
    path_tree_content = path_tree.get_tree_map()
    contents.insert(0, path_tree_content)

    # 取得したコンテンツをトークン数で調整する
    optimizer = ContentSizeOptimizer(contents, max_char=max_char, max_token=max_token, with_prompt=with_prompt, output=output)
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
    parser.add_argument("target_path", nargs="*", help="Path of the Python file from which to parse dependencies, multiple paths can be specified")
    parser.add_argument("-r", "--root_path", type=str, help="Specify the root path of the project")
    parser.add_argument("-s", "--scope_paths", nargs="*", help="Specify paths of files to scope, multiple files can be specified")
    parser.add_argument("-i", "--ignore_paths", nargs="*", help="Specify paths of files to ignore, multiple files can be specified")
    parser.add_argument("-d", "--depth", type=int, help="Specify depth of dependency analysis")
    parser.add_argument("-o", "--output", type=str, choices=["code", "path"], help="Specify the output format")
    parser.add_argument("-nc", "--no_comment", action="store_true", help="Omit document comments")
    parser.add_argument("-p", "--with_prompt", action="store_true", help="Whether to display the prompt")
    parser.add_argument("-mt", "--max_token", type=int, help="Split by a specified number of tokens when copying to the clipboard")
    parser.add_argument("-mc", "--max_char", type=int, help="Split by a specified number of characters when copying to the clipboard")
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        choices=["cursor", "chatgpt", "claude"],
        default=None,
        help="Select the mode of operation: 'cursor', 'chatgpt', or 'claude'. Leave empty for no specific mode.",
    )
    args = parser.parse_args()

    # コマンドライン引数をMainArgsに変換
    main_args: MainArgs = MainArgs(
        root_path=args.root_path or os.getcwd(),
        target_paths=args.target_path,
        scope_paths=args.scope_paths,
        ignore_paths=args.ignore_paths,
        depth=args.depth,
        output=args.output,
        no_comment=args.no_comment,
        with_prompt=args.with_prompt,
        max_char=args.max_char,
        max_token=args.max_token,
        mode=args.mode,
    )

    if main_args.mode is None:
        print_colored("\nモードを入力してください。('cursor', 'chatgpt', 'claude' のいずれか、または空白でNone)", (" default: None", "grey"))
        input_data = input("mode: ") or None
        main_args.mode = input_data

    # モードに応じたデフォルト値の設定
    if main_args.mode and main_args.mode in default_configs:
        mode_config = default_configs[main_args.mode]
        main_args.output = main_args.output or mode_config["output"]
        main_args.no_comment = main_args.no_comment if main_args.no_comment is not None else mode_config["no_comment"]
        main_args.with_prompt = main_args.with_prompt if main_args.with_prompt is not None else mode_config["with_prompt"]
        main_args.max_char = main_args.max_char or mode_config["max_char"]
        main_args.max_token = main_args.max_token or mode_config["max_token"]

    # 不足している引数がある場合は、input()で入力を求める
    if not main_args.target_paths:
        print_colored("\n依存関係を解析するファイルのパスを入力してください。", (" default: None", "grey"))
        input_data = input("target_path: ")
        if input_data:
            main_args.target_paths = input_data.split(" ")

    if not main_args.scope_paths:
        print_colored("\n探索範囲のファイルのパスを入力してください。", (" default: None", "grey"))
        input_data = input("scope_paths: ")
        if input_data:
            main_args.scope_paths = input_data.split(" ")

    if not main_args.ignore_paths:
        print_colored("\n無視するファイルのパスを入力してください。", (" default: None", "grey"))
        input_data = input("ignore_paths: ")
        if input_data:
            main_args.ignore_paths = input_data.split(" ")

    if isinstance(main_args.target_paths, list) and len(main_args.target_paths) > 0 and main_args.depth is None:
        print_colored("\n依存関係を解析する深さを入力してください。", (f" default: {default_depth}", "grey"))
        input_data = input("depth: ") or str(default_depth)
        if input_data:
            main_args.depth = int(input_data)

    # 出力形式を指定する
    if main_args.output is None:
        print_colored('\n出力形式を指定してください("code" or "path")', (" default: path", "grey"))
        input_data = input("output: ") or default_output
        if input_data == "path":
            main_args.output = "path"
            main_args.no_comment = True
            main_args.max_char = default_max_char
            main_args.max_token = default_max_token
        elif input_data == "code":
            main_args.output = "code"
        else:
            raise ValueError("output must be 'code' or 'path'")

    if main_args.no_comment is None:
        print_colored('\nコメントを除去しますか？("y" or "n")', (" default: n", "grey"))
        input_data = input("no_comment: ") or "n"
        if input_data == "y" or input_data == "yes" or input_data == "Y":
            main_args.no_comment = True
        elif input_data == "n" or input_data == "no" or input_data == "N":
            main_args.no_comment = False
        else:
            raise ValueError("no_comment must be 'y' or 'n'")

    if main_args.with_prompt is None:
        print_colored('\nプロンプトを追加しますか？("y" or "n")', (" default: y", "grey"))
        input_data = input("with_prompt: ") or "y"
        if input_data == "n" or input_data == "no" or input_data == "N":
            main_args.with_prompt = False
        else:
            main_args.with_prompt = True

    if main_args.max_token is None:
        print_colored("\n分割するトークン数を入力してください。", (f" default: {format_number(default_max_token)}", "grey"))
        input_data = input("max_token: ") or default_max_token
        if input_data:
            main_args.max_token = int(input_data)

    if main_args.max_char is None:
        print_colored("\n分割する文字数を入力してください。", (" default: 999,999,999, Gemini: 30,000", "grey"))
        input_data = input("max_char: ") or default_max_char
        if input_data:
            main_args.max_char = int(input_data)

    print("print_depth", main_args.depth)

    # メイン処理
    chunked_content = import_collect(
        main_args.root_path,
        target_paths=main_args.target_paths,
        scope_paths=main_args.scope_paths,
        ignore_paths=main_args.ignore_paths,
        depth=main_args.depth if main_args.depth is not None else default_depth,
        output=main_args.output or "code",
        no_comment=main_args.no_comment,
        with_prompt=main_args.with_prompt,
        max_char=main_args.max_char or default_max_char,
        max_token=main_args.max_token or default_max_token,
    )

    # 取得したコードと文字数やトークン数、chunkの数を表示する
    print_result(chunked_content, max_char=main_args.max_char, max_token=main_args.max_token)

    # chunked_content を順番にクリップボードにコピーする
    copy_to_clipboard(chunked_content)
