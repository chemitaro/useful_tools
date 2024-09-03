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
            - PydanticのBaseModelを継承しているクラスのバリデーションの検証は、バリデーションのメソッドで行うのではなく、クラスを初期化する際に行ってください。
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
            - PydanticのBaseModelを継承しているクラスのバリデーションの検証は、バリデーションのメソッドで行うのではなく、クラスを初期化する際に行ってください。
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
            - PydanticのBaseModelを継承しているクラスのバリデーションの検証は、バリデーションのメソッドで行うのではなく、クラスを初期化する際に行ってください。
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
        - クラス名、メソッド名、変数名は英語を使用すること。

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
        - インターフェイス(XxxIf)のテストは必要ありません。

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


def analyze_implementation_code(code: str, target_specification: str) -> str:
    """
    実装コードを分析する関数
    """
    messages = LlmMessages(
        messages=[
            LlmMessage(
                role="system",
                content=textwrap.dedent(
                    """
                    あなたは優秀なソフトウェアエンジニアで、コードの構造と機能を深く理解する専門家です。提供された実装コードを詳細に分析し、その構造、主要な機能、および重要なロジックを説明してください。
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
                    - コードの特徴やテストを行う上で注意すべき点

                    箇条書きで提供してください。
                    """
                ),
            ),
        ]
    )
    return GeminiClient().generate_text(
        llm_model=LlmModelEnum.GEMINI15FLASH,
        messages=messages,
        stream=True,
        temp=0.0,
    )


