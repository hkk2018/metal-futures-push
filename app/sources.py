# -*- coding: utf-8 -*-
"""
各市場的抓價函式。每個函式都回傳統一的 Quote。

注意：第三方資料源（akshare / yfinance / 新浪）介面與欄位偶爾改版。
若某一格抓不到，先看該函式的 docstring 指引，通常只要調一行。
框架本身（設定、組訊息、推送、排程）不受影響。
"""

from dataclasses import dataclass

import requests


@dataclass
class Quote:
    name: str           # 合約/標的名
    last: float         # 最新價
    change_pct: float   # 漲跌幅 %
    ok: bool = True
    err: str = ""


# ---------- 大陸：akshare ----------
def fetch_cn(cn_name: str) -> Quote:
    """
    大陸期貨即時（RMB）。
    用 akshare.futures_zh_realtime(symbol=中文品種名)，取持倉量最大的主力合約。
    若報錯：`pip install -U akshare`，並到 https://akshare.akfamily.xyz
    查 "futures_zh_realtime" 確認品種名（如 黄金/白银/沪铜/镍/螺纹钢/铁矿石）。
    """
    import akshare as ak

    df = ak.futures_zh_realtime(symbol=cn_name)
    sort_col = "hold" if "hold" in df.columns else df.columns[-1]
    row = df.sort_values(sort_col, ascending=False).iloc[0]
    return Quote(
        name=str(row.get("symbol", cn_name)),
        last=float(row.get("trade")),
        change_pct=float(row.get("changepercent", 0.0)),
    )


# ---------- 美國：yfinance（COMEX） ----------
def fetch_comex(ticker: str) -> Quote:
    """美國 COMEX 連續期貨（USD）。yfinance ticker：GC=F 金 / SI=F 銀 / HG=F 銅。"""
    import yfinance as yf

    t = yf.Ticker(ticker)
    h = t.history(period="5d")
    if h.empty:
        raise RuntimeError(f"yfinance 無資料：{ticker}")
    last = float(h["Close"].iloc[-1])
    prev = float(h["Close"].iloc[-2]) if len(h) > 1 else last
    pct = (last - prev) / prev * 100 if prev else 0.0
    return Quote(name=ticker, last=last, change_pct=pct)


# ---------- 倫敦：新浪外盤（LME，鎳用） ----------
def fetch_lme(symbol: str) -> Quote:
    """
    倫敦 LME（USD），走新浪外盤端點，免費免金鑰。
    端點：https://hq.sinajs.cn/list=hf_<symbol>  需帶 Referer。
    欄位順序新浪偶爾調整；若 last/漲跌不對，print(parts) 看一下索引再改。
    常見：parts[0]=最新價, parts[7]=昨結。
    """
    url = f"https://hq.sinajs.cn/list=hf_{symbol}"
    r = requests.get(
        url, headers={"Referer": "https://finance.sina.com.cn"}, timeout=10
    )
    r.encoding = "gbk"
    raw = r.text.split('"')[1]
    parts = raw.split(",")
    last = float(parts[0])
    try:
        prev = float(parts[7])
        pct = (last - prev) / prev * 100 if prev else 0.0
    except (IndexError, ValueError):
        pct = 0.0
    return Quote(name=f"LME-{symbol}", last=last, change_pct=pct)


# ---------- 台灣：期交所（目前只有黃金） ----------
def fetch_taifex(ref: str) -> Quote:
    """
    台灣期交所金屬期貨只有黃金（台幣黃金期貨 / 美元黃金期貨）。
    台期所沒有穩定的免費即時 JSON；可選做法：
      1. 抓官網每日行情頁面解析（延遲、需自行 parse）
      2. 直接用國際金價(GC=F)當參考，省事
    這裡先回傳「未接」狀態，避免假裝有資料。要哪種我再幫你接。
    """
    return Quote(name="台期所黃金", last=0.0, change_pct=0.0,
                 ok=False, err="台期所資料源未接（見 fetch_taifex 說明）")


DISPATCH = {
    "cn": fetch_cn,
    "comex": fetch_comex,
    "lme": fetch_lme,
    "taifex": fetch_taifex,
}


def fetch(source: str, ref: str) -> Quote:
    fn = DISPATCH.get(source)
    if not fn:
        return Quote(name=ref, last=0.0, change_pct=0.0, ok=False,
                     err=f"未知資料源 {source}")
    try:
        return fn(ref)
    except Exception as e:  # 單一格失敗不拖垮整批
        return Quote(name=ref, last=0.0, change_pct=0.0, ok=False, err=str(e))
