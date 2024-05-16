import argparse
import os
import sys
from dataclasses import dataclass

# 現在のファイルの絶対パスを取得
current_file_path = os.path.abspath(__file__)

# ルートディレクトリまでのパスを取得（例：2階層上がルートディレクトリの場合）
root_directory = os.path.dirname(os.path.dirname(current_file_path))

# Pythonの実行パスにルートディレクトリを追加
if root_directory not in sys.path:
    sys.path.append(root_directory)

from apps.lib.class_collector import ClassCollector  # noqa: E402
from apps.lib.class_diagram_generator import ClassDiagramGenerator  # noqa: E402
from apps.lib.dependency_analyzer.main import DependencyAnalyzer  # noqa: E402


@dataclass
class MainArgs:
    root_path: str
    target_paths: list[str] | None
    scope_paths: list[str] | None
    ignore_paths: list[str] | None
    depth: int | None


def create_class_diagram(
    root_path: str,
    target_paths: list[str] | None,
    scope_paths: list[str] | None,
    ignore_paths: list[str] | None,
    depth: int | None,
) -> str:
    """指定したPythonファイルからクラス図を作成する."""
    # ファイルの依存関係を解析
    dependency_analyzer = DependencyAnalyzer.factory(
        root_path=root_path,
        start_relative_paths=target_paths,
        scope_relative_paths=scope_paths,
        ignore_relative_paths=ignore_paths,
        depth=depth,
    )
    dependency_file_paths: list[str] = dependency_analyzer.analyze()

    # ファイルのパスからクラスを取得
    class_collector = ClassCollector(file_paths=dependency_file_paths)
    classes = class_collector.execute()

    # クラス図を作成
    class_diagram_generator = ClassDiagramGenerator(classes=classes)
    class_diagram_generator.analyze()
    class_diagram = class_diagram_generator.generate_puml()
    import pdb

    pdb.set_trace()


def main(main_args: MainArgs) -> None:
    """指定したPythonファイルからクラス図を作成して指定したファイルに出力する."""
    pass


def run_from_cli():
    """CLIから実行するための関数."""
    print("Hello, World!")
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "target_paths",
        nargs="*",
        help="Path of the Python file from which to parse dependencies, multiple paths can be specified",
    )
    parser.add_argument("-r", "--root_path", type=str, help="Specify the root path of the project")
    parser.add_argument(
        "-s", "--scope_paths", nargs="*", help="Specify paths of files to scope, multiple files can be specified"
    )
    parser.add_argument(
        "-i", "--ignore_paths", nargs="*", help="Specify paths of files to ignore, multiple files can be specified"
    )
    parser.add_argument("-d", "--depth", type=int, help="Specify depth of dependency analysis")
    # 出力先のパスを指定するオプションを追加
    parser.add_argument("-o", "--output", type=str, help="Specify the output destination")

    main_args: MainArgs = MainArgs(
        root_path=parser.parse_args().root_path or os.getcwd(),
        target_paths=parser.parse_args().target_paths,
        scope_paths=parser.parse_args().scope_paths,
        ignore_paths=parser.parse_args().ignore_paths,
        depth=parser.parse_args().depth,
    )
    create_class_diagram(
        root_path=main_args.root_path,
        target_paths=main_args.target_paths,
        scope_paths=main_args.scope_paths,
        ignore_paths=main_args.ignore_paths,
        depth=main_args.depth,
    )


if __name__ == "__main__":
    run_from_cli()
