#!/usr/bin/env python3

import os
import sys

from pydantic import BaseModel, Field
from rich.prompt import Confirm, Prompt

# 現在のファイルの絶対パスを取得
current_file_path = os.path.abspath(__file__)

# ルートディレクトリまでのパスを取得（例：2階層上がルートディレクトリの場合）
root_directory = os.path.dirname(os.path.dirname(current_file_path))

# Pythonの実行パスにルートディレクトリを追加
if root_directory not in sys.path:
    sys.path.append(root_directory)

from apps.import_collector import import_collect  # noqa: E402
from apps.lib.git_operater import get_diff_with_commit  # noqa: E402
from apps.lib.inputter import variable_input  # noqa: E402
from apps.lib.test_code_generater import (  # noqa: E402
    TestingFlameworkEnum,
    TestScopeEnum,
    analyze_test_failure_and_update,
    generate_test_code,
    update_test_code,
    update_test_code_from_git_diff,
)
from apps.lib.utils import (  # noqa: E402
    execute_command,
    make_absolute_path,
    print_colored,
    read_file_content,
    write_file_content,
)


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


def run_test_code_generator(
    root_path: str,
    target_relative_path: str,
    reference_relative_paths: list[str],
    test_relative_path: str,
    flamework: TestingFlameworkEnum,
    scope: TestScopeEnum,
    target_specification: str | None,
    supplement: str | None,
    user_instruction: str | None,
) -> None:
    loop_count = 0

    while True:
        loop_count += 1

        impl_code = import_collect(
            root_path=root_path,
            target_paths=[target_relative_path, *reference_relative_paths],
            no_comment=False,
            with_prompt=False,
            max_char=999_999_999_999,
            max_token=1_900_000,
        )[0]

        target_code = import_collect(
            root_path=root_path,
            target_paths=[target_relative_path],
            depth=0,
            no_comment=True,
            with_prompt=False,
            max_char=999_999_999_999,
            max_token=1_900_000,
        )[0]

        test_absolute_path = make_absolute_path(root_path=root_path, relative_path=test_relative_path)
        test_code = read_file_content(test_absolute_path)

        # 既存のテストコードがでに存在しているかどうかを確認する。20文字以上の場合はTrueと判定する。
        is_exist_test_code = len(test_code) >= 20

        # 実装ファイルの最終コミットとの差分を取得する
        target_git_diff = get_diff_with_commit(paths=[target_relative_path])

        # Git差分が存在するかどうかを確認する
        is_exist_git_diff = len(target_git_diff) > 0

        # テストコードが存在する場合はテストを実行する
        if is_exist_test_code:
            test_command = f"{flamework.value.command} {test_relative_path}"
            print_colored((f"テストコードを実行するコマンド: {test_command}", "green"))
            test_result_code, test_result_output = execute_command(test_command)
            print(test_result_output)
            print_colored((f"テスト結果コード: {test_result_code}", "green"))

            is_test_success = test_result_code == 0

            user_instruction = variable_input(
                message='テストコード生成時のユーザー指示を入力してください。終了する場合は"q"と入力してください。',
                color="green",
            )
        else:
            test_result_code = 0
            test_result_output = "テストコードが存在しないため、テストを実行できません。"
            is_test_success = True

        if target_specification is None:
            target_specification = target_relative_path

        if supplement is None:
            supplement = "補足情報無し"

        if is_exist_git_diff and is_exist_test_code and loop_count < 2:
            new_test_code = update_test_code_from_git_diff(
                code=impl_code,
                target_code=target_code,
                test_code=test_code,
                target_git_diff=target_git_diff,
                flamework=flamework,
                scope=scope,
                target_specification=target_specification,
                supplement=supplement,
            )
        elif is_exist_test_code and is_test_success is False:
            new_test_code = analyze_test_failure_and_update(
                code=impl_code,
                target_code=target_code,
                test_code=test_code,
                test_results=test_result_output,
                flamework=flamework,
                scope=scope,
                target_specification=target_specification,
                supplement=supplement,
            )
        elif is_exist_test_code:
            new_test_code = update_test_code(
                code=impl_code,
                target_code=target_code,
                test_code=test_code,
                flamework=flamework,
                scope=scope,
                target_specification=target_specification,
                supplement=supplement,
            )
        else:
            new_test_code = generate_test_code(
                code=impl_code,
                flamework=flamework,
                scope=scope,
                target_specification=target_specification,
                supplement=supplement,
            )

        if Confirm.ask(f"{test_relative_path}にテストコードを出力しますか？", default=True):
            write_file_content(test_absolute_path, new_test_code)
            print_colored(f"生成されたテストコードを{test_relative_path}に出力しました。", "green")

        if user_instruction == "q":
            break


def main() -> None:
    root_path = os.getcwd()
    code_relative_path = Prompt.ask("実装ファイルのパスを入力してください")
    test_relative_path = Prompt.ask("テストファイルのパスを入力してください")
    input_reference_relative_paths = Prompt.ask("参照ファイルのパスを入力してください", default=None)
    reference_relative_paths: list[str] = (
        input_reference_relative_paths.split(" ") if input_reference_relative_paths else []
    )
    target_specification = Prompt.ask(
        "テスト対象を指定する場合は、パスやクラス名や関数名を入力してください。", default=None
    )
    supplement = variable_input(message="補足説明があれば入力してください。", color=None)
    testing_framework_name = Prompt.ask(
        "テストフレームワークを入力してください。",
        choices=TestingFlameworkEnum.name_list(),
        default=TestingFlameworkEnum.PYTEST.name,
    )
    testing_framework = TestingFlameworkEnum[testing_framework_name]
    test_scope_name = Prompt.ask(
        "テストスコープを入力してください。", choices=TestScopeEnum.name_list(), default=TestScopeEnum.UNIT.name
    )
    test_scope = TestScopeEnum[test_scope_name]

    user_instruction = None

    run_test_code_generator(
        root_path=root_path,
        target_relative_path=code_relative_path,
        reference_relative_paths=reference_relative_paths,
        test_relative_path=test_relative_path,
        flamework=testing_framework,
        scope=test_scope,
        target_specification=target_specification,
        supplement=supplement,
        user_instruction=user_instruction,
    )


if __name__ == "__main__":
    main()
