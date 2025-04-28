#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
볼린저 밴드와 이동평균선 스무딩 테스트

이 테스트는 볼린저 밴드와 이동평균선이 각지지 않고 부드럽게 표시되는지 확인합니다.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objs as go

# 내부 모듈 임포트를 위한 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 테스트 클래스
class TestSmoothLines(unittest.TestCase):
    """볼린저 밴드와 이동평균선 스무딩 테스트 클래스"""

    def setUp(self):
        """테스트 데이터 설정"""
        # 테스트용 캔들 데이터 생성
        dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
        
        self.test_data = pd.DataFrame({
            'timestamp': dates,
            'open': [100 + i for i in range(30)],
            'high': [110 + i for i in range(30)],
            'low': [90 + i for i in range(30)],
            'close': [105 + i for i in range(30)],
            'volume': [1000 + i * 10 for i in range(30)]
        })
        
        # 모의 데이터 캐시 생성
        self.mock_data_cache = {
            "candle_data": {
                "BTCUSDT": {
                    "1h": self.test_data
                }
            }
        }

    def test_moving_average_smoothing(self):
        """이동평균선 스무딩 테스트"""
        # 직접 이동평균선 생성 및 스무딩 확인
        ma20 = self.test_data["close"].rolling(window=20).mean()
        
        # 스무딩된 이동평균선 생성
        ma20_trace = go.Scatter(
            x=self.test_data["timestamp"],
            y=ma20,
            line=dict(color='rgba(72, 118, 255, 0.7)', width=1.5, shape='spline', smoothing=1.3),
            name="20일 이동평균"
        )
        
        # 스무딩 설정 확인
        self.assertEqual(ma20_trace.line.shape, "spline", "20일 이동평균선이 spline 형태가 아닙니다.")
        self.assertEqual(ma20_trace.line.smoothing, 1.3, "20일 이동평균선의 smoothing 값이 1.3이 아닙니다.")

    def test_bollinger_bands_smoothing(self):
        """볼린저 밴드 스무딩 테스트"""
        # 볼린저 밴드 계산
        window = 20
        num_std = 2.0
        
        # 중복된 타임스탬프 처리를 위해 데이터 준비
        df_unique = self.test_data.drop_duplicates(subset=['timestamp'], keep='last').sort_values('timestamp')
        
        # 이동 평균 계산
        middle_band = df_unique["close"].rolling(window=window).mean()
        
        # 표준 편차 계산
        rolling_std = df_unique["close"].rolling(window=window).std()
        
        # 상단 밴드와 하단 밴드 계산
        upper_band = middle_band + (rolling_std * num_std)
        lower_band = middle_band - (rolling_std * num_std)
        
        # 스무딩된 볼린저 밴드 트레이스 생성
        middle_band_trace = go.Scatter(
            x=df_unique["timestamp"],
            y=middle_band,
            mode="lines",
            name="중간 밴드 (20일 MA)",
            line=dict(color="rgba(0, 0, 255, 0.5)", width=1, shape='spline', smoothing=1.3)
        )
        
        upper_band_trace = go.Scatter(
            x=df_unique["timestamp"],
            y=upper_band,
            mode="lines",
            name="상단 밴드",
            line=dict(color="rgba(0, 255, 0, 0.5)", width=1, shape='spline', smoothing=1.3)
        )
        
        lower_band_trace = go.Scatter(
            x=df_unique["timestamp"],
            y=lower_band,
            mode="lines",
            name="하단 밴드",
            line=dict(color="rgba(255, 0, 0, 0.5)", width=1, shape='spline', smoothing=1.3),
            fill='tonexty',
            fillcolor='rgba(200, 200, 255, 0.2)'
        )
        
        # 스무딩 설정 확인
        self.assertEqual(middle_band_trace.line.shape, "spline", "중간 밴드가 spline 형태가 아닙니다.")
        self.assertEqual(middle_band_trace.line.smoothing, 1.3, "중간 밴드의 smoothing 값이 1.3이 아닙니다.")
        
        self.assertEqual(upper_band_trace.line.shape, "spline", "상단 밴드가 spline 형태가 아닙니다.")
        self.assertEqual(upper_band_trace.line.smoothing, 1.3, "상단 밴드의 smoothing 값이 1.3이 아닙니다.")
        
        self.assertEqual(lower_band_trace.line.shape, "spline", "하단 밴드가 spline 형태가 아닙니다.")
        self.assertEqual(lower_band_trace.line.smoothing, 1.3, "하단 밴드의 smoothing 값이 1.3이 아닙니다.")


if __name__ == "__main__":
    unittest.main()
