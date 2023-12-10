from apps.lib.utils import count_tokens, format_number
import pyperclip  # type: ignore


def print_result(contents: list[str], max_char: int, max_token: int) -> None:
    """
    取得したコードと文字数やトークン数、chunkの数を表示する

    Args:
        chunked_content (List[str]): 取得したコードのリスト
        max_char (int, optional): ファイルの内容を取得する際のチャンクサイズ. Defaults to sys.maxsize.
        max_token (int, optional): ファイルの内容を取得する際のチャンクサイズ. Defaults to sys.maxsize.

    Returns:
        None
    """
    joined_content: str = ''.join(contents)
    lines = joined_content.split('\n')
    total_char = len(joined_content)
    total_lines = len(lines)
    total_token = count_tokens(joined_content)
    print('\n== Result ==\n')
    print(f'total characters: {format_number(total_char)}')
    print(f'total lines:      {format_number(total_lines)}')
    print(f'total tokens:     {format_number(total_token)} (encoded for gpt-4)')
    if len(contents) > 1:
        print(f'total chunks:     {format_number(len(contents))}')
        if max_char < total_char:
            print(f'  ({format_number(max_char)} characters per chunk.)')
        if max_token < total_token:
            print(f'  ({format_number(max_token)} tokens per chunk.)')


# chunked_content を順番にクリップボードにコピーする
def copy_to_clipboard(contents: list[str]):
    """
    chunked_content を順番にクリップボードにコピーする

    Args:
        chunked_content (list[str]): コピーする内容のリスト

    Returns:
        None
    """
    print('\n== Copy to clipboard ==')
    for content in contents:
        pyperclip.copy(content)
        # chunkのナンバーを表示する
        print(f'\nChunk {contents.index(content) + 1} of {len(contents)} copied to clipboard.')
        # 文字数とトークン数を表示する
        total_char = len(content)
        total_tokens = count_tokens(content)
        print(f'  ({format_number(total_char)} char, {format_number(total_tokens)} tokens)')
        # chunkが最後のchunkでない場合、Enterキーを押すまで待機する
        if contents.index(content) + 1 < len(contents):
            input('\nPress Enter to continue...')
