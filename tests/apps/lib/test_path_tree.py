from apps.lib.path_tree import PathTree


class TestPathTree:
    """PathTree のテスト"""

    urls = [
        'http://example.com/foo/bar',
        'http://example.com/foo/baz',
        'http://example.com/xyz',
        'http://example.com/foo/bar/item1',
        'http://example.com/foo/bar/item2',
        'http://example.com/xyz/abc',
        'http://example.com/xyz/def',
        'http://example.com/xyz/def/ghi'
    ]

    paths = [
        '/User/hoge/home/user/documents',
        '/User/hoge/home/user/documents/file.txt',
        '/User/hoge/home/user/pictures',
        '/User/hoge/home/user/pictures/photo.jpg',
        '/User/hoge/home/user/pictures/today/2021-01-01.jpg',
        '/User/hoge/home/user/pictures/today/2021-01-02.jpg',
        '/User/hoge/home/user/pictures/today/morning/2021-01-02.jpg',
        '/User/hoge/home/user/pictures/old/2020-12-31.jpg',
        '/User/hoge/home/user/pictures/old/2020-12-30.jpg',
    ]

    root_path = '/User/hoge/home/user'

    def test_init(self):
        """初期化してインスタンスを生成できることを確認する"""
        path_tree = PathTree([])
        assert type(path_tree) is PathTree

    def test_view_tree_urls(self):
        """URL のリストから木構造を生成できることを確認する"""
        url_tree = PathTree(self.urls)
        assert url_tree.get_tree_layout() == 'example.com\n├── foo\n│   ├── bar\n│   │   ├── item1\n│   │   └── item2\n│   └── baz\n└── xyz\n    ├── abc\n    └── def\n        └── ghi\n'  # noqa: E501

    def test_view_tree_paths(self):
        """パスのリストから木構造を生成できることを確認する"""
        path_tree = PathTree(self.paths)
        assert isinstance(path_tree.get_tree_layout(), str)
        assert path_tree.get_tree_layout() == 'user\n├── documents\n│   └── file.txt\n└── pictures\n    ├── photo.jpg\n    ├── today\n    │   ├── 2021-01-01.jpg\n    │   ├── 2021-01-02.jpg\n    │   └── morning\n    │       └── 2021-01-02.jpg\n    └── old\n        ├── 2020-12-31.jpg\n        └── 2020-12-30.jpg\n'  # noqa: E501

    def test_view_tree_paths_with_root(self):
        """パスのリストから木構造を生成できることを確認する"""
        path_tree = PathTree(self.paths, root_path=self.root_path)
        assert isinstance(path_tree.get_tree_layout(), str)
        assert path_tree.get_tree_layout() == 'user\n├── documents\n│   └── file.txt\n└── pictures\n    ├── photo.jpg\n    ├── today\n    │   ├── 2021-01-01.jpg\n    │   ├── 2021-01-02.jpg\n    │   └── morning\n    │       └── 2021-01-02.jpg\n    └── old\n        ├── 2020-12-31.jpg\n        └── 2020-12-30.jpg\n'  # noqa: E501

    # 単一のドメインからなる URL のリストを渡した場合、root_pathがそのドメインとなることを確認する
    def test_view_tree_urls_with_single_domain(self):
        """単一のドメインからなる URL のリストを渡した場合、root_pathがそのドメインとなることを確認する"""
        urls = [
            'http://example.com/foo/bar',
            'http://example.com/foo/baz',
            'http://example.com/xyz',
            'http://example.com/foo/bar/item1',
            'http://example.com/foo/bar/item2',
            'http://example.com/xyz/abc',
            'http://example.com/xyz/def',
            'http://example.com/xyz/def/ghi'
        ]
        url_tree = PathTree(urls)

        assert url_tree.root_path == 'example.com'

    # 複数のドメインからなる URL のリストを渡した場合、root_pathがNoneとなることを確認する
    def test_view_tree_urls_with_multiple_domains(self):
        """複数のドメインからなる URL のリストを渡した場合、root_pathがNoneとなることを確認する"""
        urls = [
            'http://example.com/foo/bar',
            'http://example.com/foo/baz',
            'http://example.com/xyz',
            'http://example.com/foo/bar/item1',
            'http://example.com/foo/bar/item2',
            'http://example.com/xyz/abc',
            'http://example.com/xyz/def',
            'http://example.com/xyz/def/ghi',
            'http://example.net/foo/bar',
            'http://hoge.net/foo/baz',
            'http://hoge.net/xyz',
            'http://hoge.net/foo/bar/item1',
            'http://hoge.net/foo/bar/item2',
            'http://hoge.net/xyz/abc',
            'http://hoge.net/xyz/def',
            'http://hoge.net/xyz/def/ghi'
        ]
        url_tree = PathTree(urls)

        assert url_tree.root_path is None
