# metal-futures-push

金屬期貨價格推送到企業微信群機器人（大陸可用）。支援**排程**與**隨時手動觸發**。

涵蓋：黃金 / 白銀 / 銅 / 鎳 / 鐵，市場為大陸(上期所·大商所) / 美國(COMEX) / 倫敦(LME, 鎳用) / 台灣(僅黃金)。
> 各市場實際有的金屬不同：台灣只有黃金；鎳的國際盤在倫敦不在美國。詳見 `app/config.py` 矩陣。

## 推送管道
企業微信群機器人：群設定 → 群機器人 → 新增 → 取得 Webhook，URL 結尾 `key=` 那串即 `WECOM_KEY`。
（沒公司也行：個人微信掃碼免費註冊企業，免認證。）

## 三種跑法

### A. 本機 / 隨時手動（最快）
```bash
pip install -r requirements.txt
export WECOM_KEY='你的key'
python -m app.cli                      # 推全部
python -m app.cli --metals 黃金,銅      # 只推部分
python -m app.cli --dry                # 只印不推（測試）
```

### B. k8s 排程 + 隨時觸發
```bash
docker build -t <reg>/metal-futures-push:latest .
docker push <reg>/metal-futures-push:latest

kubectl create secret generic metal-push-secret \
  --from-literal=WECOM_KEY='你的key' --from-literal=PUSH_TOKEN='自訂token' -n <ns>

kubectl apply -f deploy/cronjob.yaml -n <ns>        # 每小時自動推
# 隨時手動推一次：
kubectl create job --from=cronjob/metal-push manual-$(date +%s) -n <ns>

# 想要 HTTP 端點隨時觸發（手機捷徑 / curl）：
kubectl apply -f deploy/deployment.yaml -n <ns>
# curl -X POST "http://<svc>/push?token=<PUSH_TOKEN>&metals=黃金,銅"
```

### C. GitHub Actions（零自有伺服器）
把 repo 推上 GitHub，設 secret `WECOM_KEY`。
- 自動：每小時跑
- 隨時：Actions 頁面（或手機 GitHub App）按 **Run workflow**，可填要推的金屬/市場

## 改設定
- **加/減金屬或市場**：`app/config.py` 的 `INSTRUMENTS`
- **抓價邏輯**：`app/sources.py`（每個資料源獨立，壞了只修一格）
- **訊息排版**：`app/message.py`
- **頻率**：`deploy/cronjob.yaml` 或 workflow 的 `cron`

## 重要：抓價的機器要連得到資料源
- 大陸期貨：akshare 走新浪/東財，大陸境內可連
- 美國 COMEX：yfinance 走 Yahoo，**大陸境內被牆**；需在境外/台灣或 GitHub runner 上跑
- 倫敦 LME：新浪外盤，大陸可連
→ 若抓價的機器在大陸，國際盤抓不到；建議抓價放境外，再推進大陸的企業微信（推送端點全球可達）。
