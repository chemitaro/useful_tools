import inspect
from dataclasses import dataclass


@dataclass(frozen=True)
class ClassInfo:
    name: str
    module_name: str
    base_classes: list[str]
    fields: list["FieldInfo"]
    methods: list["MethodInfo"]


@dataclass(frozen=True)
class FieldInfo:
    name: str
    type: str
    visibility: str


@dataclass(frozen=True)
class MethodInfo:
    name: str
    signature: str


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

    def _analyze_base_classes(self, cls: type) -> list[str]:
        base_classes = []
        for base_class in cls.__bases__:
            # base_classがclassesに含まれている場合はmodule_nameを取得して追加
            if self._get_module_name(base_class) in self.class_info:
                base_classes.append(self._get_module_name(base_class))
        return base_classes

    def _analyze_fields(self, cls: type) -> list["FieldInfo"]:
        fields = []
        for name, obj in inspect.getmembers(cls):
            if isinstance(obj, property):
                fields.append(FieldInfo(name, str(obj.fget.__annotations__.get("return", "")), "public"))
            elif not callable(obj) and not name.startswith("__"):
                fields.append(FieldInfo(name, str(type(obj).__name__), "public"))
        return fields

    def _analyze_methods(self, cls: type) -> list["MethodInfo"]:
        methods = []
        for name, obj in inspect.getmembers(cls):
            if self._is_public_method_name(name) and callable(obj):
                print(name)
                print(obj)
                signature = str(inspect.signature(obj))
                method_info = MethodInfo(name, signature)
                methods.append(method_info)

    def generate_puml(self) -> str:
        puml = "@startuml\n"
        # クラス定義を追加

        # 継承関係を追加

        # コンポジットの関係を追加

        # 集約の関係を追加

        puml += "@enduml"
        return puml

    # クラス定義のpumlを文字列として返す
    def _generate_class_puml(self, class_info: ClassInfo) -> str:
        # クラス名を定義

        # フィールドを定義を追加

        # メソッドを定義を追加

        # クラス定義を返す
        pass

    # フィールドのpumlを文字列として返す
    def _generate_field_puml(self, field_info: FieldInfo) -> str:
        pass

    # メソッドのpumlを文字列として返す
    def _generate_method_puml(self, method_info: MethodInfo) -> str:
        pass

    # 継承関係のpumlを文字列として返す
    def _generate_inheritance_puml(self, class_info: ClassInfo) -> str:
        pass

    # コンポジットの関係をpumlとして文字列として返す
    def _generate_composition_puml(self, class_info: ClassInfo) -> str:
        pass

    # 集約の関係をpumlとして文字列として返す
    def _generate_aggregation_puml(self, class_info: ClassInfo) -> str:
        pass

    def _get_module_name(self, class_type: type) -> str:
        return f"{class_type.__module__}.{class_type.__name__}"

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
