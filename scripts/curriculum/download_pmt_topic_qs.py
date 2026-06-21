#!/usr/bin/env python3
"""download_pmt_topic_qs.py —— 用 Python 批量下载 PMT by-topic 题库

URL 模式: https://pmt.physicsandmathstutor.com/download/Maths/A-level/C1/Topic-Qs/Edexcel-Set-1/<TOPIC>.pdf
(注: 不带 QP/MS 后缀,每个 topic 1 个 PDF 含题 + 答案)
"""

import sys
from pathlib import Path
import urllib.request
import urllib.error


SCRIPT_DIR = Path(__file__).parent
REPO_DIR = SCRIPT_DIR.parent.parent
OUT_BASE = REPO_DIR / "docs" / "curriculum" / "raw_pmt"


# Topic 列表(每个 unit + exam board)
TOPICS_BY_UNIT = {
    "C1_Edexcel_Set1": {
        "base_path": "Maths/A-level/C1/Topic-Qs/Edexcel-Set-1",
        "topics": [
            "C1 Algebra - Inequalities",
            "C1 Algebra - Quadratics",
            "C1 Algebra - Simultaneous equations",
            "C1 Algebra - Surds and indices",
            "C1 Coordinate geometry - Straight lines",
            "C1 Differentiation - Stationary points",
            "C1 Differentiation - Tangents and normals",
            "C1 Differentiation - basic differentiation",
            "C1 Functions - Transformation and graphs",
            "C1 Integration - Areas",
            "C1 Integration - Basic integration",
            "C1 Sequences and series - arithmetic series",
            "C1 Sequences and series - general",
        ],
        "output_dir": "P1_questions",
    },
    "C2_Edexcel_Set1": {
        "base_path": "Maths/A-level/C2/Topic-Qs/Edexcel-Set-1",
        "topics": [
            "C2  Algebra - Remainder and Factor Theorem",
            "C2  Coordinate geometry - Circles",
            "C2  Differentiation - Stationary points",
            "C2  Differentiation - Tangents and normals",
            "C2  Differentiation - basic differentiation",
            "C2  Exponentials & Logs - Laws of logs",
            "C2  Exponentials and logs - Exponential equations",
            "C2  Integration - areas",
            "C2  Integration - basic integration",
            "C2  Sequences and series - Binomial expansion",
            "C2  Sequences and series - Geometric series",
            "C2  Trigonometry - Arc length and sector area",
            "C2  Trigonometry - Sine and cosine rule",
            "C2  Trigonometry - Trigonometric equations",
            "C2  Trigonometry - Trigonometric graphs",
            "C2  Trigonometry - Trigonometric identities",
        ],
        "output_dir": "P2_questions",
    },
    "C3_Edexcel_Set1": {
        "base_path": "Maths/A-level/C3/Topic-Qs/Edexcel-Set-1",
        "topics": [
            "C3 Algebra - Quadratics",
            "C3 Algebra - Rational Functions",
            "C3 Differentiation - Basic differentiation",
            "C3 Differentiation - Chain rule",
            "C3 Differentiation - Implicit differentiation",
            "C3 Differentiation - Products and quotients",
            "C3 Differentiation - Stationary points",
            "C3 Differentiation - Tangents and normals",
            "C3 Exponentials and logarithms - Exponential equations",
            "C3 Exponentials and logarithms - Graphs of exponentials and logs",
            "C3 Exponentials and logarithms - Laws of logs",
            "C3 Functions - Modulus Functions",
            "C3 Functions - Transformations and graphs",
            "C3 Integration - Areas",
            "C3 Integration - Basic integration",
            "C3 Integration - By parts",
            "C3 Integration - By substitution",
            "C3 Numerical Methods - Iterative equations",
            "C3 Numerical Methods - Location of roots",
            "C3 Numerical Methods - Trapezium rule",
            "C3 Sequences and series - Geometric series",
            "C3 Trigonometry - Trigonometric equations",
            "C3 Trigonometry - Trigonometric formulae",
            "C3 Trigonometry - Trigonometric graphs",
            "C3 Trigonometry - Trigonometric identities",
        ],
        "output_dir": "P3_questions",
    },
    "C4_Edexcel_Set1": {
        "base_path": "Maths/A-level/C4/Topic-Qs/Edexcel-Set-1",
        "topics": [
            "C4 Algebra - Partial fractions",
            "C4 Coordinate geometry - Parametric curves",
            "C4 Differential equations - first order",
            "C4 Differentiation - Implicit differentiation",
            "C4 Differentiation - Parametric differentiation",
            "C4 Differentiation - Products and quotients",
            "C4 Differentiation - Rates of change",
            "C4 Differentiation - Stationary points",
            "C4 Differentiation - Tangents and normals",
            "C4 Integration - Areas",
            "C4 Integration - Basic integration",
            "C4 Integration - By parts",
            "C4 Integration - By substitution",
            "C4 Integration - Using partial fractions",
            "C4 Integration - Volumes",
            "C4 Numerical Methods - Trapezium rule",
            "C4 Sequences and series - Binomial series",
            "C4 Sequences and series - Maclaurin series",
            "C4 Sequences and series - general",
            "C4 Trigonomnetry - Trigonometrical formulae and equations",
            "C4 Trigonomnetry - Trigonometrical identities",
            "C4 Vectors - Scalar products",
            "C4 Vectors - Vector lines",
        ],
        "output_dir": "P4_questions",
    },
    "M1_Edexcel_Set1": {
        "base_path": "Maths/A-level/M1/Topic-Qs/Edexcel-Set-1",
        "topics": [
            "M1 Collisions - Direct impact",
            "M1 Collisions",
            "M1 Dynamics - Analysis of force systems",
            "M1 Dynamics - Connected particles",
            "M1 Dynamics - F = ma horizontally",
            "M1 Dynamics - F = ma on a slope",
            "M1 Dynamics - Momentum and impulse",
            "M1 Dynamics",
            "M1 Kinematics - Problems with vectors",
            "M1 Kinematics - Projectiles",
            "M1 Kinematics - Uniform acceleration formulae",
            "M1 Kinematics - by graphical methods",
            "M1 Kinematics",
            "M1 Modelling",
            "M1 Moments - Moments about a point",
            "M1 Moments",
            "M1 Statics - Equilibrium problems",
            "M1 Statics",
        ],
        "output_dir": "M1_questions",
    },
    "S1_Edexcel_Set1": {
        "base_path": "Maths/A-level/S1/Topic-Qs/Edexcel-Set-1",
        "topics": [
            "S1 Correlation and regression - PMCC",
            "S1 Correlation and regression - Regression",
            "S1 Correlation and regression",
            "S1 Discrete distributions",
            "S1 Discrete random variables",
            "S1 Modelling",
            "S1 Normal distribution",
            "S1 Probability",
            "S1 Representation and summary data",
            "S1 Sampling methods",
        ],
        "output_dir": "S1_questions",
    },
}


