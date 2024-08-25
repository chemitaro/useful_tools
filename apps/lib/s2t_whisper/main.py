"""This module contains a function to record audio from the microphone and save it to a file."""

import os
import sys
import threading
import time
import wave

import numpy as np
import sounddevice as sd
from openai import OpenAI
from pydub import AudioSegment

from apps.lib.utils import print_colored

audio_file_path: str = "recording"
colors = {
    "red": "\033[91m",
    "grey": "\033[90m",
    "end": "\033[0m",
}


def record_audio(file_name: str | None = None, fs: int = 44100, channels: int = 1) -> None:
    """ユーザーがエンターキーを押すまで録音を続け、ファイルをOgg Vorbis形式で保存する関数."""
    if file_name is None:
        file_name = str(audio_file_path) + ".wav"

    # 録音用のグローバル変数
    global is_recording
    is_recording = True

    def record_internal() -> list[np.ndarray]:
        """内部で使用する録音処理関数."""
        global is_recording
        start_time = time.time()
        with sd.InputStream(samplerate=fs, channels=channels) as stream:
            frames = []
            while is_recording:
                data, _ = stream.read(fs)
                frames.append(data)

                # 経過時間の表示（秒単位でカウントアップ）
                elapsed_time = int(time.time() - start_time)
                sys.stdout.write(
                    f"\r{colors['red']}Recording in progress: {colors['end']}{elapsed_time} sec {colors['grey']}Press \"Enter\" to stop{colors['end']}"
                )  # noqa: E501
                sys.stdout.flush()

            time.sleep(1)
            return frames

    def save_to_file(frames, file_name: str) -> None:
        """録音されたフレームをWAVファイルに保存する関数."""
        wav_data = np.concatenate(frames, axis=0)
        wav_file = wave.open(file_name, "wb")
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(np.iinfo(np.int16).bits // 8)
        wav_file.setframerate(fs)
        wav_file.writeframes((np.array(wav_data * 32767, dtype=np.int16)).tobytes())
        wav_file.close()
        print("\n")
        print_colored(("Save WAV files...", "grey"))

    def convert_to_ogg(wav_filename) -> str:
        """WAVファイルをOgg Vorbis形式に変換する関数."""
        ogg_filename = wav_filename.replace(".wav", ".ogg")
        audio = AudioSegment.from_wav(wav_filename)
        audio.export(ogg_filename, format="ogg")
        print_colored(("Convert to Ogg file...", "grey"))
        os.remove(wav_filename)  # 元のWAVファイルを削除
        return ogg_filename

    # 録音スレッドを開始
    recording_thread = threading.Thread(target=lambda: save_to_file(record_internal(), file_name))
    recording_thread.start()

    # エンターキー入力を待機
    input()
    is_recording = False

    # 録音スレッドが終了するのを待つ
    recording_thread.join()

    # WAVファイルをOgg Vorbis形式に変換
    convert_to_ogg(file_name)


def convert_audio_to_text(
    file_path: str | None = None,
    model: str = "whisper-1",
    language: str = "ja",
    temperature: float = 0.0,
    prompt: str = "",
) -> str:
    """Convert an audio file to text using OpenAI's Whisper API."""
    if file_path is None:
        file_path = audio_file_path + ".ogg"
    print_colored(("Convert to text...", "grey"))
    print_colored((f" - model: {model}", "grey"))
    print_colored((f" - lang.: {language}", "grey"))
    print_colored((f" - temp.: {temperature}", "grey"))
    print_colored((f" - prompt: {prompt[:45]}...", "grey"))
    client = OpenAI()
    try:
        # Send the audio data to OpenAI's Whisper API
        transcript = client.audio.transcriptions.create(
            file=open(file_path, "rb"), model=model, language=language, temperature=temperature, prompt=prompt
        )
    except Exception as e:
        print(f"Error: {e}")
        raise e

    # Extract and return the transcribed text
    return transcript.text
