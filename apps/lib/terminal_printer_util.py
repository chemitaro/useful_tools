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
    joined_content: str = "".join(contents)
    lines = joined_content.split("\n")
    total_char = len(joined_content)
    total_lines = len(lines)
    total_token = count_tokens(joined_content)
    print_colored(("\n== Result ==\n", "green"))
    print_colored(f"total characters: {format_number(total_char)}")
    print_colored(f"total lines:      {format_number(total_lines)}")
    print_colored(f"total tokens:     {format_number(total_token)} (encoded for gpt-4)")
    if len(contents) > 1:
        print_colored(f"total chunks:     {format_number(len(contents))}")
        if max_char and max_char < total_char:
            print_colored(f"  ({format_number(max_char)} characters per chunk.)")
        if max_token and max_token < total_token:
            print_colored(f"  ({format_number(max_token)} tokens per chunk.)")
