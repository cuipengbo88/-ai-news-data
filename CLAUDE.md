# AI 日报 Skill

## 触发词
「写今日总结」「写昨日总结」「今日总结」「昨日总结」「AI 日报」「daily report」

## 自动化流程

### 抓取 + 生成（GitHub Actions 云端全自动）
- 每天 22:00 CST，GitHub Actions 自动执行：
  1. `fetch.py` → 抓取 aihot.virxact.com → 存入 `raw/`
  2. `generate_report.py` → 调 DeepSeek API 生成 HTML 报告 → 存入 `reports/`
  3. 自动 commit + push 回仓库
- 不需要电脑开机，不需要任何操作
- **前提**：GitHub 仓库已设置 `DEEPSEEK_API_KEY` secret

### 同步到桌面（用户手动或定时）
用户说触发词后：
1. 执行 `python sync_desktop.py`（git pull + 复制最新报告到桌面）
2. 报告出现在 `桌面/每日AI热点总结报告/`

或者设置 Windows 定时任务每天自动运行 `sync_desktop.py`。

### 手动生成（兜底）
如果 Actions 没跑或需要立刻出报告：
1. `git pull` 拉最新 raw 数据
2. `python generate_report.py` 本地生成（需本机有 DEEPSEEK_API_KEY 或 ANTHROPIC_API_KEY 环境变量）
3. `python sync_desktop.py` 同步到桌面

## 报告格式

输出为自包含 HTML 页面（内嵌 CSS），保留四段结构：

- 🔥 深度分析（1-2 条，每条 500-800 字）
- 📋 快讯（其余新闻，每条一句话）
- 🎬 编导可用的（1-3 项新工具/技术）
- 🛠️ Vibe Coding 可玩的（1-3 项）

关键词着色：蓝色(公司/产品) / 橙色(数字) / 红色(判断) / 绿色(利好) / 紫色(术语)

## 用户画像

- 主业：为线下实体行业老板做短视频编导（改写脚本、数据判断、改写文案）
- 兴趣：vibe coding 产品原型
- 视角：产品/商业，非纯技术向
- 风格：重点突出，实用可落地

## 约束

- 深度分析每条 500-800 字，有观点有推演
- 读者是非技术的实体老板，编导板块要接地气
- 不存在的新技术不编造，宁可少推一条
- 桌面报告命名：`YY.M.DAI热点总结.html`（如 2026年6月10日 → `26.6.10AI热点总结.html`）
