#!/usr/bin/env python3
"""
pmt_to_yaml.py —— 把 PMT PDF 笔记批量转成 learning_paths YAML

输入: docs/curriculum/raw_pmt/ 下的 PMT 提取的 .txt 文件
输出: docs/curriculum/learning_paths/ 下的 .yaml 文件

映射规则:
  GCE C1 (WMA01/01) → IAL P1 (WMA11/01)  §1-5 内容
  GCE C2 (WMA02/01) → IAL P1 §6 (Trig) + IAL P2 (WMA12/01) 大部分
  GCE C3 (WMA03/01) → IAL P2 进阶 + IAL P3 (WMA13/01)
  GCE C4 (WMA04/01) → IAL P3 进阶 + IAL P4 (WMA14/01)
  GCE M1 (WME01/01) → IAL M1 (WME01/01) - 几乎一样
  GCE S1 (WST01/01) → IAL S1 (WST01/01) - 几乎一样

注意: 2018 改革后,IAL 单元改叫 Pure 1-4,代码 WMA11-14。
       PMT 笔记标题是 "Pure Core 1-4" (GCE 旧名,2016 版),
       内容大纲基本相同(IAL 2018 改革 = GCE 2017 改革)。

用法:
  python3 pmt_to_yaml.py --unit c1           # 只转 C1
  python3 pmt_to_yaml.py --unit all          # 转所有 C1+C2+C3+C4+M1+S1
  python3 pmt_to_yaml.py --output learning_paths/from_pmt_c1.yaml
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


# ============== Configuration ==============

SCRIPT_DIR = Path(__file__).parent
REPO_DIR = SCRIPT_DIR.parent.parent
RAW_PMT_DIR = REPO_DIR / "docs" / "curriculum" / "raw_pmt"
OUTPUT_DIR = REPO_DIR / "docs" / "curriculum" / "learning_paths"


# 章节定义: 章节名 -> (PMT 笔记 file, 起始 regex, 结束 regex, KP topic 标签)
# KP topic 标签对应 IAL Pure 1-4 + M1 + S1 的官方 topic

# 关联 lesson -> PMT by-topic 题集(exercises 字段)
# lesson_id (key) -> 相对 raw_pmt/ 的题集 PDF 路径
EXERCISES = {
    # C1 lesson -> C1 by-topic 题集
    "c1-algebra-indices":        ["P1_questions/Edexcel_C1_Algebra_-_Surds_and_indices.pdf"],
    "c1-algebra-surds":          ["P1_questions/Edexcel_C1_Algebra_-_Surds_and_indices.pdf"],
    "c1-quadratics":              ["P1_questions/Edexcel_C1_Algebra_-_Quadratics.pdf"],
    "c1-simultaneous-inequalities": [
        "P1_questions/Edexcel_C1_Algebra_-_Inequalities.pdf",
        "P1_questions/Edexcel_C1_Algebra_-_Simultaneous_equations.pdf",
    ],
    "c1-coordinate-geometry":     ["P1_questions/Edexcel_C1_Coordinate_geometry_-_Straight_lines.pdf"],
    "c1-sequences":               ["P1_questions/Edexcel_C1_Sequences_and_series_-_arithmetic_series.pdf",
                                  "P1_questions/Edexcel_C1_Sequences_and_series_-_general.pdf"],
    "c1-curve-sketching":         ["P1_questions/Edexcel_C1_Functions_-_Transformation_and_graphs.pdf"],
    "c1-differentiation":         ["P1_questions/Edexcel_C1_Differentiation_-_basic_differentiation.pdf",
                                  "P1_questions/Edexcel_C1_Differentiation_-_Tangents_and_normals.pdf",
                                  "P1_questions/Edexcel_C1_Differentiation_-_Stationary_points.pdf"],
    "c1-integration":             ["P1_questions/Edexcel_C1_Integration_-_Basic_integration.pdf",
                                  "P1_questions/Edexcel_C1_Integration_-_Areas.pdf"],

    # C2 lesson -> C2 by-topic 题集
    "c2-algebra-polynomials":     ["P2_questions/Edexcel_C2__Algebra_-_Remainder_and_Factor_Theorem.pdf"],
    "c2-trigonometry":            ["P2_questions/Edexcel_C2__Trigonometry_-_Sine_and_cosine_rule.pdf",
                                  "P2_questions/Edexcel_C2__Trigonometry_-_Arc_length_and_sector_area.pdf",
                                  "P2_questions/Edexcel_C2__Trigonometry_-_Trigonometric_identities.pdf",
                                  "P2_questions/Edexcel_C2__Trigonometry_-_Trigonometric_equations.pdf",
                                  "P2_questions/Edexcel_C2__Trigonometry_-_Trigonometric_graphs.pdf"],
    "c2-coordinate-geometry-circles": ["P2_questions/Edexcel_C2__Coordinate_geometry_-_Circles.pdf"],
    "c2-sequences-binomial":      ["P2_questions/Edexcel_C2__Sequences_and_series_-_Binomial_expansion.pdf",
                                  "P2_questions/Edexcel_C2__Sequences_and_series_-_Geometric_series.pdf"],
    "c2-exponentials-logs":       ["P2_questions/Edexcel_C2__Exponentials_and_logs_-_Exponential_equations.pdf",
                                  "P2_questions/Edexcel_C2__Exponentials_&_Logs_-_Laws_of_logs.pdf"],
    "c2-differentiation-advanced": ["P2_questions/Edexcel_C2__Differentiation_-_basic_differentiation.pdf",
                                   "P2_questions/Edexcel_C2__Differentiation_-_Tangents_and_normals.pdf",
                                   "P2_questions/Edexcel_C2__Differentiation_-_Stationary_points.pdf"],
    "c2-integration-advanced":    ["P2_questions/Edexcel_C2__Integration_-_basic_integration.pdf",
                                  "P2_questions/Edexcel_C2__Integration_-_areas.pdf"],

    # ========== C3 lesson -> C3 by-topic 题集 ==========
    "c3-algebra-functions":       ["P3_questions/Edexcel_C3_Algebra_-_Quadratics.pdf",
                                  "P3_questions/Edexcel_C3_Algebra_-_Rational_Functions.pdf"],
    "c3-trig-advanced":          ["P3_questions/Edexcel_C3_Trigonometry_-_Trigonometric_identities.pdf",
                                  "P3_questions/Edexcel_C3_Trigonometry_-_Trigonometric_formulae.pdf",
                                  "P3_questions/Edexcel_C3_Trigonometry_-_Trigonometric_equations.pdf",
                                  "P3_questions/Edexcel_C3_Trigonometry_-_Trigonometric_graphs.pdf"],
    "c3-exponentials-logs":       ["P3_questions/Edexcel_C3_Exponentials_and_logarithms_-_Exponential_equations.pdf",
                                  "P3_questions/Edexcel_C3_Exponentials_and_logarithms_-_Graphs_of_exponentials_and_logs.pdf",
                                  "P3_questions/Edexcel_C3_Exponentials_and_logarithms_-_Laws_of_logs.pdf"],
    "c3-differentiation":         ["P3_questions/Edexcel_C3_Differentiation_-_Basic_differentiation.pdf",
                                  "P3_questions/Edexcel_C3_Differentiation_-_Chain_rule.pdf",
                                  "P3_questions/Edexcel_C3_Differentiation_-_Implicit_differentiation.pdf",
                                  "P3_questions/Edexcel_C3_Differentiation_-_Products_and_quotients.pdf",
                                  "P3_questions/Edexcel_C3_Differentiation_-_Stationary_points.pdf",
                                  "P3_questions/Edexcel_C3_Differentiation_-_Tangents_and_normals.pdf"],
    "c3-integration":             ["P3_questions/Edexcel_C3_Integration_-_Areas.pdf",
                                  "P3_questions/Edexcel_C3_Integration_-_Basic_integration.pdf",
                                  "P3_questions/Edexcel_C3_Integration_-_By_parts.pdf",
                                  "P3_questions/Edexcel_C3_Integration_-_By_substitution.pdf"],

    # ========== C4 lesson -> C4 by-topic 题集 ==========
    "c4-algebra":                 ["P4_questions/Edexcel_C4_Algebra_-_Partial_fractions.pdf",
                                  "P4_questions/Edexcel_C4_Sequences_and_series_-_Binomial_series.pdf",
                                  "P4_questions/Edexcel_C4_Sequences_and_series_-_Maclaurin_series.pdf",
                                  "P4_questions/Edexcel_C4_Sequences_and_series_-_general.pdf"],
    "c4-coordinate-geometry":     ["P4_questions/Edexcel_C4_Coordinate_geometry_-_Parametric_curves.pdf"],
    "c4-sequences-series":        ["P4_questions/Edexcel_C4_Sequences_and_series_-_Binomial_series.pdf",
                                  "P4_questions/Edexcel_C4_Sequences_and_series_-_Maclaurin_series.pdf",
                                  "P4_questions/Edexcel_C4_Sequences_and_series_-_general.pdf"],
    "c4-differentiation":         ["P4_questions/Edexcel_C4_Differentiation_-_Implicit_differentiation.pdf",
                                  "P4_questions/Edexcel_C4_Differentiation_-_Parametric_differentiation.pdf",
                                  "P4_questions/Edexcel_C4_Differentiation_-_Products_and_quotients.pdf",
                                  "P4_questions/Edexcel_C4_Differentiation_-_Rates_of_change.pdf",
                                  "P4_questions/Edexcel_C4_Differentiation_-_Stationary_points.pdf",
                                  "P4_questions/Edexcel_C4_Differentiation_-_Tangents_and_normals.pdf",
                                  "P4_questions/Edexcel_C4_Differential_equations_-_first_order.pdf"],
    "c4-integration":             ["P4_questions/Edexcel_C4_Integration_-_Areas.pdf",
                                  "P4_questions/Edexcel_C4_Integration_-_Basic_integration.pdf",
                                  "P4_questions/Edexcel_C4_Integration_-_By_parts.pdf",
                                  "P4_questions/Edexcel_C4_Integration_-_By_substitution.pdf",
                                  "P4_questions/Edexcel_C4_Integration_-_Using_partial_fractions.pdf",
                                  "P4_questions/Edexcel_C4_Integration_-_Volumes.pdf",
                                  "P4_questions/Edexcel_C4_Numerical_Methods_-_Trapezium_rule.pdf"],
    "c4-vectors":                 ["P4_questions/Edexcel_C4_Vectors_-_Scalar_products.pdf",
                                  "P4_questions/Edexcel_C4_Vectors_-_Vector_lines.pdf",
                                  "P4_questions/Edexcel_C4_Trigonomnetry_-_Trigonometrical_formulae_and_equations.pdf",
                                  "P4_questions/Edexcel_C4_Trigonomnetry_-_Trigonometrical_identities.pdf"],

    # ========== M1 lesson -> M1 by-topic 题集 ==========
    "m1-models-vectors":          ["M1_questions/Edexcel_M1_Modelling.pdf",
                                  "M1_questions/Edexcel_M1_Kinematics_-_Problems_with_vectors.pdf",
                                  "M1_questions/Edexcel_M1_Collisions.pdf",
                                  "M1_questions/Edexcel_M1_Collisions_-_Direct_impact.pdf"],
    "m1-kinematics":              ["M1_questions/Edexcel_M1_Kinematics.pdf",
                                  "M1_questions/Edexcel_M1_Kinematics_-_Uniform_acceleration_formulae.pdf",
                                  "M1_questions/Edexcel_M1_Kinematics_-_by_graphical_methods.pdf",
                                  "M1_questions/Edexcel_M1_Kinematics_-_Projectiles.pdf",
                                  "M1_questions/Edexcel_M1_Kinematics_-_Problems_with_vectors.pdf"],
    "m1-statics":                 ["M1_questions/Edexcel_M1_Statics.pdf",
                                  "M1_questions/Edexcel_M1_Statics_-_Equilibrium_problems.pdf",
                                  "M1_questions/Edexcel_M1_Moments.pdf",
                                  "M1_questions/Edexcel_M1_Moments_-_Moments_about_a_point.pdf"],
    "m1-dynamics":                ["M1_questions/Edexcel_M1_Dynamics.pdf",
                                  "M1_questions/Edexcel_M1_Dynamics_-_F_=_ma_horizontally.pdf",
                                  "M1_questions/Edexcel_M1_Dynamics_-_F_=_ma_on_a_slope.pdf",
                                  "M1_questions/Edexcel_M1_Dynamics_-_Connected_particles.pdf",
                                  "M1_questions/Edexcel_M1_Dynamics_-_Momentum_and_impulse.pdf",
                                  "M1_questions/Edexcel_M1_Dynamics_-_Analysis_of_force_systems.pdf"],

    # ========== S1 lesson -> S1 by-topic 题集 ==========
    "s1-representation":          ["S1_questions/Edexcel_S1_Representation_and_summary_data.pdf",
                                  "S1_questions/Edexcel_S1_Sampling_methods.pdf"],
    "s1-measures-location":       ["S1_questions/Edexcel_S1_Representation_and_summary_data.pdf"],
    "s1-measures-spread":         ["S1_questions/Edexcel_S1_Representation_and_summary_data.pdf"],
    "s1-probability":             ["S1_questions/Edexcel_S1_Probability.pdf",
                                  "S1_questions/Edexcel_S1_Modelling.pdf"],
    "s1-correlation-regression":  ["S1_questions/Edexcel_S1_Correlation_and_regression.pdf",
                                  "S1_questions/Edexcel_S1_Correlation_and_regression_-_PMCC.pdf",
                                  "S1_questions/Edexcel_S1_Correlation_and_regression_-_Regression.pdf"],
    "s1-discrete-random":         ["S1_questions/Edexcel_S1_Discrete_distributions.pdf",
                                  "S1_questions/Edexcel_S1_Discrete_random_variables.pdf"],
    "s1-normal-distribution":     ["S1_questions/Edexcel_S1_Normal_distribution.pdf"],
}


CHAPTERS = {
    # ========== C1 (覆盖 IAL P1 §1-5) ==========
    "c1-algebra-indices": {
        "source": "Edexcel_C1_Notes.txt",
        "start": r"^Indices$",
        "end": r"^Surds$",
        "ial_unit": "p1",
        "ial_topic": "algebra",
        "ial_topic_name": "Algebra",
        "lesson_name": "Laws of indices 指数律",
        "kp_id_range": "kp_alevels_mathematics_p1_001-003",
    },
    "c1-algebra-surds": {
        "source": "Edexcel_C1_Notes.txt",
        "start": r"^Surds$",
        "end": r"^2 +Quadratic functions",
        "ial_unit": "p1",
        "ial_topic": "algebra",
        "ial_topic_name": "Algebra",
        "lesson_name": "Surds 根式化简与运算",
        "kp_id_range": "kp_alevels_mathematics_p1_004-006",
    },
    "c1-quadratics": {
        "source": "Edexcel_C1_Notes.txt",
        "start": r"^2 +Quadratic functions",
        "end": r"^3 +Coordinate geometry",
        "ial_unit": "p1",
        "ial_topic": "algebra",
        "ial_topic_name": "Algebra",
        "lesson_name": "Quadratic functions and equations 二次函数与方程",
        "kp_id_range": "kp_alevels_mathematics_p1_007-012",
    },
    "c1-simultaneous-inequalities": {
        "source": "Edexcel_C1_Notes.txt",
        "start": r"^   Simultaneous equations",
        "end": r"^3 +Coordinate geometry",
        "ial_unit": "p1",
        "ial_topic": "algebra",
        "ial_topic_name": "Algebra",
        "lesson_name": "Simultaneous equations and inequalities 联立与不等式",
        "kp_id_range": "kp_alevels_mathematics_p1_013-016",
    },
    "c1-coordinate-geometry": {
        "source": "Edexcel_C1_Notes.txt",
        "start": r"^3 +Coordinate geometry",
        "end": r"^4 +Sequences and series",
        "ial_unit": "p1",
        "ial_topic": "coordinate-geometry",
        "ial_topic_name": "Coordinate geometry",
        "lesson_name": "Coordinate geometry 坐标几何基础",
        "kp_id_range": "kp_alevels_mathematics_p1_026-033",
    },
    "c1-sequences": {
        "source": "Edexcel_C1_Notes.txt",
        "start": r"^4 +Sequences and series",
        "end": r"^5 +Curve sketching",
        "ial_unit": "p1",
        "ial_topic": "sequences",
        "ial_topic_name": "Sequences and series",
        "lesson_name": "Sequences and series 数列与级数",
        "kp_id_range": "kp_alevels_mathematics_p1_034-038",
    },
    "c1-curve-sketching": {
        "source": "Edexcel_C1_Notes.txt",
        "start": r"^5 +Curve sketching",
        "end": r"^6 +Differentiation",
        "ial_unit": "p1",
        "ial_topic": "graphs",
        "ial_topic_name": "Curve sketching 图像",
        "lesson_name": "Cubic, quartic, transformations 三次四次图像与变换",
        "kp_id_range": "kp_alevels_mathematics_p1_020-022",
    },
    "c1-differentiation": {
        "source": "Edexcel_C1_Notes.txt",
        "start": r"^6 +Differentiation",
        "end": r"^7 +Integration",
        "ial_unit": "p1",
        "ial_topic": "differentiation",
        "ial_topic_name": "Differentiation",
        "lesson_name": "Differentiation 微分基础 + Tangents/Normals",
        "kp_id_range": "kp_alevels_mathematics_p1_039-047",
    },
    "c1-integration": {
        "source": "Edexcel_C1_Notes.txt",
        "start": r"^7 +Integration",
        "end": r"^Appendix",
        "ial_unit": "p1",
        "ial_topic": "integration",
        "ial_topic_name": "Integration",
        "lesson_name": "Indefinite integration 不定积分 + 反推",
        "kp_id_range": "kp_alevels_mathematics_p1_048-054",
    },

    # ========== C2 (覆盖 IAL P1 §6 + P2 全部) ==========
    "c2-algebra-polynomials": {
        "source": "Edexcel_C2_Notes.txt",
        "start": r"^1 +Algebra$",
        "end": r"^2 +Trigonometry",
        "ial_unit": "p2",  # 在 IAL P2 中
        "ial_topic": "algebra-functions",
        "ial_topic_name": "Algebra and functions",
        "lesson_name": "Polynomials, factor theorem 多项式 + 因子定理",
        "kp_id_range": "kp_alevels_mathematics_p2_005-007",
    },
    "c2-trigonometry": {
        "source": "Edexcel_C2_Notes.txt",
        "start": r"^2 +Trigonometry",
        "end": r"^3 +Coordinate Geometry",
        # C2 三角覆盖 IAL P1 §6 (基础 trig) + P2 三角 (sine/cosine rules)
        "ial_unit": "p1-p2",
        "ial_topic": "trigonometry",
        "ial_topic_name": "Trigonometry",
        "lesson_name": "Trigonometry 三角学(基础 + 进阶)",
        "kp_id_range": "kp_alevels_mathematics_p1_055-061 + p2_030-032",
    },
    "c2-coordinate-geometry-circles": {
        "source": "Edexcel_C2_Notes.txt",
        "start": r"^3 +Coordinate Geometry",
        "end": r"^4 +Sequences and series",
        "ial_unit": "p2",
        "ial_topic": "coord-geometry-circles",
        "ial_topic_name": "Coordinate geometry: circles",
        "lesson_name": "Circles, tangents 圆与切线",
        "kp_id_range": "kp_alevels_mathematics_p2_010-013",
    },
    "c2-sequences-binomial": {
        "source": "Edexcel_C2_Notes.txt",
        "start": r"^4 +Sequences and series",
        "end": r"^5 +Exponentials and logarithms",
        "ial_unit": "p2",
        "ial_topic": "sequences-series",
        "ial_topic_name": "Sequences and series",
        "lesson_name": "Geometric series, binomial series 等比与二项式",
        "kp_id_range": "kp_alevels_mathematics_p2_020-024",
    },
    "c2-exponentials-logs": {
        "source": "Edexcel_C2_Notes.txt",
        "start": r"^5 +Exponentials and logarithms",
        "end": r"^6 +Differentiation",
        "ial_unit": "p2",
        "ial_topic": "exponentials-logs",
        "ial_topic_name": "Exponentials and logarithms",
        "lesson_name": "Exponentials and logarithms 指数与对数",
        "kp_id_range": "kp_alevels_mathematics_p2_040-045",
    },
    "c2-differentiation-advanced": {
        "source": "Edexcel_C2_Notes.txt",
        "start": r"^6 +Differentiation",
        "end": r"^7 +Integration",
        "ial_unit": "p2",
        "ial_topic": "differentiation",
        "ial_topic_name": "Differentiation",
        "lesson_name": "Stationary points, max/min 驻点 + 极值",
        "kp_id_range": "kp_alevels_mathematics_p2_050-055",
    },
    "c2-integration-advanced": {
        "source": "Edexcel_C2_Notes.txt",
        "start": r"^7 +Integration",
        "end": r"^8 +Appendix",
        "ial_unit": "p2",
        "ial_topic": "integration",
        "ial_topic_name": "Integration",
        "lesson_name": "Definite integrals, area, trapezium rule 定积分 + 面积 + 梯形法",
        "kp_id_range": "kp_alevels_mathematics_p2_060-065",
    },

    # ========== C3 (覆盖 IAL P3) ==========
    "c3-algebra-functions": {
        "source": "Edexcel_C3_Notes.txt",
        "start": r"^1 +Algebra",
        "end": r"^2 +",
        "ial_unit": "p3",
        "ial_topic": "algebra-functions",
        "ial_topic_name": "Algebra and functions",
        "lesson_name": "Functions, composite, inverse, modulus 函数 + 复合 + 反 + 绝对值",
        "kp_id_range": "kp_alevels_mathematics_p3_001-010",
    },
    "c3-trig-advanced": {
        "source": "Edexcel_C3_Notes.txt",
        "start": r"^2 +Trigonometry|^Trigonometry",
        "end": r"^3 +|Differentiation",
        "ial_unit": "p3",
        "ial_topic": "trigonometry-advanced",
        "ial_topic_name": "Trigonometry (advanced)",
        "lesson_name": "Trigonometry 三角学进阶(addition formulas)",
        "kp_id_range": "kp_alevels_mathematics_p3_011-020",
    },
    "c3-exponentials-logs": {
        "source": "Edexcel_C3_Notes.txt",
        "start": r"^3 +Exponentials|^Exponentials",
        "end": r"^4 +|Differentiation",
        "ial_unit": "p3",
        "ial_topic": "exponentials-logs",
        "ial_topic_name": "Exponentials and logarithms",
        "lesson_name": "Exponentials and logs 指数与对数(进阶)",
        "kp_id_range": "kp_alevels_mathematics_p3_021-030",
    },
    "c3-differentiation": {
        "source": "Edexcel_C3_Notes.txt",
        "start": r"^4 +Differentiation|^Differentiation",
        "end": r"^5 +|Integration",
        "ial_unit": "p3",
        "ial_topic": "differentiation",
        "ial_topic_name": "Differentiation",
        "lesson_name": "Differentiation 进阶微分(product/quotient/chain rule)",
        "kp_id_range": "kp_alevels_mathematics_p3_031-040",
    },
    "c3-integration": {
        "source": "Edexcel_C3_Notes.txt",
        "start": r"^5 +Integration|^Integration",
        "end": r"^6 +|Numerical",
        "ial_unit": "p3",
        "ial_topic": "integration",
        "ial_topic_name": "Integration",
        "lesson_name": "Integration 进阶积分(替元 + 隐函数)",
        "kp_id_range": "kp_alevels_mathematics_p3_041-050",
    },

    # ========== C4 (覆盖 IAL P4) ==========
    "c4-algebra": {
        "source": "Edexcel_C4_Notes.txt",
        "start": r"^1 +",
        "end": r"^2 +",
        "ial_unit": "p4",
        "ial_topic": "algebra",
        "ial_topic_name": "Algebra and series",
        "lesson_name": "Partial fractions, binomial expansion, sums of series",
        "kp_id_range": "kp_alevels_mathematics_p4_001-020",
    },
    "c4-coordinate-geometry": {
        "source": "Edexcel_C4_Notes.txt",
        "start": r"^2 +",
        "end": r"^3 +",
        "ial_unit": "p4",
        "ial_topic": "coordinate-geometry",
        "ial_topic_name": "Coordinate geometry (parametric)",
        "lesson_name": "Parametric equations 参数方程",
        "kp_id_range": "kp_alevels_mathematics_p4_021-030",
    },
    "c4-sequences-series": {
        "source": "Edexcel_C4_Notes.txt",
        "start": r"^3 +",
        "end": r"^4 +",
        "ial_unit": "p4",
        "ial_topic": "sequences-series",
        "ial_topic_name": "Sequences and series",
        "lesson_name": "Binomial series 二项式级数(n 不是正整数)",
        "kp_id_range": "kp_alevels_mathematics_p4_031-040",
    },
    "c4-differentiation": {
        "source": "Edexcel_C4_Notes.txt",
        "start": r"^4 +",
        "end": r"^5 +",
        "ial_unit": "p4",
        "ial_topic": "differentiation",
        "ial_topic_name": "Differentiation (advanced)",
        "lesson_name": "Differentiation 进阶: exp/log/trig/parametric/implicit",
        "kp_id_range": "kp_alevels_mathematics_p4_041-060",
    },
    "c4-integration": {
        "source": "Edexcel_C4_Notes.txt",
        "start": r"^5 +",
        "end": r"^6 +",
        "ial_unit": "p4",
        "ial_topic": "integration",
        "ial_topic_name": "Integration (advanced)",
        "lesson_name": "Integration 进阶: by parts / partial fractions / volumes",
        "kp_id_range": "kp_alevels_mathematics_p4_061-080",
    },
    "c4-vectors": {
        "source": "Edexcel_C4_Notes.txt",
        "start": r"^6 +",
        "end": None,  # 到文件结尾或 Appendix
        "ial_unit": "p4",
        "ial_topic": "vectors",
        "ial_topic_name": "Vectors",
        "lesson_name": "Vectors 3D, scalar product, lines, planes",
        "kp_id_range": "kp_alevels_mathematics_p4_081-110",
    },

    # ========== M1 (Mechanics 1 选修, 用 1. xxx 格式) ==========
    "m1-models-vectors": {
        "source": "Edexcel_M1_Notes.txt",
        "start": r"^1\.\s+Mathematical Models",
        "end": r"^3\.\s+Kinematics",
        "ial_unit": "m1",
        "ial_topic": "mechanics-models",
        "ial_topic_name": "Mathematical models in mechanics",
        "lesson_name": "Mathematical models in mechanics + Vectors in mechanics",
        "kp_id_range": "kp_alevels_mathematics_m1_001-015",
    },
    "m1-kinematics": {
        "source": "Edexcel_M1_Notes.txt",
        "start": r"^3\.\s+Kinematics",
        "end": r"^4\.\s+Statics",
        "ial_unit": "m1",
        "ial_topic": "kinematics",
        "ial_topic_name": "Kinematics of a particle moving in a straight line",
        "lesson_name": "Kinematics 直线运动(匀加速 + 速度-时间图)",
        "kp_id_range": "kp_alevels_mathematics_m1_016-025",
    },
    "m1-statics": {
        "source": "Edexcel_M1_Notes.txt",
        "start": r"^4\.\s+Statics",
        "end": r"^5\.\s+Dynamics",
        "ial_unit": "m1",
        "ial_topic": "statics",
        "ial_topic_name": "Statics of a particle",
        "lesson_name": "Statics 静力学(合力 + 摩擦)",
        "kp_id_range": "kp_alevels_mathematics_m1_026-035",
    },
    "m1-dynamics": {
        "source": "Edexcel_M1_Notes.txt",
        "start": r"^5\.\s+Dynamics",
        "end": None,  # 到文件结尾
        "ial_unit": "m1",
        "ial_topic": "dynamics",
        "ial_topic_name": "Dynamics of a particle",
        "lesson_name": "Dynamics 动力学(牛顿定律 + 连接体 + 滑轮)",
        "kp_id_range": "kp_alevels_mathematics_m1_036-050",
    },

    # ========== S1 (Statistics 1 选修) ==========
    "s1-representation": {
        "source": "Edexcel_S1_Notes.txt",
        "start": r"^1 +",
        "end": r"^2 +",
        "ial_unit": "s1",
        "ial_topic": "statistical-representation",
        "ial_topic_name": "Statistical representation",
        "lesson_name": "数据收集 / 表示 / 频数分布",
        "kp_id_range": "kp_alevels_mathematics_s1_001-008",
    },
    "s1-measures-location": {
        "source": "Edexcel_S1_Notes.txt",
        "start": r"^2 +",
        "end": r"^3 +",
        "ial_unit": "s1",
        "ial_topic": "measures-location",
        "ial_topic_name": "Measures of location",
        "lesson_name": "Measures of location 均值 / 中位数 / 众数",
        "kp_id_range": "kp_alevels_mathematics_s1_009-016",
    },
    "s1-measures-spread": {
        "source": "Edexcel_S1_Notes.txt",
        "start": r"^3 +",
        "end": r"^4 +",
        "ial_unit": "s1",
        "ial_topic": "measures-spread",
        "ial_topic_name": "Measures of spread",
        "lesson_name": "Measures of spread 极差 / 方差 / 标准差",
        "kp_id_range": "kp_alevels_mathematics_s1_017-024",
    },
    "s1-probability": {
        "source": "Edexcel_S1_Notes.txt",
        "start": r"^4 +",
        "end": r"^5 +",
        "ial_unit": "s1",
        "ial_topic": "probability",
        "ial_topic_name": "Probability",
        "lesson_name": "Probability 概率基础",
        "kp_id_range": "kp_alevels_mathematics_s1_025-032",
    },
    "s1-correlation-regression": {
        "source": "Edexcel_S1_Notes.txt",
        "start": r"^5 +",
        "end": r"^6 +",
        "ial_unit": "s1",
        "ial_topic": "correlation-regression",
        "ial_topic_name": "Correlation and regression",
        "lesson_name": "Correlation and regression 相关与回归",
        "kp_id_range": "kp_alevels_mathematics_s1_033-040",
    },
    "s1-discrete-random": {
        "source": "Edexcel_S1_Notes.txt",
        "start": r"^6 +",
        "end": r"^7 +",
        "ial_unit": "s1",
        "ial_topic": "discrete-random-variables",
        "ial_topic_name": "Discrete random variables",
        "lesson_name": "Discrete random variables 离散随机变量",
        "kp_id_range": "kp_alevels_mathematics_s1_041-050",
    },
    "s1-normal-distribution": {
        "source": "Edexcel_S1_Notes.txt",
        "start": r"^7 +",
        "end": r"^8 +",
        "ial_unit": "s1",
        "ial_topic": "normal-distribution",
        "ial_topic_name": "The Normal distribution",
        "lesson_name": "Normal distribution N(μ, σ²) 正态分布",
        "kp_id_range": "kp_alevels_mathematics_s1_051-060",
    },
}


# ============== Parser ==============

def read_text(filepath: Path) -> list[str]:
    """读取 txt 文件,返回行列表(每行 strip 尾部空白)"""
    return [line.rstrip() for line in filepath.read_text(encoding="utf-8").splitlines()]


def extract_section(lines: list[str], start_re: str, end_re: Optional[str]) -> list[str]:
    """根据 start / end regex 提取章节内容"""
    start_pattern = re.compile(start_re, re.MULTILINE)
    end_pattern = re.compile(end_re, re.MULTILINE) if end_re else None

    start_idx = None
    for i, line in enumerate(lines):
        if start_pattern.match(line):
            start_idx = i
            break
    if start_idx is None:
        return []

    if end_pattern is None:
        return lines[start_idx:]

    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if end_pattern.match(lines[i]):
            end_idx = i
            break

    return lines[start_idx:end_idx]


def parse_chapter(chapter_key: str, chapter_def: dict) -> dict:
    """解析一个章节,返回 lesson 数据"""
    source_path = RAW_PMT_DIR / chapter_def["source"]
    if not source_path.exists():
        print(f"  [WARN] {source_path.name} 不存在,跳过 {chapter_key}", file=sys.stderr)
        return None

    lines = read_text(source_path)
    content_lines = extract_section(lines, chapter_def["start"], chapter_def.get("end"))

    if not content_lines:
        print(f"  [WARN] {chapter_key} 在 {chapter_def['source']} 中没找到内容", file=sys.stderr)
        return None

    # 拼接内容
    content = "\n".join(content_lines)
    # 限制长度(防 YAML 过大)
    if len(content) > 8000:
        content = content[:8000] + "\n\n... (truncated, see full PMT notes)"

    return {
        "lesson_id": chapter_key,
        "source_pmt": chapter_def["source"],
        "ial_unit": chapter_def["ial_unit"],
        "ial_topic": chapter_def["ial_topic"],
        "ial_topic_name": chapter_def["ial_topic_name"],
        "name": chapter_def["lesson_name"],
        "kp_id_range": chapter_def["kp_id_range"],
        "content": content,
    }


# ============== YAML Writer ==============

def escape_yaml_string(s: str) -> str:
    """转义 YAML 字符串"""
    # 用 literal block scalar (|) 保留换行
    return s


def build_yaml(chapters: list[dict], unit_id: str) -> str:
    """构建 YAML 文本"""
    # 按 ial_unit + ial_topic 分组
    by_unit: dict = {}
    for ch in chapters:
        u = ch["ial_unit"]
        by_unit.setdefault(u, {})
        by_unit[u].setdefault(ch["ial_topic"], []).append(ch)

    lines = [
        f"# learning_paths/from_pmt_{unit_id}.yaml",
        f"# 从 PMT 笔记自动生成",
        f"# 源: docs/curriculum/raw_pmt/Edexcel_*_Notes.txt (Simon Baxter, May/June 2016)",
        f"# 锁定: Edexcel IAL Mathematics 2018 改革版(等同 GCE 2017 改革)",
        f"# 单元代码: GCE 旧(WMA01-04, WME01, WST01) → IAL 新(WMA11-14, WME01, WST01)",
        f"# 生成时间: 2026-06-21",
        "",
        "metadata:",
        "  subject: mathematics",
        "  exam_board: edexcel_ial",
        f"  level: a-level-{unit_id}",
        f"  source: 'Physics & Maths Tutor (PMT) Edexcel {unit_id.upper()} Notes'",
        "  source_url: 'https://www.physicsandmathstutor.com/maths-revision/'",
        "  author: 'Simon Baxter (PMT, May/June 2016)'",
        "",
        "units:",
    ]

    for unit_key, topics in by_unit.items():
        lines.append(f"  - id: {unit_key}")
        # 单元 code
        unit_code_map = {
            "p1": "WMA11/01",
            "p2": "WMA12/01",
            "p3": "WMA13/01",
            "p4": "WMA14/01",
            "m1": "WME01/01",
            "s1": "WST01/01",
            "p1-p2": "WMA11/01 + WMA12/01 (跨单元)",
        }
        lines.append(f"    code: {unit_code_map.get(unit_key, 'TBD')}")
        lines.append(f"    name: 'Auto-generated from PMT {unit_key.upper()}'")
        lines.append(f"    difficulty: medium")
        lines.append(f"    source_pmt: 'Edexcel {unit_key.upper()} Notes (PMT)'")
        # 加 past_papers 字段
        lines.append("    past_papers:")
        # 找该 unit 对应的 raw_pmt/past_papers/{unit_key}/*.pdf
        # p1-p2 跨单元:合 p1 + p2 的 papers
        units_for_pp = [unit_key]
        if unit_key == "p1-p2":
            units_for_pp = ["p1", "p2"]
        for u_key in units_for_pp:
            past_papers_dir = REPO_DIR / "docs" / "curriculum" / "raw_pmt" / "past_papers" / u_key
            if past_papers_dir.exists():
                for pdf in sorted(past_papers_dir.glob("*.pdf")):
                    rel_path = pdf.relative_to(REPO_DIR / "docs" / "curriculum")
                    lines.append(f"      - \"{rel_path}\"")
        lines.append("    topics:")

        for topic_key, lessons in topics.items():
            lines.append(f"      - id: {topic_key}")
            lines.append(f"        name: \"{lessons[0]['ial_topic_name']}\"")
            lines.append("        lessons:")
            for lesson in lessons:
                lines.append(f"          - id: {lesson['lesson_id']}")
                lines.append(f"            name: \"{lesson['name']}\"")
                lines.append(f"            source_pmt: \"{lesson['source_pmt']}\"")
                lines.append(f"            kp_id_range: \"{lesson['kp_id_range']}\"")
                # 加 exercises 字段
                if lesson["lesson_id"] in EXERCISES:
                    lines.append("            exercises:")
                    for ex in EXERCISES[lesson["lesson_id"]]:
                        lines.append(f"              - \"raw_pmt/{ex}\"")
                lines.append("            content: |")
                # 内容每行加 14 空格缩进
                for line in lesson["content"].split("\n"):
                    lines.append(f"              {line}" if line else "")
                lines.append("")

    return "\n".join(lines)


# ============== Main ==============

def main():
    parser = argparse.ArgumentParser(
        description="PMT 笔记转 learning_paths YAML"
    )
    parser.add_argument(
        "--unit",
        default="all",
        choices=["c1", "c2", "c3", "c4", "m1", "s1", "all"],
        help="要转的 PMT unit (默认: all)",
    )
    parser.add_argument(
        "--output",
        help="输出 YAML 文件路径(默认: learning_paths/from_pmt_<unit>.yaml)",
    )
    args = parser.parse_args()

    if not RAW_PMT_DIR.exists():
        print(f"[ERROR] 找不到 {RAW_PMT_DIR}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 决定要处理哪些 chapter
    if args.unit == "all":
        chapter_keys = list(CHAPTERS.keys())
    else:
        chapter_keys = [k for k in CHAPTERS.keys() if k.startswith(f"{args.unit}-")]
        if not chapter_keys:
            print(f"[ERROR] 没有匹配 {args.unit} 的章节", file=sys.stderr)
            sys.exit(1)

    print(f"=== 解析 {len(chapter_keys)} 个章节 ===", file=sys.stderr)
    chapters = []
    for key in chapter_keys:
        print(f"  {key} ...", file=sys.stderr, end="")
        ch = parse_chapter(key, CHAPTERS[key])
        if ch:
            print(f" ✓ ({len(ch['content'])} chars)", file=sys.stderr)
            chapters.append(ch)
        else:
            print(" ✗ (skipped)", file=sys.stderr)

    if not chapters:
        print("[ERROR] 没解析出任何章节", file=sys.stderr)
        sys.exit(1)

    # 输出文件
    if args.output:
        output_path = Path(args.output)
    else:
        suffix = args.unit if args.unit != "all" else "all"
        output_path = OUTPUT_DIR / f"from_pmt_{suffix}.yaml"

    yaml_text = build_yaml(chapters, args.unit)
    output_path.write_text(yaml_text, encoding="utf-8")
    print(f"\n[OK] {len(chapters)} 章节写入 {output_path}", file=sys.stderr)
    print(f"     大小: {output_path.stat().st_size / 1024:.1f} KB", file=sys.stderr)


if __name__ == "__main__":
    main()
