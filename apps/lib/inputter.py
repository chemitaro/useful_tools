from apps.lib.utils import Colors, print_colored


def multiline_input(
    message: str = "複数行の入力を開始します。",
    color: Colors | None = None,
) -> str:
    """
    ユーザーから複数行の入力を受け取り、1つの文字列として返す。
    入力終了はCtrl+D（Unix系）またはCtrl+Z（Windows）で判断する。

    Args:
        message (str, optional): 入力開始時に表示するメッセージ。デフォルト値が設定されている。
        color (Literal["black", "grey", "red", "green", "yellow", "blue", "magenta", "cyan", "white"] | None, optional): メッセージの色。デフォルト値が設定されている。
    Returns:
        str: 複数行の入力を結合した1つの文字列
    """
    print_colored((f"\n{message}", color))
    print_colored(("終了するには、Unix系ではCtrl+D、WindowsではCtrl+Zを入力してください。", "grey"))
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines)


# 入力方法を後で変更できるinput
def variable_input(message: str | None = None, color: Colors | None = None) -> str:
    """
    ユーザーからの入力を受け取り、テキストとして返す。
    """
    if message is None:
        message = "入力してください。"

    print_colored((f"\n{message}", color))
    print_colored(('  複数行を入力するには、"ml"と入力してください。', "grey"))
    user_input = input("input: ")

    if user_input == "ml":
        return multiline_input()
    else:
        return user_input
