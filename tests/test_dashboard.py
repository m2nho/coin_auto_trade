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
            
    @patch("visualization.dashboard.db_manager")
    def test_get_candle_data(self, mock_db_manager):
        """캔들스틱 데이터 가져오기 테스트"""
        # 모의 세션 설정
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        # 모의 쿼리 결과 설정
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        
        # 빈 결과 반환 (샘플 데이터 생성 테스트)
        mock_query.all.return_value = []
        
        # 함수 호출
        result = get_candle_data(["BTCUSDT"], interval="1d", days=30)
        
        # 검증
        self.assertIn("BTCUSDT", result)
        self.assertFalse(result["BTCUSDT"].empty)
        self.assertEqual(len(result["BTCUSDT"]), 30)  # 30일치 샘플 데이터
        
        # 필요한 컬럼이 있는지 확인
        required_columns = ["timestamp", "open", "high", "low", "close", "volume"]
        for col in required_columns:
            self.assertIn(col, result["BTCUSDT"].columns)
        
        mock_db_manager.get_session.assert_called_once()
        mock_session.close.assert_called_once()
    
    def test_candlestick_chart_data_format(self):
        """캔들스틱 차트 데이터 형식 테스트"""
        # 샘플 데이터 생성
        sample_data = pd.DataFrame({
            "timestamp": [datetime.now() - timedelta(days=i) for i in range(10)],
            "open": [100 + i for i in range(10)],
            "high": [110 + i for i in range(10)],
            "low": [90 + i for i in range(10)],
            "close": [105 + i for i in range(10)],
            "volume": [1000 + i * 10 for i in range(10)]
        })
        
        # 데이터 형식 검증
        self.assertTrue(isinstance(sample_data["timestamp"][0], datetime))
        self.assertTrue(isinstance(sample_data["open"][0], (int, float)))
        self.assertTrue(isinstance(sample_data["high"][0], (int, float)))
        self.assertTrue(isinstance(sample_data["low"][0], (int, float)))
        self.assertTrue(isinstance(sample_data["close"][0], (int, float)))
        self.assertTrue(isinstance(sample_data["volume"][0], (int, float)))
        
        # 데이터 값 검증
        self.assertTrue(all(sample_data["high"] >= sample_data["open"]))
        self.assertTrue(all(sample_data["high"] >= sample_data["close"]))
        self.assertTrue(all(sample_data["low"] <= sample_data["open"]))
        self.assertTrue(all(sample_data["low"] <= sample_data["close"]))
        self.assertTrue(all(sample_data["volume"] > 0))
    
    @patch("visualization.dashboard.db_manager")
    def test_get_candle_data_with_different_intervals(self, mock_db_manager):
        """다양한 시간 간격의 캔들스틱 데이터 가져오기 테스트"""
        # 모의 세션 설정
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        # 모의 쿼리 결과 설정
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        # 다양한 간격으로 함수 호출
        intervals = ["1d", "4h", "1h", "30m", "15m", "5m", "1m"]
        for interval in intervals:
            result = get_candle_data(["BTCUSDT"], interval=interval, days=10)
            
            # 검증
            self.assertIn("BTCUSDT", result)
            self.assertFalse(result["BTCUSDT"].empty)
            
            # 간격에 따라 데이터 포인트 수가 다른지 확인
            if interval == "1d":
                self.assertLessEqual(len(result["BTCUSDT"]), 10)  # 10일치 데이터
            elif interval == "4h":
                self.assertLessEqual(len(result["BTCUSDT"]), 10 * 6)  # 10일 * 6 (하루에 6개의 4시간 캔들)
            elif interval == "1h":
                self.assertLessEqual(len(result["BTCUSDT"]), 10 * 24)  # 10일 * 24 (하루에 24개의 1시간 캔들)
            elif interval == "30m":
                self.assertLessEqual(len(result["BTCUSDT"]), 10 * 48)  # 10일 * 48 (하루에 48개의 30분 캔들)
            elif interval == "15m":
                self.assertLessEqual(len(result["BTCUSDT"]), 10 * 96)  # 10일 * 96 (하루에 96개의 15분 캔들)
            elif interval == "5m":
                self.assertLessEqual(len(result["BTCUSDT"]), 10 * 288)  # 10일 * 288 (하루에 288개의 5분 캔들)
            elif interval == "1m":
                self.assertLessEqual(len(result["BTCUSDT"]), 10 * 1440)  # 10일 * 1440 (하루에 1440개의 1분 캔들)
            
            # 필요한 컬럼이 있는지 확인
            required_columns = ["timestamp", "open", "high", "low", "close", "volume"]
            for col in required_columns:
                self.assertIn(col, result["BTCUSDT"].columns)
        
        # 세션이 닫혔는지 확인
        self.assertEqual(mock_session.close.call_count, len(intervals))
    
    def test_dash_state_import(self):
        """Dash State 임포트 테스트"""
        try:
            from dash import State
            self.assertTrue(True)  # 임포트 성공
        except ImportError:
            self.fail("dash.State를 임포트할 수 없습니다.")


    def test_dashboard_layout_components(self):
        """대시보드 레이아웃 컴포넌트 테스트"""
        from visualization.dashboard_layout import create_layout
        
        # 대시보드 레이아웃 생성
        layout = create_layout()
        
        # 레이아웃 구조 검증
        self.assertEqual(layout.className, "p-4")
        
        # 가격 차트가 없는지 확인 (삭제됨)
        price_chart_found = False
        for child in layout.children:
            if hasattr(child, 'id') and child.id == 'price-chart':
                price_chart_found = True
                break
        
        self.assertFalse(price_chart_found, "가격 차트가 레이아웃에서 삭제되어야 합니다")
        
        # 캔들스틱 차트가 있는지 확인
        candle_chart_found = False
        for child in layout.children:
            if hasattr(child, 'children'):
                for subchild in child.children:
                    if hasattr(subchild, 'children') and hasattr(subchild.children, 'children'):
                        for component in subchild.children.children:
                            if hasattr(component, 'id') and component.id == 'candle-chart':
                                candle_chart_found = True
                                break
        
        self.assertTrue(candle_chart_found, "캔들스틱 차트가 레이아웃에 있어야 합니다")
    def test_bollinger_bands_calculation(self):
        """볼린저 밴드 계산 테스트"""
        import pandas as pd
        import numpy as np
        from visualization.dashboard import calculate_bollinger_bands
        
        # 테스트 데이터 생성 (캔들스틱 데이터)
        df_candles = pd.DataFrame({
            "timestamp": [datetime.now() - timedelta(days=i) for i in range(30)],
            "open": [100 + i for i in range(30)],
            "high": [110 + i for i in range(30)],
            "low": [90 + i for i in range(30)],
            "close": [105 + i for i in range(30)],
            "volume": [1000 + i * 10 for i in range(30)]
        })
        
        # 볼린저 밴드 계산
        df_bb = calculate_bollinger_bands(df_candles.copy())
        
        # 결과 검증
        self.assertIn("middle_band", df_bb.columns)
        self.assertIn("upper_band", df_bb.columns)
        self.assertIn("lower_band", df_bb.columns)
        
        # 중간 밴드는 20일 이동평균이어야 함
        # 중복 타임스탬프 처리 후 계산되므로 직접 계산한 값과 비교
        df_unique = df_candles.drop_duplicates(subset=['timestamp'], keep='last').sort_values('timestamp')
        expected_middle_band = df_unique["close"].rolling(window=20).mean()
        
        # NaN 값을 제외하고 비교 (20일 이동평균이므로 처음 19개 값은 NaN)
        valid_indices = ~expected_middle_band.isna()
        pd.testing.assert_series_equal(
            df_bb.loc[df_bb["middle_band"].notna(), "middle_band"].reset_index(drop=True),
            expected_middle_band[valid_indices].reset_index(drop=True),
            check_names=False
        )
        
        # 상단 밴드와 하단 밴드 검증
        rolling_std = df_unique["close"].rolling(window=20).std()
        expected_upper_band = expected_middle_band + (rolling_std * 2.0)
        expected_lower_band = expected_middle_band - (rolling_std * 2.0)
        
        pd.testing.assert_series_equal(
            df_bb.loc[df_bb["upper_band"].notna(), "upper_band"].reset_index(drop=True),
            expected_upper_band[valid_indices].reset_index(drop=True),
            check_names=False
        )
        pd.testing.assert_series_equal(
            df_bb.loc[df_bb["lower_band"].notna(), "lower_band"].reset_index(drop=True),
            expected_lower_band[valid_indices].reset_index(drop=True),
            check_names=False
        )
        
        # 중복된 타임스탬프가 있는 경우 테스트
        # 중복 타임스탬프 데이터 생성
        df_duplicates = pd.DataFrame({
            "timestamp": [datetime.now() - timedelta(days=i) for i in range(30)] + 
                        [datetime.now() - timedelta(days=5), datetime.now() - timedelta(days=10)],  # 중복 추가
            "open": [100 + i for i in range(30)] + [200, 300],
            "high": [110 + i for i in range(30)] + [210, 310],
            "low": [90 + i for i in range(30)] + [190, 290],
            "close": [105 + i for i in range(30)] + [205, 305],
            "volume": [1000 + i * 10 for i in range(30)] + [2000, 3000]
        })
        
        # 볼린저 밴드 계산
        df_bb_dup = calculate_bollinger_bands(df_duplicates.copy())
        
        # 결과 검증 - 중복 타임스탬프가 올바르게 처리되었는지 확인
        self.assertEqual(len(df_bb_dup), len(df_duplicates), "원본 데이터프레임 길이가 유지되어야 함")
        
        # 가격 데이터로도 테스트
        df_price = pd.DataFrame({
            "timestamp": [datetime.now() - timedelta(days=i) for i in range(30)],
            "price": [105 + i for i in range(30)]
        })
        
        # 볼린저 밴드 계산
        df_bb_price = calculate_bollinger_bands(df_price.copy())
        
        # 결과 검증
        self.assertIn("middle_band", df_bb_price.columns)
        self.assertIn("upper_band", df_bb_price.columns)
        self.assertIn("lower_band", df_bb_price.columns)


if __name__ == "__main__":
    unittest.main()






