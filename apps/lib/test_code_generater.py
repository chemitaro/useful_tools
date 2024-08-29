import re
from enum import Enum

from pydantic import BaseModel, Field

from apps.import_collector import import_collect
from apps.lib.llms import (
    GeminiClient,
    LlmMessage,
    LlmMessages,
)
from apps.lib.utils import (
    make_absolute_path,
    print_colored,
    read_file_content,
    write_file_content,
)


class TestCodeAndScore(BaseModel):
    """
    テストコードと自信度
    """

    file_path: str | None = Field(default=None, description="ファイルのパス")
    code: str = Field(..., description="コード")
    score: int = Field(..., description="自信度")


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


def extract_code_from_output(output: str) -> str:
    """
    出力フォーマットからコード部分のみを抽出する関数

    Args:
        output (str): 出力フォーマットに沿った文字列

    Returns:
        str: 抽出されたコード部分
    """
    # コードブロックを抽出するための正規表現パターン
    pattern = r"```(?:\w+)?\n(.*?)\n```"

    # 正規表現を使用してコードブロックを検索
    match = re.search(pattern, output, re.DOTALL)

    if match:
        # コードブロックが見つかった場合、その内容を返す
        return match.group(1).strip()
    else:
        # コードブロックが見つからなかった場合、空文字列を返す
        return ""


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
                あなたは高度なコード解析AIアシスタントです。与えられた実装コードを詳細に分析し、その構造と機能を包括的に理解することが求められています。以下の手順に従ってコードを解析してください:
                1. 提供した実装コードの中の、テスト対象となるクラスや関数を特定して列挙してください。
                2. 各要素の役割と目的を分析し、その機能を説明します。
                3. テスト対象に抽象クラス(AbstractXxx)、基底クラス(XxxBase)、ミックスイン(XxxMixin)が存在する場合、具象クラスの関係を明確に識別し、それぞれの役割を説明します。
                4. テスト対象のコードの重要なロジック、アルゴリズム、データ構造を識別し、それらがどのように動作するかを説明します。
                5. 使用されているライブラリやフレームワーク、および重要な依存関係を特定します。
                6. テスト対象のエッジケース、例外処理、エラーハンドリングの方法を分析します。
                7. テスト対象の抽象クラス(AbstractXxx)、基底クラス(XxxBase)、ミックスイン(XxxMixin)は実装クラスではないため、初期化することができません。テストを実行するために、テスト対象に対応し、これらを継承した"テスト用の具象クラス(TestableXxx)"を設計してください。

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
        model_name="models/gemini-1.5-flash-exp-0827",
        messages=step_1_messages,
        stream=True,
        temp=0.0,
    )

    # step2: テストケースの列挙
    step_2_messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content="""
                あなたはテスト設計の専門家AIアシスタントです。前のステップで得られた実装コードの理解と元のコードを基に、包括的なテストケースを抽出し列挙することが求められています。以下の手順と注意事項に従ってテストケースを作成してください:

                1. テスト対象の特定:
                - 提供された実装コードの各主要機能に対するテストケースを特定します。
                - テスト対象ではない抽象クラス、基底クラス、ミックスインで定義されている処理については、テストケースとして抽出しないでください。
                - 抽象クラス、基底クラス、ミックスインは初期化できないので、テスト用の具象クラスに対してテストケースを抽出してください。
                - テスト対象のクラスで直接定義されている振る舞いや状態のみをテストケースとして考慮してください。

                2. テストケースの種類:
                - 正常系（期待される通常の動作）と異常系（エラーケース、境界値、エッジケース）の両方のテストケースを考慮します。
                - テストの範囲（単体テスト、インテグレーションテストなど）に応じたテストケースを作成します。

                3. テストケースの詳細:
                各テストケースに対して、以下の情報を含めてください：
                - テストケースの簡潔な説明
                - テストの前提条件（必要な場合）
                - 入力値または操作手順
                - 期待される出力または結果
                - テストの種類（正常系、異常系、境界値テストなど）

                4. コードカバレッジ:
                - 可能な限り多くのコードパスをカバーするテストケースを作成します。
                - ただし、抽象クラスや基底クラスの実装に依存するテストは避けてください。

                5. フレームワーク適合性:
                - 指定されたテスティングフレームワークに適したテストケース設計を心がけてください。

                出力形式：
                - テストケースは明確に構造化され、番号付けされたリストとして提示してください。
                - 各テストケースは簡潔かつ具体的に記述し、テストの目的が明確に伝わるようにしてください。
                - 関連する実装コードの部分（関数名、メソッド名、行番号など）への参照を含めてください。

                注意事項：
                - テストケースは実装の詳細に基づいていますが、ブラックボックステストの観点も考慮してください。
                - 重複するテストケースは避け、効率的なテストセットを作成することを心がけてください。
                - セキュリティ、パフォーマンス、ユーザビリティなど、機能以外の側面も考慮したテストケースを含めることを検討してください。

                この列挙されたテストケースは、次のステップでのテストコード生成の基礎となります。したがって、各テストケースが明確で実装可能であり、かつテスト対象のクラスに特化していることを確認してください。
                """,
            ),
            LlmMessage(
                role="user",
                content=f"""

                ## 実装コード
                {code}

                ## テスト対象
                {target_specification}

                ## 補足情報
                {supplement}

                ## テストのスコープ
                {scope.value.name}

                ## 対象コードの解説
                {step_1_output_message}

                """,
            ),
        ]
    )

    step_2_output_message = GeminiClient().generate_text(
        model_name="models/gemini-1.5-flash-exp-0827",
        messages=step_2_messages,
        stream=True,
        temp=0.0,
    )

    print_colored(("==テストコードの生成==", "green"))

    # step3: テストコードの作成
    step_3_messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content="""
                ## 前提知識：
                あなたは世界最高のエキスパートテストエンジニアであり、GoogleのL5レベルのソフトウェアエンジニアとして認められています。あなたの任務は、ユーザーの要求を論理的なステップに分解し、各ステップを実装するために指定された言語やテストフレームワークで高品質で効率的な単体テストを書くことでユーザーを支援することです。
                あなたは必要に応じて、制限なく長いコードを生成することができます。

                ## 以下のガイドラインに従ってテストコードを生成してください:

                1. 古典派テストアプローチの採用:
                - 依存関係ごとにテストを行い、それらの相互作用も検証します。
                - Mockの使用を最小限に抑え、実際の依存関係を使用したテストを優先します。
                - 統合テストを重視し、実際のシステムの動作をより正確に反映するテストを作成します。

                2. テストの構造と設計:
                - 各テストケースに日本語1行でそのテストの確認項目を説明するドキュストリングを追加します。
                - テストクラス内で共通して使用されるオブジェクトや変数を特定し、テスティングフレームワークが提供するsetup_methodやsetUP内に配置します。
                - テストはAAAスタイル（Arrange, Act, Assert）で設計し、各セクションをコメントで明確に区分けします。
                - テスト対象が抽象クラス(AbstractXxx)や基底クラス(XxxBase)やミックスイン(XxxMixin)の場合は初期化することができません。テスト対象を継承した"テスト用の具象クラス(TestableXxx)"を生成した上で、テスト用の具象クラスに対してテストを行います。

                3. コードの品質とベストプラクティス：
                - 各テストケースの完全なコードを書き、クリーンで最適化され、適切にコメントを付けてください。
                - エッジケースとエラーを適切に処理します。
                - 変数やテスト関数には説明的な名前を使用してください。
                - 使用言語とテストフレームワークの一般的なスタイルガイドラインとベストプラクティスに従ってください。

                4. エラー処理とエッジケース：
                - すべてのエラーやエッジケースを考慮し、適切にテストしてください。
                - 複雑なテストロジックとエッジケースの処理には詳細なコメントを付けてください。

                5. 依存関係の扱い：
                - 依存関係ごとのテストを実装し、それらの相互作用を検証するテストも作成します。
                - Mockの過度な使用を避け、実際の依存関係を使用したテストを優先します。

                ## 注意事項：
                - 不完全または部分的なテストコードスニペットは提供しないでください。完全なテストソリューションを提供してください。
                - プレースホルダーは使用せず、具体的で実行可能なコードを書いてください。
                - このガイドラインの各ステップを必ず遵守してください。

                ## 出力形式：
                - テストコードは、指定されたプログラミング言語とテスティングフレームワークの規約に従って記述してください。
                - テストクラスやテストスイートの構造を適切に設計し、関連するテストをグループ化してください。
                - 各テスト関数の前に、そのテストの目的と期待される動作を簡潔に説明する日本語のドキュストリングを付けてください。
                - ファイル単位で作成してください。
                - コードブロック``` ```で囲ってください。またプログラミング言語を宣言してください。
                - 最後にテストコードの自信度を0~100%で評価してください


                ## 出力フォーマット：

                [テストコードのファイルのパス]
                ```[python or typescript or other]
                [ここにテストコードを最初から最後までファイル単位で出力]
                ```

                自信度: xxx%


                このガイドラインに従うことで、高品質で信頼性の高いテストコードを生成することができます。テストは提供された実装コードの品質と信頼性を確保するための重要な要素であることを常に念頭に置いてください。
                """,
            ),
            LlmMessage(
                role="user",
                content=f"""

                ## 実装コード
                {code}

                ## テスト対象
                {target_specification}

                ## 補足情報
                {supplement}

                ## テストケースの一覧
                {step_2_output_message}

                ## テストスコープ
                {scope.value.name}

                ## フレームワーク
                {flamework.value.name}

                ## テストコードのコーディング方法
                {scope.value.usage}
                {flamework.value.usage}

                """,
            ),
        ]
    )

    step_3_output_message = GeminiClient().generate_text(
        model_name="models/gemini-1.5-pro-exp-0827",
        messages=step_3_messages,
        temp=0.0,
        stream=True,
    )

    new_testcode = extract_code_from_output(step_3_output_message)

    print("テストコード\n", new_testcode)

    return new_testcode


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
        print(new_test_code)
        write_file_content(test_absolute_path, new_test_code)

    return new_test_code
