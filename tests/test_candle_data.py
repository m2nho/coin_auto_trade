#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
캔들스틱 데이터 수집 및 저장 테스트

이 모듈은 다양한 간격의 캔들스틱 데이터가 올바르게 수집되고 저장되는지 테스트합니다.
"""

import os
import sys
import unittest
import tempfile
from datetime import datetime, timedelta

# 내부 모듈 임포트를 위한 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collectors.binance_collector import BinanceDataCollector
from database.db_manager import DatabaseManager
from database.models import CandleData


class TestCandleData(unittest.TestCase):
    """캔들스틱 데이터 수집 및 저장 테스트 클래스"""

    def setUp(self):
        """테스트 환경 설정"""
        # 임시 데이터베이스 파일 생성
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        
        # 데이터베이스 관리자 초기화
        self.db_manager = DatabaseManager(db_path=self.temp_db.name, echo=False)
        
        # Binance 수집기 초기화 (API 키 없이 테스트 모드로)
        self.symbols = ["BTCUSDT"]
        self.binance_collector = BinanceDataCollector(api_key="", api_secret="", symbols=self.symbols)
    
    def tearDown(self):
        """테스트 환경 정리"""
        # 데이터베이스 연결 종료
        self.db_manager.close()
        
        # 임시 데이터베이스 파일 삭제
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_collect_multiple_interval_candles(self):
        """여러 간격의 캔들스틱 데이터 수집 테스트"""
        try:
            # 데이터 수집
            data = self.binance_collector.collect_data()
            
            # 데이터가 수집되었는지 확인
            self.assertTrue(len(data) > 0, "데이터가 수집되지 않았습니다.")
            
            # 첫 번째 심볼의 데이터 확인
            symbol_data = data[0]
            self.assertEqual(symbol_data["symbol"], self.symbols[0], "심볼이 일치하지 않습니다.")
            
            # 캔들 데이터가 딕셔너리 형태로 저장되었는지 확인
            self.assertIsInstance(symbol_data["candles"], dict, "캔들 데이터가 딕셔너리 형태가 아닙니다.")
            
            # 모든 간격의 캔들 데이터가 있는지 확인
            expected_intervals = ["1m", "30m", "1h", "4h", "1d"]
            for interval in expected_intervals:
                self.assertIn(interval, symbol_data["candles"], f"{interval} 간격의 캔들 데이터가 없습니다.")
                self.assertTrue(len(symbol_data["candles"][interval]) > 0, f"{interval} 간격의 캔들 데이터가 비어 있습니다.")
            
            # 데이터베이스에 저장
            self.db_manager.save_coin_data(data)
            
            # 데이터베이스에서 캔들 데이터 조회
            session = self.db_manager.get_session()
            try:
                for interval in expected_intervals:
                    candles = session.query(CandleData).filter_by(
                        symbol=self.symbols[0], 
                        interval=interval
                    ).all()
                    
                    self.assertTrue(len(candles) > 0, f"{interval} 간격의 캔들 데이터가 데이터베이스에 저장되지 않았습니다.")
                    
                    # 첫 번째 캔들 데이터 확인
                    candle = candles[0]
                    self.assertEqual(candle.symbol, self.symbols[0], "심볼이 일치하지 않습니다.")
                    self.assertEqual(candle.interval, interval, "간격이 일치하지 않습니다.")
                    self.assertIsNotNone(candle.open, "시가가 없습니다.")
                    self.assertIsNotNone(candle.high, "고가가 없습니다.")
                    self.assertIsNotNone(candle.low, "저가가 없습니다.")
                    self.assertIsNotNone(candle.close, "종가가 없습니다.")
                    self.assertIsNotNone(candle.volume, "거래량이 없습니다.")
            finally:
                session.close()
                
        except Exception as e:
            self.fail(f"테스트 중 예외 발생: {e}")


if __name__ == "__main__":
    unittest.main()