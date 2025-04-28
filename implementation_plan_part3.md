## 6. Elasticsearch 통합

### 6.1 Elasticsearch 인덱스 설계

#### 6.1.1 코인 데이터 인덱스

```json
{
  "mappings": {
    "properties": {
      "symbol": { "type": "keyword" },
      "timestamp": { "type": "date" },
      "price": { "type": "float" },
      "price_change": { "type": "float" },
      "price_change_percent": { "type": "float" },
      "volume": { "type": "float" },
      "quote_volume": { "type": "float" },
      "high_price": { "type": "float" },
      "low_price": { "type": "float" },
      "count": { "type": "integer" }
    }
  },
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1
  }
}
```

#### 6.1.2 뉴스 데이터 인덱스

```json
{
  "mappings": {
    "properties": {
      "external_id": { "type": "keyword" },
      "title": { 
        "type": "text",
        "analyzer": "korean",
        "fields": {
          "keyword": { "type": "keyword", "ignore_above": 256 }
        }
      },
      "url": { "type": "keyword" },
      "source_title": { "type": "keyword" },
      "source_domain": { "type": "keyword" },
      "currency": { "type": "keyword" },
      "published_at": { "type": "date" },
      "created_at": { "type": "date" },
      "votes": { "type": "object" },
      "sentiment": { "type": "keyword" },
      "importance": { "type": "float" },
      "content_vector": { "type": "dense_vector", "dims": 1536 }
    }
  },
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 1
  }
}
```

#### 6.1.3 지식 베이스 인덱스

```json
{
  "mappings": {
    "properties": {
      "symbol": { "type": "keyword" },
      "timestamp": { "type": "date" },
      "data_type": { "type": "keyword" },
      "feature_name": { "type": "keyword" },
      "feature_value": { "type": "float" },
      "feature_text": { "type": "text" },
      "metadata": { "type": "object" }
    }
  },
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1
  }
}
```

### 6.2 Elasticsearch 관리자 모듈

새로운 `database/elasticsearch_manager.py` 모듈을 생성하여 Elasticsearch 연결 및 데이터 관리 기능을 구현합니다:

```python
# 주요 기능
class ElasticsearchManager:
    def __init__(self, hosts, username=None, password=None):
        # Elasticsearch 클라이언트 초기화
        pass
        
    def create_indices(self):
        # 필요한 인덱스 생성
        pass
        
    def save_coin_data(self, data_list):
        # 코인 데이터 저장
        pass
        
    def save_news_data(self, news_list):
        # 뉴스 데이터 저장
        pass
        
    def save_knowledge_item(self, knowledge_items):
        # 지식 베이스 항목 저장
        pass
        
    def search_coin_data(self, query):
        # 코인 데이터 검색
        pass
        
    def search_news(self, query):
        # 뉴스 데이터 검색
        pass
        
    def get_latest_coin_data(self, symbol, limit=1):
        # 최신 코인 데이터 조회
        pass
        
    def get_latest_news(self, currency=None, limit=10):
        # 최신 뉴스 조회
        pass
```

### 6.3 데이터베이스 관리자 확장

기존 `database/db_manager.py` 모듈을 확장하여 Elasticsearch 지원을 추가합니다:

```python
# 주요 변경 사항
class DatabaseManager:
    def __init__(self, db_path, echo=False, es_hosts=None, es_username=None, es_password=None):
        # SQLite 데이터베이스 초기화
        self.db_path = db_path
        self.echo = echo
        self.engine = None
        self.session_factory = None
        self.initialize_db()
        
        # Elasticsearch 관리자 초기화 (선택적)
        self.es_manager = None
        if es_hosts:
            from .elasticsearch_manager import ElasticsearchManager
            self.es_manager = ElasticsearchManager(es_hosts, es_username, es_password)
            self.es_manager.create_indices()
        
    def save_coin_data(self, data_list):
        # SQLite에 저장
        # ...
        
        # Elasticsearch에 저장 (있는 경우)
        if self.es_manager:
            self.es_manager.save_coin_data(data_list)
```

