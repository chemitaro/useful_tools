from urllib.parse import urlparse
from collections import defaultdict


class URLTree:
    tree: defaultdict

    def __init__(self, urls):
        self.tree = self.create_tree(urls)

    def parse_url(self, url):
        parsed_url = urlparse(url)
        paths = parsed_url.path.split('/')
        return filter(None, paths)  # 空の要素を除去

    def insert_into_tree(self, tree, paths):
        for path in paths:
            if path not in tree:
                tree[path] = defaultdict(dict)
            tree = tree[path]

    def create_tree(self, urls):
        tree = defaultdict(dict)
        for url in urls:
            paths = list(self.parse_url(url))
            self.insert_into_tree(tree, paths)
        return tree

    def print_tree(self, tree=None, prefix="", is_root=True):
        if tree is None:
            tree = self.tree
        result = ""
        items = list(tree.items())
        for i, (key, value) in enumerate(items):
            connector = "" if is_root else ("└── " if i == len(items) - 1 else "├── ")
            new_prefix = "" if is_root else (prefix + ("    " if i == len(items) - 1 else "│   "))
            result += prefix + connector + key + "\n"
            if isinstance(value, dict):
                result += self.print_tree(value, new_prefix, is_root=False)
        return result


# 使用例
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

url_tree = URLTree(urls)
tree_string = url_tree.print_tree()
print(tree_string)
