from urllib.parse import urlparse
from collections import defaultdict
import os


class PathTree:
    def __init__(self, paths, root_path=None):
        self.root_path = root_path
        self.tree = self.create_tree(paths)

    def parse_url(self, url):
        parsed_url = urlparse(url)
        return filter(None, parsed_url.path.split('/'))  # 空の要素を除去

    def parse_directory_path(self, path):
        if self.root_path and path.startswith(self.root_path):
            path = os.path.relpath(path, self.root_path)
        return filter(None, path.split(os.sep))  # 空の要素を除去

    def insert_into_tree(self, tree, paths):
        for path in paths:
            if path not in tree:
                tree[path] = defaultdict(dict)
            tree = tree[path]

    def create_tree(self, paths):
        tree = defaultdict(dict)
        for path in paths:
            if path.startswith('http://') or path.startswith('https://'):
                parsed_paths = list(self.parse_url(path))
            else:
                parsed_paths = list(self.parse_directory_path(path))
            self.insert_into_tree(tree, parsed_paths)
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

url_tree = PathTree(urls)
tree_string = url_tree.print_tree()
print(tree_string)


paths = [
    '/home/user/documents',
    '/home/user/documents/file.txt',
    '/home/user/pictures',
    '/home/user/pictures/photo.jpg'
]

root_path = '/home/user'

path_tree = PathTree(paths, root_path=root_path)
print(path_tree.print_tree())
