from urllib.parse import urlparse
from collections import defaultdict

def parse_url(url):
    parsed_url = urlparse(url)
    paths = parsed_url.path.split('/')
    return filter(None, paths)  # 空の要素を除去

def insert_into_tree(tree, paths):
    for path in paths:
        tree = tree[path]

def create_tree(urls):
    tree = defaultdict(lambda: defaultdict(dict))
    for url in urls:
        paths = list(parse_url(url))
        insert_into_tree(tree, paths)
    return tree

def print_tree(tree, prefix="", is_root=True):
    items = list(tree.items())
    for i, (key, value) in enumerate(items):
        connector = "" if is_root else ("└── " if i == len(items) - 1 else "├── ")
        new_prefix = "" if is_root else (prefix + ("    " if i == len(items) - 1 else "│   "))
        print(prefix + connector + key)
        if isinstance(value, dict):
            print_tree(value, new_prefix, is_root=False)

# 使用例
urls = ['http://example.com/foo/bar', 'http://example.com/foo/baz', 'http://example.com/xyz']
tree = create_tree(urls)
print_tree(tree)
