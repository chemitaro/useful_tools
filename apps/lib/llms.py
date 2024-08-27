from typing import Any, Literal, TypeVar

import google.generativeai as genai
import instructor
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.types.content_types import ContentDict
from google.generativeai.types.generation_types import (
    GenerateContentResponse,
    GenerationConfig,
)
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessageParam
from pydantic import BaseModel, Field
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown


def streaming_print_gemini(response: GenerateContentResponse) -> str:
    # Rich consoleを初期化
    console = Console()
    # マークダウンテキストを格納する変数
    full_text = ""

    # Liveコンテキストを使用してストリーミング出力を表示
    with Live(console=console, refresh_per_second=1) as live:
        for chunk in response:
            if chunk.text:
                full_text += chunk.text
                # 現在のマークダウンテキストをレンダリング
                live.update(Markdown(full_text))

    console.print()
    return full_text


def streaming_print_openai(response: Stream[ChatCompletionChunk]) -> str:
    full_text = ""
    console = Console()

    with Live(console=console, refresh_per_second=1) as live:
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_text += content
                live.update(Markdown(full_text))

    console.print()
    return full_text


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

    def format_openai(self) -> ChatCompletionMessageParam:
        return {"role": self.role, "content": self.content}  # type: ignore

    def format_instructor(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


class LlmMessages(BaseModel):
    messages: list[LlmMessage] = Field(default=[])

    def format_gemini(self) -> list[ContentDict]:
        return [message.format_gemini() for message in self.messages]

    def format_openai(self) -> list[ChatCompletionMessageParam]:
        return [message.format_openai() for message in self.messages]

    def format_instructor(self) -> list[dict[str, str]]:
        return [message.format_instructor() for message in self.messages]


T = TypeVar("T", bound=BaseModel)


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

    def generate_pydantic(
        self,
        output_type: type[T],
        model_name: str,
        messages: LlmMessages | str,
        temp: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> T:
        """指定したPydanticのモデルに構造化する"""
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

    def generate_pydantic(
        self,
        output_type: type[T],
        model_name: str,
        messages: LlmMessages | str,
        temp: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> T:
        # APIキーの設定
        if self.api_key is not None:
            genai.configure(api_key=self.api_key)

        # メッセージのフォーマット
        if isinstance(messages, str):
            messages = LlmMessages(messages=[LlmMessage(role="user", content=messages)])
        gemini_messages = messages.format_gemini()

        # 設定の準備
        generation_config = GenerationConfig(
            temperature=temp,
            max_output_tokens=max_tokens,
        )

        # モデルの準備
        model = GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
        )

        client = instructor.from_gemini(
            client=model,
            mode=instructor.Mode.GEMINI_JSON,
        )

        resp_data = client.messages.create(
            messages=gemini_messages,
            response_model=output_type,
        )

        if not isinstance(resp_data, output_type):
            raise ValueError(f"Invalid response: {resp_data}")

        return resp_data


class OpenAiClient(LlmClientBase):
    """OpenAIクライアント"""

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
        # モデルの準備
        model = OpenAI(api_key=self.api_key)

        # メッセージのフォーマット
        if isinstance(messages, str):
            messages = LlmMessages(messages=[LlmMessage(role="user", content=messages)])
        openai_messages = messages.format_openai()

        output_text = ""

        # レスポンスの生成
        response = model.chat.completions.create(
            model=model_name,
            messages=openai_messages,
            temperature=temp,
            max_tokens=max_tokens,
            stream=stream,
        )

        # ストリーミングの場合は、ストリーミングを返す. responseの型がStream[ChatCompletionChunk]の場合はこの処理を行う
        if isinstance(response, Stream):
            output_text = streaming_print_openai(response)
            return output_text
        else:
            output_text += response.choices[0].message.content or ""

            return output_text

    def generate_pydantic(
        self,
        output_type: type[T],
        model_name: str,
        messages: LlmMessages | str,
        temp: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> T:
        """指定したPydanticのモデルに構造化する"""
        raise NotImplementedError


def structured_output(
    output_type: type[T], text: str, model_name: str = "models/gemini-1.5-flash-latest", **kwargs: Any
) -> T:
    """指定したPydanticのモデルに構造化する"""
    messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content="""
                ユーザーが入力したテキストを忠実に省略せずに構造化して返してください。
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
