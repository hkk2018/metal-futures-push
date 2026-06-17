# -*- coding: utf-8 -*-
"""推送到企業微信群機器人（大陸可用）。"""

import os
import requests


def push_wecom(markdown: str, key: str | None = None) -> None:
    key = key or os.environ.get("WECOM_KEY", "").strip()
    if not key:
        raise RuntimeError("未設定 WECOM_KEY")
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"
    resp = requests.post(
        url,
        json={"msgtype": "markdown", "markdown": {"content": markdown}},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("errcode") != 0:
        raise RuntimeError(f"企業微信推送失敗：{data}")
