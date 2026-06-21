#!/usr/bin/env python3
"""download_ial_past_papers.py —— 下载 IAL past papers (2019-2024)

URL 模式:
  QP: /Papers/Edexcel-IAL/Pure/P1/QP/<date> QP.pdf
  MS: /Papers/Edexcel-IAL/Pure/P1/MA/<date> MA.pdf
"""

import sys
from pathlib import Path
from urllib.parse import quote
import urllib.request
import urllib.error


SCRIPT_DIR = Path(__file__).parent
REPO_DIR = SCRIPT_DIR.parent.parent
OUT_BASE = REPO_DIR / "docs" / "curriculum" / "raw_pmt" / "past_papers"
OUT_BASE.mkdir(parents=True, exist_ok=True)


# (unit, paper_code, qp_base, ma_base, dates)
UNITS = {
    "p1": {
        "paper_code": "WMA11/01",
        "qp_base": "Maths/A-level/Papers/Edexcel-IAL/Pure/P1/QP",
        "ma_base": "Maths/A-level/Papers/Edexcel-IAL/Pure/P1/MA",
        "dates": [
            ("January 2019", "QP"),
            ("June 2019", "QP"),
            ("January 2020", "QP"),
            ("January 2021", "QP"),
            ("January 2022", "QP"),
            ("June 2022", "QP"),
            ("January 2023", "QP"),
            ("June 2023", "QP"),
            ("January 2024", "QP"),
            ("January 2019", "MA"),
            ("June 2019", "MA"),
            ("January 2020", "MA"),
            ("January 2021", "MA"),
            ("January 2022", "MA"),
            ("June 2022", "MA"),
            ("January 2023", "MA"),
            ("June 2023", "MA"),
            ("January 2024", "MA"),
        ],
    },
    "p2": {
        "paper_code": "WMA12/01",
        "qp_base": "Maths/A-level/Papers/Edexcel-IAL/Pure/P2/QP",
        "ma_base": "Maths/A-level/Papers/Edexcel-IAL/Pure/P2/MA",
        "dates": [
            ("January 2020", "QP"),
            ("January 2021", "QP"),
            ("January 2022", "QP"),
            ("June 2022", "QP"),
            ("January 2023", "QP"),
            ("June 2023", "QP"),
            ("January 2024", "QP"),
            ("January 2020", "MA"),
            ("January 2021", "MA"),
            ("January 2022", "MA"),
            ("June 2022", "MA"),
            ("January 2023", "MA"),
            ("June 2023", "MA"),
            ("January 2024", "MA"),
        ],
    },
    "p3": {
        "paper_code": "WMA13/01",
        "qp_base": "Maths/A-level/Papers/Edexcel-IAL/Pure/P3/QP",
        "ma_base": "Maths/A-level/Papers/Edexcel-IAL/Pure/P3/MA",
        "dates": [
            ("January 2020", "QP"),
            ("January 2021", "QP"),
            ("January 2022", "QP"),
            ("June 2022", "QP"),
            ("January 2023", "QP"),
            ("June 2023", "QP"),
            ("January 2024", "QP"),
            ("January 2020", "MA"),
            ("January 2021", "MA"),
            ("January 2022", "MA"),
            ("June 2022", "MA"),
            ("January 2023", "MA"),
            ("June 2023", "MA"),
            ("January 2024", "MA"),
        ],
    },
    "p4": {
        "paper_code": "WMA14/01",
        "qp_base": "Maths/A-level/Papers/Edexcel-IAL/Pure/P4/QP",
        "ma_base": "Maths/A-level/Papers/Edexcel-IAL/Pure/P4/MA",
        "dates": [
            ("January 2021", "QP"),
            ("January 2022", "QP"),
            ("June 2022", "QP"),
            ("January 2023", "QP"),
            ("June 2023", "QP"),
            ("January 2024", "QP"),
            ("January 2021", "MA"),
            ("January 2022", "MA"),
            ("June 2022", "MA"),
            ("January 2023", "MA"),
            ("June 2023", "MA"),
            ("January 2024", "MA"),
        ],
    },
    "m1": {
        "paper_code": "WME01/01",
        "qp_base": "Maths/A-level/Papers/Edexcel-IAL/Mechanics/M1/QP",
        "ma_base": "Maths/A-level/Papers/Edexcel-IAL/Mechanics/M1/MA",
        "dates": [
            ("January 2019", "QP"),
            ("June 2019", "QP"),
            ("January 2020", "QP"),
            ("January 2021", "QP"),
            ("January 2022", "QP"),
            ("June 2022", "QP"),
            ("January 2023", "QP"),
            ("June 2023", "QP"),
            ("January 2024", "QP"),
            ("January 2019", "MA"),
            ("June 2019", "MA"),
            ("January 2020", "MA"),
            ("January 2021", "MA"),
            ("January 2022", "MA"),
            ("June 2022", "MA"),
            ("January 2023", "MA"),
            ("June 2023", "MA"),
            ("January 2024", "MA"),
        ],
    },
    "s1": {
        "paper_code": "WST01/01",
        "qp_base": "Maths/A-level/Papers/Edexcel-IAL/Statistics/S1/QP",
        "ma_base": "Maths/A-level/Papers/Edexcel-IAL/Statistics/S1/MA",
        "dates": [
            ("January 2019", "QP"),
            ("June 2019", "QP"),
            ("January 2020", "QP"),
            ("January 2021", "QP"),
            ("January 2022", "QP"),
            ("June 2022", "QP"),
            ("January 2023", "QP"),
            ("June 2023", "QP"),
            ("January 2024", "QP"),
            ("January 2019", "MA"),
            ("June 2019", "MA"),
            ("January 2020", "MA"),
            ("January 2021", "MA"),
            ("January 2022", "MA"),
            ("June 2022", "MA"),
            ("January 2023", "MA"),
            ("June 2023", "MA"),
            ("January 2024", "MA"),
        ],
    },
}


def download(url: str, dest: Path) -> bool:
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
        return False
    except Exception:
        return False


def main():
    ok = 0
    fail = 0

    for unit_key, config in UNITS.items():
        out_dir = OUT_BASE / unit_key
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n=== {unit_key} ({config['paper_code']}) ===")
        print(f"  Output: {out_dir}")

        for date, qtype in config["dates"]:
            base = config["qp_base"] if qtype == "QP" else config["ma_base"]
            url = f"https://pmt.physicsandmathstutor.com/download/{base}/{date} {qtype}.pdf"
            safe_date = date.replace(" ", "_")
            dest = out_dir / f"{safe_date}_{qtype}.pdf"

            if dest.exists() and dest.stat().st_size > 100:
                ok += 1
                continue

            if download(url, dest):
                ok += 1
                print(f"  ✓ {dest.name}")
            else:
                fail += 1
                if dest.exists():
                    dest.unlink()

    print(f"\n=== 总计: {ok} 成功, {fail} 失败 ===")


if __name__ == "__main__":
    main()
