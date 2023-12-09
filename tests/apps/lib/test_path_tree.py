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
        assert url_tree.print_tree() == 'foo\n├── bar\n│   ├── item1\n│   └── item2\n└── baz\nxyz\n├── abc\n└── def\n    └── ghi\n'

    def test_view_tree_paths(self):
        """パスのリストから木構造を生成できることを確認する"""
        path_tree = PathTree(self.paths)
        assert type(path_tree.print_tree()) == str
        assert path_tree.print_tree() == 'User\n└── hoge\n    └── home\n        └── user\n            ├── documents\n            │   └── file.txt\n            └── pictures\n                ├── photo.jpg\n                ├── today\n                │   ├── 2021-01-01.jpg\n                │   ├── 2021-01-02.jpg\n                │   └── morning\n                │       └── 2021-01-02.jpg\n                └── old\n                    ├── 2020-12-31.jpg\n                    └── 2020-12-30.jpg\n'  # noqa: E501

    def test_view_tree_paths_with_root(self):
        """パスのリストから木構造を生成できることを確認する"""
        path_tree = PathTree(self.paths, root_path=self.root_path)
        assert type(path_tree.print_tree()) == str
        assert path_tree.print_tree() == 'user\n├── documents\n│   └── file.txt\n└── pictures\n    ├── photo.jpg\n    ├── today\n    │   ├── 2021-01-01.jpg\n    │   ├── 2021-01-02.jpg\n    │   └── morning\n    │       └── 2021-01-02.jpg\n    └── old\n        ├── 2020-12-31.jpg\n        └── 2020-12-30.jpg\n'  # noqa: E501
