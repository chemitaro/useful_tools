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


from lib.clipboard_util import print_and_copy  # noqa: E402
from lib.s2t_whisper.main import convert_speech_to_text, record_audio  # noqa: E402
from lib.utils import print_colored  # noqa: E402


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


def app_run():
    """コマンドライン引数を受け取って実行する."""
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
        default='私は、Webサービスの企画、開発、運営を行う会社のCEOです。私の主な焦点は、人工知能の開発と応用、WebアプリケーションやSaaSの開発、そして不動産業界の効率化です。技術的には、まずDockerとDocker Composeを使用してローカルで開発を行います。本番環境では、バックエンドAPIをFly.ioにデプロイし管理し、フロントエンドアプリケーションはVercelにデプロイします。ソースコードはGitHubで管理され、CI/CDにはGitHub Actionsを利用しています。フレームワークに関しては、バックエンドにはPythonで開発された"Django"と"Django Rest framework"を使用しています。社内ではドメイン駆動設計を採用し、ドメインオブジェクトには"Pydantic"を使用してデータを構造化しています。フロントエンドには"Next.js"と"TypeScript"を使用しており、スタイルは"Tailwind CSS"で作成されています。現在、"Next.js"のバージョン14を使用し、"AppRouter"で開発を行っています。',  # noqa: E501
        help="Prompt for the speech.",
    )

    while True:
        # ユーザー入力を受け取る
        print("\n")
        print_colored(('Press "enter" to start recording, press "q" to exit: ', "grey"))
        user_input = input()

        # 'q'または'Q'が入力されたら終了
        if user_input.lower() == "q":
            print_colored(("Exit the program.", "grey"))
            break

        text = main(**vars(parser.parse_args()))

        # 認識結果を表示
        print_and_copy(text)


if __name__ == "__main__":
    app_run()
