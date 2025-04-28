#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
캔들스틱 데이터 테스트 실행 스크립트

이 스크립트는 캔들스틱 데이터 수집 및 저장 테스트를 실행합니다.
"""

import unittest
import logging
from tests.test_candle_data import TestCandleData

if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 테스트 실행
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCandleData)
    unittest.TextTestRunner(verbosity=2).run(suite)