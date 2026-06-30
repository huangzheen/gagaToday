"""
Pytest 配置:让 `poi-generator` (目录名,带 dash) 能被 `poi_generator` (Python 模块名,带下划线) 找到。

项目里 uvicorn 用 `uvicorn backend.poi-generator.main:app` 启动,目录名带 dash 是历史原因。
Python 标识符不能含 dash,所以 import 必须用 `poi_generator`。

测试代码统一用 `from poi_generator.schemas import ...`。
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "poi-generator"))

# 现在 poi-generator 目录已经在 sys.path,可以直接用 sys.modules 别名让 `poi_generator` 解析到它
import importlib
import importlib.util
import types


def _setup_poi_generator_alias() -> None:
    if "poi_generator" in sys.modules:
        return
    pkg_path = BACKEND_DIR / "poi-generator"
    pkg = types.ModuleType("poi_generator")
    pkg.__path__ = [str(pkg_path)]
    pkg.__file__ = str(pkg_path / "__init__.py")
    sys.modules["poi_generator"] = pkg


_setup_poi_generator_alias()