from typing import Literal
from apps.lib.utils import print_colored


def multiline_input(
    prompt: str = "複数行の入力を開始します。",
    color: Literal["black", "grey", "red", "green", "yellow", "blue", "magenta", "cyan", "white"] | None = None,
) -> str:
    """
    ユーザーから複数行の入力を受け取り、1つの文字列として返す。
    入力終了はCtrl+D（Unix系）またはCtrl+Z（Windows）で判断する。

    Args:
        prompt (str, optional): 入力開始時に表示するメッセージ。デフォルト値が設定されている。
        color (Literal["black", "grey", "red", "green", "yellow", "blue", "magenta", "cyan", "white"] | None, optional): メッセージの色。デフォルト値が設定されている。
    Returns:
        str: 複数行の入力を結合した1つの文字列
    """
    print_colored((f"\n{prompt}", color))
    print_colored(("終了するには、Unix系ではCtrl+D、WindowsではCtrl+Zを入力してください。", "grey"))
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines)


