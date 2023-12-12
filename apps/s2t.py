#!/usr/bin/env python3

import argparse
import os
import sys

# 現在のファイルの絶対パスを取得
current_file_path = os.path.abspath(__file__)

# ルートディレクトリまでのパスを取得（例：2階層上がルートディレクトリの場合）
root_directory = os.path.dirname(os.path.dirname(current_file_path))

# Pythonの実行パスにルートディレクトリを追加
if root_directory not in sys.path:
    sys.path.append(root_directory)


from apps.lib.s2t_whisper.main import convert_speech_to_text, record_audio  # noqa: E402
from apps.lib.utils import print_colored  # noqa: E402
from apps.lib.outputs import print_and_copy  # noqa: E402


def main(*, model, language, temperature, prompt) -> str:
    """メイン関数."""
    # 録音
    record_audio()

    # 音声認識
    try:
        text = convert_speech_to_text(model=model, language=language, temperature=temperature, prompt=prompt)
    except Exception:
        text = convert_speech_to_text(model=model, language=language, temperature=temperature, prompt=prompt)

    return text


def app_run(*, model, language, temperature, prompt):
    """アプリケーションを実行する関数."""
    while True:
        # ユーザー入力を受け取る
        print('\n')
        print_colored(('Press "enter" to start recording, press "q" to exit: ', "grey"))
        user_input = input()

        # 'q'または'Q'が入力されたら終了
        if user_input.lower() == 'q':
            print_colored(("Exit the program.", "grey"))
            break

        text = main(**vars(parser.parse_args()))

        # 認識結果を表示
        print_and_copy(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        This program records audio from the microphone and saves it to a file.
        """
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="whisper-1",
        choices=["whisper-1"],
        help="The model to use for transcription. Default is 'whisper-1'.",
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default="ja",
        help="Language of the speech. Default is 'Japanese'.",
    )
    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        default=0.2,
        help="Temperature of the speech. 0.0 to 1.0.",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        default="I am the CEO of a company that plans, develops, and operates web services. My primary focus is on developing web applications and SaaS for the real estate sector. In terms of technology, we first develop locally using Docker and Docker Compose. For our production environment, we deploy and manage our backend APIs on Fly.io and our frontend applications on Vercel. Our source code is managed on GitHub, and we employ GitHub Actions for CI/CD. Regarding frameworks, we use Django and the Django framework for our backend, developed in Python. Internally, we adopt Domain-Driven Design, structuring our data using Pydantic for our domain objects. For the frontend, we use Next.js and TypeScript. Our styles are crafted with Tailwind CSS. Currently, we are utilizing Version 14 of Next.js and developing with AppRouter. ",  # noqa: E501
        help="Prompt for the speech.",
    )

    app_run(**vars(parser.parse_args()))
