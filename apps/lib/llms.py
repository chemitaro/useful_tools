from typing import Any, Literal, TypeVar

import google.generativeai as genai
import instructor
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
        # roleをgeminiのものに変換
        if self.role == "system":
            role = "user"
        elif self.role == "user":
            role = "user"
        elif self.role == "assistant":
            role = "model"
        else:
            raise ValueError(f"Invalid role: {self.role}")

        return {"role": role, "parts": [{"text": self.content}]}

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
        **kwargs: Any,
    ) -> str:
        """テキストを生成する"""
        raise NotImplementedError


class GeminiClient(LlmClientBase):
    """Geminiクライアント"""

    def generate_text(
        self,
        model_name: str,
        messages: LlmMessages | str,
        temp: float | None = None,
        max_tokens: int | None = None,
        stream: bool = False,
        **kwargs: Any,
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


T = TypeVar("T", bound=BaseModel)


def structured_output(
    output_type: type[T], text: str, model_name: str = "models/gemini-1.5-flash-latest", **kwargs: Any
) -> T:
    """指定したPydanticのモデルに構造化する"""
    messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content=f"""
                ユーザーの入力したテキストを指定したJSONに構造化する。

                JSONのスキーマは以下の通り。
                {output_type.model_json_schema()}

                出力はJSONで返すこと。
                """,
            ),
            LlmMessage(
                role="user",
                content=f"""
                {text}
                """,
            ),
        ]
    )

    model = GenerativeModel(
        model_name=model_name,
        generation_config={"temperature": 0.0},
    )
    client = instructor.from_gemini(
        client=model,
        mode=instructor.Mode.GEMINI_JSON,
    )

    resp_data = client.messages.create(
        messages=messages.format_gemini(),
        response_model=output_type,
    )

    if not isinstance(resp_data, output_type):
        raise ValueError(f"Invalid response: {resp_data}")

    return resp_data
