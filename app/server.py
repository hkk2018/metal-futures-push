# -*- coding: utf-8 -*-
"""
可選：常駐 HTTP 服務，讓你「隨時」用一個請求觸發推送
（手機捷徑、curl、其他系統都能呼叫）。

啟動：uvicorn app.server:app --host 0.0.0.0 --port 8080
觸發：curl -X POST "http://<host>:8080/push?token=<PUSH_TOKEN>&metals=黃金,銅"
健康檢查：GET /healthz
"""

import os

from fastapi import FastAPI, HTTPException, Query

from .message import build_message
from .push import push_wecom

app = FastAPI(title="metal-futures-push")

# 簡單的觸發保護，避免被亂打
PUSH_TOKEN = os.environ.get("PUSH_TOKEN", "")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/push")
def push(
    token: str = Query(default=""),
    metals: str | None = Query(default=None),
    markets: str | None = Query(default=None),
    dry: bool = Query(default=False),
):
    if PUSH_TOKEN and token != PUSH_TOKEN:
        raise HTTPException(status_code=401, detail="bad token")

    m = [x.strip() for x in metals.split(",")] if metals else None
    mk = [x.strip() for x in markets.split(",")] if markets else None
    msg = build_message(metals=m, markets=mk)
    if not dry:
        push_wecom(msg)
    return {"pushed": not dry, "message": msg}
