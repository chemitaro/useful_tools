import inspect
import os
import re
from dataclasses import dataclass
from enum import Enum
from types import GenericAlias, UnionType
from typing import Any, Protocol, Self, get_type_hints

from apps.lib.utils import module_to_absolute_path, print_colored


class ClassType(Enum):
    CLASS = "class"
    ENTITY = "entity"
    INTERFACE = "interface"
    ABSTRACT = "abstract"
    ENUM = "enum"
    EXCEPTION = "exception"


class MethodDisplayType(Enum):
    HIDE = "hide"  # メソッドを非表示
    DEFINED = "defined"  # 定義されたメソッドのみを表示
    ALL = "all"  # 全てのメソッドを表示


@dataclass(frozen=True)
class BaseClassInfo:
    name: str
    module_name: str
    class_type: ClassType


@dataclass
class FieldTypeInfoIf:
    name: str
    module_name: str
    class_type: ClassType


class OriginalTypeInfo(FieldTypeInfoIf):
    pass


class OtherTypeInfo(FieldTypeInfoIf):
    pass


class ListInfo(FieldTypeInfoIf):
    element_type: FieldTypeInfoIf

    def __init__(self, name: str, module_name: str, element_type: FieldTypeInfoIf):
        self.name = name
        self.module_name = module_name
        self.element_type = element_type
        self.class_type = ClassType.CLASS


class UnionInfo(FieldTypeInfoIf):
    element_types: list[FieldTypeInfoIf]

    def __init__(self, name: str, module_name: str, element_types: list[FieldTypeInfoIf]):
        self.name = name
        self.module_name = module_name
        self.element_types = element_types
        self.class_type = ClassType.CLASS


@dataclass(frozen=True)
class FieldInfo:
    name: str
    type: FieldTypeInfoIf
    is_public: bool = True


@dataclass(frozen=True)
class MethodInfo:
    name: str
    signature: str
    is_public: bool = True


@dataclass(frozen=True)
class ClassInfo:
    name: str
    module_name: str
    class_type: ClassType
    base_classes: list[BaseClassInfo]
    fields: list[FieldInfo]
    methods: list[MethodInfo]


