#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
데이터베이스 마이그레이션 실행 스크립트

이 스크립트는 데이터베이스 마이그레이션을 수동으로 실행하는 기능을 제공합니다.
"""

import os
import sys
import logging
import argparse

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("db_migration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 내부 모듈 임포트
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.db_migration import migrate_database


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='데이터베이스 마이그레이션 실행')
    parser.add_argument('--db-path', default='bitcoin_trading.db', help='데이터베이스 파일 경로')
    args = parser.parse_args()
    
    db_path = args.db_path
    
    # 데이터베이스 파일이 존재하는지 확인
    if not os.path.exists(db_path):
        logger.error(f"데이터베이스 파일이 존재하지 않습니다: {db_path}")
        sys.exit(1)
    
    logger.info(f"데이터베이스 마이그레이션 시작: {db_path}")
    
    try:
        # 마이그레이션 실행
        migrate_database(db_path)
        logger.info("데이터베이스 마이그레이션 완료")
    except Exception as e:
        logger.error(f"데이터베이스 마이그레이션 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()