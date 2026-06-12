"""Generate AI daily report from raw news data using Claude API.

Reads raw/*.txt, calls API to produce a formatted HTML report following the
template from CLAUDE.md, and saves to reports/YYYY-MM-DD.html.

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

输出格式：完整的自包含 HTML 页面（内嵌 CSS），结构如下：

<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 日报 YYYY-MM-DD</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, "Microsoft YaHei", "PingFang SC", sans-serif;
    background: #f5f5f5; color: #333; line-height: 1.8; padding: 20px;
  }
  .container { max-width: 780px; margin: 0 auto; }
  .header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #fff; padding: 32px 28px; border-radius: 12px 12px 0 0;
  }
  .header h1 { font-size: 24px; font-weight: 700; }
  .header .date { font-size: 14px; color: #94a3b8; margin-top: 4px; }
  .section {
    background: #fff; padding: 24px 28px;
    border-bottom: 1px solid #eee;
  }
  .section:last-of-type { border-radius: 0 0 12px 12px; }
  .section h2 { font-size: 18px; margin-bottom: 14px; padding-left: 10px; border-left: 4px solid #2563EB; }
  .deep-item { margin-bottom: 24px; }
  .deep-item h3 { font-size: 16px; color: #1a1a2e; margin-bottom: 8px; }
  .deep-item p { margin-bottom: 8px; text-indent: 2em; }
  .quick-list { list-style: none; padding: 0; }
  .quick-list li { padding: 6px 0; border-bottom: 1px dashed #f0f0f0; }
  .quick-list li:last-child { border-bottom: none; }
  .tool-item { margin-bottom: 14px; padding: 12px 16px; background: #fafafa; border-radius: 8px; }
  .tool-item h4 { font-size: 15px; margin-bottom: 4px; }
  .tool-item p { font-size: 14px; color: #666; }

  /* === 内联着色类 === */
  .c-name  { color: #2563EB; font-weight: 600; }   /* 公司/产品名：蓝 */
  .c-data  { color: #EA580C; font-weight: 700; }    /* 关键数字：橙 */
  .c-warn  { color: #DC2626; font-weight: 700; }    /* 核心判断/警告：红 */
  .c-good  { color: #16A34A; font-weight: 600; }    /* 正面信号/机会：绿 */
  .c-tech  { color: #7C3AED; font-weight: 600; }    /* 技术概念：紫 */

  .footer { text-align: center; padding: 16px; font-size: 12px; color: #999; }
  .section .divider { border: none; border-top: 2px dashed #e5e7eb; margin: 20px 0; }
</style>
</head>
<body>
<div class="container">

  <!-- 头部 -->
  <div class="header">
    <h1>AI 日报 YYYY-MM-DD</h1>
    <div class="date">自动生成 · 每日更新</div>
  </div>

  <!-- 🔥 深度分析 -->
  <div class="section">
    <h2>🔥 深度分析</h2>
    <div class="deep-item">
      <h3>1. 标题</h3>
      <p>正文，对关键词使用着色类：<span class="c-name">公司/产品</span>、
      <span class="c-data">关键数字</span>、<span class="c-warn">核心判断</span>、
      <span class="c-good">正面信号</span>、<span class="c-tech">技术术语</span></p>
    </div>
    <!-- 如有多条深度分析，用 <hr class="divider"> 分隔 -->
  </div>

  <!-- 📋 快讯 -->
  <div class="section">
    <h2>📋 快讯</h2>
    <ul class="quick-list">
      <li><span class="c-name">公司/产品</span>：一句话摘要，关键数字用<span class="c-data">数字</span>标注</li>
    </ul>
  </div>

  <!-- 🎬 编导可用的 -->
  <div class="section">
    <h2>🎬 编导可用的</h2>
    <div class="tool-item"><h4>工具名称</h4><p>说明</p></div>
  </div>

  <!-- 🛠️ Vibe Coding 可玩的 -->
  <div class="section">
    <h2>🛠️ Vibe Coding 可玩的</h2>
    <div class="tool-item"><h4>工具名称</h4><p>说明</p></div>
  </div>

  <div class="footer">AI 日报 · 每日自动生成 · 数据来源 aihot.virxact.com</div>
</div>
</body>
</html>

着色规则：
- <span class="c-name">公司名/产品名</span>
- <span class="c-data">关键数字/百分比/金额</span>
- <span class="c-warn">核心判断/风险提示/重要警告</span>
- <span class="c-good">正面信号/行业利好/新机会</span>
- <span class="c-tech">技术术语/框架名/论文方法</span>

约束：
- 深度分析每条 500-800 字，有观点有推演
- 读者是非技术的实体老板，编导板块要接地气
- 不存在的新技术不编造，宁可少推一条
- 直接输出完整 HTML，不要任何前言后语
- 快讯每条至少着色公司名和关键数字


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

    try:
        response = client.messages.create(
            model=model,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text
    except Exception as e:
        print(f"[ERROR] Anthropic API call failed: {e}")
        raise


def generate_report_deepseek(date_str: str, raw_text: str, api_key: str, model: str = "deepseek-chat") -> str:
    from openai import OpenAI

    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    client = OpenAI(api_key=api_key, base_url=base_url)

    user_prompt = f"以下是 {date_str} 的AI领域热点新闻原始数据，请按模板生成当日报告：\n\n{raw_text}"

    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=16000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] DeepSeek API call failed: {e}")
        raise


def save_report(date_str: str, content: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / f"{date_str}.html"
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
