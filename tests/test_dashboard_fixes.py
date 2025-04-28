#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
대시보드 수정사항 테스트

이 모듈은 대시보드 수정사항을 테스트합니다:
1. Binance 웹소켓 연결 테스트
2. 거래량 차트 콜백 테스트
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime, timedelta

# 상위 디렉토리 추가하여 모듈 import 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collectors.binance_collector import BinanceDataCollector
from visualization.dashboard_callbacks import register_volume_chart_callback


class TestBinanceWebsocket(unittest.TestCase):
    """Binance 웹소켓 연결 테스트"""
    
    @patch('binance.streams.BinanceSocketManager')
    @patch('binance.client.Client')
    def test_start_websocket_stream(self, mock_client, mock_socket_manager):
        """웹소켓 스트림 시작 메서드 테스트"""
        # Mock 설정
        mock_bm_instance = MagicMock()
        mock_socket_manager.return_value = mock_bm_instance
        mock_bm_instance.start_symbol_ticker_socket.return_value = "test_conn_key"
        
        # 콜백 함수 정의
        def callback(msg):
            pass
        
        # BinanceDataCollector 인스턴스 생성
        collector = BinanceDataCollector("test_key", "test_secret", ["BTCUSDT"])
        
        # 웹소켓 스트림 시작
        bm, conn_key = collector.start_websocket_stream("BTCUSDT", callback)
        
        # 검증
        mock_bm_instance.start_symbol_ticker_socket.assert_called_once_with("BTCUSDT", callback)
        mock_bm_instance.start.assert_called_once()
        self.assertEqual(conn_key, "test_conn_key")
        self.assertEqual(bm, mock_bm_instance)
    
    @patch('binance.streams.BinanceSocketManager')
    @patch('binance.client.Client')
    def test_start_multiple_websocket_streams(self, mock_client, mock_socket_manager):
        """여러 웹소켓 스트림 시작 메서드 테스트"""
        # Mock 설정
        mock_bm_instance = MagicMock()
        mock_socket_manager.return_value = mock_bm_instance
        mock_bm_instance.start_symbol_ticker_socket.side_effect = ["conn_key1", "conn_key2"]
        
        # 콜백 함수 정의
        def callback(msg):
            pass
        
        # BinanceDataCollector 인스턴스 생성
        collector = BinanceDataCollector("test_key", "test_secret", ["BTCUSDT", "ETHUSDT"])
        
        # 여러 웹소켓 스트림 시작
        result = collector.start_multiple_websocket_streams(["BTCUSDT", "ETHUSDT"], callback)
        
        # 검증
        self.assertEqual(mock_bm_instance.start_symbol_ticker_socket.call_count, 2)
        mock_bm_instance.start.assert_called_once()
        self.assertEqual(result["socket_manager"], mock_bm_instance)
        self.assertEqual(result["connections"]["BTCUSDT"], "conn_key1")
        self.assertEqual(result["connections"]["ETHUSDT"], "conn_key2")


class TestVolumeChartCallback(unittest.TestCase):
    """거래량 차트 콜백 테스트"""
    
    def test_register_volume_chart_callback(self):
        """거래량 차트 콜백 등록 테스트"""
        # Mock Dash 앱 생성
        mock_app = MagicMock()
        
        # 테스트용 데이터 캐시 생성
        data_cache = {
            "candle_data": {
                "BTCUSDT": {
                    "1h": pd.DataFrame({
                        "timestamp": [datetime.now() - timedelta(hours=i) for i in range(10)],
                        "open": [10000 + i * 100 for i in range(10)],
                        "high": [10100 + i * 100 for i in range(10)],
                        "low": [9900 + i * 100 for i in range(10)],
                        "close": [10050 + i * 100 for i in range(10)],
                        "volume": [100 + i * 10 for i in range(10)]
                    })
                }
            }
        }
        
        # 콜백 등록
        register_volume_chart_callback(mock_app, data_cache)
        
        # 검증
        mock_app.callback.assert_called_once()
        
        # 콜백 함수 가져오기
        callback_decorator = mock_app.callback.call_args[0][0]
        self.assertEqual(callback_decorator.component_id, "volume-chart")
        self.assertEqual(callback_decorator.component_property, "figure")


if __name__ == "__main__":
    unittest.main()