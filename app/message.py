# -*- coding: utf-8 -*-
"""把多筆報價組成一則 Markdown 訊息，依金屬分組、並列各市場。"""

from datetime import datetime
from zoneinfo import ZoneInfo

from .config import METAL_ORDER, selected
from .sources import fetch

TZ = ZoneInfo("Asia/Taipei")  # 顯示時間時區，依需要改


def _arrow(pct: float) -> str:
    return "🔺" if pct > 0 else ("🔻" if pct < 0 else "➖")


def _fmt_price(v: float) -> str:
    """價格顯示：千分位 + 最多 2 位小數，去掉無意義的尾零。
    避免 yfinance 回傳 4172.89990234375 這種未格式化的浮點。"""
    s = f"{v:,.2f}".rstrip("0").rstrip(".")
    return s


def build_message(metals=None, markets=None) -> str:
    inss = selected(metals=metals, markets=markets)

    # 先全部抓回來
    rows = [(ins, fetch(ins.source, ins.ref)) for ins in inss]

    ts = datetime.now(TZ).strftime("%m/%d %H:%M")
    lines = [f"# 金屬期貨提醒 {ts}"]

    for metal in METAL_ORDER:
        group = [(ins, q) for ins, q in rows if ins.metal == metal]
        if not group:
            continue
        lines.append(f"\n**{metal}**")
        for ins, q in group:
            if q.ok:
                lines.append(
                    f"> {ins.market}：`{_fmt_price(q.last)}` {_arrow(q.change_pct)}{q.change_pct:+.2f}%"
                )
            else:
                lines.append(f"> {ins.market}：— （{q.err}）")

    return "\n".join(lines)
