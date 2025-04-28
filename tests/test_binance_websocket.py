#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Binance 웹소켓 테스트

이 모듈은 Binance 웹소켓 연결 및 콜백 함수를 테스트합니다.
"""

import os
import sys
import unittest
import logging
from unittest.mock import MagicMock, patch

# 내부 모듈 임포트를 위한 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_collectors.binance_collector import BinanceDataCollector

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestBinanceWebsocket(unittest.TestCase):
    """Binance 웹소켓 테스트 클래스"""

    @patch('binance.streams.BinanceSocketManager')
    @patch('binance.client.Client')
    def test_start_websocket_stream(self, mock_client, mock_socket_manager):
        """웹소켓 스트림 시작 메서드 테스트"""
        # 모의 객체 설정
        mock_bm_instance = MagicMock()
        mock_socket_manager.return_value = mock_bm_instance
        mock_bm_instance.symbol_ticker_socket.return_value = "test_conn_key"
        
        # 콜백 함수 정의
        def mock_callback(msg):
            pass
        
        # BinanceDataCollector 인스턴스 생성
        collector = BinanceDataCollector("test_api_key", "test_api_secret", ["BTCUSDT"])
        
        # 웹소켓 스트림 시작
        bm, conn_key = collector.start_websocket_stream("BTCUSDT", mock_callback)
        
        # 검증
        mock_socket_manager.assert_called_once_with(mock_client.return_value)
        mock_bm_instance.symbol_ticker_socket.assert_called_once_with("BTCUSDT")
        mock_bm_instance._start_socket.assert_called_once_with("test_conn_key", mock_callback)
        self.assertEqual(conn_key, "test_conn_key")
        self.assertEqual(bm, mock_bm_instance)

    @patch('binance.streams.BinanceSocketManager')
    @patch('binance.client.Client')
    def test_start_multiple_websocket_streams(self, mock_client, mock_socket_manager):
        """여러 웹소켓 스트림 시작 메서드 테스트"""
        # 모의 객체 설정
        mock_bm_instance = MagicMock()
        mock_socket_manager.return_value = mock_bm_instance
        mock_bm_instance.symbol_ticker_socket.return_value = "test_conn_key"
        
        # 콜백 함수 정의
        def mock_callback(msg):
            pass
        
        # BinanceDataCollector 인스턴스 생성
        collector = BinanceDataCollector("test_api_key", "test_api_secret", ["BTCUSDT", "ETHUSDT"])
        
        # 여러 웹소켓 스트림 시작
        result = collector.start_multiple_websocket_streams(["BTCUSDT", "ETHUSDT"], mock_callback)
        
        # 검증
        mock_socket_manager.assert_called_once_with(mock_client.return_value)
        self.assertEqual(mock_bm_instance.symbol_ticker_socket.call_count, 2)
        self.assertEqual(mock_bm_instance._start_socket.call_count, 2)
        self.assertEqual(result["socket_manager"], mock_bm_instance)
        self.assertEqual(len(result["connections"]), 2)
        self.assertIn("BTCUSDT", result["connections"])
        self.assertIn("ETHUSDT", result["connections"])

if __name__ == "__main__":
    unittest.main()