class ClassDiagramGenerator:
    classes: list[type]
    root_path: str
    ignore_paths: list[str]
    class_info: list[ClassInfo]
    method_display_type: MethodDisplayType

    def __init__(
        self, classes: list[type], root_path: str, ignore_paths: list[str], method_display_type: MethodDisplayType
    ):
        self.classes = classes
        self.root_path = root_path
        self.ignore_paths = ignore_paths
        self.method_display_type = method_display_type

    @classmethod
    def create(
        cls,
        classes: list[type],
        root_path: str,
        ignore_paths: list[str] | None = None,
        method_display_type: str | None = None,
    ) -> Self:
        # メソッド表示タイプが指定されていない場合はデフォルト値を設定
        if method_display_type is None:
            method_display_type = "defined"

        # ignore_pathsが指定されていない場合は空リストを設定
        if ignore_paths is None:
            ignore_paths = []

        # ignore_pathsが相対パスの場合は,絶対パスに変換する
        absolute_ignore_paths = []
        for ignore_path in ignore_paths:
            if not os.path.isabs(ignore_path):
                absolute_ignore_paths.append(os.path.join(root_path, ignore_path))
            else:
                absolute_ignore_paths.append(ignore_path)

        return cls(
            classes=classes,
            root_path=root_path,
            ignore_paths=absolute_ignore_paths,
            method_display_type=MethodDisplayType(method_display_type),
        )

    def analyze(self) -> None:
        print_colored(("\n== Analyze Classes ==\n", "green"))
        # リフレッシュ
        self.class_info = []
        # クラス情報を取得
        for cls in self.classes:
            class_info = self._analyze_class(cls)
            self.class_info.append(class_info)

    def _analyze_class(self, cls: type) -> ClassInfo:
        """
        クラスを解析してClassInfoを返す
        """
        print_colored((f"Analyzing: {cls.__name__}", "blue"))
        class_name = cls.__name__
        module_name = self._get_module_name(cls)
        class_type = self._analyze_class_type(cls)
        base_classes = self._analyze_base_classes(cls)
        if class_type == ClassType.ENUM:
            fields = self._analyze_enum_members(cls)
        else:
            fields = self._analyze_fields(cls)
        methods = self._analyze_methods(cls)
        return ClassInfo(class_name, module_name, class_type, base_classes, fields, methods)

    def _analyze_class_type(self, cls: type) -> ClassType:
        class_name = cls.__name__
        if class_name.endswith("If"):
            return ClassType.INTERFACE
        elif Protocol in cls.__bases__:
            return ClassType.INTERFACE
        elif class_name.startswith("Abstract"):
            return ClassType.ABSTRACT
        elif class_name.endswith("Mixin"):
            return ClassType.ABSTRACT
        elif issubclass(cls, Enum):
            return ClassType.ENUM
        elif issubclass(cls, Exception):
            return ClassType.EXCEPTION
        elif class_name.endswith("Entity"):
            return ClassType.ENTITY
        else:
            return ClassType.CLASS

    def _analyze_base_classes(self, cls: type) -> list[BaseClassInfo]:
        base_classes = []
        for base_class in cls.__bases__:
            # base_classがclassesに含まれている場合はmodule_nameを取得して追加
            is_add_class = self._add_class_if_root_and_not_exists(base_class)
            if is_add_class:
                base_class_name = base_class.__name__
                base_module_name = self._get_module_name(base_class)
                base_class_type = self._analyze_class_type(base_class)
                base_class_info = BaseClassInfo(base_class_name, base_module_name, base_class_type)
                base_classes.append(base_class_info)
        return base_classes

    def _analyze_fields(self, cls: type) -> list[FieldInfo]:
        fields_dict: dict[str, type] = {}

        # コンストラクタの引数を解析
        try:
            init_signature = inspect.signature(cls.__init__)  # type: ignore
            for name, param in init_signature.parameters.items():
                # self, cls, 及び、可変長引数は除外
                if name in ["self", "cls", "*"]:
                    continue

                field_type = param.annotation
                fields_dict[name] = field_type

            # クラスアノテーションを取得
            class_annotations = get_type_hints(cls)
            for name, type_ in class_annotations.items():
                fields_dict[name] = type_
        except Exception as e:
            print(f"{e}")

        # FieldInfoのリストに変換
        fields = []
        for name, type_ in fields_dict.items():
            try:
                field_type_info = self._type_to_field_type_info(type_)
                field_info = FieldInfo(name, field_type_info)
                fields.append(field_info)
            except Exception:
                continue

        return fields

    def _analyze_enum_members(self, cls: type) -> list[FieldInfo]:
        """列挙型のメンバーを解析する"""
        if not issubclass(cls, Enum):
            raise Exception(f"{cls.__name__} is not an Enum")

        fields = []
        for name, member in cls.__members__.items():
            field_type_info = self._type_to_field_type_info(type(member.value))
            field_info = FieldInfo(name, field_type_info)
            fields.append(field_info)
        return fields

    def _type_to_field_type_info(self, type_: Any) -> FieldTypeInfoIf:
        # オリジナルの型の場合
        if self._add_class_if_root_and_not_exists(type_):
            module_name = self._get_module_name(type_)
            class_type = self._analyze_class_type(type_)
            return OriginalTypeInfo(type_.__name__, module_name, class_type)

        # リストの場合
        if isinstance(type_, GenericAlias) and isinstance(type_.__origin__, type(list)):
            element_type = self._type_to_field_type_info(type_.__args__[0])
            list_name = type_.__name__
            list_module_name = self._get_module_name(type_)
            return ListInfo(name=list_name, module_name=list_module_name, element_type=element_type)

        # ユニオンの場合
        if isinstance(type_, UnionType):
            element_types: list[FieldTypeInfoIf] = []
            for element_type in type_.__args__:
                element_type_info = self._type_to_field_type_info(element_type)
                element_types.append(element_type_info)
            # element_types の name を取得して | で結合した文字列を name にする
            union_name = " | ".join([element_type.name for element_type in element_types])
            union_module_name = self._get_module_name(type_)
            return UnionInfo(name=union_name, module_name=union_module_name, element_types=element_types)

        # その他の型の場合
        if isinstance(type_, type):
            other_name = type_.__name__
            other_module_name = self._get_module_name(type_)
            other_class_type = self._analyze_class_type(type_)
            return OtherTypeInfo(name=other_name, module_name=other_module_name, class_type=other_class_type)

        # そもそも型でない場合は例外を発生させる
        raise Exception(f"Unexpected type: {type_}")

    def _analyze_methods(self, cls: type) -> list[MethodInfo]:
        if self.method_display_type == MethodDisplayType.HIDE:
            return []
        elif self.method_display_type == MethodDisplayType.DEFINED:
            return self._analyze_defined_methods(cls)
        elif self.method_display_type == MethodDisplayType.ALL:
            return self._analyze_all_methods(cls)
        else:
            return []

    def _analyze_defined_methods(self, cls: type) -> list[MethodInfo]:
        methods = []
        for name, obj in inspect.getmembers(cls):
            if inspect.isfunction(obj) and obj.__qualname__.startswith(cls.__name__):
                # パブリックメソッド以外はスキップ
                if not self._is_public_method_name(name):
                    continue
                signature = str(inspect.signature(obj))
                method_info = MethodInfo(name, signature)
                methods.append(method_info)

        return methods

    def _analyze_all_methods(self, cls: type) -> list[MethodInfo]:
        methods = []
        for name, obj in inspect.getmembers(cls):
            if inspect.isfunction(obj):
                # パブリックメソッド以外はスキップ
                if not self._is_public_method_name(name):
                    continue
                signature = str(inspect.signature(obj))
                method_info = MethodInfo(name, signature)
                methods.append(method_info)

        return methods

    def generate_puml(self) -> str:
        puml = "@startuml class_diagram\n"
        puml += "set namespaceSeparator none\n"
        puml += "skinparam linetype ortho\n"
        puml += "' skinparam linetype polyline\n"
        puml += "' skinparam linetype splines\n"
        puml += "\n"

        # クラス定義を追加
        for class_info in self.class_info:
            puml += self._generate_class_puml(class_info)
        puml += "\n"

        # 継承関係を追加
        for class_info in self.class_info:
            puml += self._generate_inheritance_puml(class_info)
        puml += "\n"

        # コンポジットの関係を追加
        for class_info in self.class_info:
            puml += self._generate_composition_puml(class_info)
        puml += "\n"

        puml += "@enduml"
        return puml

    # クラス定義のpumlを文字列として返す
    def _generate_class_puml(self, class_info: ClassInfo) -> str:
        puml = ""
        class_type = class_info.class_type.value
        class_name = self._format_class_name(class_info.name)

        puml += f'{class_type} "{class_name}" as {class_info.module_name}.{class_info.name} {{\n'

        # フィールドを定義を追加
        for field in class_info.fields:
            puml += self._generate_field_puml(field)

        # メソッドを定義を追加
        for method in class_info.methods:
            puml += self._generate_method_puml(method)

        # クラス定義を返す
        puml += "}\n\n"
        return puml

    # フィールドのpumlを文字列として返す
    def _generate_field_puml(self, field_info: FieldInfo) -> str:
        if field_info.is_public:
            return f"  +{field_info.name}: {field_info.type.name}\n"
        else:
            return f"  -{field_info.name}: {field_info.type.name}\n"

    # メソッドのpumlを文字列として返す
    def _generate_method_puml(self, method_info: MethodInfo) -> str:
        if method_info.is_public:
            return f"  +{method_info.name}()\n"
        else:
            return f"  -{method_info.name}()\n"

    # 継承関係のpumlを文字列として返す
    def _generate_inheritance_puml(self, class_info: ClassInfo) -> str:
        puml = ""
        for base_class in class_info.base_classes:
            # インターフェイスの場合は継承関係を点線で表現
            base_class_name = self._format_class_name(base_class.name)
            if base_class.class_type == ClassType.INTERFACE:
                puml += f"{base_class.module_name}.{base_class_name} <|.. {class_info.module_name}.{class_info.name}\n"
            elif base_class.class_type == ClassType.ABSTRACT:
                puml += f"{base_class.module_name}.{base_class_name} <|.. {class_info.module_name}.{class_info.name} #AAAAAA\n"
            else:
                puml += f"{base_class.module_name}.{base_class_name} <|-- {class_info.module_name}.{class_info.name}\n"
        return puml

    # コンポジットの関係をpumlとして文字列として返す
    def _generate_composition_puml(self, class_info: ClassInfo) -> str:
        relation: list[str] = []
        for field_info in class_info.fields:
            field_type = field_info.type
            if isinstance(field_type, OriginalTypeInfo):
                relation.append(
                    f'{class_info.module_name}.{class_info.name} *-- "1" {field_type.module_name}.{field_type.name}'
                )
            elif isinstance(field_type, ListInfo) and isinstance(field_type.element_type, OriginalTypeInfo):
                relation.append(
                    f'{class_info.module_name}.{class_info.name} o-- "0..*" {field_type.element_type.module_name}.{field_type.element_type.name}'
                )
            elif isinstance(field_type, UnionInfo):
                for element_type in field_type.element_types:
                    if isinstance(element_type, OriginalTypeInfo):
                        relation.append(
                            f'{class_info.module_name}.{class_info.name} o-- "0..*" {element_type.module_name}.{element_type.name}'
                        )
        # 重複を削除
        relation = list(set(relation))
        # 文字列で結合
        puml = "\n".join(relation)
        puml += "\n"
        return puml

    def _get_module_name(self, class_type: Any) -> str:
        try:
            return class_type.__module__
        except Exception as e:
            print(f"{e}")
            return ""

    # 外部から動的に取り込んだクラスのファイルパスを取得する
    def _get_imported_class_file_path(self, class_type: type) -> str:
        module_name = class_type.__module__
        file_path = module_to_absolute_path(module_name)
        return file_path

    # 内部的に取得したクラスのファイルパスを取得する
    def _get_internal_class_file_path(self, class_type: type) -> str:
        file_path = inspect.getfile(class_type)

        # 絶対パスに変換
        absolute_path = os.path.abspath(file_path)
        return absolute_path

    def _get_class_file_path(self, class_type: type) -> str:
        """クラスのファイルパスを取得する"""
        try:
            return self._get_internal_class_file_path(class_type)
        except Exception:
            return self._get_imported_class_file_path(class_type)

    def _is_public_method(self, method: MethodInfo) -> bool:
        # __init__, _  , __  で始まるメソッドは非公開
        try:
            method_name = method.name
            if method_name == "__init__":
                return True
            return not (method_name.startswith("_") or method_name.startswith("__"))
        except Exception as e:
            print(f"{e}")
            return False

    def _is_public_method_name(self, method_name: str) -> bool:
        # __init__, _  , __  で始まるメソッドは非公開
        if method_name == "__init__":
            return True
        if method_name.startswith("_") or method_name.startswith("__"):
            return False
        return True

    def _is_root_path(self, cls: Any) -> bool:
        """クラスがルートモジュールに属しているかどうかを返す"""
        try:
            path = self._get_class_file_path(cls)
            return path.startswith(self.root_path)
        except Exception as e:
            print(f"{e}")
            return False

    def _is_ignore_path(self, cls: Any) -> bool:
        """クラスが無視するパスに属しているかどうかを返す"""
        try:
            path = self._get_class_file_path(cls)
            for ignore_path in self.ignore_paths:
                if path.startswith(ignore_path):
                    return True
            return False
        except Exception as e:
            print(f"{e}")
            return False

    def _has_classes(self, cls: Any) -> bool:
        """指定したクラスがclassesに含まれているかどうかを返す"""
        return cls in self.classes

    def _add_class_if_root_and_not_exists(self, cls: Any) -> bool:
        """
        クラスがルートモジュールに属しているかどうかをboolで返す。
        そして、classesに含まれていない場合はclassesに追加する。

        Args:
            cls (type): チェックするクラス

        Returns:
            bool: クラスがルートモジュールに属しているかどうか
        """
        # 既にclassesに含まれている場合はTrueを返す
        if cls in self.classes:
            return True

        # ルートモジュールに属しているかどうかをチェック
        if isinstance(cls, type) and self._is_root_path(cls) and self._is_ignore_path(cls) is False:
            return True

        return False

    # クラス名をpumlのフォーマットで整形する
    def _format_class_name(self, class_name: str) -> str:
        # [] で囲まれた部分を削除
        class_name = re.sub(r"\[.*?\]", "", class_name)

        return class_name
