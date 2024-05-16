import inspect
from dataclasses import dataclass
from typing import get_type_hints


@dataclass(frozen=True)
class BaseClassInfo:
    name: str
    module_name: str


@dataclass(frozen=True)
class TypeInfo:
    name: str
    module_name: str


@dataclass(frozen=True)
class FieldInfo:
    name: str
    type: TypeInfo
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
    class_info: list[ClassInfo]

    def __init__(self, classes: list[type]):
        self.classes = classes
        self.class_info: list[ClassInfo] = []

    def analyze(self) -> None:
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
            if base_class in self.classes:
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
            if name != "self":
                fields_dict[name] = param.annotation

        # クラスアノテーションを取得
        class_annotations = get_type_hints(cls)
        for name, type_ in class_annotations.items():
            fields_dict[name] = type_

        # FieldInfoのリストに変換
        fields = []
        for name, type_ in fields_dict.items():
            type_name = type_.__name__
            module_name = self._get_module_name(type_)
            field_info = FieldInfo(name, TypeInfo(type_name, module_name))
            fields.append(field_info)

        return fields

    def _analyze_methods(self, cls: type) -> list[MethodInfo]:
        methods = []
        for name, obj in inspect.getmembers(cls):
            if self._is_public_method_name(name) and callable(obj):
                print(name)
                print(obj)
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

        # 集約の関係を追加

        puml += "@enduml"
        return puml

    # クラス定義のpumlを文字列として返す
    def _generate_class_puml(self, class_info: ClassInfo) -> str:
        puml = f'class "{class_info.name}" as {class_info.module_name}.{class_info.name} {{\n'

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
            if field_info.type in [info.module_name for info in self.class_info]:
                puml += f"{class_info.module_name} *-- {field_info.type}\n"
        return puml

    # 集約の関係をpumlとして文字列として返す
    def _generate_aggregation_puml(self, class_info: ClassInfo) -> str:
        pass

    def _get_module_name(self, class_type: type) -> str:
        return class_type.__module__

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
