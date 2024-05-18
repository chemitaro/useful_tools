import inspect
from dataclasses import dataclass
from types import GenericAlias, UnionType
from typing import Any, get_type_hints

from apps.lib.utils import module_to_absolute_path, print_colored


@dataclass(frozen=True)
class BaseClassInfo:
    name: str
    module_name: str


@dataclass
class FieldTypeInfoIf:
    name: str
    module_name: str


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


class UnionInfo(FieldTypeInfoIf):
    element_types: list[FieldTypeInfoIf]

    def __init__(self, name: str, module_name: str, element_types: list[FieldTypeInfoIf]):
        self.name = name
        self.module_name = module_name
        self.element_types = element_types


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
    base_classes: list[BaseClassInfo]
    fields: list[FieldInfo]
    methods: list[MethodInfo]


class ClassDiagramGenerator:
    classes: list[type]
    root_path: str
    class_info: list[ClassInfo]

    def __init__(self, classes: list[type], root_path: str):
        self.classes = classes
        self.root_path = root_path

    def analyze(self) -> None:
        print_colored(("\n== Analyze Classes ==\n", "green"))
        # リフレッシュ
        self.class_info = []
        # クラス情報を取得
        for cls in self.classes:
            self.class_info.append(self._analyze_class(cls))

    def _analyze_class(self, cls: type) -> ClassInfo:
        class_name = cls.__name__
        module_name = self._get_module_name(cls)
        base_classes = self._analyze_base_classes(cls)
        fields = self._analyze_fields(cls)
        methods = self._analyze_methods(cls)
        return ClassInfo(class_name, module_name, base_classes, fields, methods)

    def _analyze_base_classes(self, cls: type) -> list[BaseClassInfo]:
        base_classes = []
        for base_class in cls.__bases__:
            # base_classがclassesに含まれている場合はmodule_nameを取得して追加
            if self._add_class_if_root_and_not_exists(base_class):
                base_class_name = base_class.__name__
                base_module_name = self._get_module_name(base_class)
                base_class_info = BaseClassInfo(base_class_name, base_module_name)
                base_classes.append(base_class_info)
        return base_classes

    def _analyze_fields(self, cls: type) -> list[FieldInfo]:
        fields_dict: dict[str, type] = {}

        # コンストラクタの引数を解析
        init_signature = inspect.signature(cls.__init__)
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

        # FieldInfoのリストに変換
        fields = []
        for name, type_ in fields_dict.items():
            try:
                field_type_info = self._type_to_field_type_info(type_)
                field_info = FieldInfo(name, field_type_info)
                fields.append(field_info)
            except Exception as e:
                print(f"{e}")

        return fields

    def _type_to_field_type_info(self, type_: Any) -> FieldTypeInfoIf:
        # オリジナルの型の場合
        if self._add_class_if_root_and_not_exists(type_):
            module_name = self._get_module_name(type_)
            return OriginalTypeInfo(type_.__name__, module_name)

        # リストの場合
        if isinstance(type_, GenericAlias) and type_.__origin__ == list:
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
            return OtherTypeInfo(name=other_name, module_name=other_module_name)

        # そもそも型でない場合は例外を発生させる
        raise Exception(f"Unexpected type: {type_}")

    def _analyze_methods(self, cls: type) -> list[MethodInfo]:
        methods = []
        for name, obj in inspect.getmembers(cls):
            if self._is_public_method_name(name) and callable(obj):
                signature = str(inspect.signature(obj))
                method_info = MethodInfo(name, signature)
                methods.append(method_info)

        return methods

    def generate_puml(self) -> str:
        puml = "@startuml class_diagram\n"
        puml += "set namespaceSeparator none\n"
        puml += "skinparam linetype polyline\n"
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
        class_type = "class"
        if class_info.name.endswith("If") or class_info.name.endswith("Mixin"):
            class_type = "interface"
        if class_info.name.startswith("Abstract"):
            class_type = "abstract"
        puml += f'{class_type} "{class_info.name}" as {class_info.module_name}.{class_info.name} {{\n'

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
            if base_class.name.endswith("If") or base_class.name.endswith("Mixin"):
                puml += f"{base_class.module_name}.{base_class.name} <|.. {class_info.module_name}.{class_info.name}\n"
            else:
                puml += f"{base_class.module_name}.{base_class.name} <|-- {class_info.module_name}.{class_info.name}\n"
        return puml

    # コンポジットの関係をpumlとして文字列として返す
    def _generate_composition_puml(self, class_info: ClassInfo) -> str:
        puml = ""
        for field_info in class_info.fields:
            field_type = field_info.type
            if isinstance(field_type, OriginalTypeInfo):
                puml += f"{class_info.module_name}.{class_info.name} *-- {field_type.module_name}.{field_type.name}\n"
            elif isinstance(field_type, ListInfo) and isinstance(field_type.element_type, OriginalTypeInfo):
                puml += f"{class_info.module_name}.{class_info.name} o-- {field_type.element_type.module_name}.{field_type.element_type.name}\n"
        return puml

    def _get_module_name(self, class_type: type) -> str:
        return class_type.__module__

    def _get_class_file_path(self, class_type: type) -> str:
        """クラスのファイルパスを取得する"""
        module_name = class_type.__module__
        absolute_path = module_to_absolute_path(module_name)
        return absolute_path

    def _is_public_method(self, method: MethodInfo) -> bool:
        # __init__, _  , __  で始まるメソッドは非公開
        if method.__name__ == "__init__":
            return True
        return not (method.__name__.startswith("_") or method.__name__.startswith("__"))

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
        if isinstance(cls, type) and self._is_root_path(cls):
            if not self._has_classes(cls):
                self.classes.append(cls)
            print_colored((f"  +Add Class: {cls.__name__}", "green"))
            return True
        return False
