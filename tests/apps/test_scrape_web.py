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
        )

        assert isinstance(contents, list)
        assert len(contents) > 0
        assert all([isinstance(content, str) for content in contents])
        assert all([len(content) > 0 for content in contents])
        assert sum(count_tokens(content) for content in contents[1:]) < 130000
        assert contents[0].startswith('\nWeb Site Map: nextjs.org\n')
