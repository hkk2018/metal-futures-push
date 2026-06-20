# HANDOFF — 目前進度與接手說明

最後更新：初版交付。這份給「接手的人」或「Claude Code web」快速進入狀況。

## 一句話現況
程式骨架完成、語法可編譯通過。**部署方式鎖定 GitHub Actions**（cron + 手動）。
推送走企業微信群機器人，`WECOM_KEY` 由使用者提供。台灣黃金已接（台幣/克）。剩下多為首次實跑的微調。

## 已完成 ✅
- 金屬×市場設定矩陣（`app/config.py`）
- 抓價：大陸(akshare)、美國 COMEX(yfinance)、倫敦 LME 鎳(新浪外盤)
- 組訊息（依金屬分組 Markdown）、推送到企業微信群機器人
- CLI（可篩金屬/市場、`--dry` 乾跑）
- 可選 HTTP 觸發服務（FastAPI `POST /push`）
- k8s：CronJob（每小時）、Deployment+Service（HTTP）、Secret 範本
- GitHub Actions：cron + 手動 `workflow_dispatch`
- 文件：README、CLAUDE.md

## 已決定的事 🧭
- 推送走**企業微信群機器人 webhook**（少數人、無每日上限、免費）。
- 排程**首選使用者自有 k8s CronJob**（零成本、準時）；GitHub Actions 主要留作「手機一鍵手動推」。
- 鎳的國際盤掛在**倫敦 LME**，不是美國。
- 台灣金屬期貨**只有黃金**，其餘市場留空格。

## 待定 / 待辦 ⏳
1. ~~抓價機器位置~~ → **已定：只用 GitHub Actions**（runner 在境外）。
   國際盤(COMEX/LME/台幣金價)抓得到；大陸盤(akshare)從境外偶爾逾時，已在 `fetch_cn` 加重試。
2. ~~台灣黃金~~ → **已定：不提供台灣**。台期所無官方免費即時源、僅有黃金；不做估算替代（見 `docs/SOURCES.md`）。
3. **可選：PushPlus 管道** — 若想讓大陸朋友用「個人微信」收（免裝企業微信），
   在 `app/push.py` 加 `push_pushplus()`，用環境變數切換 `WECOM` / `PUSHPLUS`。
4. **akshare 品種名/介面驗證** — 首次實跑可能要微調 `config.py` 的中文品種名或 `sources.fetch_cn`。
5. **排程時段** — GitHub cron 為 UTC；只想台灣交易時段推改 `push.yml` cron（已附 `0 1-7 * * 1-5` 範例）。
6. **k8s** — `deploy/` 保留但非必要；純 GitHub Actions 可忽略。

## 如何驗證能跑
```bash
pip install -r requirements.txt
export WECOM_KEY='你的群機器人key'
python -m app.cli --dry          # 先乾跑看抓價與排版
python -m app.cli                # 實推一次，看企業微信群是否收到
```
先 `curl` 測 webhook 連通：
```bash
curl 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key' \
  -H 'Content-Type: application/json' \
  -d '{"msgtype":"text","text":{"content":"測試 ✅"}}'
```

---

## 貼給 Claude Code web 的開場 prompt（範例，依需要改）
> 這個 repo 是金屬期貨價格推送到企業微信群機器人的工具，請先讀 `CLAUDE.md` 與 `HANDOFF.md` 了解架構與待辦。
> 我要你完成 HANDOFF「待辦」第 2 項：把台灣黃金（TAIFEX）接上，先用方案 (b) 國際金價 GC=F 當參考，
> 改 `app/sources.py` 的 `fetch_taifex`，並更新 `app/config.py` 對應那筆。
> 同時補一個 `tests/` 用假資料驗證 `build_message()` 不會因單一資料源失敗而整批崩潰。
> 完成後開一個 PR，PR 說明列出你改了哪些檔與為什麼。不要把任何金鑰寫進程式。
