#!/usr/bin/env python3
"""
fetch_edexcel_specs.py —— 抓 Edexcel IAL 全部 33 科 Specification 索引

目标:
  - 从 Pearson Edexcel 官网抓全部 IAL 科目的 Specification 下载链接
  - 输出 JSON 索引,供后续 KP 拆解使用
  - 不下载 PDF(太大),只抓元数据(科名 / code / 单元列表 / 链接)

用法:
  python3 fetch_edexcel_specs.py              # 抓取 + 输出
  python3 fetch_edexcel_specs.py --no-fetch   # 跳过抓取,用已有缓存
  python3 fetch_edexcel_specs.py --subject mathematics  # 只抓取单科
  python3 fetch_edexcel_specs.py --output my_index.json # 自定义输出

依赖:
  pip install requests beautifulsoup4 pyyaml

Author: Mavis (auto-generated)
Date: 2026-06-21
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("[ERROR] 缺少依赖,请运行: pip install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)


# ============== Configuration ==============

EDEXCEL_IAL_LANDING_URL = "https://qualifications.pearson.com/en/qualifications/edexcel-international-advanced-levels.html"
EDEXCEL_IAL_SUBJECTS_URL = "https://qualifications.pearson.com/en/qualifications/edexcel-international-advanced-levels.courselist.html"
EDEXCEL_BASE = "https://qualifications.pearson.com"

OUTPUT_DIR = Path(__file__).parent.parent.parent / "docs" / "curriculum" / "tracks" / "alevels" / "past-papers"
CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_FILE = CACHE_DIR / "edexcel_ial_subjects.json"

USER_AGENT = "Mozilla/5.0 (Mavis Curriculum Scraper; +https://github.com/local/mavis)"
TIMEOUT = 30  # seconds

# 33 门 IAL 学科官方名称(用作 fallback / 校验)
KNOWN_IAL_SUBJECTS = [
    "Mathematics", "Further Mathematics", "Pure Mathematics",
    "Physics", "Chemistry", "Biology",
    "Economics", "Business", "Accounting", "Finance",
    "English Language", "English Literature",
    "History", "Geography",
    "Psychology", "Sociology",
    "Law", "Government and Politics",
    "Computer Science", "Information Technology",
    "Media Studies", "Film Studies",
    "Art and Design", "Design Technology",
    "Music", "Drama",
    "Religious Studies",
    "Statistics", "Thinking Skills", "Global Development",
    "French", "German", "Spanish", "Chinese", "Arabic", "Italian",
]

# Subject code 前缀(用于 unit code 识别)
SUBJECT_CODE_PREFIX = {
    "Mathematics": "WMA",
    "Further Mathematics": "WFM",
    "Physics": "WPH",
    "Chemistry": "WCH",
    "Biology": "WBI",
    "Economics": "WEC",
    "Business": "WBS",
    "Computer Science": "WCS",
    "English Language": "WEN",
    "English Literature": "WET",
    "History": "WHI",
    "Geography": "WGG",
    "Psychology": "WPS",
    "Sociology": "WSY",
    "Accounting": "WAC",
    "Law": "WLW",
    "Government and Politics": "WGP",
    "Information Technology": "WIT",
    "Media Studies": "WMS",
    "Film Studies": "WFS",
    "Art and Design": "WAD",
    "Design Technology": "WDT",
    "French": "WFR",
    "German": "WGE",
    "Spanish": "WSP",
    "Chinese": "WCN",
    "Arabic": "WAR",
    "Religious Studies": "WRS",
    "Statistics": "WST",
    "Thinking Skills": "WTS",
    "Global Development": "WGD",
    "Music": "WMU",
    "Drama": "WDR",
    "Pure Mathematics": "WPM",
    "Finance": "WFI",
    "Italian": "WIT2",
}


# ============== Data classes ==============

@dataclass
class UnitInfo:
    """单个 unit 的元数据"""
    code: str  # e.g., "WMA11/01"
    name: str  # e.g., "Core Mathematics 1"
    spec_url: Optional[str] = None
    past_papers_url: Optional[str] = None


@dataclass
class SubjectInfo:
    """单科 IAL 学科的元数据"""
    name: str  # e.g., "Mathematics"
    name_normalized: str  # e.g., "mathematics" (kebab-case, 用于文件路径)
    code_prefix: str  # e.g., "WMA"
    spec_url: Optional[str] = None
    past_papers_url: Optional[str] = None
    units: list[UnitInfo] = field(default_factory=list)
    spec_version: Optional[str] = None  # e.g., "2024"
    last_updated: Optional[str] = None
    fetch_status: str = "pending"  # pending / fetched / failed / manual
    notes: str = ""


# ============== Scraper ==============

def fetch_url(url: str) -> Optional[BeautifulSoup]:
    """抓取 URL 并返回 BeautifulSoup 对象,失败返回 None"""
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        print(f"[WARN] 抓取失败: {url} -> {e}", file=sys.stderr)
        return None


def extract_subject_links(landing_soup: BeautifulSoup) -> list[dict]:
    """
    从 Edexcel IAL 主页面提取所有科目链接
    页面通常列出 30+ 门 IAL 学科,每科有 Specification / Past Papers 链接
    """
    subjects = []
    # 实际页面结构会变化,这里给一个通用 pattern
    # 真实使用时要根据 Pearson 页面 DOM 调整
    for link in landing_soup.find_all("a", href=True):
        href = link["href"]
        text = link.get_text(strip=True)
        # 启发式:包含 "IAL" 或 "International" + "subject" 字样
        if re.search(r"(international-advanced|ial).*(specification|qualification)", href, re.I):
            subjects.append({
                "name": text,
                "url": EDEXCEL_BASE + href if href.startswith("/") else href,
            })
    return subjects


def extract_unit_codes(text: str, code_prefix: str) -> list[str]:
    """
    从文本中提取 unit code (e.g., WMA11/01, WMA12/01)
    格式:`{code_prefix}{number}/{paper}`
    """
    pattern = rf"\b({code_prefix}\d{{2}})/\d{{2}}\b"
    return sorted(set(re.findall(pattern, text)))


def fetch_subject_details(subject: str) -> SubjectInfo:
    """抓取单科 IAL 详情(单元列表 / spec 链接 / past papers 链接)"""
    name_normalized = subject.lower().replace(" ", "-").replace("&", "and")
    code_prefix = SUBJECT_CODE_PREFIX.get(subject, f"W{subject[:2].upper()}")

    info = SubjectInfo(
        name=subject,
        name_normalized=name_normalized,
        code_prefix=code_prefix,
    )

    # TODO: 实际抓取时需要根据 Pearson 官网的页面结构来
    # 这里给出一个失败的默认状态
    # 真实流程:
    # 1. 访问 https://qualifications.pearson.com/en/qualifications/edexcel-international-advanced-levels/{subject}.html
    # 2. 抓 "Specification & Sample Assessments" 链接
    # 3. 抓 "Past Papers" 链接
    # 4. 从 Specification PDF 抓取 unit 列表(需要 PDF 解析)
    info.fetch_status = "manual"
    info.notes = "需要根据 Edexcel 官网实际结构手动填入"

    return info


def manual_fill_units(info: SubjectInfo) -> SubjectInfo:
    """手动填入已知 IAL 单元(用作 fallback)"""
    # Mathematics IAL 已知单元
    if info.name == "Mathematics":
        info.units = [
            UnitInfo("WMA11/01", "Core Mathematics 1 (C1)"),
            UnitInfo("WMA12/01", "Core Mathematics 2 (C2)"),
            UnitInfo("WMA13/01", "Core Mathematics 3 (C3)"),
            UnitInfo("WMA14/01", "Core Mathematics 4 (C4)"),
            UnitInfo("WST01/01", "Statistics 1 (S1) - optional"),
            UnitInfo("WME01/01", "Mechanics 1 (M1) - optional"),
        ]
    elif info.name == "Further Mathematics":
        info.units = [
            UnitInfo("WFM11/01", "Further Pure Mathematics 1 (FP1)"),
            UnitInfo("WFM12/01", "Further Pure Mathematics 2 (FP2)"),
            UnitInfo("WFM13/01", "Further Pure Mathematics 3 (FP3)"),
            UnitInfo("WFM14/01", "Further Mathematics Options"),
        ]
    elif info.name == "Physics":
        info.units = [
            UnitInfo("WPH11/01", "Physics 1 (P1)"),
            UnitInfo("WPH12/01", "Physics 2 (P2)"),
            UnitInfo("WPH13/01", "Physics 3 (P3)"),
            UnitInfo("WPH14/01", "Physics 4 (P4)"),
            UnitInfo("WPH15/01", "Physics 5 (P5)"),
            UnitInfo("WPH16/01", "Physics 6 (P6)"),
        ]
    elif info.name == "Chemistry":
        info.units = [
            UnitInfo("WCH11/01", "Chemistry 1 (C1)"),
            UnitInfo("WCH12/01", "Chemistry 2 (C2)"),
            UnitInfo("WCH13/01", "Chemistry 3 (C3)"),
            UnitInfo("WCH14/01", "Chemistry 4 (C4)"),
            UnitInfo("WCH15/01", "Chemistry 5 (C5)"),
            UnitInfo("WCH16/01", "Chemistry 6 (C6)"),
        ]
    elif info.name == "Biology":
        info.units = [
            UnitInfo("WBI11/01", "Biology 1 (B1)"),
            UnitInfo("WBI12/01", "Biology 2 (B2)"),
            UnitInfo("WBI13/01", "Biology 3 (B3)"),
            UnitInfo("WBI14/01", "Biology 4 (B4)"),
            UnitInfo("WBI15/01", "Biology 5 (B5)"),
            UnitInfo("WBI16/01", "Biology 6 (B6)"),
        ]
    # ... 其他学科类似,Phase A2 补全

    info.fetch_status = "manual"
    return info


# ============== Main ==============

def load_cache() -> dict:
    """加载已有缓存"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_fetch": None, "subjects": {}}


