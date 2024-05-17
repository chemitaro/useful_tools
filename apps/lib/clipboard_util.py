import platform

import pyperclip

from apps.lib.utils import count_tokens, format_number, print_colored


def set_clipboard():
    """
    実行環境に応じて適切なクリップボード設定を適用する
    """
    system = platform.system()
    if system == "Linux":
        pyperclip.set_clipboard("xclip")
    elif system == "Darwin":
        pyperclip.set_clipboard("pbcopy")
    elif system == "Windows":
        pyperclip.set_clipboard("clip")
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


# クリップボード設定を適用
set_clipboard()


# 文字列をクリップボードにコピーする
def copy_to_clipboard(content: str) -> None:
    """
    content をクリップボードにコピーする

    Args:
        content (str): コピーする内容

    Returns:
        None
    """
    pyperclip.copy(content)


def copy_chunks_to_clipboard(chunk_contents: list[str] | str) -> None:
    """
    chunked_content を順番にクリップボードにコピーする

    Args:
        chunked_content (list[str]): コピーする内容のリスト

    Returns:
        None
    """
    if isinstance(chunk_contents, str):
        chunk_contents = [chunk_contents]

    print_colored(("\n== Copy to clipboard ==", "green"))

    for content in chunk_contents:
        copy_to_clipboard(content)
        # chunkのナンバーを表示する
        print_colored(f"\nChunk {chunk_contents.index(content) + 1} of {len(chunk_contents)} copied to clipboard.")
        # 文字数とトークン数を表示する
        total_char = len(content)
        total_tokens = count_tokens(content)
        print_colored(f"  ({format_number(total_char)} char, {format_number(total_tokens)} tokens)")
        # chunkが最後のchunkでない場合、Enterキーを押すまで待機する
        if chunk_contents.index(content) + 1 < len(chunk_contents):
            input("\nPress Enter to continue...")


def print_and_copy(text) -> None:
    """ターミナルに表示し、クリップボードにコピーする関数."""
    print("\n")
    print(text)
    print_colored(("Copy to clipboard.", "grey"))
    copy_to_clipboard(text)
