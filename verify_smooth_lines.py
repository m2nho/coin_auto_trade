#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
볼린저 밴드와 이동평균선 스무딩 검증 스크립트

이 스크립트는 볼린저 밴드와 이동평균선의 스무딩 효과를 시각적으로 검증하기 위한 차트를 생성합니다.
스무딩이 적용된 차트와 적용되지 않은 차트를 비교할 수 있습니다.
"""

import os
import sys
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# 내부 모듈 임포트를 위한 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def generate_sample_data(days=60):
    """샘플 캔들 데이터를 생성합니다."""
    dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
    
    # 약간의 변동성을 가진 가격 데이터 생성
    base_price = 50000  # 기본 가격 (BTC 기준)
    prices = []
    for i in range(days):
        if i == 0:
            prices.append(base_price)
        else:
            # 이전 가격에서 약간의 변동성 추가
            change = np.random.normal(0, 1) * 200  # 표준 편차 200의 정규 분포
            prices.append(prices[-1] + change)
    
    # 캔들스틱 데이터 생성
    data = []
    for i in range(days):
        price = prices[i]
        open_price = price * (1 + 0.01 * np.random.randn())
        close_price = price * (1 + 0.01 * np.random.randn())
        high_price = max(open_price, close_price) * (1 + 0.005 * abs(np.random.randn()))
        low_price = min(open_price, close_price) * (1 - 0.005 * abs(np.random.randn()))
        volume = price * 0.1 * (1 + 0.5 * np.random.randn())
        
        data.append({
            "timestamp": dates[i],
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": volume if volume > 0 else 100
        })
    
    return pd.DataFrame(data)

def calculate_bollinger_bands(df, window=20, num_std=2.0):
    """볼린저 밴드를 계산합니다."""
    if df.empty:
        return df
    
    # 중복된 timestamp 값이 있는 경우 처리
    # 동일한 timestamp에 대해 마지막 값만 사용
    df_unique = df.drop_duplicates(subset=['timestamp'], keep='last')
    
    # 시간순으로 정렬
    df_unique = df_unique.sort_values('timestamp')
    
    # 이동 평균 계산
    df_unique['middle_band'] = df_unique['close'].rolling(window=window).mean()
    
    # 표준 편차 계산
    rolling_std = df_unique['close'].rolling(window=window).std()
    
    # 상단 밴드와 하단 밴드 계산
    df_unique['upper_band'] = df_unique['middle_band'] + (rolling_std * num_std)
    df_unique['lower_band'] = df_unique['middle_band'] - (rolling_std * num_std)
    
    # 원본 데이터프레임에 계산된 밴드 값 병합
    # 원본 인덱스 보존을 위해 left join 사용
    result = pd.merge(
        df, 
        df_unique[['timestamp', 'middle_band', 'upper_band', 'lower_band']], 
        on='timestamp', 
        how='left'
    )
    
    return result
def create_comparison_chart(df):
    """스무딩이 적용된 차트와 적용되지 않은 차트를 비교하는 차트를 생성합니다."""
    # 볼린저 밴드 계산
    df_bb = calculate_bollinger_bands(df.copy())
    
    # 중복된 타임스탬프 처리를 위해 데이터 준비
    df_unique = df.drop_duplicates(subset=['timestamp'], keep='last').sort_values('timestamp')
    
    # 이동평균 계산
    ma20 = df_unique['close'].rolling(window=20).mean()
    ma50 = df_unique['close'].rolling(window=50).mean()
    
    # 서브플롯 생성 (2행 1열)
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("스무딩 적용 안 됨 (각진 선)", "스무딩 적용됨 (부드러운 선)"),
        vertical_spacing=0.1,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # 첫 번째 서브플롯 (스무딩 없음)
    # 캔들스틱 차트
    fig.add_trace(
        go.Candlestick(
            x=df["timestamp"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="캔들스틱",
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ),
        row=1, col=1
    )
    
    # 이동평균선 (스무딩 없음)
    fig.add_trace(
        go.Scatter(
            x=df_unique["timestamp"],
            y=ma20,
            line=dict(color='rgba(72, 118, 255, 0.7)', width=1.5),  # 스무딩 없음
            name="20일 이동평균 (각진)"
        ),
        row=1, col=1
    )
    
    # 50일 이동평균선 (스무딩 없음)
    fig.add_trace(
        go.Scatter(
            x=df_unique["timestamp"],
            y=ma50,
            line=dict(color='rgba(255, 152, 0, 0.7)', width=1.5),  # 스무딩 없음
            name="50일 이동평균 (각진)"
        ),
        row=1, col=1
    )
    
    # 볼린저 밴드 (스무딩 없음)
    fig.add_trace(
        go.Scatter(
            x=df_unique["timestamp"],
            y=df_unique["close"].rolling(window=20).mean() + df_unique["close"].rolling(window=20).std() * 2.0,
            mode="lines",
            line=dict(color="rgba(0, 255, 0, 0.5)", width=1),  # 스무딩 없음
            name="상단 밴드 (각진)"
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df_unique["timestamp"],
            y=df_unique["close"].rolling(window=20).mean() - df_unique["close"].rolling(window=20).std() * 2.0,
            mode="lines",
            line=dict(color="rgba(255, 0, 0, 0.5)", width=1),  # 스무딩 없음
            name="하단 밴드 (각진)",
            fill='tonexty',
            fillcolor='rgba(200, 200, 255, 0.2)'
        ),
        row=1, col=1
    )
    
    # 두 번째 서브플롯 (스무딩 적용)
    # 캔들스틱 차트
    fig.add_trace(
        go.Candlestick(
            x=df["timestamp"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="캔들스틱",
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ),
        row=2, col=1
    )
    
    # 이동평균선 (스무딩 적용)
    fig.add_trace(
        go.Scatter(
            x=df_unique["timestamp"],
            y=ma20,
            line=dict(color='rgba(72, 118, 255, 0.7)', width=1.5, shape='spline', smoothing=1.3),  # 스무딩 적용
            name="20일 이동평균 (부드러운)"
        ),
        row=2, col=1
    )
    
    # 50일 이동평균선 (스무딩 적용)
    fig.add_trace(
        go.Scatter(
            x=df_unique["timestamp"],
            y=ma50,
            line=dict(color='rgba(255, 152, 0, 0.7)', width=1.5, shape='spline', smoothing=1.3),  # 스무딩 적용
            name="50일 이동평균 (부드러운)"
        ),
        row=2, col=1
    )
    
    # 볼린저 밴드 (스무딩 적용)
    fig.add_trace(
        go.Scatter(
            x=df_unique["timestamp"],
            y=df_unique["close"].rolling(window=20).mean() + df_unique["close"].rolling(window=20).std() * 2.0,
            mode="lines",
            line=dict(color="rgba(0, 255, 0, 0.5)", width=1, shape='spline', smoothing=1.3),  # 스무딩 적용
            name="상단 밴드 (부드러운)"
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df_unique["timestamp"],
            y=df_unique["close"].rolling(window=20).mean() - df_unique["close"].rolling(window=20).std() * 2.0,
            mode="lines",
            line=dict(color="rgba(255, 0, 0, 0.5)", width=1, shape='spline', smoothing=1.3),  # 스무딩 적용
            name="하단 밴드 (부드러운)",
            fill='tonexty',
            fillcolor='rgba(200, 200, 255, 0.2)'
        ),
        row=2, col=1
    )
    
    # 차트 레이아웃 설정
    fig.update_layout(
        title="볼린저 밴드와 이동평균선 스무딩 비교",
        xaxis_title="시간",
        yaxis_title="가격 (USD)",
        template="plotly_white",
        height=1000,  # 높이 설정
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # x축 레이블 숨기기 (첫 번째 서브플롯)
    fig.update_xaxes(showticklabels=False, row=1, col=1)
    
    # 차트 스타일 개선
    fig.update_xaxes(
        gridcolor='rgba(200, 200, 200, 0.2)',
        showgrid=True,
        zeroline=False
    )
    
    fig.update_yaxes(
        gridcolor='rgba(200, 200, 200, 0.2)',
        showgrid=True,
        zeroline=False
    )
    
    return fig


def save_chart_to_html(fig, filename="smooth_lines_comparison.html"):
    """차트를 HTML 파일로 저장합니다."""
    fig.write_html(filename)
    print(f"차트가 {filename}에 저장되었습니다.")

def main():
    """메인 함수"""
    # 샘플 데이터 생성
    df = generate_sample_data(days=60)
    
    # 비교 차트 생성
    fig = create_comparison_chart(df)
    
    # HTML 파일로 저장
    save_chart_to_html(fig)
    
    print("스크립트 실행이 완료되었습니다. HTML 파일을 웹 브라우저에서 열어 결과를 확인하세요.")

if __name__ == "__main__":
    main()



