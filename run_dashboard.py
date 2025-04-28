#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
데이터 수집 시각화 대시보드 실행 스크립트

이 스크립트는 데이터 수집 시각화 대시보드를 실행합니다.
"""

import os
import sys
import logging
from visualization.dashboard import initialize_dashboard, run_dashboard

if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    logger.info("데이터 수집 시각화 대시보드 시작")
    
    # 데이터베이스 경로
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bitcoin_trading.db")
    
    # 대시보드 초기화 및 실행
    initialize_dashboard(db_path)
    run_dashboard(host="0.0.0.0", port=8050, debug=True)