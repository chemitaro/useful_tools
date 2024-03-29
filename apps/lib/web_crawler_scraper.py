from dataclasses import dataclass
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

from apps.lib.utils import count_tokens, format_content, format_number, print_colored


# リミットを超えたことを知らせる例外
class LimitException(Exception):
    pass


@dataclass
class ScrapedData:
    url: str
    content: str
    token_size: int
    char_size: int


class WebCrawlerScraper:
    root_urls: list[str]
    ignore_urls: set[str]
    limit_token: int
    limit_char: int
    scraped_data: list[ScrapedData] = []
    found_urls: set[str] = set()
    visited_urls: set[str] = set()

    def __init__(
        self,
        root_urls: list[str] | str,
        ignore_urls: list[str] | None = None,
        limit_token: int | None = None,
        limit_char: int | None = None,
        scraped_data: list[ScrapedData] | None = None,
        found_urls: set[str] | None = None,
        visited_urls: set[str] | None = None,
    ):
        if isinstance(root_urls, str):
            root_urls = [root_urls]
        # root_urlsを正規化する
        root_urls = [self.normalize_url(url) for url in root_urls]
        self.root_urls = root_urls

        if ignore_urls is None:
            self.ignore_urls = set()
        else:
            normalized_ignore_urls = [self.normalize_url(url) for url in ignore_urls]
            self.ignore_urls = set(normalized_ignore_urls)

        if limit_token is None:
            limit_token = 999_999_999_999
        self.limit_token = limit_token

        if limit_char is None:
            limit_char = 999_999_999_999
        self.limit_char = limit_char

        if scraped_data is not None:
            self.scraped_data = scraped_data
        if found_urls is not None:
            self.found_urls = found_urls
        if visited_urls is not None:
            self.visited_urls = visited_urls

    def normalize_url(self, url: str) -> str:
        """URLを正規化する"""
        parsed_url = urlparse(url)
        return urlunparse(parsed_url._replace(query="", fragment=""))

    def is_subpath(self, url: str) -> bool:
        """URLがルートURLのサブパスかどうかを判定する"""
        return any(url.startswith(root_url) for root_url in self.root_urls)

    def should_ignore(self, url: str) -> bool:
        """URLを無視するかどうかを判定する"""
        return any(ignore_url in url for ignore_url in self.ignore_urls)

    def explore_and_scrape(self, url: str) -> None:
        """URLを探索し、スクレイプする"""
        normalized_url = self.normalize_url(url)
        if (
            normalized_url in self.visited_urls
            or not self.is_subpath(normalized_url)
            or self.should_ignore(normalized_url)
        ):
            return

        self.visited_urls.add(normalized_url)
        print_colored(
            ("Exploring: ", "green"),
            f"{len(self.visited_urls)} / {len(self.found_urls)}",
            " ",
            (normalized_url, "grey"),
        )

        if normalized_url.endswith(".pdf") or normalized_url.endswith(".jpg") or normalized_url.endswith(".jpeg"):
            print_colored(("Skipping :", "red"), " ", (normalized_url, "grey"))
            return  # PDFや画像ファイルのURLはスキップ

        try:
            response = requests.get(normalized_url, stream=True)
            if response.status_code == 200:
                soup: BeautifulSoup = BeautifulSoup(response.content, "html.parser")
                self.scrape_content(soup, normalized_url)
            else:
                print_colored((f"Error: {normalized_url} returned status code {response.status_code}", "red"))
                return
        except requests.exceptions.RequestException as e:
            print_colored((f"Error exploring {normalized_url}: {e}", "red"))
            return

        # HTMLリンク探索
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = self.normalize_url(urljoin(normalized_url, href))
            if not (full_url.endswith(".pdf") or full_url.endswith(".jpg") or full_url.endswith(".jpeg")):
                if full_url not in self.found_urls and self.is_subpath(full_url) and not self.should_ignore(full_url):
                    self.found_urls.add(full_url)
                    print_colored(("  + Found: ", "cyan"), (full_url, "grey"))

    def scrape_content(self, soup: BeautifulSoup, url: str) -> None:
        """スクレイプしてテキストを取得する"""
        # 本文以外の要素を削除する
        for selector in ["header", "footer", "nav", "aside"]:
            for element in soup.select(selector):
                element.decompose()

        # 本文を取得する
        text = soup.get_text(separator=" ", strip=True)
        text = text.replace("\0", "")  # null文字を削除する

        token_size = count_tokens(text)
        char_size = len(text)

        if token_size + self.total_token_size() > self.limit_token:
            print_colored(("トークン数が上限を超えました。", "red"))
            raise LimitException("トークン数が上限を超えました。")

        if char_size + self.total_char_size() > self.limit_char:
            print_colored(("文字数が上限を超えました。", "red"))
            raise LimitException("文字数が上限を超えました。")

        # スクレイプデータを追加する
        scraped_data: ScrapedData = ScrapedData(url=url, content=text, token_size=token_size, char_size=char_size)
        self.scraped_data.append(scraped_data)

    def run(self) -> None:
        """URLを探索し、スクレイプする"""
        self.found_urls = set(self.root_urls)

        while self.found_urls - self.visited_urls:
            url = (self.found_urls - self.visited_urls).pop()
            try:
                self.explore_and_scrape(url)
            except LimitException:
                print_colored(("クローリングを終了します。", "red"))
                break
        print_colored(("Finished: ", "green"), f"{len(self.visited_urls)} / {len(self.found_urls)}")
        print_colored("  total token size: ", format_number(self.total_token_size()))
        print_colored("  total char size: ", format_number(self.total_char_size()))

    def sort_scraped_data(self):
        """スクレイプデータをURLのアルファベット順にソートする"""
        return dict(sorted({data.url: data.content for data in self.scraped_data}.items()))

    def get_contents(self) -> list[str]:
        """スクレイプデータをテキストに変換する"""
        contents: list[str] = []
        for data in self.scraped_data:
            contents.append(format_content(data.url, data.content, style="doc"))
        return contents

    def get_urls(self) -> list[str]:
        """スクレイプデータのURLのリストを取得する"""
        urls = []
        for data in self.scraped_data:
            urls.append(data.url)
        return urls

    def total_token_size(self) -> int:
        """スクレイプデータのトークン数の合計を取得する"""
        return sum(data.token_size for data in self.scraped_data)

    def total_char_size(self) -> int:
        """スクレイプデータの文字数の合計を取得する"""
        return sum(data.char_size for data in self.scraped_data)
