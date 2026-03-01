# FastAPI 백엔드 Dockerfile
# Python 3.12 slim 이미지 사용

FROM python:3.12-slim

WORKDIR /app

# curl 설치 (healthcheck 용도)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# 의존성 파일 먼저 복사 (Docker 레이어 캐싱 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# uvicorn으로 FastAPI 앱 실행 (핫 리로드 활성화)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