def download(url: str, dest: Path) -> bool:
    """下载 URL 到 dest,返回是否成功(自动 quote 空格)"""
    from urllib.parse import quote
    safe_url = quote(url, safe=":/?&=")
    try:
        req = urllib.request.Request(safe_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if len(data) < 100:
                return False
            dest.write_bytes(data)
            return True
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"  [ERROR] {safe_url}: {e}")
        return False
    except Exception as e:
        print(f"  [ERROR] {safe_url}: {type(e).__name__}: {e}")
        return False


def main():
    if len(sys.argv) > 1:
        unit_filter = sys.argv[1]
    else:
        unit_filter = "all"

    ok = 0
    fail = 0
    for unit_key, config in TOPICS_BY_UNIT.items():
        if unit_filter not in ("all", unit_key):
            continue

        out_dir = OUT_BASE / config["output_dir"]
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n=== {unit_key} ===")
        print(f"  Output: {out_dir}")
        print(f"  Topics: {len(config['topics'])}")

        for topic in config["topics"]:
            # 真实 URL 没有 QP/MS 后缀
            url = f"https://pmt.physicsandmathstutor.com/download/{config['base_path']}/{topic}.pdf"
            safe = topic.replace(" ", "_").replace("/", "_")
            dest = out_dir / f"Edexcel_{safe}.pdf"

            if dest.exists() and dest.stat().st_size > 100:
                ok += 1
                continue

            print(f"  [get] {dest.name}", end="")
            if download(url, dest):
                print(f" ✓ ({dest.stat().st_size // 1024}KB)")
                ok += 1
            else:
                print(" ✗")
                fail += 1
                if dest.exists():
                    dest.unlink()

    print(f"\n=== 总计: {ok} 成功, {fail} 失败 ===")


if __name__ == "__main__":
    main()
