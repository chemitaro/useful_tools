import os

import tiktoken


def count_tokens(text: str, model: str = 'gpt-4') -> int:
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
    # 相対パスの先頭にスラッシュがある場合は除去しておく
    relative_path = relative_path.lstrip('/')
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
    return os.path.relpath(absolute_path, root_path)


def read_file_content(file_path: str) -> str:
    """指定したファイルの内容を読み込み、文字列として返す"""
    with open(file_path, 'r') as f:
        content = f.read()
    return content


def format_number(number: int) -> str:
    """数値を3桁ごとにカンマ区切りにして文字列に変換する"""
    return "{:,}".format(number)
