#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
수정사항 검증 스크립트

이 스크립트는 다음 수정사항을 검증합니다:
1. BinanceSocketManager의 start 메서드 대신 _start_socket 메서드 사용
2. register_candle_chart_callback 함수 추가
"""

import os
import sys
import logging
import importlib
import inspect

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def verify_binance_collector():
    """BinanceDataCollector 클래스의 수정사항을 검증합니다."""
    try:
        from data_collectors.binance_collector import BinanceDataCollector
        
        # 인스턴스 생성
        collector = BinanceDataCollector("test_api_key", "test_api_secret", ["BTCUSDT"])
        
        # start_websocket_stream 메서드 검사
        source_code = inspect.getsource(collector.start_websocket_stream)
        if "_start_socket" in source_code and "bm.start()" not in source_code:
            logger.info("✅ BinanceDataCollector.start_websocket_stream 메서드가 올바르게 수정되었습니다.")
        else:
            logger.error("❌ BinanceDataCollector.start_websocket_stream 메서드가 올바르게 수정되지 않았습니다.")
            return False
        
        # start_multiple_websocket_streams 메서드 검사
        source_code = inspect.getsource(collector.start_multiple_websocket_streams)
        if "_start_socket" in source_code and "bm.start()" not in source_code:
            logger.info("✅ BinanceDataCollector.start_multiple_websocket_streams 메서드가 올바르게 수정되었습니다.")
        else:
            logger.error("❌ BinanceDataCollector.start_multiple_websocket_streams 메서드가 올바르게 수정되지 않았습니다.")
            return False
        
        return True
    except Exception as e:
        logger.error(f"BinanceDataCollector 검증 중 오류 발생: {e}")
        return False

def verify_dashboard_callbacks():
    """dashboard_callbacks 모듈의 수정사항을 검증합니다."""
    try:
        # 모듈 임포트
        from visualization.dashboard_callbacks import register_candle_chart_callback
        
        # register_candle_chart_callback 함수 검사
        if callable(register_candle_chart_callback):
            source_code = inspect.getsource(register_candle_chart_callback)
            if "update_candle_chart" in source_code and "go.Candlestick" in source_code:
                logger.info("✅ register_candle_chart_callback 함수가 올바르게 추가되었습니다.")
            else:
                logger.error("❌ register_candle_chart_callback 함수가 올바른 구현을 포함하고 있지 않습니다.")
                return False
        else:
            logger.error("❌ register_candle_chart_callback이 함수가 아닙니다.")
            return False
        
        # register_all_callbacks 함수에서 register_candle_chart_callback 호출 검사
        from visualization.dashboard_callbacks import register_all_callbacks
        source_code = inspect.getsource(register_all_callbacks)
        if "register_candle_chart_callback" in source_code:
            logger.info("✅ register_all_callbacks 함수에서 register_candle_chart_callback을 호출합니다.")
        else:
            logger.error("❌ register_all_callbacks 함수에서 register_candle_chart_callback을 호출하지 않습니다.")
            return False
        
        return True
    except ImportError as e:
        logger.error(f"dashboard_callbacks 모듈 임포트 실패: {e}")
        return False
    except Exception as e:
        logger.error(f"dashboard_callbacks 검증 중 오류 발생: {e}")
        return False

def main():
    """메인 함수"""
    success = True
    
    # BinanceDataCollector 검증
    logger.info("BinanceDataCollector 수정사항 검증 중...")
    if not verify_binance_collector():
        success = False
    
    # dashboard_callbacks 검증
    logger.info("dashboard_callbacks 수정사항 검증 중...")
    if not verify_dashboard_callbacks():
        success = False
    
    # 결과 출력
    if success:
        logger.info("✅ 모든 수정사항이 올바르게 적용되었습니다.")
        return 0
    else:
        logger.error("❌ 일부 수정사항이 올바르게 적용되지 않았습니다.")
        return 1

if __name__ == "__main__":
    sys.exit(main())