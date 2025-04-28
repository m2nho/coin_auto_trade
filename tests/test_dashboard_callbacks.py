#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
대시보드 콜백 테스트

이 모듈은 대시보드 콜백 함수들을 테스트합니다.
"""

import os
import sys
import unittest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# 내부 모듈 임포트를 위한 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from visualization.dashboard_callbacks import register_candle_chart_callback, register_volume_chart_callback

class TestDashboardCallbacks(unittest.TestCase):
    """대시보드 콜백 테스트 클래스"""

    def setUp(self):
        """테스트 설정"""
        # 모의 앱 객체 생성
        self.mock_app = MagicMock()
        
        # 모의 데이터 캐시 생성
        self.data_cache = {
            "coin_data": {},
            "candle_data": {
                "BTCUSDT": {
                    "1d": pd.DataFrame({
                        "timestamp": [datetime.now() - timedelta(days=i) for i in range(10)],
                        "open": [40000 + i * 100 for i in range(10)],
                        "high": [41000 + i * 100 for i in range(10)],
                        "low": [39000 + i * 100 for i in range(10)],
                        "close": [40500 + i * 100 for i in range(10)],
                        "volume": [1000 + i * 10 for i in range(10)]
                    })
                }
            },
            "news_data": [],
            "websocket_data": {},
            "collection_status": {
                "binance": {"last_update": None, "status": "unknown", "count": 0},
                "news": {"last_update": None, "status": "unknown", "count": 0}
            }
        }

    @patch('visualization.dashboard.calculate_bollinger_bands')
    def test_register_candle_chart_callback(self, mock_calculate_bollinger_bands):
        """캔들 차트 콜백 등록 테스트"""
        # 모의 볼린저 밴드 계산 함수 설정
        mock_df_with_bands = self.data_cache["candle_data"]["BTCUSDT"]["1d"].copy()
        mock_df_with_bands["middle_band"] = mock_df_with_bands["close"]
        mock_df_with_bands["upper_band"] = mock_df_with_bands["close"] * 1.05
        mock_df_with_bands["lower_band"] = mock_df_with_bands["close"] * 0.95
        mock_calculate_bollinger_bands.return_value = mock_df_with_bands
        
        # 콜백 등록
        register_candle_chart_callback(self.mock_app, self.data_cache)
        
        # 검증
        self.mock_app.callback.assert_called_once()
        
        # 콜백 함수 가져오기
        callback_args = self.mock_app.callback.call_args
        callback_function = callback_args[0][0]
        
        # 콜백 함수 실행 - 볼린저 밴드 비활성화
        with patch('visualization.dashboard_callbacks.go') as mock_go:
            mock_figure = MagicMock()
            mock_go.Figure.return_value = mock_figure
            mock_go.Candlestick.return_value = "candlestick_trace"
            
            result = callback_function(1, "BTC", "1d", "off")
            
            # 검증
            self.assertEqual(result, mock_figure)
            mock_go.Figure.assert_called_once()
            mock_figure.add_trace.assert_called_once_with("candlestick_trace")
            mock_calculate_bollinger_bands.assert_not_called()  # 볼린저 밴드 계산이 호출되지 않아야 함
            mock_figure.update_layout.assert_called_once()
        
        # 콜백 함수 실행 - 볼린저 밴드 활성화
        mock_go.reset_mock()
        mock_figure.reset_mock()
        mock_calculate_bollinger_bands.reset_mock()
        
        with patch('visualization.dashboard_callbacks.go') as mock_go:
            mock_figure = MagicMock()
            mock_go.Figure.return_value = mock_figure
            mock_go.Candlestick.return_value = "candlestick_trace"
            mock_go.Scatter.return_value = "scatter_trace"
            
            result = callback_function(1, "BTC", "1d", "on")
            
            # 검증
            self.assertEqual(result, mock_figure)
            mock_go.Figure.assert_called_once()
            mock_calculate_bollinger_bands.assert_called_once()  # 볼린저 밴드 계산이 호출되어야 함
            self.assertEqual(mock_figure.add_trace.call_count, 4)  # 캔들스틱 + 3개의 밴드 라인
            mock_figure.update_layout.assert_called_once()

    def test_register_volume_chart_callback(self):
        """거래량 차트 콜백 등록 테스트"""
        # 콜백 등록
        register_volume_chart_callback(self.mock_app, self.data_cache)
        
        # 검증
        self.mock_app.callback.assert_called_once()
        
        # 콜백 함수 가져오기
        callback_args = self.mock_app.callback.call_args
        callback_function = callback_args[0][0]
        
        # 콜백 함수 실행
        with patch('visualization.dashboard_callbacks.go') as mock_go:
            mock_figure = MagicMock()
            mock_go.Figure.return_value = mock_figure
            mock_go.Bar.return_value = "bar_trace"
            
            result = callback_function(1, "BTC", "1d")
            
            # 검증
            self.assertEqual(result, mock_figure)
            mock_go.Figure.assert_called_once()
            mock_figure.add_trace.assert_called_once_with("bar_trace")
            mock_figure.update_layout.assert_called_once()

if __name__ == "__main__":
    unittest.main()
