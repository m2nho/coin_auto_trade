#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
데이터베이스 관리 모듈

이 모듈은 데이터베이스 연결 및 데이터 관리 기능을 제공합니다:
- 데이터베이스 연결 설정
- 데이터 저장 및 검색
- 데이터베이스 백업 및 복구
"""

import logging
import os
import json
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from .models import Base, CoinData, CandleData, NewsData, Transaction, Portfolio, KnowledgeItem, PredictionModel, Prediction
from .db_migration import migrate_database

logger = logging.getLogger(__name__)


class DatabaseManager:
    """데이터베이스 연결 및 데이터 관리를 담당하는 클래스"""
    
    def __init__(self, db_path: str, echo: bool = False):
        """
        데이터베이스 관리자 초기화
        
        Args:
            db_path: 데이터베이스 파일 경로
            echo: SQL 쿼리 로깅 여부
        """
        self.db_path = db_path
        self.echo = echo
        self.engine = None
        self.session_factory = None
        self.initialize_db()
        
    def initialize_db(self) -> None:
        """데이터베이스 연결을 초기화하고 필요한 테이블을 생성합니다."""
        try:
            # 데이터베이스 디렉토리가 없으면 생성
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                
            # 데이터베이스 파일이 이미 존재하는 경우 마이그레이션 실행
            if os.path.exists(self.db_path):
                logger.info("기존 데이터베이스 파일 발견, 마이그레이션 실행 중...")
                migrate_database(self.db_path)
                
            # SQLite 데이터베이스 연결 설정
            self.engine = create_engine(f"sqlite:///{self.db_path}", echo=self.echo)
            
            # 테이블 생성
            Base.metadata.create_all(self.engine)
            
            # 세션 팩토리 생성
            self.session_factory = scoped_session(sessionmaker(bind=self.engine))
            
            logger.info("데이터베이스 초기화 완료")
            
        except SQLAlchemyError as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            raise
    
    def get_session(self):
        """데이터베이스 세션을 반환합니다."""
        if not self.session_factory:
            self.initialize_db()
        return self.session_factory()
    
    def save_coin_data(self, data_list: List[Dict[str, Any]]) -> None:
        """
        코인 데이터를 저장합니다.
        
        Args:
            data_list: 코인 데이터 목록
        """
        session = self.get_session()
        try:
            for data in data_list:
                # 티커 데이터 저장
                ticker = data.get("ticker", {})
                if ticker:
                    coin_data = CoinData(
                        symbol=data["symbol"],
                        timestamp=datetime.fromtimestamp(data["timestamp"]),
                        price=ticker["price"],
                        price_change=ticker.get("price_change"),
                        price_change_percent=ticker.get("price_change_percent"),
                        volume=ticker.get("volume"),
                        quote_volume=ticker.get("quote_volume"),
                        high_price=ticker.get("high_price"),
                        low_price=ticker.get("low_price"),
                        count=ticker.get("count")
                    )
                    session.add(coin_data)
                
                # 캔들 데이터 저장 (Binance 형식)
                candles = data.get("candles", [])
                for candle in candles:
                    candle_data = CandleData(
                        symbol=data["symbol"],
                        interval="1m",  # Binance 기본 간격
                        open_time=datetime.fromtimestamp(candle["open_time"] / 1000),  # 밀리초를 초로 변환
                        open=candle["open"],
                        high=candle["high"],
                        low=candle["low"],
                        close=candle["close"],
                        volume=candle["volume"],
                        close_time=datetime.fromtimestamp(candle["close_time"] / 1000),  # 밀리초를 초로 변환
                        quote_volume=candle.get("quote_volume"),
                        trades=candle.get("trades"),
                        taker_buy_base_volume=candle.get("taker_buy_base_volume"),
                        taker_buy_quote_volume=candle.get("taker_buy_quote_volume"),
                        value=None  # Binance API에서는 제공하지 않음
                    )
                    session.add(candle_data)
            
            session.commit()
            logger.debug(f"{len(data_list)} 개의 코인 데이터 저장 완료")
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"코인 데이터 저장 실패: {e}")
            raise
        finally:
            session.close()
    
    def save_news_data(self, news_list: List[Dict[str, Any]]) -> None:
        """
        뉴스 데이터를 저장합니다.
        
        Args:
            news_list: 뉴스 데이터 목록
        """
        session = self.get_session()
        try:
            for news in news_list:
                # 이미 존재하는 뉴스인지 확인
                existing = session.query(NewsData).filter_by(external_id=str(news["id"])).first()
                if existing:
                    continue
                    
                # 새 뉴스 데이터 저장
                news_data = NewsData(
                    external_id=str(news["id"]),
                    title=news["title"],
                    content=news.get("content"),  # Added content field
                    summary=news.get("summary"),  # Added summary field
                    url=news["url"],
                    source_title=news.get("source_title"),
                    source_domain=news.get("source_domain"),
                    currency=news["currency"],
                    published_at=datetime.fromisoformat(news["published_at"].replace("Z", "+00:00")),
                    created_at=datetime.fromisoformat(news["created_at"].replace("Z", "+00:00")),
                    votes=json.dumps(news.get("votes", {})),
                    sentiment=news.get("sentiment"),
                    importance=news.get("importance"),
                    collected_at=datetime.fromisoformat(news["collected_at"])
                )
                session.add(news_data)
            
            session.commit()
            logger.debug(f"{len(news_list)} 개의 뉴스 데이터 저장 완료")
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"뉴스 데이터 저장 실패: {e}")
            raise
        finally:
            session.close()
    
    def save_history_data(self, portfolio_list: List[Dict[str, Any]]) -> None:
        """
        포트폴리오 데이터를 저장합니다.
        
        Args:
            portfolio_list: 포트폴리오 데이터 목록
        """
        session = self.get_session()
        try:
            for item in portfolio_list:
                # 이미 존재하는 포트폴리오 항목인지 확인
                existing = session.query(Portfolio).filter_by(symbol=item["symbol"]).first()
                
                if existing:
                    # 기존 항목 업데이트
                    existing.amount = item["amount"]
                    existing.avg_buy_price = item["avg_buy_price"]
                    existing.last_updated = datetime.fromisoformat(item["last_updated"])
                else:
                    # 새 포트폴리오 항목 추가
                    portfolio = Portfolio(
                        symbol=item["symbol"],
                        amount=item["amount"],
                        avg_buy_price=item["avg_buy_price"],
                        last_updated=datetime.fromisoformat(item["last_updated"])
                    )
                    session.add(portfolio)
            
            session.commit()
            logger.debug(f"{len(portfolio_list)} 개의 포트폴리오 데이터 저장 완료")
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"포트폴리오 데이터 저장 실패: {e}")
            raise
        finally:
            session.close()
            
    def save_knowledge_item(self, knowledge_items: List[Dict[str, Any]]) -> None:
        """
        지식 베이스 항목을 저장합니다.
        
        Args:
            knowledge_items: 지식 베이스 항목 목록
        """
        session = self.get_session()
        try:
            for item in knowledge_items:
                knowledge_item = KnowledgeItem(
                    symbol=item["symbol"],
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    data_type=item["data_type"],
                    feature_name=item["feature_name"],
                    feature_value=item.get("feature_value"),
                    feature_text=item.get("feature_text"),
                    meta_info=json.dumps(item.get("metadata", {}))  # Use meta_info instead of metadata
                )
                session.add(knowledge_item)
            
            session.commit()
            logger.debug(f"{len(knowledge_items)} 개의 지식 베이스 항목 저장 완료")
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"지식 베이스 항목 저장 실패: {e}")
            raise
        finally:
            session.close()
    
    def get_latest_coin_data(self, symbol: str, limit: int = 1) -> List[Dict[str, Any]]:
        """
        특정 심볼의 최신 코인 데이터를 가져옵니다.
        
        Args:
            symbol: 코인 심볼
            limit: 가져올 데이터 수
            
        Returns:
            최신 코인 데이터 목록
        """
        session = self.get_session()
        try:
            results = session.query(CoinData).filter_by(symbol=symbol).order_by(desc(CoinData.timestamp)).limit(limit).all()
            
            data_list = []
            for result in results:
                data_list.append({
                    "id": result.id,
                    "symbol": result.symbol,
                    "timestamp": result.timestamp.isoformat(),
                    "price": result.price,
                    "price_change": result.price_change,
                    "price_change_percent": result.price_change_percent,
                    "volume": result.volume,
                    "quote_volume": result.quote_volume,
                    "high_price": result.high_price,
                    "low_price": result.low_price,
                    "count": result.count
                })
                
            return data_list
            
        except SQLAlchemyError as e:
            logger.error(f"코인 데이터 조회 실패: {e}")
            raise
        finally:
            session.close()
    
    def get_latest_news(self, currency: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 뉴스를 가져옵니다.
        
        Args:
            currency: 필터링할 통화 (선택 사항)
            limit: 가져올 뉴스 수
            
        Returns:
            최신 뉴스 목록
        """
        session = self.get_session()
        try:
            query = session.query(NewsData).order_by(desc(NewsData.published_at))
            
            if currency:
                query = query.filter_by(currency=currency)
                
            results = query.limit(limit).all()
            
            news_list = []
            for result in results:
                news_list.append({
                    "id": result.id,
                    "external_id": result.external_id,
                    "title": result.title,
                    "content": result.content,  # Added content field
                    "summary": result.summary,  # Added summary field
                    "url": result.url,
                    "source_title": result.source_title,
                    "source_domain": result.source_domain,
                    "currency": result.currency,
                    "published_at": result.published_at.isoformat(),
                    "created_at": result.created_at.isoformat(),
                    "votes": json.loads(result.votes) if result.votes else {},
                    "sentiment": result.sentiment,
                    "importance": result.importance
                })
                
            return news_list
            
        except SQLAlchemyError as e:
            logger.error(f"뉴스 데이터 조회 실패: {e}")
            raise
        finally:
            session.close()
    
    def backup_database(self, backup_path: str) -> str:
        """
        데이터베이스를 백업합니다.
        
        Args:
            backup_path: 백업 파일 저장 경로
            
        Returns:
            백업 파일 경로
        """
        try:
            # 백업 디렉토리가 없으면 생성
            if not os.path.exists(backup_path):
                os.makedirs(backup_path)
                
            # 백업 파일 이름 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_path, f"backup_{timestamp}.db")
            
            # 데이터베이스 파일 복사
            shutil.copy2(self.db_path, backup_file)
            
            logger.info(f"데이터베이스 백업 완료: {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"데이터베이스 백업 실패: {e}")
            raise
    
    def close(self) -> None:
        """데이터베이스 연결을 닫습니다."""
        if self.session_factory:
            self.session_factory.remove()
            logger.info("데이터베이스 연결 닫힘")






