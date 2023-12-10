from apps.scrape_web import main


class TestScrapeWeb:
    url = 'https://www.nintendo.co.jp/n02/shvc/bm4j/'

    def test_main(self):
        """メインの処理を実行できることを確認する"""
        # スクレイピングを実行する
        contents = main([self.url])

        assert type(contents) is list
