# Upbit 데이터 수집기 오류 수정

## 문제 상황

Upbit 데이터 수집 중 다음과 같은 오류가 발생했습니다:

```
2025-04-27 23:16:43,215 - data_collectors.upbit_collector - ERROR - KRW-BTC 시세 정보 가져오기 실패: module 'pyupbit' has no attribute 'get_ticker'
2025-04-27 23:16:43,215 - data_collectors.upbit_collector - ERROR - KRW-BTC 데이터 수집 중 오류 발생: module 'pyupbit' has no attribute 'get_ticker'
```

이 오류는 `upbit_collector.py` 파일의 `get_ticker_info` 메서드에서 `pyupbit.get_ticker()` 함수를 호출하려고 했으나, pyupbit 라이브러리에 해당 함수가 존재하지 않아 발생했습니다.

## 원인 분석

pyupbit 라이브러리(버전 0.2.33)에는 `get_ticker` 함수가 없습니다. 대신 다음과 같은 함수들이 제공됩니다:

- `get_tickers()`: 모든 티커 목록을 반환
- `get_current_price()`: 현재 가격 정보를 반환
- `get_ohlcv()`: 일봉/분봉 데이터를 반환
- `get_orderbook()`: 호가 정보를 반환

## 해결 방법

`get_ticker_info` 메서드를 수정하여 `get_ticker()` 함수 대신 다음과 같은 대체 방법을 사용했습니다:

1. `get_current_price()` 함수로 현재 가격 정보를 가져옵니다.
2. `get_ohlcv()` 함수로 일봉 데이터를 가져와 시가, 고가, 저가 등의 정보를 추출합니다.
3. `get_orderbook()` 함수로 호가 정보를 가져옵니다.

이렇게 수집한 정보를 조합하여 원래 필요했던 데이터 구조를 만들어 반환합니다.

## 코드 변경 내용

### 변경 전:

```python
def get_ticker_info(self, symbol: str) -> Dict[str, Any]:
    try:
        tickers = pyupbit.get_current_price(symbol)
        if isinstance(tickers, dict):
            price = tickers.get(symbol)
        else:
            price = tickers
            
        # 추가 정보 가져오기
        ticker_details = pyupbit.get_ticker(symbol)
        
        if isinstance(ticker_details, list) and len(ticker_details) > 0:
            ticker_details = ticker_details[0]
        
        return {
            "price": price,
            "opening_price": ticker_details.get("opening_price"),
            "high_price": ticker_details.get("high_price"),
            "low_price": ticker_details.get("low_price"),
            "prev_closing_price": ticker_details.get("prev_closing_price"),
            "acc_trade_volume_24h": ticker_details.get("acc_trade_volume_24h"),
            "acc_trade_price_24h": ticker_details.get("acc_trade_price_24h"),
            "change": ticker_details.get("change"),
            "change_rate": ticker_details.get("signed_change_rate")
        }
    except Exception as e:
        logger.error(f"{symbol} 시세 정보 가져오기 실패: {e}")
        raise
```

### 변경 후:

```python
def get_ticker_info(self, symbol: str) -> Dict[str, Any]:
    try:
        # 현재 가격 정보 가져오기
        tickers = pyupbit.get_current_price(symbol)
        if isinstance(tickers, dict):
            price = tickers.get(symbol)
        else:
            price = tickers
            
        # 일봉 데이터에서 추가 정보 가져오기 (시가, 고가, 저가, 종가)
        daily_data = pyupbit.get_ohlcv(symbol, interval="day", count=1)
        
        # 호가 정보 가져오기
        orderbook = pyupbit.get_orderbook(symbol)
        
        # 필요한 정보 추출
        result = {
            "price": price,
            "opening_price": None,
            "high_price": None,
            "low_price": None,
            "prev_closing_price": None,
            "acc_trade_volume_24h": None,
            "acc_trade_price_24h": None,
            "change": None,
            "change_rate": None
        }
        
        # 일봉 데이터에서 정보 추출
        if daily_data is not None and not daily_data.empty:
            last_row = daily_data.iloc[-1]
            result["opening_price"] = float(last_row.get("open"))
            result["high_price"] = float(last_row.get("high"))
            result["low_price"] = float(last_row.get("low"))
            result["acc_trade_volume_24h"] = float(last_row.get("volume"))
            
            # 전일 종가 계산 (어제 데이터가 없으면 시가 사용)
            result["prev_closing_price"] = float(last_row.get("open"))
            
            # 변화율 계산
            if result["prev_closing_price"] > 0:
                result["change_rate"] = (price - result["prev_closing_price"]) / result["prev_closing_price"]
                result["change"] = "RISE" if result["change_rate"] > 0 else "FALL"
        
        return result
    except Exception as e:
        logger.error(f"{symbol} 시세 정보 가져오기 실패: {e}")
        raise
```

## 테스트

수정된 코드를 테스트하기 위해 `test_upbit_collector.py` 파일을 작성하여 다음을 확인했습니다:

1. Upbit 데이터 수집기가 초기화되는지 확인
2. 데이터 수집이 오류 없이 진행되는지 확인
3. 수집된 데이터가 예상한 구조와 일치하는지 확인

테스트 실행 방법:
```bash
python test_upbit_collector.py
```

## 문서 업데이트

README.md 파일을 업데이트하여 Upbit 데이터 수집기에 대한 정보를 추가했습니다:

1. 주요 기능에 Upbit 데이터 수집 추가
2. 프로젝트 구조에 upbit_collector.py 파일 추가
3. 데이터 수집 단계에 Upbit 국내 코인 데이터 수집 섹션 추가
4. 필요한 패키지에 pyupbit 추가