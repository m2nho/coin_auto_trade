#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Binance 데이터 수집기 테스트

이 모듈은 Binance 데이터 수집기의 기능을 테스트합니다.
"""

import logging
import sys
import os
import yaml
from data_collectors.binance_collector import BinanceDataCollector

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path='config/config.yaml'):
    """설정 파일을 로드합니다."""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"설정 파일 로드 중 오류 발생: {e}")
        sys.exit(1)

def test_binance_collector():
    """Binance 데이터 수집기 테스트 함수"""
    # 설정 로드
    config = load_config()
    
    try:
        # Binance 데이터 수집기 초기화
        collector = BinanceDataCollector(
            api_key=config['binance']['api_key'],
            api_secret=config['binance']['api_secret'],
            symbols=config['binance']['symbols']
        )
        logger.info(f"Binance 데이터 수집기 초기화 완료: {config['binance']['symbols']}")
        
        # 데이터 수집 테스트
        data = collector.collect_data()
        logger.info(f"{len(data)} 개의 Binance 코인 데이터 수집 완료")
        
        # 수집된 데이터 확인
        for coin_data in data:
            symbol = coin_data["symbol"]
            ticker = coin_data["ticker"]
            logger.info(f"{symbol} 현재 가격: {ticker['price']}")
            logger.info(f"{symbol} 가격 변화: {ticker['price_change']}")
            logger.info(f"{symbol} 가격 변화율: {ticker['price_change_percent']}%")
            logger.info(f"{symbol} 고가: {ticker['high_price']}")
            logger.info(f"{symbol} 저가: {ticker['low_price']}")
            logger.info(f"{symbol} 24시간 거래량: {ticker['volume']}")
            logger.info(f"{symbol} 24시간 거래대금: {ticker['quote_volume']}")
            logger.info("---")
        
        return True
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    success = test_binance_collector()
    sys.exit(0 if success else 1)