# -*- coding: utf-8 -*-
"""
唯一需要維護的設定檔：金屬 × 市場 的矩陣。
要加金屬、加市場、停用某一格，只改這裡。

source 種類：
  "cn"     -> 大陸期貨（akshare，RMB）
  "comex"  -> 美國 COMEX（yfinance，USD）
  "lme"    -> 倫敦 LME（新浪外盤，USD）  # 鎳的國際盤在這
  # 台灣不提供：台期所無官方免費即時源、且僅有黃金（見 docs/SOURCES.md）

ref 欄位依 source 不同：
  cn     -> akshare 的中文品種名（如 "黄金"、"沪铜"、"沪镍"）
  comex  -> yfinance ticker（如 "GC=F"）
  lme    -> 新浪外盤代號（如 "NID"）
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Instrument:
    metal: str        # 金屬中文名（分組用）
    market: str       # 市場顯示名
    source: str       # 資料源類型
    ref: str          # 該資料源的查詢代號
    enabled: bool = True


# 金屬顯示順序
METAL_ORDER = ["黃金", "白銀", "銅", "鎳", "鐵"]

INSTRUMENTS = [
    # ---- 黃金 ----
    Instrument("黃金", "滬金(大陸)",   "cn",     "黄金"),
    Instrument("黃金", "COMEX(美國)", "comex",  "GC=F"),
    # 台灣：台期所無官方免費即時源，且僅有黃金一項；為求數據可靠，台灣一律不提供（見 docs/SOURCES.md）
    # ---- 白銀 ----
    Instrument("白銀", "滬銀(大陸)",   "cn",     "白银"),
    Instrument("白銀", "COMEX(美國)", "comex",  "SI=F"),
    # 台灣無白銀期貨
    # ---- 銅 ----
    Instrument("銅",   "滬銅(大陸)",   "cn",     "沪铜"),
    Instrument("銅",   "COMEX(美國)", "comex",  "HG=F"),
    # 台灣無銅期貨
    # ---- 鎳 ----
    Instrument("鎳",   "滬鎳(大陸)",   "cn",     "沪镍"),
    Instrument("鎳",   "LME(倫敦)",   "lme",    "NID"),   # 鎳國際盤在倫敦，不在美國
    # ---- 鐵 ----
    Instrument("鐵",   "螺紋鋼(大陸)", "cn",     "螺纹钢"),
    Instrument("鐵",   "鐵礦石(大陸)", "cn",     "铁矿石"),
]


def selected(metals=None, markets=None):
    """依命令列/環境變數過濾要推哪些。"""
    out = []
    for ins in INSTRUMENTS:
        if not ins.enabled:
            continue
        if metals and ins.metal not in metals:
            continue
        if markets and not any(m in ins.market for m in markets):
            continue
        out.append(ins)
    return out
