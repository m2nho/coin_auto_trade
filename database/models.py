#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
데이터베이스 모델 정의

이 모듈은 SQLAlchemy ORM을 사용하여 데이터베이스 모델을 정의합니다:
- 코인 가격 데이터 모델
- 뉴스 데이터 모델
- 투자 이력 데이터 모델
- 지식 베이스 데이터 모델
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class CoinData(Base):
    """코인 가격 데이터 모델"""
    __tablename__ = 'coin_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    price = Column(Float, nullable=False)
    price_change = Column(Float)
    price_change_percent = Column(Float)
    volume = Column(Float)
    quote_volume = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    count = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<CoinData(symbol='{self.symbol}', timestamp='{self.timestamp}', price={self.price})>"


class CandleData(Base):
    """캔들스틱 데이터 모델"""
    __tablename__ = 'candle_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    interval = Column(String(10), nullable=False)
    open_time = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    close_time = Column(DateTime, nullable=False)
    quote_volume = Column(Float)
    trades = Column(Integer)
    taker_buy_base_volume = Column(Float)
    taker_buy_quote_volume = Column(Float)
    value = Column(Float)  # 추가: 거래대금
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<CandleData(symbol='{self.symbol}', interval='{self.interval}', open_time='{self.open_time}')>"


class NewsData(Base):
    """뉴스 데이터 모델"""
    __tablename__ = 'news_data'
    
    id = Column(Integer, primary_key=True)
    external_id = Column(String(100), nullable=False, unique=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)  # 뉴스 본문 내용 (v1.1에서 추가됨)
    summary = Column(Text)  # 뉴스 요약 내용 (v1.1에서 추가됨)
    url = Column(String(1000), nullable=False)
    source_title = Column(String(200))
    source_domain = Column(String(200))
    currency = Column(String(20), nullable=False, index=True)
    published_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)
    votes = Column(JSON)
    sentiment = Column(String(20))
    importance = Column(Float)
    collected_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<NewsData(id={self.id}, title='{self.title[:30]}...', currency='{self.currency}')>"


class Transaction(Base):
    """거래 내역 데이터 모델"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    type = Column(String(10), nullable=False)  # 'buy' 또는 'sell'
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, default=0)
    total = Column(Float, nullable=False)
    exchange = Column(String(100))
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, symbol='{self.symbol}', type='{self.type}', amount={self.amount})>"


class Portfolio(Base):
    """포트폴리오 데이터 모델"""
    __tablename__ = 'portfolio'
    
    symbol = Column(String(20), primary_key=True)
    amount = Column(Float, nullable=False)
    avg_buy_price = Column(Float, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Portfolio(symbol='{self.symbol}', amount={self.amount}, avg_buy_price={self.avg_buy_price})>"


class KnowledgeItem(Base):
    """지식 베이스 항목 모델"""
    __tablename__ = 'knowledge_items'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    data_type = Column(String(50), nullable=False)  # 'price', 'news', 'analysis'
    feature_name = Column(String(100), nullable=False)
    feature_value = Column(Float)
    feature_text = Column(Text)
    meta_info = Column(JSON)  # Renamed from 'metadata' to avoid conflict with SQLAlchemy's reserved name
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<KnowledgeItem(id={self.id}, symbol='{self.symbol}', data_type='{self.data_type}', feature_name='{self.feature_name}')>"


class PredictionModel(Base):
    """예측 모델 메타데이터 모델"""
    __tablename__ = 'prediction_models'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    model_type = Column(String(100), nullable=False)
    target = Column(String(100), nullable=False)
    features = Column(JSON, nullable=False)
    parameters = Column(JSON)
    performance = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<PredictionModel(id={self.id}, name='{self.name}', model_type='{self.model_type}')>"


class Prediction(Base):
    """예측 결과 모델"""
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('prediction_models.id'), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    target = Column(String(100), nullable=False)
    prediction_value = Column(Float)
    prediction_text = Column(Text)
    confidence = Column(Float)
    features_used = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    
    model = relationship("PredictionModel")
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, model_id={self.model_id}, symbol='{self.symbol}', target='{self.target}')>"



