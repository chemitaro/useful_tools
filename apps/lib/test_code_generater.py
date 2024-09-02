import re
import textwrap
from enum import Enum

from pydantic import BaseModel, Field

from apps.lib.llms import (
    GeminiClient,
    LlmMessage,
    LlmMessages,
    LlmModelEnum,
)
from apps.lib.utils import (
    print_markdown,
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
    command: str


class TestingFlameworkEnum(Enum):
    PYTEST = TestingFlamework(
        name="pytest",
        usage=textwrap.dedent(
            """
            コーディング規約の追加事項
            - テスト対象のクラスや関数ごとにTestクラスを作成し、テストケースをメソッドとして記述してください。
            - データの事前準備などの共通の処理があればsetup_method, teardown_method、pytest_fixtureを使用して再利用してください。
            """
        ),
        command="pytest",
    )
    UNITTEST = TestingFlamework(
        name="unittest",
        usage=textwrap.dedent(
            """
            コーディング規約の追加事項
            - テスト対象のクラスや関数ごとにTestクラスを作成し、テストケースをメソッドとして記述してください。
            - アサーションにはマッチャーは使用しないでください。assertのみを使用してください。
            - データの事前準備などの共通の処理があればsetUp, tearDownを使用して再利用してください。
            """
        ),
        command="pytest",
    )
    DJANGO = TestingFlamework(
        name="django.test.unittest",
        usage=textwrap.dedent(
            """
            コーディング規約の追加事項
            - テスト対象のクラスや関数ごとにTestクラスを作成し、テストケースをメソッドとして記述してください。
            - アサーションにはマッチャーは使用しないでください。assertのみを使用してください。
            - データの事前準備などの共通の処理があればsetUp, tearDownを使用して再利用してください。
            """
        ),
        command="pytest",
    )
    VITEST = TestingFlamework(
        name="vitest",
        usage=textwrap.dedent(
            """
            コーディング規約の追加事項
            - vitestのテストコードを生成してください
            """
        ),
        command="vitest",
    )
    JEST = TestingFlamework(
        name="jest",
        usage=textwrap.dedent(
            """
            コーディング規約の追加事項
            - jestのテストコードを生成してください
            """
        ),
        command="jest",
    )

    @classmethod
    def name_list(cls) -> list[str]:
        return [flamework.name for flamework in cls]


class TestScope(BaseModel):
    name: str
    usage: str


class TestScopeEnum(Enum):
    UNIT = TestScope(
        name="unit test",
        usage="- DBへのアクセスは行わないでMockを使用してください。\n- 外部のAPIやファイルのアクセスもMockを使用してください。",
    )
    INTEGRATION = TestScope(
        name="integration test",
        usage="- DBへのアクセスはそのまま行います。\n- 外部のAPIやファイルのアクセスもそのまま行います。",
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
        return output


TEST_CODE_CONVENTION_AND_KNOWLEDGE = textwrap.dedent(
    """
    # テストコード作成のための規約とベストプラクティス

    ## 1. 基本知識
    - あなたは世界最高のエキスパートテストエンジニアであり、GoogleのL5レベルのソフトウェアエンジニアです。
    - 高品質で効率的な単体テストを書くことが求められています。
    - 必要に応じて、制限なく長いコードを生成できます。

    ## 2. テストの設計と構造
    a. 命名規則:
        - テストクラス名: 'Test' + テスト対象のクラス名 (例: TestMyClass)
        - テストメソッド名: 'test_' + テストの内容を簡潔に表す名前 (例: test_valid_input)
        - 変数名とメソッド名: スネークケース (例: my_variable)

    b. テスト構造:
        - Arrange-Act-Assert (AAA) パターンを使用
        - 各セクションを明確にコメントで区切る (# Arrange, # Act, # Assert)
        - 各テストメソッドに日本語1行の説明（ドキュストリング）を追加

    c. テストケースの設計:
        - 正常系、異常系、エッジケースを考慮
        - 依存関係ごとのテストと相互作用の検証
        - テストの独立性を確保（他のテストに依存しない）

    d. セットアップとクリーンアップ:
        - 共通のセットアップコード: setUp メソッド（またはフレームワーク固有の同等物）を使用
        - 共通のクリーンアップコード: tearDown メソッド（またはフレームワーク固有の同等物）を使用
        - 重いセットアップが必要な場合: クラスレベルのセットアップを検討

    e. 特殊なケース:
        - 抽象クラス(AbstractXxx)、基底クラス(XxxBase)、ミックスイン(XxxMixin)のテスト:
            テスト用の具象クラス(TestableXxx)を作成してテストを実施

    ## 3. テストコードの品質
    a. アサーション:
        - 具体的なアサーションメソッドを使用 (例: assertEqual, assertTrue, assertRaises)
        - 各アサーションに失敗時の有用なメッセージを含める

    b. モックとスタブ:
        - 適切なモッキングライブラリを使用
        - モックオブジェクトの使用は最小限に抑え、実際の依存関係を優先

    c. テストデータ:
        - 可能な限りテストメソッド内で定義
        - 共通のテストデータはクラスレベルの定数または適切なフィクスチャとして定義

    d. コメントとドキュメンテーション:
        - 各テストメソッドの目的を簡潔に説明するドキュストリングを含める
        - 複雑なテストロジックには適切なインラインコメントを追加

    e. コードの品質:
        - クリーンで最適化されたコードを書く
        - 説明的な変数名とテスト関数名を使用
        - 言語とフレームワーク固有のスタイルガイドラインに従う

    ## 4. テスト戦略
    a. テストアプローチ:
        - 古典的なテストアプローチを採用（状態検証を優先）
        - 統合テストを重視し、実際のシステムの動作をより正確に反映

    b. カバレッジ:
        - コードの重要な部分を網羅的にテスト
        - エッジケースとエラー条件も適切にテスト

    c. パフォーマンスとリソース管理:
        - リソースを適切に管理し、テスト終了時にクリーンアップ
        - テストの実行速度と網羅性のバランスを考慮

    ## 5. 注意事項
    - 不完全または部分的なテストコードは提供しない
    - プレースホルダーは使用せず、具体的で実行可能なコードを書く
    - テストフレームワークと言語の特性を最大限に活用する
    - テストはコードの品質と信頼性を確保するための重要な要素であることを常に意識する

    これらの規約とガイドラインに従うことで、読みやすく、保守しやすい、そして信頼性の高いテストコードを作成できます。
    """
)


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
                content=textwrap.dedent(
                    """
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
                """
                ),
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
        messages=step_1_messages,
        llm_model=LlmModelEnum.GEMINI15FLASH,
        stream=True,
        temp=0.0,
    )

    print_markdown(step_1_output_message)

    # step2: テストケースの列挙
    step_2_messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content=textwrap.dedent(
                    """
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
                """
                ),
            ),
            LlmMessage(
                role="user",
                content=textwrap.dedent(
                    f"""
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
                    """
                ),
            ),
        ]
    )

    step_2_output_message = GeminiClient().generate_text(
        llm_model=LlmModelEnum.GEMINI15FLASH,
        messages=step_2_messages,
        stream=True,
        temp=0.0,
    )

    print_markdown(step_2_output_message)

    # step3: テストコードの作成
    step_3_messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content=textwrap.dedent(
                    f"""
                    {TEST_CODE_CONVENTION_AND_KNOWLEDGE}

                    ## テストコードのコーディング方法
                    {scope.value.usage}
                    {flamework.value.usage}

                    ## タスクの内容と指示:
                    あなたの任務は、提供された実装コードに対する高品質なテストコードを生成することです。以下の指示に従ってください：

                    1. 不完全または部分的なテストコードスニペットは提供しないでください。完全なテストソリューションを提供してください。
                    2. プレースホルダーは使用せず、具体的で実行可能なコードを書いてください。
                    3. このガイドラインの各ステップを必ず遵守してください。

                    ## 出力形式：
                    - テストコードは、指定されたプログラミング言語とテスティングフレームワークの規約に従って記述してください。
                    - テストクラスやテストスイートの構造を適切に設計し、関連するテストをグループ化してください。
                    - 各テスト関数の前に、そのテストの目的と期待される動作を簡潔に説明する日本語のドキュストリングを付けてください。
                    - ファイル単位で作成してください。
                    - コードブロック``` ```で囲ってください。またプログラミング言語を宣言してください。
                    - 最後にテストコードの自信度を0~100%で評価してください。

                    ## 出力フォーマット：

                    [テストコードのファイルのパス]
                    ```[python or typescript or other]
                    [ここにテストコードを最初から最後までファイル単位で出力]
                    ```

                    自信度: xxx%

                    このガイドラインに従うことで、高品質で信頼性の高いテストコードを生成することができます。テストは提供された実装コードの品質と信頼性を確保するための重要な要素であることを常に念頭に置いてください。
                    """
                ),
            ),
            LlmMessage(
                role="user",
                content=textwrap.dedent(
                    f"""
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
                    """
                ),
            ),
        ]
    )

    step_3_output_message = GeminiClient().generate_text(
        llm_model=LlmModelEnum.GEMINI15FLASH,
        messages=step_3_messages,
        temp=0.0,
        stream=True,
    )

    print_markdown(step_3_output_message)
    new_testcode = extract_code_from_output(step_3_output_message)

    return new_testcode


