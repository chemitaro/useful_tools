import time
from typing import Any, Literal, TypeVar

import google.generativeai as genai
import instructor
from google.api_core import exceptions as google_exceptions
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.types.content_types import ContentDict
from google.generativeai.types.generation_types import (
    GenerateContentResponse,
    GenerationConfig,
)
from instructor import Mode, from_openai
from openai import OpenAI, OpenAIError, Stream
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

    def format_instructor(self) -> ChatCompletionMessageParam:
        return {"role": self.role, "content": self.content}  # type: ignore


class LlmMessages(BaseModel):
    messages: list[LlmMessage] = Field(default=[])

    def format_gemini(self) -> list[ContentDict]:
        return [message.format_gemini() for message in self.messages]

    def format_openai(self) -> list[ChatCompletionMessageParam]:
        return [message.format_openai() for message in self.messages]

    def format_instructor(self) -> list[ChatCompletionMessageParam]:
        return [message.format_instructor() for message in self.messages]


T = TypeVar("T", bound=BaseModel)


class LlmClientBase(BaseModel):
    """LLMクライアントの基底クラス"""

    api_key: str | None = Field(default=None)

    def generate_text(
        self,
        messages: LlmMessages | str,
        model_name: str | None = None,
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
        messages: LlmMessages | str,
        model_name: str | None = None,
        temp: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> T:
        """指定したPydanticのモデルに構造化する"""
        raise NotImplementedError


class GeminiClient(LlmClientBase):
    """Geminiクライアント"""

    DEFAULT_MODEL: str = "models/gemini-1.5-flash-latest"

    def generate_text(
        self,
        messages: LlmMessages | str,
        model_name: str | None = None,
        temp: float | None = None,
        max_tokens: int | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> str:
        # APIキーの設定
        if self.api_key is not None:
            genai.configure(api_key=self.api_key)

        # モデルの準備
        if model_name is None:
            model_name = self.DEFAULT_MODEL
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
        max_retries = 3
        retry_delay = 1  # 初期遅延（秒）

        for attempt in range(max_retries):
            try:
                response = llm.generate_content(gemini_messages, generation_config=generation_config, stream=stream)
                break  # 成功した場合、ループを抜ける
            except google_exceptions.GoogleAPIError as e:
                if attempt == max_retries - 1:  # 最後の試行の場合
                    raise  # エラーを再発生させる
                print(f"エラーが発生しました。リトライします（{attempt + 1}/{max_retries}）: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数バックオフ

        if stream is True:
            streaming_print_gemini(response)

        return response.text

    def generate_pydantic(
        self,
        output_type: type[T],
        messages: LlmMessages | str,
        model_name: str | None = None,
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
        if model_name is None:
            model_name = self.DEFAULT_MODEL

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

    DEFAULT_MODEL: str = "gpt-4o-mini"

    def generate_text(
        self,
        messages: LlmMessages | str,
        model_name: str | None = None,
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
        if model_name is None:
            model_name = self.DEFAULT_MODEL

        max_retries = 3
        retry_delay = 1  # 初期遅延（秒）

        for attempt in range(max_retries):
            try:
                response = model.chat.completions.create(
                    model=model_name,
                    messages=openai_messages,
                    temperature=temp,
                    max_tokens=max_tokens,
                    stream=stream,
                )
                break  # 成功した場合、ループを抜ける
            except OpenAIError as e:
                if attempt == max_retries - 1:  # 最後の試行の場合
                    raise  # エラーを再発生させる
                print(f"エラーが発生しました。リトライします（{attempt + 1}/{max_retries}）: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数バックオフ

        # ストリーミングの場合は、ストリーミングを返す. responseの型がStream[ChatCompletionChunk]の場合はこの処理を行う
        if isinstance(response, Stream):
            generated_text = streaming_print_openai(response)
            output_text += generated_text
        else:
            generated_text = response.choices[0].message.content or ""
            output_text += generated_text

        return output_text

    def generate_pydantic(
        self,
        output_type: type[T],
        messages: LlmMessages | str,
        model_name: str | None = None,
        temp: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> T:
        """指定したPydanticのモデルに構造化する"""
        # モデルの準備
        model = OpenAI(api_key=self.api_key)

        # メッセージのフォーマット
        if isinstance(messages, str):
            messages = LlmMessages(messages=[LlmMessage(role="user", content=messages)])
        openai_messages = messages.format_openai()

        # レスポンスの生成
        if model_name is None:
            model_name = self.DEFAULT_MODEL

        max_retries = 3
        retry_delay = 1  # 初期遅延（秒）

        for attempt in range(max_retries):
            try:
                response = model.beta.chat.completions.parse(
                    model=model_name,
                    messages=openai_messages,
                    response_format=output_type,
                    temperature=temp,
                    max_tokens=max_tokens,
                )
                break  # 成功した場合、ループを抜ける
            except OpenAIError as e:
                if attempt == max_retries - 1:  # 最後の試行の場合
                    raise  # エラーを再発生させる
                print(f"エラーが発生しました。リトライします（{attempt + 1}/{max_retries}）: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数バックオフ

        parsed_data = response.choices[0].message.parsed

        if not isinstance(parsed_data, output_type):
            raise ValueError(f"Invalid response: {parsed_data}")

        return parsed_data


def convert_text_to_pydantic(output_type: type[T], text: str) -> T:
    """指定したPydanticのモデルに構造化する"""
    messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content="""
                あなたは、ユーザーが入力したテキスト情報を指定されたPydanticデータ構造に変換する専門家です。
                以下の指示に従って、入力されたテキストを解析し、適切なデータ構造に変換してください：

                1. 入力されたテキストを注意深く読み、必要な情報を抽出してください。
                2. 抽出した情報を、指定されたPydanticデータ構造に合わせて整理してください。
                3. データ構造に合わない情報がある場合は、適切に処理または無視してください。
                4. 変換されたデータは、Pythonの辞書形式で出力してください。
                5. データ型は可能な限り適切なものを使用してください（例：整数、浮動小数点数、文字列、ブール値など）。
                6. 日付や時刻の情報がある場合は、適切な形式に変換してください。
                7. リストや入れ子構造が必要な場合は、適切に処理してください。
                8. 必須フィールドに情報がない場合は、Noneまたは適切なデフォルト値を使用してください。

                あなたの役割は、テキストを正確に解析し、指定されたデータ構造に変換することです。
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

    model = OpenAiClient()
    resp_data = model.generate_pydantic(
        output_type=output_type,
        messages=messages,
        model_name="gpt-4o-mini",
        temp=0.0,
    )

    return resp_data


def convert_text_to_pydantic_with_instructor(output_type: type[T], text: str) -> T:
    """指定したPydanticのモデルに構造化する"""
    messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content="""
                あなたは、ユーザーが入力したテキスト情報を指定されたPydanticデータ構造に変換する専門家です。
                以下の指示に従って、入力されたテキストを解析し、適切なデータ構造に変換してください：

                1. 入力されたテキストを注意深く読み、必要な情報を抽出してください。
                2. 抽出した情報を、指定されたPydanticデータ構造に合わせて整理してください。
                3. データ構造に合わない情報がある場合は、適切に処理または無視してください。
                4. 変換されたデータは、Pythonの辞書形式で出力してください。
                5. データ型は可能な限り適切なものを使用してください（例：整数、浮動小数点数、文字列、ブール値など）。
                6. 日付や時刻の情報がある場合は、適切な形式に変換してください。
                7. リストや入れ子構造が必要な場合は、適切に処理してください。
                8. 必須フィールドに情報がない場合は、Noneまたは適切なデフォルト値を使用してください。

                あなたの役割は、テキストを正確に解析し、指定されたデータ構造に変換することです。
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

    client = from_openai(OpenAI(), mode=Mode.TOOLS_STRICT)

    resp = client.chat.completions.create(
        response_model=output_type,
        messages=messages.format_instructor(),
        model="gpt-4o-mini",
    )

    return resp
