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
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Microsoft YaHei", sans-serif;
    background: #f5f5f7;
    color: #1d1d1f;
    line-height: 1.8;
    padding: 32px 20px;
    -webkit-font-smoothing: antialiased;
  }

  .container {
    max-width: 720px;
    margin: 0 auto;
    background: #ffffff;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,0.04), 0 1px 4px rgba(0,0,0,0.02);
  }

  /* 头部 */
  .header {
    background: #fafafa;
    color: #1d1d1f;
    padding: 48px 40px 36px;
    text-align: center;
    border-bottom: 1px solid #f0f0f0;
  }
  .header h1 {
    font-size: 34px; font-weight: 700; letter-spacing: -0.5px;
    background: linear-gradient(135deg, #1d1d1f 0%, #555 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .header .date {
    font-size: 14px; color: #86868b; margin-top: 8px;
    font-weight: 500; letter-spacing: 2px; text-transform: uppercase;
  }

  /* 内容区 */
  .section {
    padding: 40px;
    border-bottom: 1px solid #f5f5f7;
  }
  .section:last-of-type { border-bottom: none; }

  .section h2 {
    font-size: 22px; font-weight: 700; margin-bottom: 24px;
    color: #1d1d1f; letter-spacing: -0.3px;
    display: flex; align-items: center; gap: 10px;
  }

  /* 深度分析 */
  .deep-item { margin-bottom: 32px; }
  .deep-item:last-child { margin-bottom: 0; }
  .deep-item h3 {
    font-size: 17px; font-weight: 600; color: #1d1d1f;
    margin-bottom: 12px; letter-spacing: -0.2px;
  }
  .deep-item p {
    margin-bottom: 12px; text-indent: 2em;
    font-size: 15px; color: #424245; font-weight: 400;
  }

  /* 快讯列表 */
  .quick-list { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 8px; }
  .quick-list li {
    padding: 14px 18px;
    background: #fafafa; border-radius: 12px;
    font-size: 14px; color: #424245;
    transition: background 0.2s;
  }

  /* 工具卡片 */
  .tool-item {
    margin-bottom: 12px; padding: 20px 24px;
    background: #fafafa; border-radius: 16px;
    border: 1px solid #f0f0f0;
  }
  .tool-item:last-child { margin-bottom: 0; }
  .tool-item h4 { font-size: 16px; font-weight: 600; margin-bottom: 6px; color: #1d1d1f; }
  .tool-item p { font-size: 14px; color: #6e6e73; line-height: 1.7; }

  /* === 内联着色类 === */
  .c-name  {
    color: #0071e3; font-weight: 600;
    background: #f0f7ff; padding: 2px 8px; border-radius: 6px;
  }
  .c-data  {
    color: #e05a00; font-weight: 700;
    background: #fff5ee; padding: 2px 8px; border-radius: 6px;
  }
  .c-warn  {
    color: #d12b2b; font-weight: 700;
    background: #fff0f0; padding: 2px 10px; border-radius: 6px;
  }
  .c-good  {
    color: #1b8a3d; font-weight: 600;
    background: #edfaf1; padding: 2px 8px; border-radius: 6px;
  }
  .c-tech  {
    color: #894ecc; font-weight: 600;
    background: #f6f0ff; padding: 2px 8px; border-radius: 6px;
  }

  /* 分隔线 */
  hr.divider {
    border: none; border-top: 1px solid #f0f0f0; margin: 28px 0;
  }

  /* 页脚 */
  .footer {
    text-align: center; padding: 28px;
    font-size: 12px; color: #aeaeb2; font-weight: 500;
    letter-spacing: 1px; background: #fafafa;
  }
</style>
</head>
<body>
<div class="container">

  <!-- 头部 -->
  <div class="header">
    <h1>🔥 AI 日报 YYYY-MM-DD</h1>
    <div class="date">每日自动生成 · 数据来源 aihot.virxact.com</div>
  </div>

  <!-- 🔥 深度分析 -->
  <div class="section">
    <h2>📰 深度分析</h2>
    <div class="deep-item">
      <h3>1. 标题</h3>
      <p>正文，对关键词使用着色类：<span class="c-name">公司/产品</span>、
      <span class="c-data">关键数字</span>、<span class="c-warn">核心判断</span>、
      <span class="c-good">正面信号</span>、<span class="c-tech">技术术语</span></p>
    </div>
  </div>

  <!-- 📋 快讯 -->
  <div class="section">
    <h2>📋 快讯速览</h2>
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

  <div class="footer">AI 日报 · 每日自动生成</div>
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
- 直接输出完整 HTML，不要任何前言后语，不要用 ```html 代码块包装
- 输出必须以 <!DOCTYPE html> 开头，以 </html> 结尾
- 快讯每条至少着色公司名和关键数字
"""


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


def clean_html_output(content: str) -> str:
    """Strip markdown code fences and explanatory text around HTML content."""
    # Remove ```html and ``` fences
    content = content.replace("```html", "").replace("```", "")

    # Find the HTML document boundaries
    doctype = "<!DOCTYPE html>"
    idx = content.find(doctype)
    if idx != -1:
        content = content[idx:]

    end_tag = "</html>"
    idx = content.rfind(end_tag)
    if idx != -1:
        content = content[:idx + len(end_tag)]

    return content.strip()


def save_report(date_str: str, content: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / f"{date_str}.html"
    content = clean_html_output(content)
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