def generate_test_code(
    code: str,
    target_code: str,
    flamework: TestingFlameworkEnum,
    scope: TestScopeEnum,
    target_specification: str,
    supplement: str,
) -> str:
    """
    テストコードを生成する関数
    """

    # テストケースを列挙する関数
    def extract_test_cases(
        target_code: str, target_specification: str, impl_code_analysis: str, supplement: str, scope: TestScopeEnum
    ) -> str:
        messages = LlmMessages(
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
                        - 関連する実装コードの部分（関数名、クラス名、メソッド名）への参照を含めてください。

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
                        ## テストコードのコーディング規約
                        {TEST_CODE_CONVENTION_AND_KNOWLEDGE}

                        ## テストコードのコーディング方法
                        {scope.value.usage}
                        {flamework.value.usage}

                        ## 対象コードの解説
                        {impl_code_analysis}

                        ## テスト対象のコード
                        {target_code}

                        ## テスト対象
                        {target_specification}

                        ## 補足情報
                        {supplement}

                        ## テストのスコープ
                        {scope.value.name}
                        """
                    ),
                ),
            ]
        )

        output_message = GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15FLASH,
            messages=messages,
            stream=True,
            temp=0.0,
        )

        return output_message

    def generate_test_code(
        code: str, flamework: TestingFlameworkEnum, scope: TestScopeEnum, target_specification: str, supplement: str
    ) -> str:
        """
        テストコードを生成する関数
        """
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        f"""
                        ## テストコードのコーディング規約
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
                        {extract_test_cases_result}

                        ## テストスコープ
                        {scope.value.name}

                        ## フレームワーク
                        {flamework.value.name}
                        """
                    ),
                ),
            ]
        )

        output_message = GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15PRO,
            messages=messages,
            temp=0.0,
            stream=True,
        )

        return output_message

    # step1:実装コードを分析する
    print_markdown("## 実装コードの分析")
    analyze_implementation_code_result = analyze_implementation_code(
        code=code, target_specification=target_specification
    )
    print_markdown(analyze_implementation_code_result)

    # step2: テストケースの列挙
    print_markdown("## テストケースの列挙")
    extract_test_cases_result = extract_test_cases(
        target_code=target_code,
        target_specification=target_specification,
        impl_code_analysis=analyze_implementation_code_result,
        supplement=supplement,
        scope=scope,
    )
    print_markdown(extract_test_cases_result)

    # step3: テストコードの作成
    print_markdown("## テストコードの作成")
    generate_test_code_result = generate_test_code(
        code=code, flamework=flamework, scope=scope, target_specification=target_specification, supplement=supplement
    )
    print_markdown(generate_test_code_result)

    new_testcode = extract_code_from_output(generate_test_code_result)

    return new_testcode


# 既存のテストコードをアップデートする関数
def update_test_code(
    code: str,
    target_code: str,
    test_code: str,
    flamework: TestingFlameworkEnum,
    scope: TestScopeEnum,
    target_specification: str,
    supplement: str,
) -> str:
    """
    既存のテストコードをアップデートする関数
    """

    def analyze_implementation_code(code: str, target_specification: str) -> str:
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは優秀なソフトウェアエンジニアで、コードの構造と機能を深く理解する専門家です。提供された実装コードを詳細に分析し、その構造、主要な機能、および重要なロジックを説明してください。
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
                        - コードの特徴やテストを行う上で注意すべき点

                        箇条書きで提供してください。
                        """
                    ),
                ),
            ]
        )
        return GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15FLASH,
            messages=messages,
            stream=True,
            temp=0.0,
        )

    def analyze_test_coverage(target_code: str, test_code: str, code_analysis_result: str) -> str:
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは経験豊富なテストエンジニアで、実装コードとテストコードを比較し、テストカバレッジを分析する専門家です。提供された情報を基に、テストの網羅性を評価し、不足しているテストケースを特定してください。
                        """
                    ),
                ),
                LlmMessage(
                    role="user",
                    content=textwrap.dedent(
                        f"""
                        以下の情報を基に、テストカバレッジを分析し、不足しているテストケースを特定してください：

                        テストの種類：{scope.value.name}
                        {scope.value.usage}

                        テスト対象のコード：
                        {target_code}

                        実装コードの分析結果：
                        {code_analysis_result}

                        分析の対象のコード：
                        {target_specification}

                        現在のテストコード：
                        {test_code}

                        分析結果として、以下の情報を提供してください：
                        - テストされている機能や条件のリスト
                        - テストされていない機能や条件のリスト
                        - 現在のテストカバレッジの推定

                        注意点：
                        - コードは生成せずに、自然言語で回答してください。

                        箇条書きで提供してください。
                        """
                    ),
                ),
            ]
        )
        return GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15FLASH,
            messages=messages,
            stream=True,
            temp=0.0,
        )

    def design_new_test_cases(
        coverage_analysis_result: str, scope: TestScopeEnum, flamework: TestingFlameworkEnum
    ) -> str:
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは創造的なテスト設計者で、効果的なテストケースを設計する専門家です。カバレッジ分析の結果を基に、新しいテストケースを設計し、既存のテストスイートを補完してください。
                        """
                    ),
                ),
                LlmMessage(
                    role="user",
                    content=textwrap.dedent(
                        f"""
                        以下の情報を基に、新しいテストケースを設計してください：
                        プロジェクトのテストコーディング規約：
                        {TEST_CODE_CONVENTION_AND_KNOWLEDGE}
                        {flamework.value.usage}

                        テストの種類：{scope.value.name}
                        {scope.value.usage}

                        テスト対象のコード：
                        {target_code}

                        現在のテストコード：
                        {test_code}

                        テストカバレッジ分析結果：
                        {coverage_analysis_result}

                        設計するテストケースは、以下の点に注意してください：
                        - テストの網羅性を向上させること
                        - エッジケースや境界値を考慮すること
                        - テストフレームワークの特性を活かすこと
                        - テストの可読性と保守性を確保すること
                        - 自然言語で回答してください。

                        各テストケースについて、以下の情報を提供してください：
                        - テストの目的
                        - 入力値と期待される出力
                        - テストの前提条件（必要な場合）
                        - テスト手順の概要

                        注意点：
                        - コードは生成せずに、自然言語で回答してください。

                        箇条書きで提供してください。
                        """
                    ),
                ),
            ]
        )
        return GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15FLASH,
            messages=messages,
            stream=True,
            temp=0.0,
        )

    def generate_test_code(
        test_case_design: str, code: str, test_code: str, scope: TestScopeEnum, flamework: TestingFlameworkEnum
    ) -> str:
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは熟練したテストコード開発者で、高品質なテストコードを生成する専門家です。設計されたテストケースに基づいて、プロジェクトの規約に準拠した新しいテストコードを生成してください。
                        """
                    ),
                ),
                LlmMessage(
                    role="user",
                    content=textwrap.dedent(
                        f"""
                        以下の情報を基に、更新するテストコードを生成してください：

                        プロジェクトのテストコーディング規約：
                        {TEST_CODE_CONVENTION_AND_KNOWLEDGE}
                        {flamework.value.usage}

                        テストの種類：{scope.value.name}

                        現在の実装コード：
                        {code}

                        現在のテストコード：
                        {test_code}

                        テストケース更新計画：
                        {test_case_design}

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
        return GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15PRO,
            messages=messages,
            stream=True,
            temp=0.0,
        )

    def integrate_test_code(generated_test_code: str, existing_test_code: str, flamework: TestingFlameworkEnum) -> str:
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは経験豊富なソフトウェア統合エンジニアで、新しく生成されたテストコードを既存のテストスイートにシームレスに統合する専門家です。コードの一貫性と全体的な構造を維持しながら、新しいテストを適切に配置してください。
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
                        {generated_test_code}

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
        return GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15FLASH,
            messages=messages,
            stream=True,
            temp=0.0,
        )

    def assess_test_quality(
        integrated_test_code: str, target_code: str, scope: TestScopeEnum, flamework: TestingFlameworkEnum
    ) -> str:
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは精密なコード品質アナリストで、テストコードの品質を客観的に評価する専門家です。統合されたテストコードを分析し、その品質、網羅性、規約準拠度を評価してください。
                        """
                    ),
                ),
                LlmMessage(
                    role="user",
                    content=textwrap.dedent(
                        f"""
                        以下の情報を基に、統合されたテストコードの品質を評価してください：

                        統合されたテストコード：
                        {integrated_test_code}

                        テスト対象のコード：
                        {target_code}

                        テストの種類：{scope.value.name}

                        テストフレームワーク：
                        {flamework.value.usage}

                        評価結果として、以下の情報を提供してください：
                        - コーディング規約への準拠度
                        - テストカバレッジの予測
                        - テストケースの網羅性評価
                        - 改善が必要な箇所のリストと具体的な改善提案

                        回答は箇条書きで提供してください。また、重要度に応じて改善提案に優先順位を付けてください。
                        """
                    ),
                ),
            ]
        )
        return GeminiClient().generate_text(
            llm_model=LlmModelEnum.GEMINI15FLASH,
            messages=messages,
            stream=True,
            temp=0.0,
        )

    # ステップ1: コード解析
    print_markdown("## コード解析")
    code_analysis_result = analyze_implementation_code(code, target_specification)
    print_markdown(code_analysis_result)

    # ステップ2: テストカバレッジ分析
    print_markdown("## テストカバレッジ分析")
    coverage_analysis_result = analyze_test_coverage(target_code, test_code, code_analysis_result)
    print_markdown(coverage_analysis_result)

    # ステップ3: テストケース設計
    print_markdown("## 新しいテストケース設計")
    test_case_design = design_new_test_cases(coverage_analysis_result, scope, flamework)
    print_markdown(test_case_design)

    # ステップ4: テストコード生成
    print_markdown("## テストコードの生成")
    generated_test_code = generate_test_code(test_case_design, target_code, test_code, scope, flamework)
    print_markdown(generated_test_code)

    # ステップ5: テストコード統合
    print_markdown("## テストコードの統合")
    integrated_test_code = integrate_test_code(generated_test_code, test_code, flamework)
    print_markdown(integrated_test_code)

    # ステップ6: テストコード品質評価
    print_markdown("## テストコード品質評価")
    quality_assessment = assess_test_quality(integrated_test_code, target_code, scope, flamework)
    print_markdown(quality_assessment)

    # 最終的に更新されたテストコードを返す
    updated_test_code = extract_code_from_output(integrated_test_code)
    return updated_test_code


# Git差分からテストコードをアップデートする関数
def update_test_code_from_git_diff(
    code: str,
    target_code: str,
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
                        - コードの特徴やテストを行う上での注意点

                        回答は箇条書きで提供してください。
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

                        回答は箇条書きで提供してください。
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

                        回答は箇条書きで提供してください。
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

                        回答は箇条書きで提供してください。
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
            llm_model=LlmModelEnum.GEMINI15PRO,
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

                        回答は箇条書きで提供してください。また、重要度に応じて改善提案に優先順位を付けてください。
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
    print_markdown("## 実装コードの解析")
    code_analysis_result = code_analysis(code=code, target_specification=target_specification)
    print_markdown(code_analysis_result)

    # Git差分の分析
    print_markdown("## Git差分の分析")
    git_diff_analysis_result = git_diff_analysis(
        target_git_diff=target_git_diff, code=code, code_analysis_result=code_analysis_result
    )
    print_markdown(git_diff_analysis_result)

    # テストケースへの影響分析
    print_markdown("## テストケースへの影響分析")
    test_impact_analysis_result = test_impact_analysis(
        git_diff_analysis_result=git_diff_analysis_result,
        test_code=test_code,
        single_code=target_code,
        test_scope=scope,
    )
    print_markdown(test_impact_analysis_result)

    # テストケース更新計画
    print_markdown("## テストケース更新計画")
    test_case_update_plan_result = test_case_update_plan(
        test_impact_analysis_result=test_impact_analysis_result, code=code, scope=scope, flamework=flamework
    )
    print_markdown(test_case_update_plan_result)

    # テストコードの生成
    print_markdown("## テストコードの生成")
    test_code_generation_result = test_code_generation(
        test_case_update_plan_result=test_case_update_plan_result,
        code=code,
        test_code=test_code,
        scope=scope,
        flamework=flamework,
    )
    print_markdown(test_code_generation_result)

    # テストコードの統合
    print_markdown("## テストコードの統合")
    test_code_integration_result = test_code_integration(
        test_code_generation_result=test_code_generation_result, test_code=test_code, flamework=flamework
    )
    print_markdown(test_code_integration_result)

    # テストコードの品質評価
    print_markdown("## テストコードの品質評価")
    test_quality_assessment_result = test_quality_assessment(
        test_code_integration_result=test_code_integration_result, code=code, test_scope=scope, test_flamework=flamework
    )
    print_markdown(test_quality_assessment_result)

    updated_test_code = extract_code_from_output(test_code_integration_result)
    return updated_test_code


def analyze_test_failure_and_update(
    code: str,
    target_code: str,
    test_code: str,
    test_results: str,
    flamework: TestingFlameworkEnum,
    scope: TestScopeEnum,
    target_specification: str,
    supplement: str,
) -> str:
    """テスト失敗の原因を解析し、必要に応じてテストコードを修正する関数

    Args:
        code (str): 実装コード
        single_code (str): 単一の実装コード
        test_code (str): テストコード
        test_results (str): テスト結果
        target_git_diff (str): 対象のGit差分
        flamework (TestingFlameworkEnum): テストフレームワーク
        scope (TestScopeEnum): テストスコープ
        target_specification (str): テスト対象
        supplement (str): 補足情報

    Returns:
        str: 更新されたテストコード
    """

    def analyze_failure(test_results: str, code: str, test_code: str) -> str:
        """テスト失敗の原因を解析する関数

        Args:
            test_results (str): テスト結果
            code (str): 実装コード
            test_code (str): テストコード

        Returns:
            str: 解析結果
        """
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは優秀なソフトウェアエンジニアで、テスト失敗の原因を特定する専門家です。
                        提供されたテスト結果、実装コード、およびテストコードを基に、失敗の原因を特定してください。
                        """
                    ),
                ),
                LlmMessage(
                    role="user",
                    content=textwrap.dedent(
                        f"""
                        以下の情報を基に、テスト失敗の原因を分析してください：

                        実装コード：
                        {code}

                        テストコード：
                        {test_code}

                        テスト結果：
                        {test_results}

                        分析結果として、以下の情報を提供してください：
                        - 具体的な失敗箇所
                        - 具体的な失敗原因
                        - 失敗の区分（実装コードのバグ / テストコードの誤り）

                        回答は箇条書きで提供してください。
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

    def is_test_code_fault(analyze_failure_result: str) -> bool:
        """テストコードの修正が必要かどうかを判断する関数

        Args:
            analyze_failure_result (str): 失敗解析結果

        Returns:
            bool: テストコードの修正が必要かどうか
        """

        # テストコードに誤りがあるかどうか判定結果を持つクラス
        class TestCodeFault(BaseModel):
            is_test_code_fault: bool = Field(
                ..., description="テストコードに誤りがある場合はTrue, 誤りがない場合はFalse"
            )

        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは優秀なテストコードの修正専門家で、テストコードの修正が必要かどうかを判断する専門家です。
                        提供された失敗解析結果を基に、テストコードの修正が必要かどうかを判断してください。
                        """
                    ),
                ),
                LlmMessage(
                    role="user",
                    content=textwrap.dedent(
                        f"""
                        以下の情報を基に、テストコードの修正が必要かどうかを判断してください：

                        失敗解析結果：
                        {analyze_failure_result}
                        テストコードに誤りがある場合はTrue, 誤りがない場合はFalseを出力してください。
                        """
                    ),
                ),
            ]
        )
        response = GeminiClient().generate_pydantic(
            output_type=TestCodeFault,
            messages=messages,
            temp=0.0,
        )
        return response.is_test_code_fault

    def test_case_update_plan(
        analyze_failure_result: str, code: str, scope: TestScopeEnum, flamework: TestingFlameworkEnum
    ) -> str:
        """テストケース更新計画を立案する関数

        Args:
            analyze_failure_result (str): 失敗解析結果
            code (str): 実装コード
            scope (TestScopeEnum): テストスコープ
            flamework (TestingFlameworkEnum): テストフレームワーク

        Returns:
            str: テストケース更新計画
        """
        messages = LlmMessages(
            messages=[
                LlmMessage(
                    role="system",
                    content=textwrap.dedent(
                        """
                        あなたは優秀なテスト設計者で、効果的なテストケース更新計画を立案する専門家です。
                        失敗解析結果を基に、各テストケースの更新方針を決定し、優先順位を付けてください。
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

                        現在の実装コード：
                        {code}

                        テストコード：
                        {test_code}

                        失敗解析結果：
                        {analyze_failure_result}

                        更新計画として、以下の情報を提供してください：
                        - テスト対象のクラス名、関数名、メソッド名
                        - 更新の種類（追加、変更、削除）
                        - 各テストケースの更新計画（追加すべきアサーション、変更すべき入力値など）
                        - 更新の優先順位
                        - 自然言語で設計してください。

                        禁止事項
                        - 絶対にコードは生成しないでください。

                        回答は箇条書きで提供してください。
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
        analyze_failure_result: str,
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

                        失敗解析結果：
                        {analyze_failure_result}

                        テストケース更新計画：
                        {test_case_update_plan_result}

                        生成するテストコードは、以下の点に注意してください：
                        - プロジェクトのコーディング規約に準拠すること
                        - テストコードは変更点に対してのみ生成すること
                        - 変更のないコードは省略して、変更のあるテストケースのみを生成すること
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

    # テスト失敗の原因を解析
    print_markdown("## テスト失敗の原因を解析")
    analyze_failure_result = analyze_failure(test_results=test_results, code=code, test_code=test_code)
    print_markdown(analyze_failure_result)

    # テストコードの修正が必要かどうかを判断
    print_markdown("## テストコードの修正が必要かどうかを判断")
    if is_test_code_fault(analyze_failure_result):
        # テストケース更新計画
        print_markdown("## テストケース更新計画")
        test_case_update_plan_result = test_case_update_plan(
            analyze_failure_result=analyze_failure_result, code=code, scope=scope, flamework=flamework
        )
        print_markdown(test_case_update_plan_result)

        # テストコードの生成
        print_markdown("## テストコードの生成")
        test_code_generation_result = test_code_generation(
            test_case_update_plan_result=test_case_update_plan_result,
            code=code,
            test_code=test_code,
            analyze_failure_result=analyze_failure_result,
            scope=scope,
            flamework=flamework,
        )
        print_markdown(test_code_generation_result)

        # テストコードの統合
        print_markdown("## テストコードの統合")
        test_code_integration_result = test_code_integration(
            test_code_generation_result=test_code_generation_result, test_code=test_code, flamework=flamework
        )
        print_markdown(test_code_integration_result)

        updated_test_code = extract_code_from_output(test_code_integration_result)
        return updated_test_code
    else:
        return "実装コードの修正が必要です。"
