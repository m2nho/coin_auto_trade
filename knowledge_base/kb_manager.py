#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
지식 베이스 관리 모듈

이 모듈은 암호화폐 데이터를 분석하고 지식 베이스를 구축하는 기능을 제공합니다:
- 데이터 통합 및 분석
- 지식 표현 및 저장
- 예측 모델 관리
"""

import logging
import json
import pickle
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union, Tuple

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report

from .data_processor import DataProcessor
from database.db_manager import DatabaseManager
from database.models import KnowledgeItem, PredictionModel, Prediction

logger = logging.getLogger(__name__)


class KnowledgeBaseManager:
    """암호화폐 데이터를 분석하고 지식 베이스를 구축하는 클래스"""
    
    def __init__(self, db_manager: DatabaseManager, config: Dict[str, Any]):
        """
        지식 베이스 관리자 초기화
        
        Args:
            db_manager: 데이터베이스 관리자 인스턴스
            config: 지식 베이스 설정
        """
        self.db_manager = db_manager
        self.config = config
        self.data_processor = DataProcessor()
        self.models_dir = "models"
        
        # 모델 디렉토리가 없으면 생성
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
    
    def update_knowledge_base(self, symbols: List[str]) -> None:
        """
        지식 베이스를 업데이트합니다.
        
        Args:
            symbols: 업데이트할 코인 심볼 목록
        """
        try:
            for symbol in symbols:
                logger.info(f"{symbol} 지식 베이스 업데이트 시작")
                
                # 코인 데이터 가져오기
                coin_data = self.db_manager.get_latest_coin_data(symbol, limit=1000)
                
                # 뉴스 데이터 가져오기
                currency = symbol.replace("USDT", "")
                news_data = self.db_manager.get_latest_news(currency=currency, limit=100)
                
                # 데이터 처리 및 특성 추출
                price_df = self.data_processor.process_price_data(coin_data)
                news_df = self.data_processor.process_news_data(news_data)
                
                if not price_df.empty:
                    price_features = self.data_processor.extract_price_features(price_df)
                    
                    # 가격 특성에서 지식 항목 추출
                    self.extract_price_knowledge(symbol, price_features)
                
                if not news_df.empty:
                    news_features = self.data_processor.extract_news_sentiment_features(news_df)
                    
                    # 뉴스 특성에서 지식 항목 추출
                    self.extract_news_knowledge(symbol, news_features)
                
                # 모델 업데이트
                if not price_df.empty and not news_df.empty:
                    merged_features = self.data_processor.merge_features(price_features, news_features)
                    self.update_prediction_models(symbol, merged_features)
                
                logger.info(f"{symbol} 지식 베이스 업데이트 완료")
                
        except Exception as e:
            logger.error(f"지식 베이스 업데이트 중 오류 발생: {e}")
            raise
    
    def extract_price_knowledge(self, symbol: str, price_features: pd.DataFrame) -> None:
        """
        가격 특성에서 지식 항목을 추출합니다.
        
        Args:
            symbol: 코인 심볼
            price_features: 가격 특성 DataFrame
        """
        try:
            knowledge_items = []
            
            # 최신 데이터 가져오기
            latest_data = price_features.iloc[-1]
            timestamp = latest_data.name.isoformat()
            
            # 가격 변화율 지식 항목
            knowledge_items.append({
                "symbol": symbol,
                "timestamp": timestamp,
                "data_type": "price",
                "feature_name": "price_change_24h",
                "feature_value": float(latest_data.get("price_change_24h", 0)),
                "metadata": {
                    "price": float(latest_data.get("price", 0)),
                    "volume": float(latest_data.get("volume", 0))
                }
            })
            
            # 거래량 변화율 지식 항목
            knowledge_items.append({
                "symbol": symbol,
                "timestamp": timestamp,
                "data_type": "price",
                "feature_name": "volume_change_24h",
                "feature_value": float(latest_data.get("volume_change_24h", 0)),
                "metadata": {
                    "volume": float(latest_data.get("volume", 0))
                }
            })
            
            # 기술적 지표 지식 항목
            for indicator in ["rsi_14", "macd", "macd_hist"]:
                if indicator in latest_data:
                    knowledge_items.append({
                        "symbol": symbol,
                        "timestamp": timestamp,
                        "data_type": "technical",
                        "feature_name": indicator,
                        "feature_value": float(latest_data.get(indicator, 0)),
                        "metadata": {}
                    })
            
            # 이동 평균 교차 지식 항목
            if "ma_20" in latest_data and "ma_50" in latest_data:
                ma_cross = "bullish" if latest_data["ma_20"] > latest_data["ma_50"] else "bearish"
                knowledge_items.append({
                    "symbol": symbol,
                    "timestamp": timestamp,
                    "data_type": "technical",
                    "feature_name": "ma_cross",
                    "feature_text": ma_cross,
                    "metadata": {
                        "ma_20": float(latest_data.get("ma_20", 0)),
                        "ma_50": float(latest_data.get("ma_50", 0))
                    }
                })
            
            # 지식 항목 저장
            self.db_manager.save_knowledge_item(knowledge_items)
            logger.debug(f"{symbol} 가격 지식 항목 {len(knowledge_items)}개 추출 완료")
            
        except Exception as e:
            logger.error(f"가격 지식 추출 중 오류 발생: {e}")
            raise
            
    def extract_news_knowledge(self, symbol: str, news_features: pd.DataFrame) -> None:
        """
        뉴스 특성에서 지식 항목을 추출합니다.
        
        Args:
            symbol: 코인 심볼
            news_features: 뉴스 특성 DataFrame
        """
        try:
            knowledge_items = []
            
            # 최신 데이터가 없으면 종료
            if news_features.empty:
                logger.debug(f"{symbol} 뉴스 데이터 없음")
                return
                
            # 최신 데이터 가져오기
            latest_data = news_features.iloc[-1]
            timestamp = latest_data.name.isoformat()
            
            # 뉴스 감성 지식 항목
            if "sentiment_score" in latest_data:
                knowledge_items.append({
                    "symbol": symbol,
                    "timestamp": timestamp,
                    "data_type": "news",
                    "feature_name": "sentiment_score",
                    "feature_value": float(latest_data.get("sentiment_score", 0)),
                    "metadata": {
                        "news_count": int(latest_data.get("news_count", 0)),
                        "positive_count": int(latest_data.get("positive_count", 0)),
                        "negative_count": int(latest_data.get("negative_count", 0))
                    }
                })
            
            # 뉴스 중요도 지식 항목
            if "importance_score" in latest_data:
                knowledge_items.append({
                    "symbol": symbol,
                    "timestamp": timestamp,
                    "data_type": "news",
                    "feature_name": "importance_score",
                    "feature_value": float(latest_data.get("importance_score", 0)),
                    "metadata": {
                        "news_count": int(latest_data.get("news_count", 0))
                    }
                })
            
            # 지식 항목 저장
            if knowledge_items:
                self.db_manager.save_knowledge_item(knowledge_items)
                logger.debug(f"{symbol} 뉴스 지식 항목 {len(knowledge_items)}개 추출 완료")
            
        except Exception as e:
            logger.error(f"뉴스 지식 추출 중 오류 발생: {e}")
            raise
            
    def update_prediction_models(self, symbol: str, features: pd.DataFrame) -> None:
        """
        예측 모델을 업데이트합니다.
        
        Args:
            symbol: 코인 심볼
            features: 특성 DataFrame
        """
        try:
            # 데이터가 충분하지 않으면 종료
            if len(features) < 30:  # 최소 30개의 데이터 포인트 필요
                logger.debug(f"{symbol} 예측 모델 업데이트를 위한 데이터 부족")
                return
                
            logger.info(f"{symbol} 예측 모델 업데이트 시작")
            
            # 가격 예측 모델 (회귀)
            self._update_price_prediction_model(symbol, features)
            
            # 방향 예측 모델 (분류)
            self._update_direction_prediction_model(symbol, features)
            
            logger.info(f"{symbol} 예측 모델 업데이트 완료")
            
        except Exception as e:
            logger.error(f"예측 모델 업데이트 중 오류 발생: {e}")
            raise
            
    def _update_price_prediction_model(self, symbol: str, features: pd.DataFrame) -> None:
        """
        가격 예측 모델을 업데이트합니다.
        
        Args:
            symbol: 코인 심볼
            features: 특성 DataFrame
        """
        try:
            # 타겟 변수 생성 (24시간 후 가격)
            features['target_price'] = features['price'].shift(-24)  # 24시간 후 가격
            features = features.dropna()  # NaN 값 제거
            
            # 특성 선택
            feature_cols = [
                'price', 'volume', 'price_change_24h', 'volume_change_24h',
                'rsi_14', 'macd', 'macd_hist', 'ma_20', 'ma_50',
                'sentiment_score', 'importance_score'
            ]
            
            # 사용 가능한 특성만 선택
            available_features = [col for col in feature_cols if col in features.columns]
            
            if len(available_features) < 3:  # 최소 3개의 특성 필요
                logger.debug(f"{symbol} 가격 예측 모델을 위한 특성 부족")
                return
                
            X = features[available_features].values
            y = features['target_price'].values
            
            # 학습/테스트 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # 모델 학습
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # 모델 평가
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            # 모델 저장
            model_path = os.path.join(self.models_dir, f"{symbol}_price_prediction.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
                
            # 모델 메타데이터 저장
            session = self.db_manager.get_session()
            try:
                # 기존 모델 비활성화
                existing_models = session.query(PredictionModel).filter_by(
                    name=f"{symbol}_price_prediction",
                    active=True
                ).all()
                
                for existing in existing_models:
                    existing.active = False
                
                # 새 모델 메타데이터 저장
                model_metadata = PredictionModel(
                    name=f"{symbol}_price_prediction",
                    model_type="RandomForestRegressor",
                    target="price_24h",
                    features=json.dumps(available_features),
                    parameters=json.dumps({"n_estimators": 100}),
                    performance=json.dumps({"rmse": float(rmse)}),
                    active=True
                )
                session.add(model_metadata)
                session.commit()
                
            except Exception as e:
                session.rollback()
                raise
            finally:
                session.close()
                
            logger.debug(f"{symbol} 가격 예측 모델 업데이트 완료 (RMSE: {rmse:.4f})")
            
        except Exception as e:
            logger.error(f"가격 예측 모델 업데이트 중 오류 발생: {e}")
            raise
            
    def _update_direction_prediction_model(self, symbol: str, features: pd.DataFrame) -> None:
        """
        가격 방향 예측 모델을 업데이트합니다.
        
        Args:
            symbol: 코인 심볼
            features: 특성 DataFrame
        """
        try:
            # 타겟 변수 생성 (24시간 후 가격 방향)
            features['future_price'] = features['price'].shift(-24)  # 24시간 후 가격
            features['price_direction'] = (features['future_price'] > features['price']).astype(int)  # 1: 상승, 0: 하락
            features = features.dropna()  # NaN 값 제거
            
            # 특성 선택
            feature_cols = [
                'price_change_24h', 'volume_change_24h',
                'rsi_14', 'macd', 'macd_hist',
                'sentiment_score', 'importance_score'
            ]
            
            # 사용 가능한 특성만 선택
            available_features = [col for col in feature_cols if col in features.columns]
            
            if len(available_features) < 3:  # 최소 3개의 특성 필요
                logger.debug(f"{symbol} 방향 예측 모델을 위한 특성 부족")
                return
                
            X = features[available_features].values
            y = features['price_direction'].values
            
            # 학습/테스트 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # 모델 학습
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # 모델 평가
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # 모델 저장
            model_path = os.path.join(self.models_dir, f"{symbol}_direction_prediction.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
                
            # 모델 메타데이터 저장
            session = self.db_manager.get_session()
            try:
                # 기존 모델 비활성화
                existing_models = session.query(PredictionModel).filter_by(
                    name=f"{symbol}_direction_prediction",
                    active=True
                ).all()
                
                for existing in existing_models:
                    existing.active = False
                
                # 새 모델 메타데이터 저장
                model_metadata = PredictionModel(
                    name=f"{symbol}_direction_prediction",
                    model_type="RandomForestClassifier",
                    target="price_direction_24h",
                    features=json.dumps(available_features),
                    parameters=json.dumps({"n_estimators": 100}),
                    performance=json.dumps({"accuracy": float(accuracy)}),
                    active=True
                )
                session.add(model_metadata)
                session.commit()
                
            except Exception as e:
                session.rollback()
                raise
            finally:
                session.close()
                
            logger.debug(f"{symbol} 방향 예측 모델 업데이트 완료 (정확도: {accuracy:.4f})")
            
        except Exception as e:
            logger.error(f"방향 예측 모델 업데이트 중 오류 발생: {e}")
            raise

