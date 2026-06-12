"""Generate AI daily report from raw news data using Claude API.

Reads raw/*.txt, calls Anthropic API to produce a formatted report following the
template from CLAUDE.md, and saves to reports/YYYY-MM-DD.md.

Usage:
    python generate_report.py              # latest raw file
    python generate_report.py 2026-06-10   # specific date
"""

import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
RAW_DIR = ROOT / "raw"
REPORTS_DIR = ROOT / "reports"

SYSTEM_PROMPT = """你是AI日报主编，为一位实体行业短视频编导撰写每日AI热点总结报告。

读者画像：主业为线下实体老板做短视频编导（改写脚本、数据判断、文案），业余做vibe coding产品原型。视角偏产品/商业，非纯技术。风格要求重点突出、实用可落地。

报告模板：

# AI 日报 YYYY-MM-DD

## 🔥 深度分析
（选1-2条最重要的新闻深度展开，每条500-800字）
结构：事实概要 → 为什么重要 → 行业影响推演 → 与你（编导/vibe coding）的具体关联

## 📋 快讯
（其余新闻，每条一句话，用 - 列表）

## 🎬 编导可用的
（脚本改写、文案生成、数据分析、视频制作相关的新工具/技术，1-3项）
（从实体行业老板的内容需求出发，说清楚能怎么用、省多少时间）

## 🛠️ Vibe Coding 可玩的
（AI编程工具、低代码平台、新框架/产品，1-3项）
（面向快速原型开发，强调上手难度和实际能用起来的场景）

约束：
- 深度分析每条500-800字，有观点有推演
- 读者是非技术的实体老板，编导板块要接地气
- 不存在的新技术不编造，宁可少推一条
- 直接输出报告正文，不要任何前言后语"""


def find_latest_raw() -> Path | None:
    txt_files = sorted(RAW_DIR.glob("*.txt"))
    # Filter out AIHOT.html if it somehow matches
    txt_files = [f for f in txt_files if f.stem != "AIHOT"]
    return txt_files[-1] if txt_files else None


def load_raw(path: Path, max_chars: int = 40000) -> str:
    raw = path.read_text(encoding="utf-8")
    if len(raw) > max_chars:
        raw = raw[:max_chars] + "\n\n[内容过长，已截断]"
    return raw


def generate_report(date_str: str, raw_text: str, api_key: str, model: str = "claude-sonnet-4-6") -> str:
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)

    user_prompt = f"以下是 {date_str} 的AI领域热点新闻原始数据，请按模板生成当日报告：\n\n{raw_text}"

    response = client.messages.create(
        model=model,
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return response.content[0].text


def generate_report_deepseek(date_str: str, raw_text: str, api_key: str, model: str = "deepseek-chat") -> str:
    from openai import OpenAI

    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    client = OpenAI(api_key=api_key, base_url=base_url)

    user_prompt = f"以下是 {date_str} 的AI领域热点新闻原始数据，请按模板生成当日报告：\n\n{raw_text}"

    response = client.chat.completions.create(
        model=model,
        max_tokens=8000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content


def save_report(date_str: str, content: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / f"{date_str}.md"

    # Ensure title uses correct date
    if content.startswith("# AI 日报 "):
        # Replace date placeholder or keep existing
        pass

    out_path.write_text(content, encoding="utf-8")
    return out_path


def main():
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    if deepseek_key:
        provider = "deepseek"
        api_key = deepseek_key
        model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    elif anthropic_key:
        provider = "anthropic"
        api_key = anthropic_key
        model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    else:
        print("ERROR: Neither DEEPSEEK_API_KEY nor ANTHROPIC_API_KEY is set.")
        print("Set one via: export DEEPSEEK_API_KEY=sk-...")
        sys.exit(1)

    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        latest = find_latest_raw()
        if not latest:
            print("ERROR: No raw files found in", RAW_DIR)
            sys.exit(1)
        date_str = latest.stem  # e.g. "2026-06-10"

    raw_path = RAW_DIR / f"{date_str}.txt"
    if not raw_path.exists():
        print(f"ERROR: Raw file not found: {raw_path}")
        sys.exit(1)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Loading raw: {raw_path}")
    raw_text = load_raw(raw_path)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generating report via {provider} ({model})...")
    if provider == "deepseek":
        report = generate_report_deepseek(date_str, raw_text, api_key, model)
    else:
        report = generate_report(date_str, raw_text, api_key, model)

    out_path = save_report(date_str, report)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Report saved: {out_path}")
    print(f"  Length: {len(report)} chars, ~{len(report.splitlines())} lines")


if __name__ == "__main__":
    main()