def save_cache(data: dict) -> None:
    """保存缓存"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data["last_fetch"] = datetime.now().isoformat()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[OK] 缓存已保存: {CACHE_FILE}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="抓 Edexcel IAL 全部 33 科 Specification 索引"
    )
    parser.add_argument("--no-fetch", action="store_true", help="跳过抓取,只用已有缓存")
    parser.add_argument("--subject", help="只抓取单科,如 'mathematics'")
    parser.add_argument("--output", help="自定义输出文件路径")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = Path(args.output) if args.output else OUTPUT_DIR / "ial-subjects-index.json"

    # 加载缓存
    cache = load_cache()

    if args.no_fetch:
        print("[INFO] 跳过抓取,使用缓存", file=sys.stderr)
        subjects_dict = cache.get("subjects", {})
    else:
        # 抓取主页面
        print(f"[INFO] 抓取 Edexcel IAL 主页面: {EDEXCEL_IAL_LANDING_URL}", file=sys.stderr)
        soup = fetch_url(EDEXCEL_IAL_LANDING_URL)
        if soup is None:
            print("[WARN] 主页面抓取失败,使用 fallback", file=sys.stderr)
            subjects_to_process = KNOWN_IAL_SUBJECTS
        else:
            # 实际抓取逻辑(根据页面结构调整)
            # 这里 fallback 到 KNOWN 列表
            print("[INFO] 主页面抓取成功,但需要手动解析(页面结构因版本而异)", file=sys.stderr)
            subjects_to_process = KNOWN_IAL_SUBJECTS

        if args.subject:
            subjects_to_process = [s for s in subjects_to_process if s.lower().replace(" ", "-") == args.subject.lower()]

        # 处理每科
        subjects_dict = {}
        for subject in subjects_to_process:
            print(f"[INFO] 处理: {subject}", file=sys.stderr)
            info = fetch_subject_details(subject)
            if not info.units:
                # 没抓到 unit,用手动 fill
                info = manual_fill_units(info)
            subjects_dict[info.name_normalized] = asdict(info)

        # 保存缓存
        cache["subjects"] = subjects_dict
        save_cache(cache)

    # 写输出
    output = {
        "generated_at": datetime.now().isoformat(),
        "source": "Edexcel IAL Pearson Qualifications",
        "subjects_count": len(subjects_dict),
        "subjects": subjects_dict,
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[OK] 索引已写入: {output_file}", file=sys.stderr)
    print(f"     共 {len(subjects_dict)} 科", file=sys.stderr)

    # 打印摘要
    print("\n=== 摘要 ===", file=sys.stderr)
    for name, info in subjects_dict.items():
        units_count = len(info.get("units", []))
        print(f"  - {info['name']:<30s} {info['code_prefix']:<5s} {units_count} units", file=sys.stderr)


if __name__ == "__main__":
    main()
