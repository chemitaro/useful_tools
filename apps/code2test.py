#!/usr/bin/env python3

import os
import sys

import instructor
from google.generativeai import GenerativeModel
from pydantic import BaseModel, Field
from rich.prompt import Prompt

# 現在のファイルの絶対パスを取得
current_file_path = os.path.abspath(__file__)

# ルートディレクトリまでのパスを取得（例：2階層上がルートディレクトリの場合）
root_directory = os.path.dirname(os.path.dirname(current_file_path))

# Pythonの実行パスにルートディレクトリを追加
if root_directory not in sys.path:
    sys.path.append(root_directory)

from apps.lib.inputter import variable_input  # noqa: E402
from apps.lib.llms import GeminiClient, LlmMessage, LlmMessages  # noqa: E402
from apps.lib.test_code_generater import (  # noqa: E402
    TestingFlameworkEnum,
    TestScopeEnum,
    call_test_code_generator,
)
from apps.lib.utils import print_colored  # noqa: E402


class User(BaseModel):
    name: str
    age: int


class CodeAndScore(BaseModel):
    code: str = Field(
        description="コードをそのまま省略せずに修正や加工しないで返してください。",
        min_length=1,
    )
    score: int = Field(
        title="自信度",
        description="生成したコードの自信度を0~100で評価してください。",
        gt=0,
        lt=100,
    )


def main() -> None:
    root_path = os.getcwd()
    code_relative_path = Prompt.ask("実装ファイルのパスを入力してください。")
    test_relative_path = Prompt.ask("テストファイルのパスを入力してください。")
    target_specification = Prompt.ask("テスト対象の仕様を入力してください。", default=None)
    supplement = Prompt.ask("補足情報を入力してください。", default=None)
    testing_framework_name = Prompt.ask(
        "テストフレームワークを入力してください。", choices=TestingFlameworkEnum.name_list()
    )
    testing_framework = TestingFlameworkEnum[testing_framework_name]
    test_scope_name = Prompt.ask("テストスコープを入力してください。", choices=TestScopeEnum.name_list())
    test_scope = TestScopeEnum[test_scope_name]

    call_test_code_generator(
        root_path=root_path,
        target_relative_path=code_relative_path,
        reference_relative_paths=[],
        test_relative_path=test_relative_path,
        flamework=testing_framework,
        scope=test_scope,
        target_specification=target_specification,
        supplement=supplement,
        user_instruction=None,
    )

    print_colored(("code2test", "green"))

    print(os.getenv("GOOGLE_API_KEY"))
    model = GenerativeModel(model_name="models/gemini-1.5-flash-latest")
    client = instructor.from_gemini(
        client=model,
        mode=instructor.Mode.GEMINI_JSON,
    )

    resp = client.messages.create(
        messages=[
            {
                "role": "user",
                "content": "Extract Jason is 25 years old.",
            }
        ],
        response_model=User,
    )
    assert isinstance(resp, User)
    print(resp.name)
    print(resp.age)

    print("ストリーミング開始")

    janken_messages = LlmMessages(
        messages=[
            LlmMessage(
                role="user",
                content="じゃんけんゲームのプログラムをpythonで作成してください。一つのファイルに実装する想定で作成してください。また、そのプログラムの自信度を0~100で評価してください。",
            ),
        ]
    )
    answer = GeminiClient().generate_text(
        model_name="models/gemini-1.5-flash-latest",
        messages=janken_messages,
        stream=True,
    )

    resp_data = client.messages.create(
        messages=[
            {
                "role": "system",
                "content": "データを整理して返してください。",
            },
            {
                "role": "user",
                "content": answer,
            },
        ],
        response_model=CodeAndScore,
    )

    assert isinstance(resp_data, CodeAndScore)
    print_colored(("code", "green"))
    print(resp_data.code)
    print_colored(("score", "green"))
    print(resp_data.score)

    text = variable_input()
    print_colored((text, "green"))


if __name__ == "__main__":
    main()
