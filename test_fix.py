#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
대시보드 모듈 임포트 테스트

이 스크립트는 visualization.dashboard 모듈에서 initialize_dashboard 함수를 
임포트할 수 있는지 테스트합니다.
"""

import logging
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_binance_streams():
    """Binance streams 모듈 테스트"""
    try:
        logger.info("binance.streams 모듈 임포트 시도")
        from binance.streams import BinanceSocketManager
        logger.info("임포트 성공: binance.streams.BinanceSocketManager")
        return True
    except ImportError as e:
        logger.error(f"binance.streams 모듈을 불러올 수 없습니다: {e}")
        return False

def test_dash_state():
    """Dash State 임포트 테스트"""
    try:
        logger.info("dash.State 임포트 시도")
        from dash import State
        logger.info("임포트 성공: dash.State")
        return True
    except ImportError as e:
        logger.error(f"dash.State를 불러올 수 없습니다: {e}")
        return False

def test_dashboard_module():
    """대시보드 모듈 테스트"""
    try:
        logger.info("visualization.dashboard 모듈에서 initialize_dashboard 함수 임포트 시도")
        from visualization.dashboard import initialize_dashboard
        logger.info("임포트 성공: initialize_dashboard 함수를 성공적으로 임포트했습니다.")
        
        # 추가 검증: 다른 필요한 함수들도 임포트 가능한지 확인
        from visualization.dashboard import run_dashboard, get_news_data
        logger.info("추가 함수 임포트 성공: run_dashboard, get_news_data")
        
        # dashboard_callbacks.py의 함수 임포트 확인
        from visualization.dashboard_callbacks import register_collection_stats_callback, register_pagination_callbacks
        logger.info("dashboard_callbacks.py 함수 임포트 성공: register_collection_stats_callback, register_pagination_callbacks")
        
        return True
    except ImportError as e:
        logger.error(f"대시보드 모듈을 불러올 수 없습니다: {e}")
        return False

if __name__ == "__main__":
    success = True
    
    # Binance streams 모듈 테스트
    if not test_binance_streams():
        success = False
    
    # Dash State 임포트 테스트
    if not test_dash_state():
        success = False
    
    # 대시보드 모듈 테스트
    if not test_dashboard_module():
        success = False
    
    if success:
        logger.info("모든 테스트가 성공적으로 완료되었습니다.")
        sys.exit(0)  # 성공
    else:
        logger.error("일부 테스트가 실패했습니다.")
        sys.exit(1)  # 실패
