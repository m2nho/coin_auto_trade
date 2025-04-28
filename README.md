# 비트코인 자동 거래 프로그램

이 프로젝트는 다양한 소스에서 암호화폐 데이터를 수집하고 지식 베이스를 구축하여 자동화된 거래 결정을 지원하는 시스템입니다.

## 민감한 정보 관리

이 프로젝트는 API 키, 데이터베이스 파일 등 민감한 정보를 포함하고 있습니다. 이러한 정보는 Git 저장소에 포함되지 않도록 `.gitignore` 파일을 통해 관리됩니다.

### 설정 파일 관리

1. `config/config.template.yaml` 파일을 `config/config.yaml`로 복사합니다.
2. 복사한 파일에 실제 API 키와 비밀 정보를 입력합니다.
3. `config/config.yaml` 파일은 `.gitignore`에 의해 Git에 포함되지 않습니다.

```bash
# 설정 파일 템플릿을 복사하여 사용
cp config/config.template.yaml config/config.yaml

# 복사한 파일을 편집하여 실제 API 키 등을 입력
nano config/config.yaml  # 또는 원하는 편집기 사용
```

## 주요 기능

1. Binance에서 실시간 코인 데이터 수집
2. CryptoPanic에서 코인 관련 뉴스 수집
3. 투자 이력 추적 및 분석
4. 수집된 데이터를 통합 지식 베이스로 구성

## 프로젝트 구조

```
bitcoin-trading/
├── .gitignore              # Git에서 제외할 파일 목록
├── config/                 # 설정 파일
│   ├── config.template.yaml # 설정 파일 템플릿
│   └── config.yaml         # 실제 설정 파일 (Git에 포함되지 않음)
├── data_collectors/        # 데이터 수집 모듈
│   ├── binance_collector.py # Binance API 연동 모듈
│   ├── upbit_collector.py  # Upbit API 연동 모듈
│   ├── news_collector.py   # CryptoPanic API 연동 모듈
│   └── history_tracker.py  # 투자 이력 추적 모듈
├── database/               # 데이터베이스 관련 모듈
│   ├── db_manager.py       # 데이터베이스 관리 모듈
│   └── models.py           # 데이터 모델 정의
├── knowledge_base/         # 지식 베이스 모듈
│   ├── kb_manager.py       # 지식 베이스 관리 모듈
│   └── data_processor.py   # 데이터 처리 및 분석 모듈
├── tests/                  # 테스트 코드
│   ├── test_collectors.py  # 데이터 수집 테스트
│   ├── test_database.py    # 데이터베이스 테스트
│   └── test_kb.py          # 지식 베이스 테스트
├── visualization/          # 시각화 모듈
│   ├── dashboard.py        # 대시보드 메인 모듈
│   ├── dashboard_layout.py # 대시보드 레이아웃 정의
│   └── dashboard_callbacks.py # 대시보드 콜백 함수
├── main.py                 # 메인 실행 파일
├── requirements.txt        # 필요한 패키지 목록
└── README.md               # 프로젝트 설명
```

## 상세 프로젝트 계획

### 1. 데이터 수집 단계

#### 1.1 Binance 실시간 데이터 수집
- Binance API를 사용하여 실시간 가격, 거래량, 시장 깊이 등의 데이터 수집
- WebSocket을 통한 실시간 데이터 스트리밍 구현
- 수집된 데이터의 전처리 및 정규화

#### 1.3 CryptoPanic 뉴스 데이터 수집
- CryptoPanic API를 활용한 코인 관련 뉴스 및 소셜 미디어 데이터 수집
- 뉴스 감성 분석 및 중요도 평가
- 코인별 뉴스 분류 및 저장

#### 1.4 투자 이력 추적
- 사용자 거래 내역 기록 및 관리
- 수익률 계산 및 포트폴리오 성과 분석
- 거래 패턴 분석 및 최적화 제안

### 2. 데이터베이스 구축

#### 2.1 데이터 모델 설계
- 코인 가격 데이터 모델
- 뉴스 및 감성 데이터 모델
- 투자 이력 데이터 모델
- 분석 결과 데이터 모델

#### 2.2 데이터베이스 관리
- SQLite 또는 PostgreSQL 데이터베이스 구축
- 효율적인 데이터 저장 및 검색 구조 설계
- 데이터 백업 및 복구 메커니즘

### 3. 지식 베이스 구축

