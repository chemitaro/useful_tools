from apps.lib.utils import Colors, print_colored
from apps.s2t import speech_and_convert_text


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


def voice_input(message: str | None = None, prompt: str | None = None) -> str:
    """
    ユーザーからの音声入力を受け取り、テキストとして返す。
    """
    if message is None:
        message = "音声入力を開始します。"
    if prompt is None:
        prompt = ""

    print_colored((f"\n{message}", "green"))
    text = speech_and_convert_text(model="whisper-1", language="ja", temperature=0.2, prompt=prompt)
    print_colored((f"\n{text}"))
    return text


# 入力方法を後で変更できるinput
def variable_input(message: str | None = None, color: Colors | None = None) -> str:
    """
    ユーザーからの入力を受け取り、テキストとして返す。
    """
    if message is None:
        message = "入力してください。"

    print_colored((f"\n{message}", color))
    print_colored(('  複数行を入力するには、"ml"と入力してください。', "grey"))
    print_colored(('  音声入力するには、"vo"と入力してください。', "grey"))
    user_input = input("input: ")

    if user_input == "ml":
        return multiline_input()
    elif user_input == "vo":
        return voice_input()
    else:
        return user_input
