import os
from collections import defaultdict
from urllib.parse import urlparse

from apps.lib.utils import make_relative_path


class PathTree:
    paths: list[str]
    root_path: str | None
    tree: defaultdict[str, dict]

    def __init__(self, paths: list[str], root_path: str | None = None):
        self.root_path = root_path
        self.paths = paths
        self.tree = self.create_tree(self.paths)

    def parse_url(self, url: str) -> list[str]:
        parsed_url = urlparse(url)
        return list(filter(None, parsed_url.path.split('/')))  # 空の要素を除去

    def parse_directory_path(self, path: str) -> list[str]:
        if self.root_path and path.startswith(self.root_path):
            root_dir_path = os.path.dirname(self.root_path)
            path = make_relative_path(root_dir_path, path)
        return list(filter(None, path.split(os.sep)))  # 空の要素を除去

    def insert_into_tree(self, tree: dict[str, dict], paths: list[str]) -> None:
        for path in paths:
            if path not in tree:
                tree[path] = defaultdict(dict)
            tree = tree[path]

    def create_tree(self, paths: list[str]) -> defaultdict[str, dict]:
        tree: defaultdict[str, dict] = defaultdict(dict)
        for path in paths:
            if path.startswith('http://') or path.startswith('https://'):
                parsed_paths = self.parse_url(path)
            else:
                parsed_paths = self.parse_directory_path(path)
            self.insert_into_tree(tree, parsed_paths)
        return tree

    def get_tree_layout(self, tree: dict[str, dict] | None = None, prefix: str = "", is_root: bool = True) -> str:
        if tree is None:
            tree = self.tree
        result = ""
        items = list(tree.items())
        for i, (key, value) in enumerate(items):
            connector = "" if is_root else ("└── " if i == len(items) - 1 else "├── ")
            new_prefix = "" if is_root else (prefix + ("    " if i == len(items) - 1 else "│   "))
            result += prefix + connector + key + "\n"
            if isinstance(value, dict):
                result += self.get_tree_layout(value, new_prefix, is_root=False)
        return result
