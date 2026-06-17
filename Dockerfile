FROM python:3.12-slim

ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

# 預設行為：推一次後結束（給 CronJob / kubectl create job 用）
# 要跑常駐 HTTP 服務時，部署改 command 為：
#   uvicorn app.server:app --host 0.0.0.0 --port 8080
ENTRYPOINT ["python", "-m", "app.cli"]
