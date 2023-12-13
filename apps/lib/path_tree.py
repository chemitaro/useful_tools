import os
from collections import defaultdict
from urllib.parse import urlparse

from apps.lib.utils import format_content, make_relative_path, print_colored


class PathTree:
    paths: list[str]
    root_path: str | None
    tree: defaultdict[str, dict] = defaultdict(dict)

    def __init__(self, paths: list[str], root_path: str | None = None):
        self.paths = paths
        if root_path:
            self.root_path = root_path
        else:
            self.root_path = self.find_common_root()
        self.create_tree()

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

    def is_url(self) -> bool:
        # すべてのパスがURLかどうかを判定する
        return all(path.startswith('http://') or path.startswith('https://') for path in self.paths)

    # pathsの中の起点となるパスを取得する
    def get_root_path(self) -> str:
        if self.root_path:
            return self.root_path
        else:
            if self.is_url():
                return self.paths[0]
            else:
                return os.path.commonpath(self.paths)

    def find_common_root(self) -> str | None:
        """与えられたパスまたはURLのリストから共通のルートを見つけ出す"""
        # self.root_pathが定義されていて、値が存在する場合にその値を返す
        if hasattr(self, 'root_path') and self.root_path:
            return self.root_path

        if len(self.paths) == 0:
            return None

        if self.is_url():
            # URLの場合、ドメインと最初のパスのセグメントを基にルートを特定
            common_root = urlparse(self.paths[0]).netloc
            paths_segments = [self.parse_url(path) for path in self.paths]
            common_segments = os.path.commonprefix(paths_segments)
            return f"http://{common_root}/{'/'.join(common_segments)}"
        else:
            # ディレクトリパスの場合
            return os.path.commonpath(self.paths)

    def create_tree(self) -> None:
        # まずself.treeを空のdefaultdictにする
        self.tree = defaultdict(dict)

        self.tree: defaultdict[str, dict] = defaultdict(dict)
        for path in self.paths:
            if self.is_url():
                parsed_paths = self.parse_url(path)
            else:
                parsed_paths = self.parse_directory_path(path)
            self.insert_into_tree(self.tree, parsed_paths)

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

    def get_tree_map(self) -> str:
        title: str
        if self.is_url():
            title = f'Web Site Map: {self.get_root_path()}'
        else:
            title = f'Directory Structure Chart: {self.get_root_path()}'

        # titleにpathsを追加
        return format_content(title, self.get_tree_layout(), style='doc')

    def print_tree_map(self) -> None:
        print_colored(("\n== Tree Map ==", "green"))
        print_colored("\n", self.get_tree_layout())
