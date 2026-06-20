# metal-futures-push

金屬期貨價格推送到企業微信群機器人（大陸可用）。支援**排程**與**隨時手動觸發**。

> 接手或交給 Claude Code 前，先看 [`CLAUDE.md`](./CLAUDE.md)（架構脈絡）與 [`HANDOFF.md`](./HANDOFF.md)（目前進度、待辦、開場 prompt）。

涵蓋：黃金 / 白銀 / 銅 / 鎳 / 鐵，市場為大陸(上期所·大商所) / 美國(COMEX) / 倫敦(LME, 鎳用)。
> **台灣不提供**：台期所無官方免費即時源、且僅有黃金。每個來源的採用理由與失敗情形見 [`docs/SOURCES.md`](./docs/SOURCES.md)。

## 推送管道
企業微信群機器人：群設定 → 群機器人 → 新增 → 取得 Webhook，URL 結尾 `key=` 那串即 `WECOM_KEY`。
（沒公司也行：個人微信掃碼免費註冊企業，免認證。）

## 跑法：GitHub Actions（主要方式，零自有伺服器）
1. 把 repo 推上 GitHub。
2. `Settings → Secrets and variables → Actions → New repository secret`，新增 `WECOM_KEY`，值貼 webhook 的 key。
3. 完成。`.github/workflows/push.yml` 已設好：
   - **自動**：每小時整點推（cron 為 UTC，要改台灣時段見 workflow 內註解）。
   - **隨時**：`Actions` 頁籤 → 選 `metal-push` → **Run workflow**（手機 GitHub App 也能按），可填要推的金屬/市場。

> 公開 repo 的 Actions 免費無上限；私有 repo 每月 2000 分鐘，每小時跑可能擦邊，建議設公開（金鑰在 Secrets，公開也安全）或降頻。

### 注意：GitHub runner 在境外
- 美國 COMEX（yfinance）、倫敦 LME（新浪外盤）、台幣金價：**抓得到**。
- 大陸盤（akshare）：從境外 runner 抓**偶爾慢或逾時**，已加重試；若某次缺值多半是這個，下次排程會補上。

## 其他跑法（可選，沒用到可忽略 `deploy/`）

<details>
<summary>本機 / 隨時手動（除錯方便）</summary>

```bash
pip install -r requirements.txt
export WECOM_KEY='你的key'
python -m app.cli                      # 推全部
python -m app.cli --metals 黃金,銅      # 只推部分
python -m app.cli --dry                # 只印不推（測試）
```
</details>

<details>
<summary>k8s 排程 + HTTP 觸發（有自己叢集才需要）</summary>

```bash
docker build -t <reg>/metal-futures-push:latest . && docker push <reg>/metal-futures-push:latest
kubectl create secret generic metal-push-secret \
  --from-literal=WECOM_KEY='你的key' --from-literal=PUSH_TOKEN='自訂token' -n <ns>
kubectl apply -f deploy/cronjob.yaml -n <ns>                       # 每小時自動推
kubectl create job --from=cronjob/metal-push manual-$(date +%s) -n <ns>   # 手動補推
kubectl apply -f deploy/deployment.yaml -n <ns>                   # 可選 HTTP 端點
```
</details>

## 改設定
- **加/減金屬或市場**：`app/config.py` 的 `INSTRUMENTS`
- **抓價邏輯**：`app/sources.py`（每個資料源獨立，壞了只修一格）
- **訊息排版**：`app/message.py`
- **頻率 / 時段**：`.github/workflows/push.yml` 的 `cron`（UTC）
