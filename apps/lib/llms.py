from typing import Any, Literal, override

import google.generativeai as genai
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.types.content_types import ContentDict
from google.generativeai.types.generation_types import (
    GenerateContentResponse,
    GenerationConfig,
)
from pydantic import BaseModel, Field
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown


def streaming_print_gemini(response: GenerateContentResponse) -> None:
    # Rich consoleを初期化
    console = Console()
    # マークダウンテキストを格納する変数
    markdown_text = ""

    # Liveコンテキストを使用してストリーミング出力を表示
    with Live(console=console, refresh_per_second=4) as live:
        for chunk in response:
            if chunk.text:
                markdown_text += chunk.text
                # 現在のマークダウンテキストをレンダリング
                live.update(Markdown(markdown_text))

    print()


class LlmMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

    def format_gemini(self) -> ContentDict:
        return {"role": self.role, "parts": [{"text": self.content}]}

    def format_openai(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}

    def format_instructor(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


class LlmMessages(BaseModel):
    messages: list[LlmMessage] = Field(default=[])

    def format_gemini(self) -> list[ContentDict]:
        return [message.format_gemini() for message in self.messages]

    def format_openai(self) -> list[dict[str, str]]:
        return [message.format_openai() for message in self.messages]

    def format_instructor(self) -> list[dict[str, str]]:
        return [message.format_instructor() for message in self.messages]


class LlmClientBase(BaseModel):
    """LLMクライアントの基底クラス"""

    api_key: str | None = Field(default=None)

    def generate_text(
        self,
        model_name: str,
        messages: LlmMessages | str,
        temp: float | None = None,
        max_tokens: int | None = None,
        stream: bool = False,
        **kwargs: Any
    ) -> str:
        """テキストを生成する"""
        raise NotImplementedError


class GeminiClient(LlmClientBase):
    """Geminiクライアント"""

    @override
    def generate_text(
        self,
        model_name: str,
        messages: LlmMessages | str,
        temp: float | None = None,
        max_tokens: int | None = None,
        stream: bool = False,
        **kwargs: Any
    ) -> str:
        # APIキーの設定
        if self.api_key is not None:
            genai.configure(api_key=self.api_key)

        # モデルの準備
        llm = GenerativeModel(model_name)

        # 設定の準備
        generation_config = GenerationConfig(
            temperature=temp,
            max_output_tokens=max_tokens,
        )

        # メッセージのフォーマット
        if isinstance(messages, str):
            messages = LlmMessages(messages=[LlmMessage(role="user", content=messages)])
        gemini_messages = messages.format_gemini()

        # レスポンスの生成
        response = llm.generate_content(gemini_messages, generation_config=generation_config, stream=stream)

        if stream is True:
            streaming_print_gemini(response)

        return response.text
