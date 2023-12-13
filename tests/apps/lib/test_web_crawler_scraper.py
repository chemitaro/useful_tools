from apps.lib.web_crawler_scraper import WebCrawlerScraper, ScrapedData


class TestWebCrawlerScraper:
    """WebCrawlerScraperクラスのテスト"""

    scraped_data = [
        ScrapedData(url='https://example.com', content='Example Domain Domain Domain Domain Domain Domain', token_size=5, char_size=5),
        ScrapedData(url='https://example.com/foo', content='Example Foo Foo Foo Foo Foo Foo Foo Foo Foo Foo Foo', token_size=5, char_size=5),
        ScrapedData(url='https://example.com/bar', content='Example Hogehoge Hogehoge Hogehoge Hogehoge Hogehoge', token_size=5, char_size=5),
        ScrapedData(url='https://example.com/baz', content='Example Fugafuga Fugafuga Fugafuga Fugafuga Fugafuga', token_size=5, char_size=5),
    ]

    def test_init_from_url(self):
        """単独のurlで初期化してインスタンスを生成できることを確認する"""
        web_crawler_scraper = WebCrawlerScraper('https://example.com')
        assert type(web_crawler_scraper) is WebCrawlerScraper
        assert web_crawler_scraper.root_urls == ['https://example.com']

    def test_init_from_urls(self):
        """複数のurlで初期化してインスタンスを生成できることを確認する"""
        web_crawler_scraper = WebCrawlerScraper(['https://example.com', 'https://example.com/foo'])
        assert type(web_crawler_scraper) is WebCrawlerScraper
        assert web_crawler_scraper.root_urls == ['https://example.com', 'https://example.com/foo']

    def test_init_from_url_and_ignore_url(self):
        """単独のurlと無視するurlで初期化してインスタンスを生成できることを確認する"""
        web_crawler_scraper = WebCrawlerScraper('https://example.com', ignore_urls=['https://example.com/foo'])
        assert type(web_crawler_scraper) is WebCrawlerScraper
        assert web_crawler_scraper.root_urls == ['https://example.com']
        assert web_crawler_scraper.ignore_urls == {'https://example.com/foo'}

    def test_initial_url_with_params(self):
        """パラメータ付きのURLで初期化してインスタンスを生成できることを確認する"""
        web_crawler_scraper = WebCrawlerScraper('https://example.com?foo=bar')
        assert type(web_crawler_scraper) is WebCrawlerScraper
        assert web_crawler_scraper.root_urls == ['https://example.com']

    def test_normalize_url(self):
        """URLを正規化できることを確認する"""
        web_crawler_scraper = WebCrawlerScraper('https://example.com?foo=bar#baz')
        assert web_crawler_scraper.normalize_url('https://example.com?foo=bar#baz') == 'https://example.com'

    def test_is_subpath(self):
        """URLがルートURLのサブパスかどうかを判定できることを確認する"""
        web_crawler_scraper = WebCrawlerScraper('https://example.com')
        assert web_crawler_scraper.is_subpath('https://example.com')
        assert web_crawler_scraper.is_subpath('https://example.com/foo')
        assert web_crawler_scraper.is_subpath('https://example.com/foo/bar')
        assert not web_crawler_scraper.is_subpath('https://no-example.org')

    def test_should_ignore(self):
        """URLを無視するかどうかを判定できることを確認する"""
        web_crawler_scraper = WebCrawlerScraper('https://example.com', ignore_urls=['https://example.com/foo'])
        assert web_crawler_scraper.should_ignore('https://example.com/foo')
        assert web_crawler_scraper.should_ignore('https://example.com/foo/bar')
        assert not web_crawler_scraper.should_ignore('https://example.com')
        assert not web_crawler_scraper.should_ignore('https://no-example.org')

    def test_get_contents(self):
        """URLからコンテンツを取得できることを確認する"""
        web_crawler_scraper = WebCrawlerScraper(
            'https://example.com',
            scraped_data=self.scraped_data
        )
        contents = web_crawler_scraper.get_contents()
        assert len(contents) == 4
        assert contents[0] == '\nhttps://example.com\n"""\nExample Domain Domain Domain Domain Domain Domain\n"""\n'
        assert contents[1] == '\nhttps://example.com/foo\n"""\nExample Foo Foo Foo Foo Foo Foo Foo Foo Foo Foo Foo\n"""\n'
        assert contents[2] == '\nhttps://example.com/bar\n"""\nExample Hogehoge Hogehoge Hogehoge Hogehoge Hogehoge\n"""\n'
        assert contents[3] == '\nhttps://example.com/baz\n"""\nExample Fugafuga Fugafuga Fugafuga Fugafuga Fugafuga\n"""\n'

    def test_get_urls(self):
        """URLからURLを取得できることを確認する"""
        web_crawler_scraper = WebCrawlerScraper(
            'https://example.com',
            scraped_data=self.scraped_data
        )
        urls = web_crawler_scraper.get_urls()

        assert len(urls) == 4
        assert urls[0] == 'https://example.com'
        assert urls[1] == 'https://example.com/foo'
        assert urls[2] == 'https://example.com/bar'
        assert urls[3] == 'https://example.com/baz'

    def test_total_token_size(self):
        """トークン数の合計を取得できることを確認する"""
        web_crawler_scraper = WebCrawlerScraper(
            'https://example.com',
            scraped_data=self.scraped_data
        )
        assert web_crawler_scraper.total_token_size() == 20

    def test_total_char_size(self):
        """文字数の合計を取得できることを確認する"""
        web_crawler_scraper = WebCrawlerScraper(
            'https://example.com',
            scraped_data=self.scraped_data
        )
        assert web_crawler_scraper.total_char_size() == 20

    def test_run_scraping(self):
        """スクレイピングを実行できることを確認する"""
        web_crawler_scraper = WebCrawlerScraper(
            'https://www.nintendo.co.jp/n02/shvc/bm4j/'
        )
        web_crawler_scraper.run()

        assert len(web_crawler_scraper.scraped_data) == 7
        assert all([type(scraped_data) is ScrapedData for scraped_data in web_crawler_scraper.scraped_data])
        assert all([scraped_data.url.startswith('https://www.nintendo.co.jp') for scraped_data in web_crawler_scraper.scraped_data])
        assert all([scraped_data.token_size > 0 for scraped_data in web_crawler_scraper.scraped_data])
        assert all([scraped_data.char_size > 0 for scraped_data in web_crawler_scraper.scraped_data])
        assert all([type(scraped_data.content) is str for scraped_data in web_crawler_scraper.scraped_data])
        assert all([len(scraped_data.content) > 0 for scraped_data in web_crawler_scraper.scraped_data])

    def test_run_scraping_with_two_urls(self):
        """複数のURLでスクレイピングを実行できることを確認する"""
        web_crawler_scraper = WebCrawlerScraper(
            ['https://www.nintendo.co.jp/n02/shvc/bm4j/', 'https://www.nintendo.co.jp/n02/shvc/bplj/']
        )
        web_crawler_scraper.run()

        assert len(web_crawler_scraper.scraped_data) == 12
        assert all([type(scraped_data) is ScrapedData for scraped_data in web_crawler_scraper.scraped_data])
        assert all([scraped_data.url.startswith('https://www.nintendo.co.jp') for scraped_data in web_crawler_scraper.scraped_data])
        assert all([scraped_data.token_size > 0 for scraped_data in web_crawler_scraper.scraped_data])
        assert all([scraped_data.char_size > 0 for scraped_data in web_crawler_scraper.scraped_data])
        assert all([type(scraped_data.content) is str for scraped_data in web_crawler_scraper.scraped_data])
        assert all([len(scraped_data.content) > 0 for scraped_data in web_crawler_scraper.scraped_data])

    # トークン数のリミットでスクレイピングが停止することを確認する
    def test_run_scraping_with_limit_token(self):
        """トークン数のリミットでスクレイピングが停止することを確認する"""
        web_crawler_scraper = WebCrawlerScraper(
            'https://www.nintendo.co.jp/',
            limit_token=10000
        )
        web_crawler_scraper.run()

        assert web_crawler_scraper.total_token_size() < 10000

    # 文字数のリミットでスクレイピングが停止することを確認する
    def test_run_scraping_with_limit_char(self):
        """文字数のリミットでスクレイピングが停止することを確認する"""
        web_crawler_scraper = WebCrawlerScraper(
            'https://www.nintendo.co.jp/',
            limit_char=10000
        )
        web_crawler_scraper.run()

        assert web_crawler_scraper.total_char_size() < 10000
