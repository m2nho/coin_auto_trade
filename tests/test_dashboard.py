#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
대시보드 테스트

이 모듈은 시각화 대시보드의 기능을 테스트합니다.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta

# 상위 디렉토리 추가하여 모듈 임포트 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from visualization.dashboard import (
    get_coin_data, get_candle_data, get_news_data, update_data_cache, initialize_dashboard
)
from database.models import NewsData


class TestDashboard(unittest.TestCase):
    """대시보드 기능 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 테스트용 데이터 생성
        self.mock_coin_data = {
            "BTCUSDT": pd.DataFrame({
                "timestamp": [datetime.now() - timedelta(hours=i) for i in range(24)],
                "price": [50000 - i * 100 for i in range(24)],
                "volume": [100 + i for i in range(24)],
                "symbol": ["BTCUSDT"] * 24,
                "exchange": ["Binance"] * 24
            })
        }
        
        self.mock_candle_data = {
            "BTCUSDT": pd.DataFrame({
                "timestamp": [datetime.now() - timedelta(days=i) for i in range(30)],
                "open": [50000 - i * 100 for i in range(30)],
                "high": [50500 - i * 100 for i in range(30)],
                "low": [49500 - i * 100 for i in range(30)],
                "close": [50200 - i * 100 for i in range(30)],
                "volume": [1000 + i * 10 for i in range(30)],
                "symbol": ["BTCUSDT"] * 30,
                "exchange": ["Binance"] * 30
            })
        }
        
        self.mock_news_data = pd.DataFrame({
            "id": list(range(10)),
            "title": [f"뉴스 제목 {i}" for i in range(10)],
            "content": [f"뉴스 내용 {i}" for i in range(10)],  # 추가된 content 필드
            "summary": [f"뉴스 요약 {i}" for i in range(10)],  # 추가된 summary 필드
            "url": [f"https://example.com/news/{i}" for i in range(10)],
            "source": ["News Source"] * 10,
            "currency": ["BTC"] * 5 + ["ETH"] * 5,
            "published_at": [datetime.now() - timedelta(hours=i) for i in range(10)],
            "sentiment": ["positive"] * 3 + ["neutral"] * 4 + ["negative"] * 3
        })
    
    @patch("visualization.dashboard.db_manager")
    def test_get_coin_data(self, mock_db_manager):
        """코인 데이터 가져오기 테스트"""
        # 모의 세션 설정
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        # 모의 쿼리 결과 설정
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        
        # 빈 결과 반환
        mock_query.all.return_value = []
        
        # 함수 호출
        result = get_coin_data(["BTCUSDT"], hours=24)
        
        # 검증
        self.assertEqual(result, {})
        mock_db_manager.get_session.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch("visualization.dashboard.update_data_cache")
    def test_update_data_cache(self, mock_update):
        """데이터 캐시 업데이트 테스트"""
        # 함수 호출
        update_data_cache()
        
        # 검증
        mock_update.assert_called_once()
    
    def test_data_cache_structure(self):
        """데이터 캐시 구조 테스트"""
        from visualization.dashboard import data_cache
        
        # 데이터 캐시 구조 검증
        self.assertIn("coin_data", data_cache)
        self.assertIn("candle_data", data_cache)
        self.assertIn("news_data", data_cache)
        self.assertIn("collection_status", data_cache)
        
        # 수집 상태 구조 검증 (Upbit 제외)
        self.assertIn("binance", data_cache["collection_status"])
        self.assertIn("news", data_cache["collection_status"])
        # Upbit 관련 검증 제거
    
    @patch("visualization.dashboard.db_manager")
    def test_get_news_data(self, mock_db_manager):
        """뉴스 데이터 가져오기 테스트"""
        # 모의 세션 설정
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        # 모의 뉴스 데이터 생성
        mock_news = []
        for i in range(5):
            news = MagicMock()
            news.id = i
            news.title = f"뉴스 제목 {i}"
            news.content = f"뉴스 내용 {i}"  # content 필드 추가
            news.summary = f"뉴스 요약 {i}"  # summary 필드 추가
            news.url = f"https://example.com/news/{i}"
            news.source = "News Source"
            news.published_at = datetime.now() - timedelta(hours=i)
            news.sentiment = "neutral"
            news.currency = "BTC"
            mock_news.append(news)
        
        # 모의 쿼리 결과 설정
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_news
        
        # 함수 호출
        result = get_news_data(hours=24)
        
        # 검증
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 5)
        self.assertIn("content", result.columns)  # content 컬럼이 있는지 확인
        self.assertIn("summary", result.columns)  # summary 컬럼이 있는지 확인
        mock_db_manager.get_session.assert_called_once()
        mock_session.close.assert_called_once()
    
    def test_news_data_model(self):
        """NewsData 모델 테스트"""
        # NewsData 모델에 content와 summary 필드가 있는지 확인
        news = NewsData()
        self.assertTrue(hasattr(news, 'content'), "NewsData 모델에 content 필드가 없습니다")
        self.assertTrue(hasattr(news, 'summary'), "NewsData 모델에 summary 필드가 없습니다")
    
    @patch("visualization.dashboard.initialize_db_manager")
    @patch("visualization.dashboard.update_data_cache")
    @patch("visualization.dashboard.start_websocket_streams")
    @patch("visualization.dashboard.threading.Thread")
    @patch("visualization.dashboard.register_all_callbacks")
    def test_initialize_dashboard(self, mock_register_callbacks, mock_thread, 
                                 mock_start_websocket, mock_update_cache, mock_init_db):
        """대시보드 초기화 테스트"""
        # 함수 호출
        app = initialize_dashboard("test_db.db")
        
        # 검증
        mock_init_db.assert_called_once_with("test_db.db")
        mock_update_cache.assert_called_once()
        mock_start_websocket.assert_called_once()
        self.assertEqual(mock_thread.call_count, 2)  # 두 개의 스레드가 생성되어야 함
        mock_register_callbacks.assert_called_once()
        
    def test_binance_websocket_import(self):
        """Binance 웹소켓 모듈 임포트 테스트"""
        try:
            from binance.streams import BinanceSocketManager
            self.assertTrue(True)  # 임포트 성공
        except ImportError:
            self.fail("binance.streams 모듈을 임포트할 수 없습니다.")
            
    def test_dash_state_import(self):
        """Dash State 임포트 테스트"""
        try:
            from dash import State
            self.assertTrue(True)  # 임포트 성공
        except ImportError:
            self.fail("dash.State를 임포트할 수 없습니다.")


if __name__ == "__main__":
    unittest.main()