### 6.4 설정 파일 확장

`config/config.yaml` 파일에 Elasticsearch 설정을 추가합니다:

```yaml
# Elasticsearch 설정
elasticsearch:
  enabled: true
  hosts:
    - "http://elasticsearch:9200"
  username: "elastic"
  password: "changeme"
  indices:
    coin_data: "bitcoin_coin_data"
    news_data: "bitcoin_news_data"
    knowledge_items: "bitcoin_knowledge"
    predictions: "bitcoin_predictions"
  settings:
    number_of_shards: 3
    number_of_replicas: 1
```

## 7. AWS Bedrock 통합

### 7.1 AWS Bedrock 개요

AWS Bedrock은 Amazon의 생성형 AI 서비스로, 다양한 기반 모델(foundation models)을 API를 통해 사용할 수 있게 해줍니다. 이 프로젝트에서는 다음과 같은 AWS Bedrock 기능을 활용합니다:

1. **텍스트 생성 및 분석**: Claude, Titan 등의 모델을 사용하여 뉴스 데이터 분석
2. **임베딩 생성**: 텍스트 데이터를 벡터로 변환하여 의미적 검색 지원
3. **감성 분석**: 뉴스 및 소셜 미디어 데이터의 감성 분석

### 7.2 Bedrock 관리자 모듈

새로운 `knowledge_base/bedrock_manager.py` 모듈을 생성하여 AWS Bedrock 연결 및 AI 기능을 구현합니다:

```python
# 주요 기능
class BedrockManager:
    def __init__(self, region, models):
        # AWS Bedrock 클라이언트 초기화
        pass
        
    def analyze_news_sentiment(self, news_text):
        # 뉴스 감성 분석
        pass
        
    def generate_market_insights(self, data):
        # 시장 인사이트 생성
        pass
        
    def create_text_embeddings(self, text):
        # 텍스트 임베딩 생성
        pass
        
    def predict_market_trend(self, data):
        # 시장 동향 예측
        pass
```

### 7.3 지식 베이스 관리자 확장

기존 `knowledge_base/kb_manager.py` 모듈을 확장하여 AWS Bedrock 지원을 추가합니다:

```python
# 주요 변경 사항
class KnowledgeBaseManager:
    def __init__(self, db_manager, config):
        self.db_manager = db_manager
        self.config = config
        self.data_processor = DataProcessor()
        self.models_dir = "models"
        
        # 모델 디렉토리가 없으면 생성
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
            
        # Bedrock 관리자 초기화 (선택적)
        self.bedrock_manager = None
        if 'bedrock' in config and config['bedrock'].get('enabled', False):
            from .bedrock_manager import BedrockManager
            self.bedrock_manager = BedrockManager(
                region=config['bedrock']['region'],
                models=config['bedrock']['models']
            )
    
    def extract_news_knowledge(self, symbol, news_features):
        # 기존 뉴스 지식 추출 로직
        # ...
        
        # Bedrock을 사용한 고급 감성 분석 (있는 경우)
        if self.bedrock_manager and not news_features.empty:
            for idx, row in news_features.iterrows():
                if 'title' in row and 'content' in row:
                    text = f"{row['title']} {row['content']}"
                    sentiment = self.bedrock_manager.analyze_news_sentiment(text)
                    # 감성 분석 결과 저장
                    # ...
```

### 7.4 설정 파일 확장

`config/config.yaml` 파일에 AWS Bedrock 설정을 추가합니다:

```yaml
# AWS Bedrock 설정
bedrock:
  enabled: true
  region: "us-east-1"  # 또는 가용한 리전
  models:
    text_generation: "anthropic.claude-3-sonnet-20240229-v1:0"
    embeddings: "amazon.titan-embed-text-v1"
  parameters:
    max_tokens: 1000
    temperature: 0.7
    top_p: 0.9
```