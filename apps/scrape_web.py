#!/usr/bin/env python3

import argparse
import os
import sys
from dataclasses import dataclass
from typing import Literal

# 現在のファイルの絶対パスを取得
current_file_path = os.path.abspath(__file__)

# ルートディレクトリまでのパスを取得（例：2階層上がルートディレクトリの場合）
root_directory = os.path.dirname(os.path.dirname(current_file_path))

# Pythonの実行パスにルートディレクトリを追加
if root_directory not in sys.path:
    sys.path.append(root_directory)


from apps.lib.content_size_optimizer import ContentSizeOptimizer  # noqa: E402
from apps.lib.outputs import (FileWriter, copy_to_clipboard,  # noqa: E402
                              print_result)
from apps.lib.path_tree import PathTree  # noqa: E402
from apps.lib.web_crawler_scraper import WebCrawlerScraper  # noqa: E402

# noqa: E402

default_root_urls: list[str] = ['']
default_ignore_urls: list[str] = []
default_file_dir: str = '~/Desktop'
default_file_name: str = 'page-content'


@dataclass
class ScrapeWebArgs:
    root_urls: list[str] | None
    ignore_urls: list[str] | None
    output_type: Literal["copy", "file"] | None
    limit_token: int | None
    limit_char: int | None
    max_char: int | None
    max_token: int | None
    file_name: str | None


def main(
    root_urls: list[str],
    ignore_urls: list[str] | None = None,
    limit_token: int | None = None,
    limit_char: int | None = None
) -> list[str]:
    """指定したURLからサイトマップを作成します。"""
    if ignore_urls is None:
        ignore_urls = []

    # 引数の検証
    if type(root_urls) is not list:
        raise TypeError('root_urls must be list')

    # Webクローラーを初期化する
    web_crawler_scraper = WebCrawlerScraper(
        root_urls=root_urls,
        ignore_urls=ignore_urls,
        limit_token=limit_token,
        limit_char=limit_char
    )

    # Webクローラーを実行して、スクレイピングする
    web_crawler_scraper.run()

    web_crawler_scraper.sort_scraped_data()
    contents = web_crawler_scraper.get_contents()

    # 探索したurlをツリー形式で表示に変換する
    urls = web_crawler_scraper.get_urls()
    path_tree = PathTree(urls)
    url_tree = path_tree.get_tree_map()

    print(url_tree)

    # contentsの一番最初にurl_treeを追加する
    contents.insert(0, url_tree)

    return contents


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='指定したURLからサイトマップを作成します。'
    )
    parser.add_argument(
        'root_urls',
        metavar='root_url',
        type=str,
        nargs='*',
    )
    parser.add_argument(
        '-i',
        '--ignore_urls',
        metavar='ignore_url',
        type=str,
        nargs='*',
    )
    parser.add_argument(
        '-o',
        '--output_type',
        type=str,
        choices=['copy', 'file'],
    )
    parser.add_argument(
        '-lc',
        '--limit_char',
        type=int,
        default=999_999_999,
        help='Limit the number of characters when scraping'
    )
    parser.add_argument(
        '-lt',
        '--limit_token',
        type=int,
        default=999_999_999,
        help='Limit the number of tokens when scraping'
    )
    parser.add_argument(
        '-mc',
        '--max_char',
        type=int,
        default=999_999_999,
        help='Split by a specified number of characters when copying to the clipboard'
    )
    parser.add_argument(
        '-mt',
        '--max_token',
        type=int,
        help='Split by a specified number of tokens when copying to the clipboard'
    )
    parser.add_argument(
        '-f',
        '--file_name',
        metavar='output_file_name',
        type=str
    )
    args = parser.parse_args()
    scrape_web_args = ScrapeWebArgs(
        root_urls=args.root_urls,
        ignore_urls=args.ignore_urls,
        output_type=args.output_type,
        limit_token=args.limit_token,
        limit_char=args.limit_char,
        max_char=args.max_char,
        max_token=args.max_token,
        file_name=args.file_name
    )

    # 不足している引数がある場合は、input()で入力を求める
    while scrape_web_args.root_urls is None or len(scrape_web_args.root_urls) == 0:
        print('\nURLを入力してください。')
        root_urls: str = input('root_urls: ')
        if root_urls:
            scrape_web_args.root_urls = root_urls.split(' ')
            break

    if scrape_web_args.ignore_urls is None:
        print('\n無視するURLを入力してください。')
        ignore_urls: str = input('ignore_urls: ')
        if ignore_urls:
            scrape_web_args.ignore_urls = ignore_urls.split(' ')

    if scrape_web_args.output_type is None:
        print('\n出力先方法を入力してください。(copy or file) default: copy')
        output_type: str = input('output_type: ')
        if output_type == 'file':
            scrape_web_args.output_type = 'file'
        else:
            scrape_web_args.output_type = 'copy'

    if scrape_web_args.limit_token is None:
        print('\nクローリングを行うトークン数の上限を入力してください。 default: 999,999,999')
        limit_token: str = input('limit_token: ')
        if limit_token:
            scrape_web_args.limit_token = int(limit_token)
        else:
            scrape_web_args.limit_token = 999_999_999

    if scrape_web_args.limit_char is None:
        print('\nクローリングを行う文字数の上限を入力してください。 default: 999,999,999')
        limit_char: str = input('limit_char: ')
        if limit_char:
            scrape_web_args.limit_char = int(limit_char)
        else:
            scrape_web_args.limit_char = 999_999_999

    if scrape_web_args.output_type == 'copy':
        if scrape_web_args.max_token is None:
            print('\n分割するトークン数を入力してください。 default: 120,000')
            max_token: str = input('max_token: ')
            if max_token:
                scrape_web_args.max_token = int(max_token)
            else:
                scrape_web_args.max_token = 120_000
        if scrape_web_args.max_char is None:
            print('\n分割する文字数を入力してください。 default: 999,999,999')
            max_char: str = input('max_char: ')
            if max_char:
                scrape_web_args.max_char = int(max_char)
            else:
                scrape_web_args.max_char = 999_999_999

    if scrape_web_args.output_type == 'file':
        if scrape_web_args.file_name is None:
            print(f'\nファイル名を入力してください。 default: {default_file_name}')
            file_name: str = input('file_name: ')
            if file_name:
                scrape_web_args.file_name = file_name
            else:
                scrape_web_args.file_name = default_file_name

    # メイン処理
    contents: list[str] = main(
        root_urls=scrape_web_args.root_urls,
        ignore_urls=scrape_web_args.ignore_urls,
        limit_token=scrape_web_args.limit_token,
        limit_char=scrape_web_args.limit_char
    )

    # 出力方法がcopyの場合
    if scrape_web_args.output_type == 'copy':
        # データをトークン数に合わせて調整する.
        optimizer = ContentSizeOptimizer(
            contents=contents,
            max_token=scrape_web_args.max_token,
            max_char=scrape_web_args.max_char
        )
        optimized_contents = optimizer.optimize_contents()

        print_result(
            contents,
            max_char=scrape_web_args.max_char,
            max_token=scrape_web_args.max_token
        )

        # クリップボードにコピーする
        copy_to_clipboard(optimized_contents)

    # 出力方法がfileの場合
    if scrape_web_args.output_type == 'file':
        print_result(
            contents,
            max_char=scrape_web_args.max_char,
            max_token=scrape_web_args.max_token
        )
        # ファイルに書き込む
        file_writer = FileWriter(
            file_name=scrape_web_args.file_name or default_file_name,
            file_dir=default_file_dir
        )
        file_writer.write(contents)