#### 3.1 데이터 통합 및 처리
- 다양한 소스의 데이터 통합
- 시계열 데이터 분석 및 패턴 인식
- 머신러닝 모델을 위한 특성 추출

#### 3.2 지식 표현 및 추론
- 코인 시장 상태에 대한 지식 표현 구조 설계
- 규칙 기반 및 통계적 추론 메커니즘 구현
- 지식 업데이트 및 학습 메커니즘

### 4. 시스템 통합 및 테스트

#### 4.1 모듈 통합
- 데이터 수집, 저장, 분석 모듈의 통합
- 실시간 처리 파이프라인 구축
- 오류 처리 및 복구 메커니즘 구현

#### 4.2 테스트 및 검증
- 단위 테스트 및 통합 테스트 구현
- 백테스팅을 통한 전략 검증
- 성능 및 안정성 테스트

## 설치 및 실행 방법

```bash
# 저장소 복제
git clone https://github.com/username/bitcoin-trading.git
cd bitcoin-trading

# 필요한 패키지 설치
pip install -r requirements.txt

# 설정 파일 준비
cp config/config.template.yaml config/config.yaml
# config/config.yaml 파일을 편집하여 API 키 등 설정

# 프로그램 실행
python3 main.py

# 시각화 대시보드와 함께 실행
python3 main.py --dashboard

# 특정 포트에서 대시보드 실행
python3 main.py --dashboard --dashboard-port 8080

# 대시보드만 별도로 실행
python3 run_dashboard.py

# 데이터베이스 마이그레이션 수동 실행 (필요한 경우)
python3 run_db_migration.py --db-path bitcoin_trading.db
```

## 데이터베이스 마이그레이션

이 프로젝트는 데이터베이스 스키마 변경을 자동으로 처리하는 마이그레이션 시스템을 포함하고 있습니다.

### 자동 마이그레이션

프로그램이 시작될 때 자동으로 데이터베이스 스키마를 확인하고 필요한 경우 마이그레이션을 실행합니다. 이 과정은 다음과 같이 작동합니다:

1. 데이터베이스 파일이 존재하는지 확인
2. 기존 테이블의 스키마를 검사하여 누락된 컬럼이 있는지 확인
3. 누락된 컬럼이 있으면 자동으로 추가
4. 누락된 테이블이 있으면 자동으로 생성

### 수동 마이그레이션

자동 마이그레이션이 실패하거나 수동으로 마이그레이션을 실행해야 하는 경우, 다음 명령을 사용할 수 있습니다:

```bash
python3 run_db_migration.py --db-path 데이터베이스_파일_경로
```

기본적으로 `bitcoin_trading.db` 파일을 대상으로 마이그레이션을 실행합니다.

## 시각화 대시보드

이 프로젝트는 데이터 수집 과정과 결과를 시각적으로 모니터링할 수 있는 대시보드를 제공합니다.

### 대시보드 기능

1. **데이터 수집 상태 모니터링**: Binance, Upbit, 뉴스 데이터 수집 상태를 실시간으로 확인
2. **코인 가격 차트**: 다양한 코인의 가격 추이를 시각적으로 표시
3. **거래량 비교 차트**: 거래소별 거래량 비교
4. **캔들스틱 차트**: 코인의 일봉/분봉 데이터를 캔들스틱 차트로 표시
5. **뉴스 데이터 테이블**: 최근 수집된 뉴스 데이터 표시
6. **데이터 수집 통계**: 데이터 소스별 수집 통계 시각화

### 대시보드 접속 방법

1. 프로그램을 `--dashboard` 옵션과 함께 실행
2. 웹 브라우저에서 `http://localhost:8050` 접속 (포트는 `--dashboard-port` 옵션으로 변경 가능)
3. 또는 `run_dashboard.py` 스크립트를 별도로 실행하여 대시보드만 사용 가능

## 필요한 패키지

- python-binance: Binance API 연동
- pyupbit: Upbit API 연동
- requests: HTTP 요청 처리
- pandas: 데이터 분석 및 처리
- sqlalchemy: 데이터베이스 ORM
- pytest: 테스트 프레임워크
- pyyaml: 설정 파일 처리
- dash: 대시보드 웹 애플리케이션 프레임워크
- plotly: 인터랙티브 시각화 라이브러리
- dash-bootstrap-components: 대시보드 UI 컴포넌트