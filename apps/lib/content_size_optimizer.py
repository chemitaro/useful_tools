from dataclasses import dataclass
from apps.lib.utils import count_tokens


@dataclass
class CalcSizedContent:
    content: str
    token: int
    char: int


class ContentSizeOptimizer:
    max_token: int
    max_char: int

    def __init__(
        self,
        max_token: int = 120_000,
        max_char: int = 9_999_999
    ):
        self.max_token = max_token
        self.max_char = max_char

    def optimize(self, contents: list[str]) -> list[str]:
        """コンテンツのサイズを最大トークン数と最大文字数を超えないように結合したり分割したりする"""
        # 文字数とトークン数を計算して辞書型まとめてリストに格納する
        calc_sized_contents: list[CalcSizedContent] = [self.calc_size(content) for content in contents]

        # 文字数とトークン数の合計が最大文字数と最大トークン数を超えないようにコンテンツを結合する
        concat_contents = self.concat_contents(calc_sized_contents)

        return concat_contents

    # 文字数とトークン数を計算して辞書型にして返す
    def calc_size(self, content: str) -> CalcSizedContent:
        token_size = count_tokens(content)
        char_size = len(content)
        if self.max_token < token_size or self.max_char < char_size:
            # 未実装: 文字数もしくはトークン数が最大文字数もしくは最大トークン数を超えているコンテンツを抽出して分割する。
            raise ValueError(f'コンテンツのサイズが最大文字数および最大トークン数を超えています。: token_size={token_size}, char_size={char_size}')
        calc_sized_content = CalcSizedContent(
            content=content,
            token=token_size,
            char=char_size
        )
        return calc_sized_content

    # 文字数とトークン数の合計が最大文字数と最大トークン数を超えないようにコンテンツを結合する
    def concat_contents(self, contents: list[CalcSizedContent]) -> list[str]:
        """文字数もしくはトークン数が最大文字数および最大トークン数を超えないようにコンテンツの文字列を結合する"""
        total_token: int = 0
        total_char: int = 0
        buffer_content = ""
        connected_contents = []

        for content in contents:
            total_token += content.token
            total_char += content.char
            if self.max_token < total_token or self.max_char < total_char:
                connected_contents.append(buffer_content)
                buffer_content = ""
                total_token = content.token
                total_char = content.char
            else:
                buffer_content += content.content
        connected_contents.append(buffer_content)
        return connected_contents
