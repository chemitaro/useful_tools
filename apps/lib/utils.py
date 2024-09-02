import os
from typing import Literal, Tuple, TypeAlias

import pyperclip
import tiktoken
from rich.console import Console
from rich.markdown import Markdown
import subprocess

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    受け取ったテキストのトークン数を返す

    Args:
        text (str): 受け取ったテキスト
        model (str, optional): トークナイザーのモデル名. Defaults to 'gpt-4'.

    Returns:
        int: 受け取ったテキストのトークン数
    """
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def make_absolute_path(root_path: str, relative_path: str) -> str:
    """ルートパスと相対パスを組み合わせて絶対パスを生成する

    Args:
        root_path (str): ルートパス
        relative_path (str): 相対パス

    Returns:
        str: 絶対パス
    """
    # relative_pathが絶対パスである場合はそのまま返す
    if os.path.isabs(relative_path):
        return relative_path

    # 相対パスの先頭にスラッシュがある場合は除去しておく
    relative_path = relative_path.lstrip("/")
    absolute_path = os.path.join(root_path, relative_path)
    return absolute_path


def make_relative_path(root_path: str, absolute_path: str) -> str:
    """ルートパスと絶対パスを組み合わせて相対パスを生成する

    Args:
        root_path (str): ルートパス
        absolute_path (str): 絶対パス

    Returns:
        str: 相対パス
    """
    # absolute_pathが相対パスである場合はそのまま返す
    if not os.path.isabs(absolute_path):
        return absolute_path

    return os.path.relpath(absolute_path, root_path)


def path_to_module(path: str) -> str:
    """パスをモジュール名に変換する"""
    # パスの正規化
    path = os.path.normpath(path)

    # ファイルの拡張子を除去
    if os.path.isfile(path):
        path, _ = os.path.splitext(path)

    # パスセパレータをドットに置換
    module_name = path.replace(os.sep, ".")

    # 先頭のドットを除去
    if module_name.startswith("."):
        module_name = module_name[1:]

    return module_name


def module_to_absolute_path(module: str) -> str:
    """モジュール名を絶対パスに変換する"""
    # ドットをパスセパレータに置換
    path = module.replace(".", os.sep)

    # 頭に/がない場合には追加
    if not path.startswith(os.sep):
        path = os.sep + path

    # ファイルかディレクトリかを判定し、ファイルの場合は .py を追加
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path + ".py"):
        return path + ".py"
    else:
        return module


def read_file_content(file_path: str) -> str:
    """指定したファイルの内容を読み込み、文字列として返す"""
    with open(file_path, "r") as f:
        content = f.read()
    return content


def write_file_content(file_path: str, content: str) -> None:
    """指定したファイルの内容を書き込む"""
    with open(file_path, "w") as f:
        f.write(content)


def format_number(number: int) -> str:
    """数値を3桁ごとにカンマ区切りにして文字列に変換する"""
    return "{:,}".format(number)


def format_content(name: str, content: str, style: Literal["doc", "code"] = "doc") -> str:
    """受け取ったコンテントをパス名```コンテントの内容```の形式に整形します。"""
    boundary: str
    if style == "doc":
        boundary = '"""'
    elif style == "code":
        boundary = "```"
    else:
        boundary = '"""'

    formatted_content = f"\n### {name}\n{boundary}\n{content}\n{boundary}\n"
    return formatted_content


# 色リストを型として定義
Colors: TypeAlias = Literal["black", "grey", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]


def print_colored(*args: object | Tuple[str, Colors]) -> None:
    """指定されたテキストと色の組み合わせを連結して表示する関数.

    Args:
        *args
            object: 表示するテキスト
            Tuple[str, Literal["black", "grey", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]]: 表示するテキストと色の組み合わせ

    Returns:
        None
    """
    colors = {
        "black": "\033[30m",
        "grey": "\033[90m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
    }

    colored_text = ""
    for arg in args:
        if isinstance(arg, tuple) and len(arg) == 2:
            text, color = arg
            color_code = colors.get(color, "")
            colored_text += f"{color_code}{text}\033[0m"
        elif isinstance(arg, str):
            text = arg
            colored_text += text
        else:
            text = str(arg)
            colored_text += text

    print(colored_text)


def print_markdown(text: str) -> None:
    """受け取ったテキストをMarkdown形式で表示する"""

    md = Markdown(text)
    console = Console()
    console.print(md)
    print()


def truncate_string(text: str, length: int) -> str:
    """指定した長さに文字列を短縮する。必要に応じて末尾にドットを3つ付ける。

    Args:
        text (str): 短縮する文字列。
        length (int): 文字列を短縮する長さ。

    Returns:
        str: 短縮された文字列。
    """
    if len(text) > length:
        return text[:length] + "..."
    else:
        return text


def get_clipboard_content() -> str:
    try:
        content = pyperclip.paste()
        return content
    except pyperclip.PyperclipException as e:
        print(f"クリップボードにアクセスできません: {str(e)}")
        return ""


def execute_command(command: str) -> Tuple[int, str]:
    """
    引数で受け取ったコマンドをコマンドラインから実行し、その結果の出力を文字列として返す

    Args:
        command (str): 実行するコマンド

    Returns:
        str: コマンドの実行結果
    """
    try:
        result = subprocess.run(command, shell=True, check=False, capture_output=True, text=True)
        return result.returncode, result.stdout + result.stderr
    except Exception as e:
        return -1, f"エラー: コマンドの実行に失敗しました。\n{str(e)}"


