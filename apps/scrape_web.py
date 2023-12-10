#!/usr/bin/env python3

import argparse
import os
import sys

from apps.lib.web_crawler_scraper import WebCrawlerScraper
from apps.lib.path_tree import PathTree

# 現在のファイルの絶対パスを取得
current_file_path = os.path.abspath(__file__)

# ルートディレクトリまでのパスを取得（例：2階層上がルートディレクトリの場合）
root_directory = os.path.dirname(os.path.dirname(current_file_path))

# Pythonの実行パスにルートディレクトリを追加
if root_directory not in sys.path:
    sys.path.append(root_directory)


default_root_urls: list[str] = ['']
default_ignore_urls: list[str] = []
default_file_dir: str = '~/Desktop'
default_file_name: str = 'page-content'


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
    url_tree = path_tree.get_tree_layout()

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
        default=default_root_urls
    )
    parser.add_argument(
        '-i',
        '--ignore-urls',
        metavar='ignore_url',
        type=str,
        nargs='*',
        default=default_ignore_urls
    )
    parser.add_argument(
        '-o',
        '--output-type',
        type=str,
        choices=['copy', '.text'],
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
        default=120_000,
        help='Split by a specified number of tokens when copying to the clipboard'
    )
    parser.add_argument(
        '-f',
        '--file_name',
        metavar='output_file_name',
        type=str
    )
    args = parser.parse_args()