# 既存のテストコードをアップデートする関数
def update_test_code(
    code: str,
    test_code: str,
    target_git_diff: str,
    flamework: TestingFlameworkEnum,
    scope: TestScopeEnum,
    target_specification: str,
    supplement: str,
) -> str:
    """
    既存のテストコードをアップデートする関数
    """

    # 実装コードの解析と理解
    implementation_analysis_messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content=textwrap.dedent(
                    """
                    あなたは高度なコード解析AIアシスタントです。与えられた実装コードを詳細に分析し、その構造と機能を包括的に理解することが求められています。以下の手順に従ってコードを解析してください:
                    1. 提供した実装コードの中の、テスト対象となるクラスや関数を特定して列挙してください。
                    2. 各要素の役割と目的を分析し、その機能を説明します。
                    3. テスト対象に抽象クラス(AbstractXxx)、基底クラス(XxxBase)、ミックスイン(XxxMixin)が存在する場合、具象クラスの関係を明確に識別し、それぞれの役割を説明します。
                    4. テスト対象のコードの重要なロジック、アルゴリズム、データ構造を識別し、それらがどのように動作するかを説明します。
                    5. テスト対象のエッジケース、例外処理、エラーハンドリングの方法を分析します。

                    出力形式：
                    - 分析結果は構造化された形式で提示してください。各セクションには明確な見出しをつけてください。
                    - 技術的な専門用語を適切に使用し、必要に応じて簡潔な説明を加えてください。
                    - コードの重要な部分については、該当する関数名やクラス名、メソッド名を参照してください。

                    注意事項：
                    - 提供されたコードの範囲（ファイル、モジュール、クラスなど）に焦点を当てて分析を行ってください。
                    - コードの意図を推測する際は、確実な情報と推測を明確に区別してください。
                    - 分析は客観的かつ中立的な立場で行い、個人的な意見や批判は避けてください。
                    - 抽象クラス、基底クラス、ミックスインで定義されている振る舞いと、具象クラスで実装されている振る舞いを区別して説明してください。

                    この分析結果は、後続のテストケース抽出とテストコード生成のステップで重要な入力となります。したがって、テスト可能な機能や境界条件に特に注意を払い、具象クラスの実装に焦点を当てた分析を心がけてください。
                    """
                ),
            ),
            LlmMessage(
                role="user",
                content=textwrap.dedent(
                    f"""
                    ## 既存のテストコード
                    {test_code}

                    ## 実装コード
                    {code}

                    ## テスト対象
                    {target_specification}
                    """
                ),
            ),
        ]
    )
    implementation_analysis_output = GeminiClient().generate_text(
        model_name="models/gemini-1.5-flash-exp-0827",
        messages=implementation_analysis_messages,
        stream=True,
        temp=0.0,
    )

    print_markdown(implementation_analysis_output)

    if target_git_diff == "":
        git_diff_analysis_output = "変更なし"
    else:
        git_diff_analysis_messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは高度なコード変更分析AIアシスタントです。提供されたGitの差分、実装コード、および実装コードの解析結果を基に、実装コードにどのような変更があったかを詳細に分析し理解することが求められています。以下の手順に従って分析を行ってください：

                        1. Gitの差分を詳細に確認し、追加、削除、変更された部分を特定してください。
                        2. 実装コードの全体的な構造と、変更が加えられた箇所の関係性を分析してください。
                        3. 変更の種類（機能追加、バグ修正、リファクタリングなど）を識別し、その目的を推測してください。
                        4. 変更が既存の機能やロジックにどのような影響を与えるか評価してください。
                        5. 新しく追加された機能や変更された機能の詳細を説明してください。
                        6. 削除された機能やコードがある場合、その理由と影響を考察してください。
                        7. 変更によって生じる可能性のある新たな依存関係や副作用を特定してください。

                        出力形式：
                        - 分析結果は構造化された形式で提示してください。各セクションには明確な見出しをつけてください。
                        - 重要な変更点については、該当するコードの行番号や関数名を参照して具体的に示してください。
                        - 技術的な専門用語を適切に使用し、必要に応じて簡潔な説明を加えてください。
                        - コードを生成することはできません。必ず自然言語で出力してください。
                        - 日本語で出力してください。

                        注意事項：
                        - 分析は客観的かつ中立的な立場で行い、個人的な意見や批判は避けてください。
                        - 変更の意図を推測する際は、確実な情報と推測を明確に区別してください。
                        - テスト対象のスコープとフレームワークを考慮に入れて分析を行ってください。
                        - 絶対にコードを生成しないでください。

                        この分析結果は、後続のテストコード更新のステップで重要な入力となります。したがって、実装コードの変更を正確に理解し、テストコードへの影響を適切に予測することに注力してください。
                        """
                    ),
                ),
                LlmMessage(
                    role="user",
                    content=textwrap.dedent(
                        f"""
                        ## 実装コード
                        {code}

                        ## 実装コードの解析結果
                        {implementation_analysis_output}

                        ## 分析の対象
                        {target_specification}

                        ## gitの差分
                        {target_git_diff}
                        """
                    ),
                ),
            ]
        )

        git_diff_analysis_output = GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15FLASH,
            messages=git_diff_analysis_messages,
            stream=True,
            temp=0.0,
        )

        print_markdown(git_diff_analysis_output)

    # ステップ2: 既存のテストコードの解析と理解
    test_code_analysis_messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content=textwrap.dedent(
                    """
                    あなたは高度なテストコード解析AIアシスタントです。与えられた既存のテストコードを詳細に分析し、その構造と内容を包括的に理解することが求められています。以下の手順に従ってテストコードを解析してください:

                    1. テストコードの全体的な構造を把握し、テストクラスやテスト関数の構成を説明してください。
                    2. 各テストケースの目的と、テストしている機能や動作を特定し、説明してください。
                    3. テストカバレッジの範囲を分析し、どの部分の機能がテストされているかを明確にしてください。
                    4. テストコードの品質を0~100%で評価してください。

                    出力形式：
                    - 分析結果は構造化された形式で提示してください。各セクションには明確な見出しをつけてください。
                    - 技術的な専門用語を適切に使用し、必要に応じて簡潔な説明を加えてください。
                    - テストコードの重要な部分については、該当する行番号やテスト関数名を参照してください。
                    - コードを生成することはできません。必ず自然言語で出力してください。
                    - 日本語で出力してください。

                    注意事項：
                    - テストコードの品質や網羅性について客観的に評価してください。
                    - テストの意図を推測する際は、確実な情報と推測を明確に区別してください。
                    - 分析は客観的かつ中立的な立場で行い、個人的な意見や批判は避けてください。
                    - 絶対にコードを生成しないでください。

                    この分析結果は、後続のテストコード更新のステップで重要な入力となります。したがって、既存のテストの範囲と品質を正確に把握することに注力してください。
                    """
                ),
            ),
            LlmMessage(
                role="user",
                content=textwrap.dedent(
                    f"""
                    ## 既存のテストコード
                    {test_code}

                    ## テスト対象
                    {target_specification}

                    ## テストフレームワーク
                    {flamework.value.name}

                    ## テストスコープ
                    {scope.value.name}
                    """
                ),
            ),
        ]
    )
    test_code_analysis_output = GeminiClient().generate_text(
        llm_model=LlmModelEnum.GEMINI15FLASH,
        messages=test_code_analysis_messages,
        stream=True,
        temp=0.0,
    )

    print_markdown(test_code_analysis_output)

    # ステップ3: 既存のテストコードと実装コードを比較して、カバーされていない部分を識別
    uncovered_areas_identification_messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content=textwrap.dedent(
                    """
                    あなたは高度なテストカバレッジ分析AIアシスタントです。与えられた実装コードと既存のテストコードを比較し、テストでカバーされていない部分を特定することが求められています。以下の手順に従って分析を行ってください:

                    1. 実装コードの各クラス、メソッド、関数に対して、対応するテストが存在するかを確認してください。
                    2. テストが存在しない、または不十分なコード部分を特定し、リストアップしてください。特に以下の点に注意してカバレッジを分析してください：
                        - 主要な機能や重要なロジックのテストカバレッジ
                        - エッジケースや異常系のテストカバレッジ
                        - 新しく追加された機能や変更された部分のテストカバレッジ

                    出力形式：
                    - 分析結果は構造化された形式で提示してください。各セクションには明確な見出しをつけてください。
                    - カバーされていない部分は、該当するコードの行番号や関数名を参照して具体的に示してください。
                    - コードを生成することはできません。必ず自然言語で出力してください。
                    - 日本語で出力してください。

                    注意事項：
                    - 分析は客観的かつ中立的な立場で行い、個人的な意見や批判は避けてください。
                    - テストの品質や効率性についても考慮し、単なるカバレッジの量だけでなく、テストの有効性も評価してください。
                    - テスト対象のスコープとフレームワークを考慮に入れて分析を行ってください。
                    - 絶対にコードを生成しないでください。

                    この分析結果は、後続のテストコード更新のステップで重要な入力となります。したがって、カバーされていない部分を正確に特定し、有効な改善提案を行うことに注力してください。
                    """
                ),
            ),
            LlmMessage(
                role="user",
                content=textwrap.dedent(
                    f"""
                    ## 実装コード
                    {code}

                    ## 既存のテストコード
                    {test_code}

                    ## gitの差分
                    {target_git_diff}

                    ## テスト対象
                    {target_specification}

                    ## テストフレームワーク
                    {flamework.value.name}

                    ## テストスコープ
                    {scope.value.name}

                    ## 実装コードの解析結果
                    {implementation_analysis_output}

                    ## gitの差分の解析結果
                    {git_diff_analysis_output}

                    ## 既存テストコードの解析結果
                    {test_code_analysis_output}
                    """
                ),
            ),
        ]
    )
    uncovered_areas_identification_output = GeminiClient().generate_text(
        llm_model=LlmModelEnum.GEMINI15FLASH,
        messages=uncovered_areas_identification_messages,
        stream=True,
        temp=0.0,
    )

    print_markdown(uncovered_areas_identification_output)

    # ステップ4: 既存のテストコードと実装コードを比較して、修正が必要なテストケースや不要になったテストケースを特定
    test_case_review_messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content=textwrap.dedent(
                    """
                    あなたは高度なテスト分析AIアシスタントです。与えられた実装コードと既存のテストコードを比較し、不要になったテストケースを特定することが求められています。以下の手順に従って分析を行ってください:

                    1. 実装コードの変更点を特定し、それに関連する既存のテストケースを見つけてください。
                    2. 以下の観点から、各テストケースを評価してください：
                        - 実装の変更により、テストケースの期待値や入力値の修正が必要になっていないか
                        - テストケースが現在の実装と矛盾していないか
                        - テストケースが冗長になっていないか、または他のテストケースと重複していないか
                    3. 実装から削除された機能や変更された仕様に関連するテストケースを特定し、それらが不要になっていないか評価してください。
                    4. 修正が必要なテストケースについて、どのような修正が必要かを具体的に説明してください。
                    5. 不要になったテストケースについて、なぜそれらが不要になったのかを説明してください。

                    出力形式：
                    - 分析結果は構造化された形式で提示してください。各セクションには明確な見出しをつけてください。
                    - 修正が必要なテストケースや不要になったテストケースは、該当するテストコードの行番号やテスト関数名を参照して具体的に示してください。
                    - 修正の提案は簡潔かつ具体的に記述し、実装可能な形で提示してください。
                    - コードを生成することはできません。必ず自然言語で出力してください。

                    注意事項：
                    - 分析は客観的かつ中立的な立場で行い、個人的な意見や批判は避けてください。
                    - テストの品質や効率性についても考慮し、単なる網羅性だけでなく、テストの有効性も評価してください。
                    - テスト対象のスコープとフレームワークを考慮に入れて分析を行ってください。
                    - 絶対にコードを生成しないでください。

                    この分析結果は、後続のテストコード更新のステップで重要な入力となります。したがって、修正が必要なテストケースと不要になったテストケースを正確に特定し、有効な改善提案を行うことに注力してください。
                    """
                ),
            ),
            LlmMessage(
                role="user",
                content=textwrap.dedent(
                    f"""
                    ## 実装コード
                    {code}

                    ## gitの差分
                    {target_git_diff}

                    ## 既存のテストコード
                    {test_code}

                    ## テスト対象
                    {target_specification}

                    ## テストフレームワーク
                    {flamework.value.name}

                    ## テストスコープ
                    {scope.value.name}

                    ## 実装コードの解析結果
                    {implementation_analysis_output}

                    ## 既存テストコードの解析結果
                    {test_code_analysis_output}

                    ## gitの差分の解析結果
                    {git_diff_analysis_output}

                    ## カバレッジ分析結果
                    {uncovered_areas_identification_output}
                    """
                ),
            ),
        ]
    )
    test_case_review_output = GeminiClient().generate_text(
        llm_model=LlmModelEnum.GEMINI15FLASH,
        messages=test_case_review_messages,
        stream=True,
        temp=0.0,
    )

    print_markdown(test_case_review_output)

    # ステップ5: 実装コードの変更に基づいて、更新が必要なテストケースと新たに追加すべきテストケースをリストアップ
    test_case_update_list_messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content=textwrap.dedent(
                    """
                    あなたは高度なテスト設計AIアシスタントです。文字数に制限がない特別な言語モデルが使用されています。
                    提供された情報に基づいて、更新が必要なテストケースと新たに追加すべきテストケースをリストアップすることが求められています。以下の手順に従って分析を行ってください:

                    1. これまでの分析結果を総合的に考慮し、以下の項目をリストアップしてください：
                        a. 更新が必要な既存のテストケース
                        b. 新たに追加すべきテストケース
                    2. 各テストケースについて、以下の情報を提供してください：
                        - テストケースの簡潔な説明
                        - テストの目的
                        - 入力値や前提条件
                        - 期待される結果
                    3. 更新が必要なテストケースについては、どのような更新が必要かを具体的に説明してください。
                    4. 新たに追加すべきテストケースについては、なぜそのテストが必要なのかを説明してください。

                    出力形式：
                    - リストアップしたテストケースは、明確に構造化された形式で提示してください。
                    - 各テストケースには番号を付け、更新が必要なものと新規追加のものを区別してください。
                    - 技術的な専門用語を適切に使用し、必要に応じて簡潔な説明を加えてください。
                    - コードを生成することはできません。必ず自然言語で出力してください。

                    注意事項：
                    - テスト対象のスコープとフレームワークを考慮に入れてテストケースを設計してください。
                    - テストの網羅性と効率性のバランスを考慮し、重複を避けつつ十分なカバレッジを確保してください。
                    - 実装コードの変更点や新機能に特に注意を払い、それらが適切にテストされるようにしてください。
                    - 絶対にコードを生成しないでください。

                    この分析結果は、最終的なテストコードの更新に直接使用されます。したがって、具体的で実装可能なテストケースのリストを作成することに注力してください。
                    """
                ),
            ),
            LlmMessage(
                role="user",
                content=textwrap.dedent(
                    f"""
                    ## 実装コード
                    {code}

                    ## gitの差分
                    {target_git_diff}

                    ## 既存のテストコード
                    {test_code}

                    ## テスト対象
                    {target_specification}

                    ## テストフレームワーク
                    {flamework.value.name}

                    ## テストスコープ
                    {scope.value.name}

                    ## 実装コードの解析結果
                    {implementation_analysis_output}

                    ## 既存テストコードの解析結果
                    {test_code_analysis_output}

                    ## カバレッジ分析結果
                    {uncovered_areas_identification_output}

                    ## gitの差分の解析結果
                    {git_diff_analysis_output}

                    ## 修正が必要なテストケースと不要になったテストケースの特定
                    {test_case_review_output}
                    """
                ),
            ),
        ]
    )
    test_case_update_list_output = GeminiClient().generate_text(
        llm_model=LlmModelEnum.GEMINI15FLASH,
        messages=test_case_update_list_messages,
        stream=True,
        temp=0.0,
    )

    print_markdown(test_case_update_list_output)

    # ステップ6: 既存のテストコードに対して、テストケースの更新と追加を満たすようにテストコードをアップデート
    test_code_changes_messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content=textwrap.dedent(
                    f"""
                    {TEST_CODE_CONVENTION_AND_KNOWLEDGE}

                    ## テストコードのコーディング方法
                    {scope.value.usage}
                    {flamework.value.usage}

                    ## タスクの内容と指示:
                    あなたは高度なテストコード更新AIアシスタントです。出力する文字数の制限がない特別な言語モデルが使用されています。
                    これまでの分析結果とリストアップされたテストケースに基づいて、既存のテストコードを更新することが求められています。以下の手順に従ってテストコードを更新してください:

                    1. リストアップされた更新が必要なテストケースと新たに追加すべきテストケースを確認してください。
                    2. 既存のテストコードの構造を維持しながら、以下の更新を行ってください：
                        a. 更新が必要なテストケースを修正する
                        b. 新たなテストケースを追加する
                        c. 不要になったテストケースを削除する
                    3. 更新されたテストコードが指定されたテストフレームワーク（{flamework.value.name}）とテストスコープ（{scope.value.name}）に適合していることを確認してください。
                    4. テストコードの可読性と保守性を向上させるために、適切なコメントを追加してください。
                    5. テストケース間の依存関係や実行順序を考慮し、必要に応じてテストの構造を最適化してください。
                    6. 以下の命名のクラスは初期化することができません。テストを行う場合はテスト対象のクラスを継承したテスト実行用のクラス(TestableXxx)を作成してください。
                        - AbstractXxx : 抽象クラス
                        - XxxBase : 基底クラス
                        - XxxMixin : Mixinクラス

                    ## 出力形式：
                    - 冒頭に、更新の概要と主な変更点の説明文を記述してください。
                    - 変更のないコードは省略して、変更箇所のみを出力してください。
                    - 変更された部分には、簡潔なコメントを付けて変更内容を説明してください。
                    - 削除する部分には、コメントで削除したことを明記してください。

                    ## 出力フォーマット：

                    [更新の概要と主な変更点の説明文]

                    ```[python or typescript or other]
                    [変更後のテストコード]
                    # 変更ないテストコードは省略
                    ```

                    自信度: xxx%

                    ## 注意事項：
                    - テストコードの一貫性を保ち、上記のコーディング規約に厳密に従ってください。
                    - テストの網羅性と効率性のバランスを維持してください。
                    - 実装コードの変更に対応した適切なアサーションを使用してください。
                    - テストデータやモックオブジェクトが適切に更新されていることを確認してください。

                    この更新されたテストコードは、最終的な出力として使用されます。したがって、完全で実行可能なテストコードを生成することに注力してください。
                    """
                ),
            ),
            LlmMessage(
                role="user",
                content=textwrap.dedent(
                    f"""
                    ## 実装コード
                    {code}

                    ## gitの差分
                    {target_git_diff}

                    ## 既存のテストコード
                    {test_code}

                    ## テスト対象
                    {target_specification}

                    ## 更新が必要なテストケースと新たに追加すべきテストケースのリスト
                    {test_case_update_list_output}

                    ## 補足情報
                    {supplement}
                    """
                ),
            ),
        ]
    )
    test_code_changes_output = GeminiClient().generate_text(
        llm_model=LlmModelEnum.GEMINI15FLASH,
        messages=test_code_changes_messages,
        stream=True,
        temp=0.0,
    )

    updated_test_code_messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content=textwrap.dedent(
                    """
                    あなたは高度なテストコード統合AIアシスタントです。あなたは完全なコードを統合する役割があるため、出力する文字数の制限がない特別な言語モデルです。
                    既存のテストコードと変更箇所を統合して、完全な更新済みテストコードを生成することが求められています。以下の指示に従ってください：

                    1. 既存のテストコードと変更箇所を慎重に理解してください。
                    2. 変更箇所を適切な位置に統合し、完全な更新済みテストコードをファイル単位で省略ぜずに全てを生成してください。
                    3. 不要になったテストケースは削除し、新しいテストケースを適切な位置に追加してください。

                    出力形式：
                    - 実行可能な完全なテストコードを出力してください。
                    - 完全な更新済みテストコードを出力してください。省略せずに全体を記述してください。
                    - コードブロックの前に、ファイルパスを記載してください。
                    - 一つのテストファイルを生成してください。つまり、生成するコードブロックは一つだけです。

                    出力フォーマット：

                    [ファイルパス]
                    ```[python or typescript or other]
                    [完全な更新済みテストコード]
                    ```

                    注意事項：
                    - 追加や変更や省力を行わずに、正確にコードを統合してください。
                    - すべての変更が適切に統合されていることを確認してください。
                    - エラーがなく、実行可能な完全なテストコードを出力してください。
                    - git diffを生成しないでください。
                    """
                ),
            ),
            LlmMessage(
                role="user",
                content=textwrap.dedent(
                    f"""
                    ## 既存のテストコード
                    {test_code}

                    ## テストコードの変更箇所
                    {test_code_changes_output}

                    上記の情報を基に、完全な更新済みテストコードを生成してください。
                    """
                ),
            ),
        ]
    )

    updated_test_code_output = GeminiClient().generate_text(
        llm_model=LlmModelEnum.GEMINI15FLASH,
        messages=updated_test_code_messages,
        stream=True,
        temp=0.0,
    )

    print_markdown(updated_test_code_output)

    # 更新されたテストコードを抽出
    updated_test_code = extract_code_from_output(updated_test_code_output)

    return updated_test_code


# Git差分からテストコードをアップデートする関数
def update_test_code_from_git_diff(
    code: str,
    single_code: str,
    test_code: str,
    target_git_diff: str,
    flamework: TestingFlameworkEnum,
    scope: TestScopeEnum,
    target_specification: str,
    supplement: str,
) -> str:
    """Git差分からテストコードをアップデートする関数

    Args:
        code (str): 実装コード
        single_code (str): 単一の実装コード
        test_code (str): 既存のテストコード
        target_git_diff (str): 対象のGit差分
        flamework (TestingFlameworkEnum): テストフレームワーク
        scope (TestScopeEnum): テストスコープ
        target_specification (str): テスト対象
        supplement (str): 補足情報

    Returns:
        str: 更新されたテストコード
    """

    def code_analysis(code: str, target_specification: str) -> str:
        """実装コードを解析する関数

        Args:
            code (str): 実装コード

        Returns:
            str: 解析結果
        """
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは優秀なソフトウェアエンジニアで、コードの構造と機能を深く理解する専門家です。
                        提供された実装コードを詳細に分析し、その構造、主要な機能、および重要なロジックを説明してください。
                        """
                    ),
                ),
                LlmMessage(
                    role="user",
                    content=textwrap.dedent(
                        f"""
                        以下の実装コードを分析し、その構造と機能を説明してください：
                        {code}

                        解説の対象のコードは以下の通りです。
                        {target_specification}

                        分析結果として、以下の情報を提供してください：
                        - コードの全体的な構造
                        - 主要な関数やメソッドの一覧とその役割
                        - 重要なロジックや処理の流れ
                        - 使用されている主要なデータ構造やアルゴリズム
                        - コードの特徴や注意すべき点

                        回答は簡潔にまとめ、箇条書きで提供してください。
                        """
                    ),
                ),
            ]
        )
        response = GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15FLASH,
            messages=messages,
            stream=True,
            temp=0.0,
        )
        return response

    def git_diff_analysis(target_git_diff: str, code: str, code_analysis_result: str) -> str:
        """Git差分を分析する関数

        Args:
            target_git_diff (str): 対象のGit差分
            code (str): 実装コード

        Returns:
            str: 分析結果
        """
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは優秀なソフトウェアエンジニアで、コードの変更を分析する専門家です。
                        Gitの差分情報と現在の実装コードを基に、変更点を特定し、その影響を分析してください。
                        """
                    ),
                ),
                LlmMessage(
                    role="user",
                    content=textwrap.dedent(
                        f"""
                        以下の情報を基に、実装コードの変更点を分析してください：

                        現在の実装コード：
                        {code}

                        Gitの差分情報：
                        {target_git_diff}

                        分析結果として、以下の情報を提供してください：
                        - 変更された関数やメソッドのリスト
                        - 各変更の種類（追加、削除、修正）
                        - 変更の概要説明

                        回答は簡潔にまとめ、箇条書きで提供してください。
                        """
                    ),
                ),
            ]
        )
        response = GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15FLASH,
            messages=messages,
            stream=True,
            temp=0.0,
        )
        return response

    def test_impact_analysis(
        git_diff_analysis_result: str, test_code: str, single_code: str, test_scope: TestScopeEnum
    ) -> str:
        """テストケースへの影響を分析する関数

        Args:
            git_diff_analysis_result (str): 変更分析結果
            test_code (str): 既存のテストコード
            single_code (str): 単一の実装コード
            test_scope (TestScopeEnum): テストスコープ

        Returns:
            str: 分析結果
        """
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは経験豊富なテストエンジニアで、コードの変更がテストに与える影響を分析する専門家です。
                        実装コードの変更に基づいて、影響を受けるテストケースを特定し、その関連性を説明してください。
                        """
                    ),
                ),
                LlmMessage(
                    role="user",
                    content=textwrap.dedent(
                        f"""
                        以下の情報を基に、テストケースへの影響を分析してください：

                        テストの種類：{test_scope.value.name}

                        実装コード：
                        {single_code}

                        現在のテストコード：
                        {test_code}

                        変更分析結果：
                        {git_diff_analysis_result}

                        分析結果として、以下の情報を提供してください：
                        - 更新が必要なテストケースのリスト
                        - 各テストケースと関連する実装コードの変更点のマッピング

                        回答は簡潔にまとめ、箇条書きで提供してください。
                        """
                    ),
                ),
            ]
        )
        response = GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15FLASH,
            messages=messages,
            stream=True,
            temp=0.0,
        )
        return response

    def test_case_update_plan(
        test_impact_analysis_result: str, code: str, scope: TestScopeEnum, flamework: TestingFlameworkEnum
    ) -> str:
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは優秀なテスト設計者で、効果的なテストケース更新計画を立案する専門家です。
                        テストへの影響分析結果を基に、各テストケースの更新方針を決定し、優先順位を付けてください。
                        """
                    ),
                ),
                LlmMessage(
                    role="user",
                    content=textwrap.dedent(
                        f"""
                        以下の情報を基に、テストケースの更新計画を立案してください：

                        プロジェクトのテストコーディング規約：
                        {TEST_CODE_CONVENTION_AND_KNOWLEDGE}
                        {flamework.value.usage}

                        テストの種類：{scope.value.name}
                        {scope.value.usage}

                        現在のテストコード：
                        {code}

                        テスト影響分析結果：
                        {test_impact_analysis_result}

                        更新計画として、以下の情報を提供してください：
                        - テスト対象のクラス名、関数名、メソッド名
                        - 更新の種類（追加、変更、削除）
                        - 各テストケースの更新計画（追加すべきアサーション、変更すべき入力値など）
                        - 更新の優先順位
                        - 自然言語で設計してください。
