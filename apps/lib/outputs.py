import os

import pyperclip  # type: ignore

from apps.lib.utils import count_tokens, format_number, print_colored


def print_result(contents: list[str], max_char: int | None, max_token: int | None) -> None:
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
    print_colored(('\n== Result ==\n', "green"))
    print_colored(f'total characters: {format_number(total_char)}')
    print_colored(f'total lines:      {format_number(total_lines)}')
    print_colored(f'total tokens:     {format_number(total_token)} (encoded for gpt-4)')
    if len(contents) > 1:
        print_colored(f'total chunks:     {format_number(len(contents))}')
        if max_char and max_char < total_char:
            print_colored(f'  ({format_number(max_char)} characters per chunk.)')
        if max_token and max_token < total_token:
            print_colored(f'  ({format_number(max_token)} tokens per chunk.)')


def copy_to_clipboard(contents: list[str]):
    """
    chunked_content を順番にクリップボードにコピーする

    Args:
        chunked_content (list[str]): コピーする内容のリスト

    Returns:
        None
    """
    print_colored(('\n== Copy to clipboard ==', "green"))
    for content in contents:
        pyperclip.copy(content)
        # chunkのナンバーを表示する
        print_colored(f'\nChunk {contents.index(content) + 1} of {len(contents)} copied to clipboard.')
        # 文字数とトークン数を表示する
        total_char = len(content)
        total_tokens = count_tokens(content)
        print_colored(f'  ({format_number(total_char)} char, {format_number(total_tokens)} tokens)')
        # chunkが最後のchunkでない場合、Enterキーを押すまで待機する
        if contents.index(content) + 1 < len(contents):
            input('\nPress Enter to continue...')


# ファイルに書き出す
class FileWriter:
    """ファイルに書き出す"""

    file_path: str
    file_dir: str

    def __init__(
        self,
        file_name: str,
        file_dir: str = '~/Desktop',
        extension: str = 'txt'
    ):
        """ファイル名とファイルのディレクトリを指定する"""
        self.file_path = f'{file_dir}/{file_name}.{extension}'
        self.file_dir = file_dir

    def write(self, contents: list[str]) -> None:
        """ファイルに書き出す"""
        print_colored(('\n== Write to file ==\n', "green"))
        self.create_dir()
        text = '\n'.join(contents)
        with open(self.file_path, 'w') as f:
            f.write(text)
        print_colored(('Saved to File: ', 'green'), self.file_path)

    # ディレクトリが存在しない場合は作成する
    def create_dir(self) -> None:
        """ディレクトリが存在しない場合は作成する"""
        if not os.path.exists(self.file_dir):
            print_colored(('Creating directory: ', 'green'), self.file_dir)
            os.makedirs(self.file_dir)
