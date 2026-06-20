# CLAUDE.md — 專案脈絡（給 Claude Code 與協作者）

## 這個專案在做什麼
定時 / 隨時把**常見金屬期貨價格**推送到**企業微信群機器人**，給少數人（含大陸朋友）當價格提醒。
金屬：黃金 / 白銀 / 銅 / 鎳 / 鐵。市場：大陸(上期所·大商所) / 美國(COMEX) / 倫敦(LME) / 台灣(僅黃金)。

## 推送管道
企業微信「群機器人」webhook（不是個人微信、也不是 AI 智慧機器人）。
- 訊息送到某個**內部群**；群成員裝企業微信、留在群裡即收得到。
- 程式只需要 webhook 的 `key`（環境變數 `WECOM_KEY`），不需要對方帳號或 corpid/secret。
- 端點 `qyapi.weixin.qq.com` 全球可達（不被 GFW 擋），所以抓價程式放境外也能推進大陸。

## 架構（單一職責分檔）
```
app/config.py    金屬×市場矩陣 —— 要加/減金屬或市場只改這裡
app/sources.py   各市場抓價函式（cn=akshare / comex=yfinance / lme=新浪外盤 / taifex=未接）
app/message.py   把多筆報價組成 Markdown 訊息（依金屬分組）
app/push.py      推送到企業微信群機器人
app/cli.py       命令列：python -m app.cli [--metals ..] [--markets ..] [--dry]
app/server.py    可選 FastAPI：POST /push 隨時觸發
deploy/          k8s：cronjob(排程) / deployment(HTTP服務) / secret 範本
.github/workflows/push.yml  GitHub Actions：cron + workflow_dispatch(手動)
```

## 資料源與已知脆弱點
- **大陸盤**：akshare `futures_zh_realtime(symbol=中文品種名)`，取持倉量最大的主力合約。
  akshare 介面/品種名偶爾改版，壞了先 `pip install -U akshare` 再對照官方文件。
- **美國 COMEX**：yfinance ticker（GC=F 金 / SI=F 銀 / HG=F 銅），穩定。
- **倫敦 LME（鎳）**：新浪外盤 `hq.sinajs.cn/list=hf_NID`，需帶 Referer；欄位順序偶爾調整。
- **台灣 TAIFEX**：目前**未接**（`fetch_taifex` 回傳未接狀態，不假裝有資料）。台期所金屬只有黃金。
- 每一格抓價獨立 try/except，單格失敗不拖垮整批。

## 重要約束：抓價的機器要連得到資料源
- akshare(大陸盤) 走新浪/東財 → 大陸境內可連；境外/GitHub runner 抓偶爾慢或不穩。
- yfinance(美國盤) 走 Yahoo → **大陸境內被牆**，需境外/台灣或 GitHub runner。
- 建議分工：**大陸盤跑在大陸境內（如自有 k8s），國際盤跑在境外/GitHub Actions**，各推同一個 webhook。

## 怎麼跑（擇一）
- 本機/隨時：`export WECOM_KEY=...; python -m app.cli`
- k8s 排程：`deploy/cronjob.yaml`（每小時）；手動補一次 `kubectl create job --from=cronjob/metal-push manual-$(date +%s)`
- GitHub Actions：設 secret `WECOM_KEY`；自動每小時 + Actions 頁「Run workflow」手動（手機也能按）

## 慣例
- 金鑰一律走環境變數 / k8s Secret / GitHub Secrets，**不准寫進程式或提交到 repo**。
- GitHub Actions 的 cron 是 **UTC**，排台灣時間要自行換算。
- 回應與註解用繁體中文，程式碼/路徑用英文。
