#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
대시보드 콜백 테스트 실행 스크립트
"""

import unittest
import sys
import os

# 내부 모듈 임포트를 위한 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 테스트 모듈 임포트
from tests.test_dashboard_callbacks import TestDashboardCallbacks
from tests.test_binance_websocket import TestBinanceWebsocket

if __name__ == "__main__":
    # 테스트 스위트 생성
    suite = unittest.TestSuite()
    
    # 대시보드 콜백 테스트 추가
    suite.addTest(unittest.makeSuite(TestDashboardCallbacks))
    
    # Binance 웹소켓 테스트 추가
    suite.addTest(unittest.makeSuite(TestBinanceWebsocket))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 테스트 결과에 따라 종료 코드 설정
    sys.exit(not result.wasSuccessful())