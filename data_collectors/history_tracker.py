#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
투자 이력 추적기

이 모듈은 사용자의 암호화폐 투자 이력을 추적하고 관리합니다.
- 거래 내역 기록
- 포트폴리오 성과 분석
- 투자 패턴 분석
"""

import logging
import sqlite3
import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import os

logger = logging.getLogger(__name__)


class InvestmentHistoryTracker:
    """사용자의 암호화폐 투자 이력을 추적하고 관리하는 클래스"""
    
    def __init__(self, db_path: str):
        """
        투자 이력 추적기 초기화
        
        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.conn = None
        self.initialize_db()
        
    def initialize_db(self) -> None:
        """데이터베이스 연결을 초기화하고 필요한 테이블을 생성합니다."""
        try:
            # 데이터베이스 디렉토리가 없으면 생성
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # 거래 내역 테이블 생성
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL,
                fee REAL DEFAULT 0,
                total REAL NOT NULL,
                exchange TEXT,
                note TEXT,
                created_at TEXT NOT NULL
            )
            ''')
            
            # 포트폴리오 테이블 생성
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                symbol TEXT PRIMARY KEY,
                amount REAL NOT NULL,
                avg_buy_price REAL NOT NULL,
                last_updated TEXT NOT NULL
            )
            ''')
            
            self.conn.commit()
            logger.info("투자 이력 데이터베이스 초기화 완료")
            
        except sqlite3.Error as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            raise
    
    def add_transaction(self, symbol: str, type_: str, amount: float, price: float,
                       fee: float = 0, exchange: str = None, note: str = None) -> int:
        """
        새로운 거래 내역을 추가합니다.
        
        Args:
            symbol: 코인 심볼 (예: "BTC")
            type_: 거래 유형 ("buy" 또는 "sell")
            amount: 거래 수량
            price: 거래 가격
            fee: 거래 수수료
            exchange: 거래소 이름
            note: 추가 메모
            
        Returns:
            추가된 거래 내역의 ID
        """
        if not self.conn:
            self.initialize_db()
            
        try:
            cursor = self.conn.cursor()
            
            # 총 거래 금액 계산
            total = amount * price
            if type_.lower() == "buy":
                total = -total - fee
            else:
                total = total - fee
                
            # 현재 시간
            now = datetime.now().isoformat()
            
            # 거래 내역 추가
            cursor.execute('''
            INSERT INTO transactions (timestamp, symbol, type, amount, price, fee, total, exchange, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (now, symbol, type_.lower(), amount, price, fee, total, exchange, note, now))
            
            # 포트폴리오 업데이트
            self.update_portfolio(symbol, type_.lower(), amount, price)
            
            self.conn.commit()
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"거래 내역 추가 실패: {e}")
            raise
    
    def update_portfolio(self, symbol: str, type_: str, amount: float, price: float) -> None:
        """
        포트폴리오를 업데이트합니다.
        
        Args:
            symbol: 코인 심볼 (예: "BTC")
            type_: 거래 유형 ("buy" 또는 "sell")
            amount: 거래 수량
            price: 거래 가격
        """
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            
            # 현재 포트폴리오 상태 조회
            cursor.execute('SELECT amount, avg_buy_price FROM portfolio WHERE symbol = ?', (symbol,))
            result = cursor.fetchone()
            
            if type_ == "buy":
                if result:
                    # 기존 보유량이 있는 경우, 평균 매수가 업데이트
                    current_amount, current_avg_price = result
                    new_amount = current_amount + amount
                    new_avg_price = ((current_amount * current_avg_price) + (amount * price)) / new_amount
                    
                    cursor.execute('''
                    UPDATE portfolio SET amount = ?, avg_buy_price = ?, last_updated = ?
                    WHERE symbol = ?
                    ''', (new_amount, new_avg_price, now, symbol))
                else:
                    # 새로운 코인 추가
                    cursor.execute('''
                    INSERT INTO portfolio (symbol, amount, avg_buy_price, last_updated)
                    VALUES (?, ?, ?, ?)
                    ''', (symbol, amount, price, now))
            
            elif type_ == "sell":
                if result:
                    current_amount, current_avg_price = result
                    new_amount = current_amount - amount
                    
                    if new_amount > 0:
                        # 일부 판매, 평균 매수가는 변경 없음
                        cursor.execute('''
                        UPDATE portfolio SET amount = ?, last_updated = ?
                        WHERE symbol = ?
                        ''', (new_amount, now, symbol))
                    else:
                        # 전량 판매 또는 초과 판매, 포트폴리오에서 제거
                        cursor.execute('DELETE FROM portfolio WHERE symbol = ?', (symbol,))
                else:
                    # 보유하지 않은 코인 판매 (오류 상황)
                    logger.warning(f"보유하지 않은 코인 {symbol} 판매 시도")
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"포트폴리오 업데이트 실패: {e}")
            raise
    
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """
        현재 포트폴리오 상태를 가져옵니다.
        
        Returns:
            포트폴리오 데이터 목록
        """
        if not self.conn:
            self.initialize_db()
            
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT symbol, amount, avg_buy_price, last_updated FROM portfolio')
            
            portfolio = []
            for row in cursor.fetchall():
                symbol, amount, avg_buy_price, last_updated = row
                portfolio.append({
                    "symbol": symbol,
                    "amount": amount,
                    "avg_buy_price": avg_buy_price,
                    "last_updated": last_updated
                })
                
            return portfolio
            
        except sqlite3.Error as e:
            logger.error(f"포트폴리오 조회 실패: {e}")
            raise
    
    def get_transactions(self, symbol: str = None, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        거래 내역을 가져옵니다.
        
        Args:
            symbol: 필터링할 코인 심볼 (선택 사항)
            start_date: 시작 날짜 (ISO 형식, 선택 사항)
            end_date: 종료 날짜 (ISO 형식, 선택 사항)
            
        Returns:
            거래 내역 데이터 목록
        """
        if not self.conn:
            self.initialize_db()
            
        try:
            cursor = self.conn.cursor()
            
            query = 'SELECT * FROM transactions'
            params = []
            
            # 필터 조건 추가
            conditions = []
            if symbol:
                conditions.append('symbol = ?')
                params.append(symbol)
            if start_date:
                conditions.append('timestamp >= ?')
                params.append(start_date)
            if end_date:
                conditions.append('timestamp <= ?')
                params.append(end_date)
                
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
                
            query += ' ORDER BY timestamp DESC'
            
            cursor.execute(query, params)
            
            transactions = []
            for row in cursor.fetchall():
                (id_, timestamp, symbol, type_, amount, price, fee, 
                 total, exchange, note, created_at) = row
                
                transactions.append({
                    "id": id_,
                    "timestamp": timestamp,
                    "symbol": symbol,
                    "type": type_,
                    "amount": amount,
                    "price": price,
                    "fee": fee,
                    "total": total,
                    "exchange": exchange,
                    "note": note,
                    "created_at": created_at
                })
                
            return transactions
            
        except sqlite3.Error as e:
            logger.error(f"거래 내역 조회 실패: {e}")
            raise
    
    def calculate_profit_loss(self, symbol: str = None) -> Dict[str, Any]:
        """
        수익/손실을 계산합니다.
        
        Args:
            symbol: 계산할 코인 심볼 (선택 사항, 없으면 전체 포트폴리오)
            
        Returns:
            수익/손실 데이터
        """
        # 이 기능은 추후 구현 예정
        pass
    
    def import_transactions_from_csv(self, file_path: str) -> int:
        """
        CSV 파일에서 거래 내역을 가져옵니다.
        
        Args:
            file_path: CSV 파일 경로
            
        Returns:
            가져온 거래 내역 수
        """
        # 이 기능은 추후 구현 예정
        pass
    
    def export_transactions_to_csv(self, file_path: str, symbol: str = None) -> int:
        """
        거래 내역을 CSV 파일로 내보냅니다.
        
        Args:
            file_path: CSV 파일 경로
            symbol: 내보낼 코인 심볼 (선택 사항)
            
        Returns:
            내보낸 거래 내역 수
        """
        # 이 기능은 추후 구현 예정
        pass
    
    def update_history(self) -> List[Dict[str, Any]]:
        """
        투자 이력을 업데이트하고 최신 데이터를 반환합니다.
        
        Returns:
            최신 투자 이력 데이터
        """
        # 현재 구현에서는 단순히 포트폴리오 데이터를 반환
        # 실제 구현에서는 외부 거래소 API에서 거래 내역을 가져와 동기화할 수 있음
        return self.get_portfolio()
    
    def close(self) -> None:
        """데이터베이스 연결을 닫습니다."""
        if self.conn:
            self.conn.close()
            self.conn = None