from dataclasses import dataclass
import inspect
from typing import Dict, List, Type


@dataclass(frozen=True)
class ClassInfo:
    name: str
    module_name: str
    base_classes: List[str]
    fields: List["FieldInfo"]
    methods: List["MethodInfo"]

@dataclass(frozen=True)
class FieldInfo:
    name: str
    type: str
    visibility: str

@dataclass(frozen=True)
class MethodInfo:
    name: str
    parameters: List["ParameterInfo"]
    return_type: str
    visibility: str

@dataclass(frozen=True)
class ParameterInfo:
    name: str
    type: str


class ClassDiagramGenerator:
    def __init__(self, classes: List[Type]):
        self.classes = classes
        self.class_info: Dict[str, ClassInfo] = {}

    def analyze_classes(self) -> None:
        for cls in self.classes:
            class_name = cls.__name__
            module_name = self.get_module_name(cls)
            base_classes = [self.get_module_name(base) for base in cls.__bases__]
            fields = self.analyze_fields(cls)
            methods = self.analyze_methods(cls)

            class_info = ClassInfo(class_name, module_name, base_classes, fields, methods)
            self.class_info[f"{module_name}.{class_name}"] = class_info

    def analyze_fields(self, cls: Type) -> List["FieldInfo"]:
        fields = []
        for name, obj in inspect.getmembers(cls):
            if isinstance(obj, property):
                fields.append(FieldInfo(name, str(obj.fget.__annotations__.get("return", "")), "public"))
            elif not callable(obj) and not name.startswith("__"):
                fields.append(FieldInfo(name, str(type(obj).__name__), "public"))
        return fields

    def analyze_methods(self, cls: Type) -> List["MethodInfo"]:
        methods = []
        for name, obj in inspect.getmembers(cls, predicate=inspect.isfunction):
            if not name.startswith("__") or name in ("__init__", "__str__", "__repr__"):
                parameters = [
                    ParameterInfo(param.name, str(param.annotation))
                    for param in inspect.signature(obj).parameters.values()
                ]
                return_type = str(inspect.signature(obj).return_annotation)
                visibility = "public" if self.is_public_method(obj) else "private"
                methods.append(MethodInfo(name, parameters, return_type, visibility))
        return methods

    def generate_puml(self) -> str:
        puml = "@startuml\n"
        for class_info in self.class_info.values():
            puml += f"class \"{class_info.name}\" as {class_info.module_name}.{class_info.name} {{\n"
            for field in class_info.fields:
                puml += f"  {field.visibility} {field.name}: {field.type}\n"
            for method in class_info.methods:
                params = ", ".join(f"{param.name}: {param.type}" for param in method.parameters)
                puml += f"  {method.visibility} {method.name}({params}): {method.return_type}\n"
            puml += "}\n"
        for class_info in self.class_info.values():
            for base_class in class_info.base_classes:
                puml += f"{class_info.module_name}.{class_info.name} --|> {base_class}\n"
        puml += "@enduml\n"
        return puml

    def get_module_name(self, class_type: Type) -> str:
        return class_type.__module__

    def is_public_method(self, method: MethodInfo) -> bool:
        return not method.name.startswith("_")
