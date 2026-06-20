# HANDOFF — 目前進度與接手說明

最後更新：初版交付。這份給「接手的人」或「Claude Code web」快速進入狀況。

## 一句話現況
程式骨架與三種跑法（CLI / k8s / GitHub Actions）都已完成、語法可編譯通過。
推送管道為企業微信群機器人，`WECOM_KEY` 已可由使用者提供。尚有幾項抓價源與部署決策待定。

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
1. **抓價機器位置（GFW）** — 使用者的 k8s 在大陸還是境外尚未確認。
   - 若在大陸：yfinance(美國盤) 會被牆 → 需把國際盤改由境外/GitHub Actions 抓。
   - 若在境外：akshare(大陸盤) 偶爾不穩 → 視情況加重試或換源。
   - 建議落地：大陸盤在境內、國際盤在境外，各推同一 webhook。
2. **台灣黃金（TAIFEX）** — `fetch_taifex` 尚未接。二選一：
   - (a) 解析台期所官網每日行情（延遲、需 parse）
   - (b) 直接用國際金價 GC=F 當參考（省事）
3. **可選：PushPlus 管道** — 若想讓大陸朋友用「個人微信」收（免裝企業微信），
   在 `app/push.py` 加 `push_pushplus()`，用環境變數切換 `WECOM` / `PUSHPLUS`。
4. **akshare 品種名/介面驗證** — 首次實跑可能要微調 `config.py` 的中文品種名或 `sources.fetch_cn`。
5. **排程時間** — GitHub Actions cron 為 UTC；如只想交易時段推，改 cron 或在程式判斷時段。

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
