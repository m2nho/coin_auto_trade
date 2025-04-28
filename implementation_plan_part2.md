## 4. 아키텍처 설계

### 4.1 전체 아키텍처

새로운 시스템은 다음과 같은 컨테이너화된 마이크로서비스 아키텍처로 구성됩니다:

```
+----------------------------------+
|        Docker Environment        |
|                                  |
|  +-------------+  +------------+ |
|  | Application |  |  Kibana    | |
|  | Container   |  | Container  | |
|  +-------------+  +------------+ |
|         |              |         |
|         v              v         |
|  +-------------+  +------------+ |
|  |Elasticsearch|  |  Logstash  | |
|  | Container   |  | Container  | |
|  +-------------+  +------------+ |
|         |                        |
+---------|------------------------+
          |
          v
+------------------+    +------------------+
| Binance API      |    | AWS Bedrock      |
| (External)       |    | (External)       |
+------------------+    +------------------+
```

### 4.2 구성 요소

1. **애플리케이션 컨테이너**
   - 기존 비트코인 자동 거래 프로그램
   - Elasticsearch 클라이언트 통합
   - AWS Bedrock 클라이언트 통합

2. **Elasticsearch 컨테이너**
   - 데이터 저장 및 인덱싱
   - 검색 및 분석 기능 제공
   - 실시간 데이터 처리

3. **Kibana 컨테이너**
   - Elasticsearch 데이터 시각화
   - 대시보드 및 보고서 생성
   - 사용자 인터페이스 제공

4. **Logstash 컨테이너 (선택사항)**
   - 데이터 수집 및 변환
   - 로그 처리 및 분석
   - 데이터 파이프라인 구성

### 4.3 데이터 흐름

1. **데이터 수집**
   - Binance API에서 코인 데이터 수집
   - CryptoPanic API에서 뉴스 데이터 수집
   - 투자 이력 데이터 생성

2. **데이터 저장**
   - 수집된 데이터를 Elasticsearch에 저장
   - 기존 SQLite 데이터베이스는 백업 또는 마이그레이션 용도로 유지

3. **데이터 분석**
   - Elasticsearch의 분석 기능 활용
   - AWS Bedrock을 통한 고급 AI 분석
   - 분석 결과를 Elasticsearch에 저장

4. **데이터 시각화**
   - Kibana를 통한 데이터 시각화
   - 실시간 대시보드 제공
   - 분석 결과 보고서 생성

## 5. 컨테이너 환경 구성

### 5.1 Docker 구성

#### 5.1.1 Dockerfile

애플리케이션 컨테이너를 위한 Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1

# 애플리케이션 실행
CMD ["python", "main.py"]
```

#### 5.1.2 Docker Compose

다중 컨테이너 환경을 위한 docker-compose.yml:

```yaml
version: '3.8'

services:
  app:
    build: .
    volumes:
      - ./:/app
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - AWS_REGION=ap-northeast-2
    depends_on:
      - elasticsearch
    restart: unless-stopped

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.6.0
    environment:
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms1g -Xmx1g
      - xpack.security.enabled=false
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    restart: unless-stopped

  kibana:
    image: docker.elastic.co/kibana/kibana:8.6.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    restart: unless-stopped

  logstash:
    image: docker.elastic.co/logstash/logstash:8.6.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    depends_on:
      - elasticsearch
    restart: unless-stopped

volumes:
  elasticsearch-data:
```

### 5.2 네트워크 구성

- 모든 컨테이너는 Docker Compose에서 생성한 기본 네트워크를 통해 통신
- Elasticsearch는 9200 포트를 통해 접근 가능
- Kibana는 5601 포트를 통해 접근 가능
- 외부 API 접근은 애플리케이션 컨테이너를 통해 이루어짐

### 5.3 볼륨 구성

- **elasticsearch-data**: Elasticsearch 데이터 영구 저장
- **애플리케이션 볼륨**: 소스 코드 및 설정 파일 마운트
- **로그 볼륨**: 애플리케이션 및 서비스 로그 저장