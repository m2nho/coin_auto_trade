#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Binance 데이터 수집기

이 모듈은 Binance API를 사용하여 실시간 코인 데이터를 수집합니다.
- 실시간 가격 데이터
- 캔들스틱 데이터
- 시장 깊이 데이터
- 거래량 데이터
"""

import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

logger = logging.getLogger(__name__)


class BinanceDataCollector:
    """Binance API를 사용하여 암호화폐 데이터를 수집하는 클래스"""

    def __init__(self, api_key: str, api_secret: str, symbols: List[str]):
        """
        Binance 데이터 수집기 초기화
        
        Args:
            api_key: Binance API 키
            api_secret: Binance API 시크릿
            symbols: 데이터를 수집할 심볼 목록 (예: ["BTCUSDT", "ETHUSDT"])
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.symbols = symbols
        self.client = None
        self.initialize_client()
        
    def initialize_client(self) -> None:
        """Binance API 클라이언트를 초기화합니다."""
        try:
            self.client = Client(self.api_key, self.api_secret)
            # API 연결 테스트
            self.client.ping()
            logger.info("Binance API 클라이언트 초기화 성공")
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Binance API 클라이언트 초기화 실패: {e}")
            raise
            
    def collect_data(self) -> List[Dict[str, Any]]:
        """
        모든 설정된 심볼에 대한 데이터를 수집합니다.
        
        Returns:
            수집된 코인 데이터 목록
        """
        results = []
        
        # 수집할 캔들 간격 목록
        intervals = ["1m", "30m", "1h", "4h", "1d"]
        
        for symbol in self.symbols:
            try:
                # 티커 데이터 수집
                ticker_data = self.get_ticker_data(symbol)
                
                # 각 간격별 캔들스틱 데이터 수집
                candles_by_interval = {}
                for interval in intervals:
                    # 간격에 따라 적절한 데이터 수 조정
                    limit = 100
                    if interval == "1h":
                        limit = 100
                    elif interval == "4h":
                        limit = 100
                    elif interval == "1d":
                        limit = 30  # 30일치 데이터
                    
                    candle_data = self.get_candle_data(symbol, interval=interval, limit=limit)
                    candles_by_interval[interval] = candle_data
                    logger.debug(f"{symbol} {interval} 캔들 데이터 {len(candle_data)}개 수집 완료")
                
                # 데이터 통합
                combined_data = {
                    "symbol": symbol,
                    "timestamp": datetime.now().timestamp(),
                    "ticker": ticker_data,
                    "candles": candles_by_interval
                }
                
                results.append(combined_data)
                logger.info(f"{symbol} 데이터 수집 완료")
                
            except Exception as e:
                logger.error(f"{symbol} 데이터 수집 중 오류 발생: {e}")
                
        return results
    
    def get_ticker_data(self, symbol: str) -> Dict[str, Any]:
        """
        특정 심볼의 티커 데이터를 가져옵니다.
        
        Args:
            symbol: 데이터를 가져올 심볼 (예: "BTCUSDT")
            
        Returns:
            티커 데이터 딕셔너리
        """
        try:
            ticker = self.client.get_ticker(symbol=symbol)
            return {
                "price": float(ticker["lastPrice"]),
                "price_change": float(ticker["priceChange"]),
                "price_change_percent": float(ticker["priceChangePercent"]),
                "volume": float(ticker["volume"]),
                "quote_volume": float(ticker["quoteVolume"]),
                "high_price": float(ticker["highPrice"]),
                "low_price": float(ticker["lowPrice"]),
                "count": int(ticker["count"])
            }
        except Exception as e:
            logger.error(f"{symbol} 티커 데이터 가져오기 실패: {e}")
            raise
    
    def get_candle_data(self, symbol: str, interval: str = "1m", limit: int = 100) -> List[Dict[str, Any]]:
        """
        특정 심볼의 캔들스틱 데이터를 가져옵니다.
        
        Args:
            symbol: 데이터를 가져올 심볼 (예: "BTCUSDT")
            interval: 캔들 간격 (예: "1m", "5m", "1h", "1d")
            limit: 가져올 캔들 수
            
        Returns:
            캔들스틱 데이터 목록
        """
        try:
            candles = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            formatted_candles = []
            for candle in candles:
                formatted_candles.append({
                    "open_time": candle[0],
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5]),
                    "close_time": candle[6],
                    "quote_volume": float(candle[7]),
                    "trades": int(candle[8]),
                    "taker_buy_base_volume": float(candle[9]),
                    "taker_buy_quote_volume": float(candle[10])
                })
                
            return formatted_candles
        except Exception as e:
            logger.error(f"{symbol} 캔들 데이터 가져오기 실패: {e}")
            raise
    
    def get_order_book(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """
        특정 심볼의 주문서 데이터를 가져옵니다.
        
        Args:
            symbol: 데이터를 가져올 심볼 (예: "BTCUSDT")
            limit: 가져올 주문 수
            
        Returns:
            주문서 데이터 딕셔너리
        """
        try:
            order_book = self.client.get_order_book(symbol=symbol, limit=limit)
            return {
                "bids": order_book["bids"],
                "asks": order_book["asks"],
                "timestamp": datetime.now().timestamp()
            }
        except Exception as e:
            logger.error(f"{symbol} 주문서 데이터 가져오기 실패: {e}")
            raise
    
    def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict[str, Any]]:
        """
        특정 심볼의 최근 거래 데이터를 가져옵니다.
        
        Args:
            symbol: 데이터를 가져올 심볼 (예: "BTCUSDT")
            limit: 가져올 거래 수
            
        Returns:
            최근 거래 데이터 목록
        """
        try:
            trades = self.client.get_recent_trades(symbol=symbol, limit=limit)
            return trades
        except Exception as e:
            logger.error(f"{symbol} 최근 거래 데이터 가져오기 실패: {e}")
            raise
    
    def start_websocket_stream(self, symbol: str, callback) -> None:
        """
        웹소켓 스트림을 시작합니다.
        
        Args:
            symbol: 스트림을 시작할 심볼 (예: "BTCUSDT")
            callback: 데이터를 받을 때 호출할 콜백 함수
        """
        try:
            # 소켓 매니저 초기화
            from binance.streams import BinanceSocketManager
            bm = BinanceSocketManager(self.client)
            
            # 심볼에 대한 실시간 가격 스트림 시작
            # 최신 버전의 python-binance 라이브러리에서는 start_symbol_ticker_socket 메서드를 사용
            conn_key = bm.start_symbol_ticker_socket(symbol, callback)
            
            # 웹소켓 시작
            bm.start()
            
            logger.info(f"{symbol} 웹소켓 스트림 시작 성공")
            return bm, conn_key
        except Exception as e:
            logger.error(f"{symbol} 웹소켓 스트림 시작 실패: {e}")
            raise
    
    def start_multiple_websocket_streams(self, symbols: List[str], callback) -> Dict[str, Any]:
        """
        여러 심볼에 대한 웹소켓 스트림을 시작합니다.
        
        Args:
            symbols: 스트림을 시작할 심볼 목록 (예: ["BTCUSDT", "ETHUSDT"])
            callback: 데이터를 받을 때 호출할 콜백 함수
            
        Returns:
            웹소켓 연결 정보 딕셔너리
        """
        try:
            # 소켓 매니저 초기화
            from binance.streams import BinanceSocketManager
            bm = BinanceSocketManager(self.client)
            
            # 연결 정보 저장
            connections = {}
            
            # 각 심볼에 대한 실시간 가격 스트림 시작
            for symbol in symbols:
                # 최신 버전의 python-binance 라이브러리에서는 start_symbol_ticker_socket 메서드를 사용
                conn_key = bm.start_symbol_ticker_socket(symbol, callback)
                connections[symbol] = conn_key
            
            # 웹소켓 시작
            bm.start()
            
            logger.info(f"{len(symbols)}개 심볼에 대한 웹소켓 스트림 시작 성공")
            return {"socket_manager": bm, "connections": connections}
        except Exception as e:
            logger.error(f"웹소켓 스트림 시작 실패: {e}")
            raise
    
    def stop_websocket_stream(self, socket_manager, conn_key) -> None:
        """
        웹소켓 스트림을 중지합니다.
        
        Args:
            socket_manager: BinanceSocketManager 인스턴스
            conn_key: 연결 키
        """
        try:
            socket_manager.stop_socket(conn_key)
            logger.info("웹소켓 스트림 중지 성공")
        except Exception as e:
            logger.error(f"웹소켓 스트림 중지 실패: {e}")
            raise
    
    def stop_all_websocket_streams(self, socket_manager) -> None:
        """
        모든 웹소켓 스트림을 중지합니다.
        
        Args:
            socket_manager: BinanceSocketManager 인스턴스
        """
        try:
            socket_manager.close()
            logger.info("모든 웹소켓 스트림 중지 성공")
        except Exception as e:
            logger.error(f"모든 웹소켓 스트림 중지 실패: {e}")
            raise









