from dataclasses import dataclass

from apps.lib.utils import count_tokens, print_colored


@dataclass
class CalcSizedContent:
    content: str
    token: int
    char: int


class ContentSizeOptimizer:
    max_token: int | None
    max_char: int | None
    calc_sized_contents: list[CalcSizedContent] = []

    def __init__(
        self,
        contents: list[str],
        max_token: int | None = None,
        max_char: int | None = None
    ):
        if max_token is None:
            max_token = 25_000
        if max_char is None:
            max_char = 999_999_999

        self.max_token = max_token
        self.max_char = max_char
        self.calc_size_contents(contents)

    def optimize_contents(self) -> list[str]:
        """コンテンツのサイズを最大トークン数と最大文字数を超えないように結合したり分割したりする"""
        # 文字数とトークン数の合計が最大文字数と最大トークン数を超えないようにコンテンツを結合する
        concat_contents = self.concat_contents()

        return concat_contents

    def calc_size_contents(self, contents) -> None:
        self.calc_sized_contents = []
        for content in contents:
            calc_sized_content: CalcSizedContent = self.calc_size_content(content)
            self.calc_sized_contents.append(calc_sized_content)

    # 文字数とトークン数を計算して辞書型にして返す
    def calc_size_content(self, content: str) -> CalcSizedContent:
        token_size = count_tokens(content)
        char_size = len(content)
        if self.max_token and self.max_token < token_size or self.max_char and self.max_char < char_size:
            # 未実装: 文字数もしくはトークン数が最大文字数もしくは最大トークン数を超えているコンテンツを抽出して分割する。
            print_colored((f'コンテンツのサイズが最大文字数および最大トークン数を超えています。: token_size={token_size}, char_size={char_size}', "red"))
        calc_sized_content = CalcSizedContent(
            content=content,
            token=token_size,
            char=char_size
        )
        return calc_sized_content

    # 文字数とトークン数の合計が最大文字数と最大トークン数を超えないようにコンテンツを結合する
    def concat_contents(self) -> list[str]:
        """文字数もしくはトークン数が最大文字数および最大トークン数を超えないようにコンテンツの文字列を結合する"""
        total_token: int = 0
        total_char: int = 0
        buffer_content = ""
        connected_contents = []

        for content in self.calc_sized_contents:
            total_token += content.token
            total_char += content.char
            if self.max_token and self.max_token < total_token or self.max_char and self.max_char < total_char:
                connected_contents.append(buffer_content)
                buffer_content = content.content
                total_token = content.token
                total_char = content.char
            else:
                buffer_content += content.content
        connected_contents.append(buffer_content)
        return connected_contents

    def calc_total_token(self) -> int:
        """合計トークン数を計算する"""
        total_token = 0
        for content in self.calc_sized_contents:
            total_token += content.token
        return total_token

    def calc_total_char(self) -> int:
        """合計文字数を計算する"""
        total_char = 0
        for content in self.calc_sized_contents:
            total_char += content.char
        return total_char
