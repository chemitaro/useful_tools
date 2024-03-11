from dataclasses import dataclass
from typing import Literal

from apps.lib.utils import count_tokens, print_colored


@dataclass
class CalcSizedContent:
    content: str
    token: int
    char: int


class ContentSizeOptimizer:
    """コンテンツのサイズを最大トークン数と最大文字数を超えないように結合したり分割したりする"""

    max_token: int | None
    max_char: int | None
    with_prompt: bool | None
    output: Literal["code", "path"] | None
    calc_sized_contents: list[CalcSizedContent] = []
    optimized_contents: list[str] = []

    def __init__(
        self,
        contents: list[str],
        max_token: int | None = None,
        max_char: int | None = None,
        with_prompt: bool = False,
        output: Literal["code", "path"] = "path",
    ):
        """コンストラクタ"""
        if max_token is None:
            max_token = 25_000
        if max_char is None:
            max_char = 999_999_999
        if with_prompt is None:
            with_prompt = True
        if output is None:
            output = "path"

        self.max_token = max_token
        self.max_char = max_char
        self.with_prompt = with_prompt
        self.output = output
        # with_promptがTrueの場合はmax_tokenとmax_charを小さくしておく
        if self.with_prompt:
            self.max_token -= 50
            self.max_char -= 150
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
            print_colored(
                (f"コンテンツのサイズが最大文字数および最大トークン数を超えています。: token_size={token_size}, char_size={char_size}", "red")
            )
            # ファイルのパスを表示する
            print_colored((content.split("\n")[1], "gray"))
        calc_sized_content = CalcSizedContent(content=content, token=token_size, char=char_size)
        return calc_sized_content

    # 文字数とトークン数の合計が最大文字数と最大トークン数を超えないようにコンテンツを結合する
    def concat_contents(self) -> list[str]:
        """文字数もしくはトークン数が最大文字数および最大トークン数を超えないようにコンテンツの文字列を結合する"""
        total_token: int = 0
        total_char: int = 0
        buffer_content = ""
        self.optimized_contents = []

        for content in self.calc_sized_contents:
            total_token += content.token
            total_char += content.char
            if self.max_token and self.max_token < total_token or self.max_char and self.max_char < total_char:
                self.optimized_contents.append(buffer_content)
                buffer_content = content.content
                total_token = content.token
                total_char = content.char
            else:
                buffer_content += content.content
        self.optimized_contents.append(buffer_content)

        # プロンプトを追加する
        if self.with_prompt:
            self.add_prompts()

        return self.optimized_contents

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

    def add_prompts(self) -> None:
        """各コンテンツの前後にプロンプトを追加する"""
        segment_count = len(self.optimized_contents)

        for i, content in enumerate(self.optimized_contents):
            segment_number = i + 1  # セグメントの番号

            # セグメントが一つだけの場合
            if segment_count == 1 and self.output == "code":
                prompt_start = "# Prompt: Below is the complete document, consisting of a single segment. Please respond to the questions after reading this document.\n"  # noqa: E501
                prompt_end = "\n# Prompt: Document transmission of the single segment is complete. Please respond to the questions now."  # noqa: E501
                self.optimized_contents[i] = prompt_start + content + prompt_end

            if segment_count == 1 and self.output == "path":
                prompt_start = "# Prompt: Below are the paths to the files related to the question and their dependent files.\n"
                prompt_end = "\n# Prompt: Please answer the questions with an understanding of the above files.\n@Codebase\n"
                self.optimized_contents[i] = prompt_start + content + prompt_end

            # 複数のセグメントがある場合
            else:
                if i == 0:  # 最初のセグメント
                    prompt_start = f"# Prompt: Beginning the document transmission. This is part {segment_number} of {segment_count} total segments. Please respond with 'OK, waiting' and do not take any action until all segments have been sent.\n"  # noqa: E501
                elif i == segment_count - 1:  # 最後のセグメント
                    prompt_start = f"# Prompt: This is the final segment of the document, segment {segment_number} of {segment_count} total segments. After this segment, please respond to the questions.\n"  # noqa: E501
                else:  # 中間のセグメント
                    prompt_start = f"# Prompt: Continuing the document transmission. This is segment {segment_number} of {segment_count} total segments. Please respond with 'OK, waiting' and do not take any action until all segments have been sent.\n"  # noqa: E501
                prompt_end = f"\n# Prompt: End of segment {segment_number} of {segment_count} total segments. Please wait for the next segment to be sent."  # noqa: E501
                self.optimized_contents[i] = prompt_start + content + prompt_end
