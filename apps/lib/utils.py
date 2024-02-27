import os
from typing import Literal, Tuple

import tiktoken


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


def read_file_content(file_path: str) -> str:
    """指定したファイルの内容を読み込み、文字列として返す"""
    with open(file_path, "r") as f:
        content = f.read()
    return content


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


def print_colored(*args: object | Tuple[str, Literal["black", "grey", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]]) -> None:
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
