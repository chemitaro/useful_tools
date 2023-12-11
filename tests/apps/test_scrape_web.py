from apps.scrape_web import main
from apps.lib.utils import count_tokens


class TestScrapeWeb:
    url = 'https://nextjs.org/docs/app'

    def test_main(self):
        """メインの処理を実行できることを確認する"""
        # スクレイピングを実行する
        contents = main(
            [self.url],
            limit_token=120000,
            limit_char=120000
        )

        assert type(contents) is list
        assert len(contents) > 0
        assert all([type(content) is str for content in contents])
        assert all([len(content) > 0 for content in contents])
        assert sum(count_tokens(content) for content in contents[1:]) < 120000
        assert sum(len(content) for content in contents[1:]) < 120000
        assert contents[0].startswith('Web Site Map: https://nextjs.org/docs/app\n')
