#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
데이터 수집 시각화 대시보드

이 모듈은 Dash와 Plotly를 사용하여 데이터 수집 과정과 결과를 시각적으로 표시합니다.
- 실시간 코인 가격 차트
- 거래량 데이터 시각화
- 뉴스 데이터 요약
- 데이터 수집 상태 모니터링
"""

import os
import sys
import time
import logging
import threading
import json
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import dash
from dash import dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np

# 내부 모듈 임포트
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager
from database.models import CoinData, CandleData, NewsData
from visualization.dashboard_layout import create_layout
from visualization.dashboard_callbacks import register_all_callbacks
from data_collectors.binance_collector import BinanceDataCollector

logger = logging.getLogger(__name__)

# 전역 변수 - 데이터 캐시
data_cache = {
    "coin_data": {},
    "candle_data": {},
    "news_data": [],
    "websocket_data": {},  # 웹소켓으로부터 받은 실시간 데이터
    "collection_status": {
        "binance": {"last_update": None, "status": "unknown", "count": 0},
        "news": {"last_update": None, "status": "unknown", "count": 0}
        # Upbit 관련 상태 정보 제거됨
    }
}

# 웹소켓 관련 변수
websocket_connections = {}
websocket_data_queue = queue.Queue()
binance_collector = None

# 대시보드 스타일 설정
COLORS = {
    "background": "#f8f9fa",
    "text": "#343a40",
    "binance": "#F0B90B",  # Binance 노란색
    "news": "#28a745",     # 뉴스 녹색
    "positive": "#28a745", # 긍정 녹색
    "negative": "#dc3545", # 부정 빨간색
    "neutral": "#6c757d"   # 중립 회색
}

# 대시보드 앱 초기화
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
app.title = "암호화폐 데이터 수집 대시보드"

# 데이터베이스 관리자 초기화
db_manager = None

def initialize_db_manager(db_path: str) -> None:
    """데이터베이스 관리자를 초기화합니다."""
    global db_manager
    db_manager = DatabaseManager(db_path=db_path, echo=False)
    logger.info("대시보드용 데이터베이스 관리자 초기화 완료")

def initialize_dashboard(db_path: str) -> dash.Dash:
    """
    대시보드를 초기화합니다.
    
    Args:
        db_path: 데이터베이스 파일 경로
        
    Returns:
        초기화된 Dash 앱 객체
    """
    # 데이터베이스 관리자 초기화
    initialize_db_manager(db_path)
    
    # 초기 데이터 로드
    update_data_cache()
    
    # 웹소켓 스트림 시작
    try:
        start_websocket_streams()
        
        # 웹소켓 데이터 처리 스레드 시작
        websocket_thread = threading.Thread(target=process_websocket_data, daemon=True)
        websocket_thread.start()
    except Exception as e:
        logger.error(f"웹소켓 스트림 초기화 실패: {e}")
    
    # 대시보드 레이아웃 설정
    app.layout = create_layout()
    
    # 콜백 등록
    register_all_callbacks(app, data_cache)
    
    # 데이터 업데이트 스레드 시작
    update_thread = threading.Thread(target=data_update_thread, daemon=True)
    update_thread.start()
    
    return app

def get_coin_data(symbols: List[str], hours: int = 24) -> Dict[str, pd.DataFrame]:
    """
    지정된 시간 동안의 코인 데이터를 가져옵니다.
    
    Args:
        symbols: 코인 심볼 목록
        hours: 가져올 데이터의 시간 범위 (시간)
        
    Returns:
        심볼별 코인 데이터 DataFrame 딕셔너리
    """
    if not db_manager:
        logger.error("데이터베이스 관리자가 초기화되지 않았습니다.")
        return {}
        
    result = {}
    session = db_manager.get_session()
    
    try:
        for symbol in symbols:
            # 지정된 시간 이후의 데이터만 가져오기
            start_time = datetime.now() - timedelta(hours=hours)
            
            # 코인 데이터 쿼리
            query = session.query(CoinData).filter(
                CoinData.symbol == symbol,
                CoinData.timestamp >= start_time
            ).order_by(CoinData.timestamp)
            
            # 결과를 DataFrame으로 변환
            rows = []
            for row in query.all():
                rows.append({
                    "timestamp": row.timestamp,
                    "price": row.price,
                    "volume": row.volume,
                    "symbol": row.symbol,
                    "exchange": "Binance"
                })
            
            if rows:
                df = pd.DataFrame(rows)
                result[symbol] = df
                
        return result
        
    except Exception as e:
        logger.error(f"코인 데이터 가져오기 실패: {e}")
        return {}
    finally:
        session.close()

def get_candle_data(symbols: List[str], interval: str = "day", days: int = 30) -> Dict[str, pd.DataFrame]:
    """
    캔들스틱 데이터를 가져옵니다.
    
    Args:
        symbols: 코인 심볼 목록
        interval: 캔들 간격 ("day", "minute30" 등)
        days: 가져올 데이터의 일 수
        
    Returns:
        심볼별 캔들 데이터 DataFrame 딕셔너리
    """
    if not db_manager:
        logger.error("데이터베이스 관리자가 초기화되지 않았습니다.")
        return {}
        
    result = {}
    session = db_manager.get_session()
    
    try:
        for symbol in symbols:
            # 지정된 일 수 이후의 데이터만 가져오기
            start_time = datetime.now() - timedelta(days=days)
            
            # 캔들 데이터 쿼리
            query = session.query(CandleData).filter(
                CandleData.symbol == symbol,
                CandleData.interval == interval,
                CandleData.open_time >= start_time
            ).order_by(CandleData.open_time)
            
            # 결과를 DataFrame으로 변환
            rows = []
            for row in query.all():
                rows.append({
                    "timestamp": row.open_time,
                    "open": row.open,
                    "high": row.high,
                    "low": row.low,
                    "close": row.close,
                    "volume": row.volume,
                    "symbol": row.symbol,
                    "exchange": "Binance"
                })
            
            if rows:
                df = pd.DataFrame(rows)
                result[symbol] = df
                
        return result
        
    except Exception as e:
        logger.error(f"캔들 데이터 가져오기 실패: {e}")
        return {}
    finally:
        session.close()

def calculate_bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    """
    볼린저 밴드를 계산합니다.
    
    Args:
        df: 가격 데이터가 포함된 DataFrame (price 컬럼 필요)
        window: 이동 평균 기간
        num_std: 표준 편차 배수
        
    Returns:
        볼린저 밴드가 추가된 DataFrame
    """
    if df.empty:
        return df
    
    # 이동 평균 계산
    df['middle_band'] = df['price'].rolling(window=window).mean()
    
    # 표준 편차 계산
    rolling_std = df['price'].rolling(window=window).std()
    
    # 상단 밴드와 하단 밴드 계산
    df['upper_band'] = df['middle_band'] + (rolling_std * num_std)
    df['lower_band'] = df['middle_band'] - (rolling_std * num_std)
    
    return df

def get_news_data(hours: int = 24) -> pd.DataFrame:
    """
    지정된 시간 동안의 뉴스 데이터를 가져옵니다.
    
    Args:
        hours: 가져올 데이터의 시간 범위 (시간)
        
    Returns:
        뉴스 데이터 DataFrame
    """
    if not db_manager:
        logger.error("데이터베이스 관리자가 초기화되지 않았습니다.")
        return pd.DataFrame()
        
    session = db_manager.get_session()
    
    try:
        # 지정된 시간 이후의 데이터만 가져오기
        start_time = datetime.now() - timedelta(hours=hours)
        
        # 뉴스 데이터 쿼리
        query = session.query(NewsData).filter(
            NewsData.published_at >= start_time
        ).order_by(NewsData.published_at.desc())
        
        # 결과를 DataFrame으로 변환
        rows = []
        for row in query.all():
            rows.append({
                "id": row.id,
                "external_id": row.external_id,
                "title": row.title,
                "content": row.content if row.content else "내용이 없습니다.",
                "summary": row.summary if row.summary else "요약이 없습니다.",
                "url": row.url,
                "source": row.source_title,
                "source_title": row.source_title,
                "source_domain": row.source_domain,
                "published_at": row.published_at,
                "currency": row.currency
            })
        
        if rows:
            return pd.DataFrame(rows)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"뉴스 데이터 가져오기 실패: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def handle_websocket_message(msg: Dict[str, Any]) -> None:
    """
    웹소켓 메시지를 처리합니다.
    
    Args:
        msg: 웹소켓 메시지
    """
    try:
        # 메시지 타입 확인
        if msg.get('e') == '24hrTicker':
            symbol = msg.get('s')
            price = float(msg.get('c', 0))
            volume = float(msg.get('v', 0))
            timestamp = datetime.now()
            
            # 웹소켓 데이터 큐에 추가
            websocket_data_queue.put({
                "symbol": symbol,
                "price": price,
                "volume": volume,
                "timestamp": timestamp
            })
            
            # 데이터 캐시 업데이트
            if symbol not in data_cache["websocket_data"]:
                data_cache["websocket_data"][symbol] = []
            
            # 최대 1000개의 데이터만 유지
            if len(data_cache["websocket_data"][symbol]) >= 1000:
                data_cache["websocket_data"][symbol].pop(0)
            
            data_cache["websocket_data"][symbol].append({
                "timestamp": timestamp,
                "price": price,
                "volume": volume
            })
            
            logger.debug(f"웹소켓 데이터 수신: {symbol}, 가격: {price}, 거래량: {volume}")
    except Exception as e:
        logger.error(f"웹소켓 메시지 처리 중 오류 발생: {e}")

def start_websocket_streams() -> None:
    """
    웹소켓 스트림을 시작합니다.
    """
    global binance_collector, websocket_connections
    
    try:
        # Binance API 키 (실제 사용 시 환경 변수나 설정 파일에서 가져와야 함)
        api_key = ""
        api_secret = ""
        
        # Binance 심볼 목록
        binance_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOGEUSDT"]
        
        # Binance 데이터 수집기 초기화
        binance_collector = BinanceDataCollector(api_key, api_secret, binance_symbols)
        
        # 웹소켓 스트림 시작
        websocket_connections = binance_collector.start_multiple_websocket_streams(
            binance_symbols, handle_websocket_message
        )
        
        logger.info("웹소켓 스트림 시작 완료")
    except Exception as e:
        logger.error(f"웹소켓 스트림 시작 실패: {e}")

def stop_websocket_streams() -> None:
    """
    웹소켓 스트림을 중지합니다.
    """
    global binance_collector, websocket_connections
    
    try:
        if websocket_connections and "socket_manager" in websocket_connections:
            binance_collector.stop_all_websocket_streams(websocket_connections["socket_manager"])
            websocket_connections = {}
            logger.info("웹소켓 스트림 중지 완료")
    except Exception as e:
        logger.error(f"웹소켓 스트림 중지 실패: {e}")

def update_data_cache() -> None:
    """데이터 캐시를 업데이트합니다."""
    global data_cache
    
    try:
        # Binance 심볼 목록 (Upbit 제외)
        binance_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOGEUSDT"]
        
        # 코인 데이터 가져오기
        coin_data = get_coin_data(binance_symbols, hours=24)
        data_cache["coin_data"] = coin_data
        
        # 캔들 데이터 가져오기
        candle_data = get_candle_data(binance_symbols, interval="day", days=30)
        data_cache["candle_data"] = candle_data
        
        # 뉴스 데이터 가져오기 (제한 없이 모든 데이터 가져오기)
        news_df = get_news_data(hours=72)  # 3일치 데이터
        if not news_df.empty:
            data_cache["news_data"] = news_df.to_dict("records")
        
        # 수집 상태 업데이트
        now = datetime.now()
        
        # Binance 데이터 수집 상태
        binance_count = sum(len(df) for symbol, df in coin_data.items() if "USDT" in symbol)
        if binance_count > 0:
            data_cache["collection_status"]["binance"] = {
                "last_update": now.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "active",
                "count": binance_count
            }
        
        # 뉴스 데이터 수집 상태
        if not news_df.empty:
            data_cache["collection_status"]["news"] = {
                "last_update": now.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "active",
                "count": len(news_df)
            }
            
        logger.debug("데이터 캐시 업데이트 완료")
        
    except Exception as e:
        logger.error(f"데이터 캐시 업데이트 실패: {e}")

def process_websocket_data() -> None:
    """
    웹소켓 데이터를 처리합니다.
    """
    while True:
        try:
            # 큐에서 데이터 가져오기
            while not websocket_data_queue.empty():
                data = websocket_data_queue.get()
                
                # 데이터베이스에 저장 (필요한 경우)
                # save_to_database(data)
                
                # 로깅
                logger.debug(f"웹소켓 데이터 처리: {data['symbol']}, 가격: {data['price']}")
                
            # 잠시 대기
            time.sleep(0.1)
        except Exception as e:
            logger.error(f"웹소켓 데이터 처리 중 오류 발생: {e}")
            time.sleep(1)

def data_update_thread(interval: int = 60) -> None:
    """
    백그라운드에서 주기적으로 데이터를 업데이트하는 스레드 함수
    
    Args:
        interval: 업데이트 간격 (초)
    """
    while True:
        try:
            update_data_cache()
            time.sleep(interval)
        except Exception as e:
            logger.error(f"데이터 업데이트 스레드 오류: {e}")
            time.sleep(10)  # 오류 발생 시 10초 대기 후 재시도

def run_dashboard(host: str = "0.0.0.0", port: int = 8050, debug: bool = False) -> None:
    """
    대시보드를 실행합니다.
    
    Args:
        host: 호스트 주소
        port: 포트 번호
        debug: 디버그 모드 여부
    """
    app.run_server(host=host, port=port, debug=debug)

if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 데이터베이스 경로
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bitcoin_trading.db")
    
    # 대시보드 초기화 및 실행
    initialize_dashboard(db_path)
    run_dashboard(debug=True)

















