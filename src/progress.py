#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按年级、城市、日期，推算本周各科大概进度，并生成聊天提示词。

用法：
  python3 src/progress.py --grade 4 --city 武汉 --date 2026-10-26
  python3 src/progress.py --grade 4 --city 武汉 --date 2026-10-26 --json
"""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SUBJECTS = ("chinese", "math", "english")
SUBJECT_LABEL = {"chinese": "语文", "math": "数学", "english": "英语"}
TOTAL_WEEKS = 20


def load_json(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_city(city: str) -> dict:
    cities = load_json(DATA / "cities.json")
    defaults = cities["defaults"]
    item = cities["cities"].get(city, {})
    merged = dict(defaults)
    merged.update({k: v for k, v in item.items() if k != "note"})
    return merged


def term_start(today: date, city_cfg: dict) -> date:
    year = today.year
    autumn = datetime.strptime(f"{year}-{city_cfg['termStartAutumn']}", "%Y-%m-%d").date()
    spring = datetime.strptime(f"{year}-{city_cfg['termStartSpring']}", "%Y-%m-%d").date()
    if today >= autumn:
        return autumn
    if today >= spring:
        return spring
    return datetime.strptime(f"{year - 1}-{city_cfg['termStartAutumn']}", "%Y-%m-%d").date()


def semester_of(today: date, start: date) -> str:
    return "上" if start.month >= 8 else "下"


def week_no(today: date, start: date) -> int:
    return max(1, min(TOTAL_WEEKS, (today - start).days // 7 + 1))


def unit_for_week(units: list, week: int) -> dict:
    """把单元按周等比摊开；返回本周单元和是否处在复习周。"""
    if not units:
        return {"unit": None, "index": 0, "total": 0, "review": True}
    per = TOTAL_WEEKS / len(units)
    idx = min(len(units) - 1, max(0, int((week - 1) / per)))
    return {"unit": units[idx], "index": idx + 1, "total": len(units), "review": False}


def build(grade: int, city: str, today: date) -> dict:
    cfg = load_city(city)
    edition = cfg["edition"]
    start = term_start(today, cfg)
    semester = semester_of(today, start)
    week = week_no(today, start)

    out = {
        "grade": grade,
        "city": city,
        "edition": edition,
        "date": today.isoformat(),
        "semester": semester,
        "week": week,
        "subjects": {},
    }
    for subject in SUBJECTS:
        data = load_json(DATA / edition / f"{subject}.json")
        grade_data = data["grades"].get(str(grade), {})
        units = grade_data.get(semester)
        if not units:
            out["subjects"][subject] = {"available": False}
            continue
        info = unit_for_week(units, week)
        info["available"] = True
        info["label"] = SUBJECT_LABEL[subject]
        out["subjects"][subject] = info
    return out


def to_prompt(result: dict, nickname: str = "小肥鱼") -> str:
    lines = [
        f"你是{nickname}，{result['grade']} 年级小学生，{result['city']}，人教版。",
        f"今天是 {result['date']}，第 {result['week']} 周。",
        "这周各科大概在学：",
    ]
    for subject, info in result["subjects"].items():
        if not info.get("available"):
            continue
        lines.append(f"- {info['label']}：{info['unit']}")
    lines += [
        "用 1~2 句话说说今天在学校学到的东西，要有一个具体的小细节（老师让做什么、你哪里没听懂），",
        "不要报章节号，不要像汇报，像跟家长随口聊天；总共不超过 50 字。",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grade", type=int, required=True, choices=range(1, 7))
    parser.add_argument("--city", default="武汉")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    today = datetime.strptime(args.date, "%Y-%m-%d").date()
    result = build(args.grade, args.city, today)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(to_prompt(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
