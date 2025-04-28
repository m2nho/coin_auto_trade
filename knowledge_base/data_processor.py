#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
데이터 처리 모듈

이 모듈은 수집된 암호화폐 데이터를 처리하고 분석하는 기능을 제공합니다:
- 시계열 데이터 처리
- 특성 추출
- 데이터 정규화
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union, Tuple

logger = logging.getLogger(__name__)


class DataProcessor:
    """수집된 암호화폐 데이터를 처리하고 분석하는 클래스"""
    
    def __init__(self):
        """데이터 처리기 초기화"""
        pass
    
    def process_price_data(self, price_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        가격 데이터를 처리하여 DataFrame으로 변환합니다.
        
        Args:
            price_data: 가격 데이터 목록
            
        Returns:
            처리된 가격 데이터 DataFrame
        """
        try:
            # 데이터가 없으면 빈 DataFrame 반환
            if not price_data:
                return pd.DataFrame()
                
            # 리스트를 DataFrame으로 변환
            df = pd.DataFrame(price_data)
            
            # 타임스탬프를 datetime 객체로 변환
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # 시간순으로 정렬
            df = df.sort_values('timestamp')
            
            # 인덱스 설정
            df = df.set_index('timestamp')
            
            return df
            
        except Exception as e:
            logger.error(f"가격 데이터 처리 중 오류 발생: {e}")
            raise
    
    def process_news_data(self, news_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        뉴스 데이터를 처리하여 DataFrame으로 변환합니다.
        
        Args:
            news_data: 뉴스 데이터 목록
            
        Returns:
            처리된 뉴스 데이터 DataFrame
        """
        try:
            # 데이터가 없으면 빈 DataFrame 반환
            if not news_data:
                return pd.DataFrame()
                
            # 리스트를 DataFrame으로 변환
            df = pd.DataFrame(news_data)
            
            # 타임스탬프를 datetime 객체로 변환
            df['published_at'] = pd.to_datetime(df['published_at'])
            
            # 시간순으로 정렬
            df = df.sort_values('published_at')
            
            # 인덱스 설정
            df = df.set_index('published_at')
            
            return df
            
        except Exception as e:
            logger.error(f"뉴스 데이터 처리 중 오류 발생: {e}")
            raise
    
    def extract_price_features(self, price_df: pd.DataFrame) -> pd.DataFrame:
        """
        가격 데이터에서 특성을 추출합니다.
        
        Args:
            price_df: 가격 데이터 DataFrame
            
        Returns:
            특성이 추가된 DataFrame
        """
        try:
            # 데이터가 없으면 빈 DataFrame 반환
            if price_df.empty:
                return pd.DataFrame()
                
            # 복사본 생성
            df = price_df.copy()
            
            # 가격 변화율 계산
            df['price_change_1h'] = df['price'].pct_change(periods=60)  # 1시간 변화율 (1분 간격 데이터 기준)
            df['price_change_24h'] = df['price'].pct_change(periods=1440)  # 24시간 변화율
            
            # 거래량 변화율 계산
            df['volume_change_1h'] = df['volume'].pct_change(periods=60)
            df['volume_change_24h'] = df['volume'].pct_change(periods=1440)
            
            # 이동 평균 계산
            df['ma_5'] = df['price'].rolling(window=5).mean()
            df['ma_20'] = df['price'].rolling(window=20).mean()
            df['ma_50'] = df['price'].rolling(window=50).mean()
            df['ma_200'] = df['price'].rolling(window=200).mean()
            
            # 볼린저 밴드 계산
            df['ma_20_std'] = df['price'].rolling(window=20).std()
            df['upper_band'] = df['ma_20'] + (df['ma_20_std'] * 2)
            df['lower_band'] = df['ma_20'] - (df['ma_20_std'] * 2)
            
            # RSI 계산 (14일)
            delta = df['price'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            df['rsi_14'] = 100 - (100 / (1 + rs))
            
            # MACD 계산
            df['ema_12'] = df['price'].ewm(span=12, adjust=False).mean()
            df['ema_26'] = df['price'].ewm(span=26, adjust=False).mean()
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']
            
            # NaN 값 제거
            df = df.dropna()
            
            return df
            
        except Exception as e:
            logger.error(f"가격 특성 추출 중 오류 발생: {e}")
            raise
    
    def extract_news_sentiment_features(self, news_df: pd.DataFrame, resample_freq: str = '1H') -> pd.DataFrame:
        """
        뉴스 데이터에서 감성 특성을 추출합니다.
        
        Args:
            news_df: 뉴스 데이터 DataFrame
            resample_freq: 리샘플링 빈도 (예: '1H', '1D')
            
        Returns:
            감성 특성 DataFrame
        """
        try:
            # 데이터가 없으면 빈 DataFrame 반환
            if news_df.empty:
                return pd.DataFrame()
                
            # 감성 점수 매핑
            sentiment_map = {
                'positive': 1,
                'neutral': 0,
                'negative': -1
            }
            
            # 감성 점수 변환
            news_df['sentiment_score'] = news_df['sentiment'].map(sentiment_map)
            
            # 중요도로 가중치 부여
            news_df['weighted_sentiment'] = news_df['sentiment_score'] * news_df['importance']
            
            # 시간별 집계
            resampled = news_df.resample(resample_freq)
            
            # 특성 추출
            sentiment_features = pd.DataFrame({
                'news_count': resampled['id'].count(),
                'avg_sentiment': resampled['sentiment_score'].mean(),
                'weighted_sentiment': resampled['weighted_sentiment'].mean(),
                'positive_ratio': resampled['sentiment_score'].apply(lambda x: (x > 0).mean()),
                'negative_ratio': resampled['sentiment_score'].apply(lambda x: (x < 0).mean()),
                'importance_avg': resampled['importance'].mean()
            })
            
            # NaN 값 0으로 채우기
            sentiment_features = sentiment_features.fillna(0)
            
            return sentiment_features
            
        except Exception as e:
            logger.error(f"뉴스 감성 특성 추출 중 오류 발생: {e}")
            raise
    
    def merge_features(self, price_features: pd.DataFrame, news_features: pd.DataFrame) -> pd.DataFrame:
        """
        가격 특성과 뉴스 특성을 병합합니다.
        
        Args:
            price_features: 가격 특성 DataFrame
            news_features: 뉴스 특성 DataFrame
            
        Returns:
            병합된 특성 DataFrame
        """
        try:
            # 둘 중 하나라도 비어있으면 비어있지 않은 것 반환
            if price_features.empty:
                return news_features
            if news_features.empty:
                return price_features
                
            # 인덱스 기준으로 병합
            merged = pd.merge(price_features, news_features, left_index=True, right_index=True, how='outer')
            
            # 뉴스 데이터가 없는 시간대는 0으로 채우기
            for col in news_features.columns:
                if col in merged.columns:
                    merged[col] = merged[col].fillna(0)
            
            # 가격 데이터는 전방 채우기
            for col in price_features.columns:
                if col in merged.columns:
                    merged[col] = merged[col].fillna(method='ffill')
            
            return merged
            
        except Exception as e:
            logger.error(f"특성 병합 중 오류 발생: {e}")
            raise
    
    def normalize_features(self, features_df: pd.DataFrame, method: str = 'minmax') -> pd.DataFrame:
        """
        특성을 정규화합니다.
        
        Args:
            features_df: 특성 DataFrame
            method: 정규화 방법 ('minmax' 또는 'zscore')
            
        Returns:
            정규화된 특성 DataFrame
        """
        try:
            # 데이터가 없으면 빈 DataFrame 반환
            if features_df.empty:
                return pd.DataFrame()
                
            # 복사본 생성
            df = features_df.copy()
            
            # 정규화할 수치형 열 선택
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            
            if method == 'minmax':
                # Min-Max 정규화 (0~1 범위)
                for col in numeric_cols:
                    min_val = df[col].min()
                    max_val = df[col].max()
                    if max_val > min_val:
                        df[col] = (df[col] - min_val) / (max_val - min_val)
            
            elif method == 'zscore':
                # Z-score 정규화 (평균 0, 표준편차 1)
                for col in numeric_cols:
                    mean_val = df[col].mean()
                    std_val = df[col].std()
                    if std_val > 0:
                        df[col] = (df[col] - mean_val) / std_val
            
            return df
            
        except Exception as e:
            logger.error(f"특성 정규화 중 오류 발생: {e}")
            raise
    
    def create_lagged_features(self, df: pd.DataFrame, lag_periods: List[int], columns: List[str] = None) -> pd.DataFrame:
        """
        시계열 데이터에 대한 지연 특성을 생성합니다.
        
        Args:
            df: 원본 DataFrame
            lag_periods: 지연 기간 목록 (예: [1, 2, 3])
            columns: 지연 특성을 생성할 열 목록 (None이면 모든 열)
            
        Returns:
            지연 특성이 추가된 DataFrame
        """
        try:
            # 데이터가 없으면 빈 DataFrame 반환
            if df.empty:
                return pd.DataFrame()
                
            # 복사본 생성
            result_df = df.copy()
            
            # 열 목록이 없으면 모든 수치형 열 사용
            if columns is None:
                columns = df.select_dtypes(include=['float64', 'int64']).columns
            
            # 각 열과 지연 기간에 대해 지연 특성 생성
            for col in columns:
                for lag in lag_periods:
                    result_df[f"{col}_lag_{lag}"] = df[col].shift(lag)
            
            # NaN 값 제거
            result_df = result_df.dropna()
            
            return result_df
            
        except Exception as e:
            logger.error(f"지연 특성 생성 중 오류 발생: {e}")
            raise