￥
                        禁止事項
                        - 絶対にコードは生成しないでください。

                        回答は簡潔にまとめ、箇条書きで提供してください。
                        """
                    ),
                ),
            ]
        )
        response = GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15FLASH,
            messages=messages,
            stream=True,
            temp=0.0,
        )
        return response

    def test_code_generation(
        test_case_update_plan_result: str,
        code: str,
        test_code: str,
        scope: TestScopeEnum,
        flamework: TestingFlameworkEnum,
    ) -> str:
        """テストコードを生成する関数

        Args:
            test_case_update_plan_result (str): テストケース更新計画
            code (str): 実装コード
            test_code (str): 既存のテストコード

        Returns:
            str: 生成されたテストコード
        """
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは熟練したテストコード開発者で、高品質なテストコードを生成する専門家です。
                        更新計画に基づいて、プロジェクトの規約に準拠した新しいテストコードを生成してください。
                        """
                    ),
                ),
                LlmMessage(
                    role="user",
                    content=textwrap.dedent(
                        f"""
                        以下の情報を基に、更新されたテストコードを生成してください：

                        プロジェクトのテストコーディング規約：
                        {TEST_CODE_CONVENTION_AND_KNOWLEDGE}
                        {flamework.value.usage}

                        テストの種類：{scope.value.name}

                        現在の実装コード：
                        {code}

                        現在のテストコード：
                        {test_code}

                        テストケース更新計画：
                        {test_case_update_plan_result}

                        生成するテストコードは、以下の点に注意してください：
                        - プロジェクトのコーディング規約に準拠すること
                        - テストコードは変更点に対してのみ生成すること
                        - 変更のないコードは省略すること
                        - 削除するコードは作事除することをコメントで宣言すること
                        - 可読性が高く、メンテナンスしやすいこと
                        - 適切なアサーションを含むこと

                        各テストケース単位で更新されたコードを提供してください。
                        """
                    ),
                ),
            ]
        )
        response = GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15FLASH,
            messages=messages,
            stream=True,
            temp=0.0,
        )
        return response

    def test_code_integration(test_code_generation_result: str, test_code: str, flamework: TestingFlameworkEnum) -> str:
        """テストコードを統合する関数

        Args:
            test_code_generation_result (str): 生成されたテストコード
            test_code (str): 既存のテストコード

        Returns:
            str: 統合されたテストコード
        """
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは経験豊富なソフトウェア統合エンジニアで、新しく生成されたテストコードを既存のテストスイートにシームレスに統合する専門家です。
                        コードの一貫性と全体的な構造を維持しながら、新しいテストを適切に配置してください。
                        """
                    ),
                ),
                LlmMessage(
                    role="user",
                    content=textwrap.dedent(
                        f"""
                        あなたは既存のテストコードに新しいテストコードを統合する専門家です。
                        テストコードを忠実に完璧に統合する能力があります。
                        必要に応じて、際限なく長いコードを生成することができます。
                        以下の情報を基に、新しく生成されたテストコードを既存のテストスイートに統合してください：

                        プロジェクトのテストコーディング規約：
                        {TEST_CODE_CONVENTION_AND_KNOWLEDGE}
                        {flamework.value.usage}

                        現在のテストコード(全体)：
                        {test_code}

                        生成された新しいテストコード(各テストケース)：
                        {test_code_generation_result}

                        統合の際は、以下の点に注意してください：
                        - テストの論理的なグループ化を維持すること
                        - 重複を避け、コードの一貫性を保つこと
                        - 既存のテストスイートの構造を尊重すること
                        - 既存のコードを省略したり、削除したりしないこと
                        - 既存のコメントやdocstringは削除しないこと
                        - 出力された情報をそのままファイルに書き込みます。なので、余分な情報（フィアイルのパスやコードブロック``` ```）は不要です。

                        出力フォーマット：
                        - 直接ファイルに書き込み、実行可能なテストコードを出力してください。

                        統合後の実行可能な完全なテストコード(全体)を提供してください。
                        """
                    ),
                ),
            ]
        )
        response = GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15PRO,
            messages=messages,
            stream=True,
            temp=0.0,
        )
        return response

    def test_quality_assessment(
        test_code_integration_result: str, code: str, test_scope: TestScopeEnum, test_flamework: TestingFlameworkEnum
    ) -> str:
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは精密なコード品質アナリストで、テストコードの品質を客観的に評価する専門家です。
                        生成されたテストコードを分析し、その品質、網羅性、規約準拠度を評価してください。
                        """
                    ),
                ),
                LlmMessage(
                    role="user",
                    content=textwrap.dedent(
                        f"""
                        以下の情報を基に、生成されたテストコードの品質を評価してください：

                        プロジェクトのテストコーディング規約：
                        {TEST_CODE_CONVENTION_AND_KNOWLEDGE}
                        {test_flamework.value.name}

                        テストの種類：{test_scope.value.name}

                        実装コード：
                        {code}

                        テストコード：
                        {test_code_integration_result}

                        評価結果として、以下の情報を提供してください：
                        - コーディング規約への準拠度
                        - テストカバレッジの予測
                        - テストケースの網羅性評価
                        - 改善が必要な箇所のリストと具体的な改善提案

                        回答は簡潔にまとめ、箇条書きで提供してください。また、重要度に応じて改善提案に優先順位を付けてください。
                        """
                    ),
                ),
            ]
        )
        response = GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15FLASH,
            messages=messages,
            stream=True,
            temp=0.0,
        )
        return response

    # 実装コードの解析
    code_analysis_result = code_analysis(code=code, target_specification=target_specification)
    print_markdown(code_analysis_result)

    # Git差分の分析
    git_diff_analysis_result = git_diff_analysis(
        target_git_diff=target_git_diff, code=code, code_analysis_result=code_analysis_result
    )
    print_markdown(git_diff_analysis_result)

    # テストケースへの影響分析
    test_impact_analysis_result = test_impact_analysis(
        git_diff_analysis_result=git_diff_analysis_result,
        test_code=test_code,
        single_code=single_code,
        test_scope=scope,
    )
    print_markdown(test_impact_analysis_result)

    # テストケース更新計画
    test_case_update_plan_result = test_case_update_plan(
        test_impact_analysis_result=test_impact_analysis_result, code=code, scope=scope, flamework=flamework
    )
    print_markdown(test_case_update_plan_result)

    # テストコードの生成
    test_code_generation_result = test_code_generation(
        test_case_update_plan_result=test_case_update_plan_result,
        code=code,
        test_code=test_code,
        scope=scope,
        flamework=flamework,
    )
    print_markdown(test_code_generation_result)

    # テストコードの統合
    test_code_integration_result = test_code_integration(
        test_code_generation_result=test_code_generation_result, test_code=test_code, flamework=flamework
    )
    print_markdown(test_code_integration_result)

    # テストコードの品質評価
    test_quality_assessment_result = test_quality_assessment(
        test_code_integration_result=test_code_integration_result, code=code, test_scope=scope, test_flamework=flamework
    )
    print_markdown(test_quality_assessment_result)
    updated_test_code = extract_code_from_output(test_code_integration_result)

    return updated_test_code
