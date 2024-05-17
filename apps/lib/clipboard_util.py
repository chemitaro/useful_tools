import pyperclip

from apps.lib.utils import count_tokens, format_number, print_colored


def copy_to_clipboard(contents: list[str] | str) -> None:
    """
    chunked_content を順番にクリップボードにコピーする

    Args:
        chunked_content (list[str]): コピーする内容のリスト

    Returns:
        None
    """
    if isinstance(contents, str):
        contents = [contents]

    print_colored(("\n== Copy to clipboard ==", "green"))

    for content in contents:
        pyperclip.copy(content)
        # chunkのナンバーを表示する
        print_colored(f"\nChunk {contents.index(content) + 1} of {len(contents)} copied to clipboard.")
        # 文字数とトークン数を表示する
        total_char = len(content)
        total_tokens = count_tokens(content)
        print_colored(f"  ({format_number(total_char)} char, {format_number(total_tokens)} tokens)")
        # chunkが最後のchunkでない場合、Enterキーを押すまで待機する
        if contents.index(content) + 1 < len(contents):
            input("\nPress Enter to continue...")


def print_and_copy(text) -> None:
    """ターミナルに表示し、クリップボードにコピーする関数."""
    print("\n")
    print(text)
    print_colored(("Copy to clipboard.", "grey"))
    pyperclip.copy(text)
