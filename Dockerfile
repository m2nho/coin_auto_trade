FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 필요한 Python 패키지 설치
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV ELASTICSEARCH_HOSTS=http://elasticsearch:9200
ENV CONFIG_PATH=/app/config/config.yaml

# 볼륨 설정
VOLUME ["/app/data", "/app/logs"]

# 애플리케이션 실행
CMD ["python", "main.py"]