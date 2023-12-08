import enum
import os


class ProgramType(enum.Enum):
    PYTHON = ['.py']
    JAVASCRIPT = ['.js', '.json', '.jsx', '.ts', '.tsx']
    UNKNOWN = ['']

    # 渡されたファイルのパスの拡張子からプログラムの種類を判定するメソッドを定義する
    @classmethod
    def get_program_type(cls, file_path: str) -> 'ProgramType':
        ext = os.path.splitext(file_path)[1]
        if ext in cls.PYTHON.value:
            return cls.PYTHON
        elif ext in cls.JAVASCRIPT.value:
            return cls.JAVASCRIPT
        else:
            return cls.UNKNOWN
