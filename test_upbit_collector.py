#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Upbit 데이터 수집기 테스트 (DEPRECATED)

이 모듈은 더 이상 사용되지 않습니다. 대신 test_binance_collector.py를 사용하세요.
"""

import logging
import sys
import warnings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 경고 표시
warnings.warn(
    "test_upbit_collector.py is deprecated and will be removed in a future version. "
    "Use test_binance_collector.py instead.",
    DeprecationWarning,
    stacklevel=2
)

def test_upbit_collector():
    """
    Upbit 데이터 수집기 테스트 함수 (DEPRECATED)
    
    이 함수는 더 이상 사용되지 않습니다. 대신 test_binance_collector.py를 사용하세요.
    """
    logger.warning("test_upbit_collector is deprecated. Use test_binance_collector instead.")
    logger.info("이 테스트는 더 이상 실행되지 않습니다. test_binance_collector.py를 사용하세요.")
    return False

if __name__ == "__main__":
    logger.warning("test_upbit_collector.py is deprecated. Use test_binance_collector.py instead.")
    sys.exit(1)
