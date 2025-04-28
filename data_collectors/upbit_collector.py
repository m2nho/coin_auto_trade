#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Upbit 데이터 수집기 (DEPRECATED)

이 모듈은 더 이상 사용되지 않습니다. 대신 Binance 데이터 수집기를 사용하세요.
"""

import logging
import warnings

logger = logging.getLogger(__name__)

# 경고 표시
warnings.warn(
    "UpbitDataCollector is deprecated and will be removed in a future version. "
    "Use BinanceDataCollector instead.",
    DeprecationWarning,
    stacklevel=2
)

class UpbitDataCollector:
    """
    Upbit API를 사용하여 암호화폐 데이터를 수집하는 클래스 (DEPRECATED)
    
    이 클래스는 더 이상 사용되지 않습니다. 대신 BinanceDataCollector를 사용하세요.
    """

    def __init__(self, symbols=None):
        """
        Upbit 데이터 수집기 초기화 (DEPRECATED)
        
        이 클래스는 더 이상 사용되지 않습니다. 대신 BinanceDataCollector를 사용하세요.
        """
        logger.warning("UpbitDataCollector is deprecated. Use BinanceDataCollector instead.")
        self.symbols = symbols or []
        
    def collect_data(self):
        """
        데이터 수집 메서드 (DEPRECATED)
        
        이 메서드는 더 이상 사용되지 않습니다. 대신 BinanceDataCollector를 사용하세요.
        """
        logger.warning("UpbitDataCollector.collect_data is deprecated. Use BinanceDataCollector instead.")
        return []

