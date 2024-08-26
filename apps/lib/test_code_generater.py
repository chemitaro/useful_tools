from enum import Enum

from pydantic import BaseModel

from apps.import_collector import import_collect
from apps.lib.llms import GeminiClient, LlmMessage, LlmMessages
from apps.lib.utils import make_absolute_path, read_file_content


class TestingFlamework(BaseModel):
    name: str
    usage: str


class TestingFlameworkEnum(Enum):
    PYTEST = TestingFlamework(
        name="pytest",
        usage="テスト対象のクラスや関数ごとにTestクラスを作成し、テストケースをメソッドとして記述してください。\nデータの事前準備などの共通の処理があればsetup_method, teardown_method、pytest_fixtureを使用して再利用してください。\n",
    )
    UNITTEST = TestingFlamework(
        name="unittest",
        usage="テスト対象のクラスや関数ごとにTestクラスを作成し、テストケースをメソッドとして記述してください。\nアサーションにはマッチャーは使用しないでください。assertのみを使用してください。\nデータの事前準備などの共通の処理があればsetUp, tearDownを使用して再利用してください。",
    )
    DJANGO = TestingFlamework(
        name="django.test.unittest",
        usage="テスト対象のクラスや関数ごとにTestクラスを作成し、テストケースをメソッドとして記述してください。\nアサーションにはマッチャーは使用しないでください。assertのみを使用してください。\nデータの事前準備などの共通の処理があればsetUp, tearDownを使用して再利用してください。",
    )
    VITEST = TestingFlamework(name="vitest", usage="vitestのテストコードを生成してください")
    JEST = TestingFlamework(name="jest", usage="jestのテストコードを生成してください")

    @classmethod
    def name_list(cls) -> list[str]:
        return [flamework.name for flamework in cls]


class TestScope(BaseModel):
    name: str
    usage: str


class TestScopeEnum(Enum):
    UNIT = TestScope(
        name="unit test",
        usage="DBへのアクセスは行わないでMockを使用してください。\n外部のAPIやファイルのアクセスもMockを使用してください。",
    )
    INTEGRATION = TestScope(
        name="integration test",
        usage="DBへのアクセスはそのまま行います。\n外部のAPIやファイルのアクセスもそのまま行います。",
    )

    @classmethod
    def name_list(cls) -> list[str]:
        return [scope.name for scope in cls]


def generate_test_code(
    code: str,
    flamework: TestingFlameworkEnum,
    scope: TestScopeEnum,
    target_specification: str,
    supplement: str,
) -> str:
    """
    テストコードを生成する関数
    """

    # step1: 実装コードの理解
    step_1_messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content="""
                あなたは高度なコード解析AIアシスタントです。与えられた実装コードを詳細に分析し、その構造と機能を包括的に理解することが求められています。以下の手順に従ってコードを解析してください：
                1. コードの全体的な構造を把握し、主要な要素（クラス、関数、メソッドなど）を特定します。
                2. 各要素の役割と目的を分析し、その機能を簡潔に説明します。
                3. コード内の重要なロジック、アルゴリズム、データ構造を識別し、それらがどのように動作するかを説明します。
                4. 使用されているライブラリやフレームワーク、および重要な依存関係を特定します。
                5. コード内のエッジケース、例外処理、エラーハンドリングの方法を分析します。
                6. コードの潜在的な問題点や改善の余地がある部分を特定します。
                7. 抽象クラス、基底クラス、ミックスインと具象クラスの関係を明確に識別し、それぞれの役割を説明します。

                出力形式：
                - 分析結果は構造化された形式で提示してください。各セクションには明確な見出しをつけてください。
                - 技術的な専門用語を適切に使用し、必要に応じて簡潔な説明を加えてください。
                - コードの重要な部分については、該当する行番号や関数名を参照してください。
                - 抽象クラス、基底クラス、ミックスインと具象クラスの関係を明確に示してください。

                注意事項：
                - 提供されたコードの範囲（ファイル、モジュール、クラスなど）に焦点を当てて分析を行ってください。
                - コードの意図を推測する際は、確実な情報と推測を明確に区別してください。
                - 分析は客観的かつ中立的な立場で行い、個人的な意見や批判は避けてください。
                - 抽象クラス、基底クラス、ミックスインで定義されている振る舞いと、具象クラスで実装されている振る舞いを区別して説明してください。

                この分析結果は、後続のテストケース抽出とテストコード生成のステップで重要な入力となります。したがって、テスト可能な機能や境界条件に特に注意を払い、具象クラスの実装に焦点を当てた分析を心がけてください。
                """,
            ),
            LlmMessage(
                role="user",
                content=f"""
                ## 実装コード
                {code}

                ## テスト対象
                {target_specification}
                """,
            ),
        ]
    )
    step_1_output_message = GeminiClient().generate_text(
        model_name="models/gemini-1.5-flash-latest",
        messages=step_1_messages,
        stream=True,
    )

    # step2: テストケースの列挙
    # step3: テストコードの作成

    return step_1_output_message


# 既存のテストコードをアップデートする関数
def update_test_code(code: str, test_code: str) -> str:
    """
    既存のテストコードをアップデートする関数
    """
    return "update test code"


def call_test_code_generator(
    root_path: str,
    target_relative_path: str,
    reference_relative_paths: list[str],
    test_relative_path: str,
    flamework: TestingFlameworkEnum,
    scope: TestScopeEnum,
    target_specification: str | None,
    supplement: str | None,
    user_instruction: str | None,
) -> str:
    target_code = import_collect(
        root_path=root_path,
        target_paths=[target_relative_path, *reference_relative_paths],
        no_comment=False,
        with_prompt=False,
        max_char=999_999_999_999,
        max_token=1_900_000,
    )[0]
    test_absolute_path = make_absolute_path(root_path=root_path, relative_path=test_relative_path)
    test_code = read_file_content(test_absolute_path)

    # 既存のテストコードがでに存在しているかどうかを確認する。20文字以上の場合はTrueと判定する。
    is_exist_test_code = len(test_code) >= 20

    if target_specification is None:
        target_specification = target_relative_path

    if supplement is None:
        supplement = "補足情報無し"

    if is_exist_test_code:
        new_test_code = update_test_code(target_code, test_code)
    else:
        new_test_code = generate_test_code(
            code=target_code,
            flamework=flamework,
            scope=scope,
            target_specification=target_specification,
            supplement=supplement,
        )

    return new_test_code