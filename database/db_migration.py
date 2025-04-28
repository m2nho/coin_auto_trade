#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
데이터베이스 마이그레이션 스크립트

이 스크립트는 데이터베이스 스키마를 업데이트하는 기능을 제공합니다:
- 누락된 컬럼 추가
- 스키마 변경 적용
"""

import os
import logging
import sqlite3
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from .models import Base

logger = logging.getLogger(__name__)

def check_and_add_columns(db_path):
    """
    데이터베이스에 누락된 컬럼이 있는지 확인하고 추가합니다.
    
    Args:
        db_path: 데이터베이스 파일 경로
    """
    try:
        # SQLite 데이터베이스 연결
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # news_data 테이블이 존재하는지 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news_data'")
        if cursor.fetchone() is None:
            logger.info("news_data 테이블이 존재하지 않습니다. 마이그레이션이 필요하지 않습니다.")
            conn.close()
            return
        
        # 테이블 정보 가져오기
        cursor.execute("PRAGMA table_info(news_data)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # content 컬럼이 없으면 추가
        if 'content' not in columns:
            logger.info("news_data 테이블에 content 컬럼 추가 중...")
            cursor.execute("ALTER TABLE news_data ADD COLUMN content TEXT")
            logger.info("content 컬럼 추가 완료")
        
        # summary 컬럼이 없으면 추가
        if 'summary' not in columns:
            logger.info("news_data 테이블에 summary 컬럼 추가 중...")
            cursor.execute("ALTER TABLE news_data ADD COLUMN summary TEXT")
            logger.info("summary 컬럼 추가 완료")
        
        # 변경사항 저장
        conn.commit()
        conn.close()
        logger.info("데이터베이스 마이그레이션 완료")
        
    except Exception as e:
        logger.error(f"데이터베이스 마이그레이션 중 오류 발생: {e}")
        raise

def migrate_database(db_path):
    """
    데이터베이스 마이그레이션을 실행합니다.
    
    Args:
        db_path: 데이터베이스 파일 경로
    """
    # 데이터베이스 파일이 존재하는지 확인
    if not os.path.exists(db_path):
        logger.info(f"데이터베이스 파일이 존재하지 않습니다: {db_path}")
        return
    
    try:
        # 누락된 컬럼 추가
        check_and_add_columns(db_path)
        
        # SQLAlchemy 엔진 생성
        engine = create_engine(f"sqlite:///{db_path}")
        
        # 테이블 구조 검사
        inspector = inspect(engine)
        
        # 모든 테이블이 존재하는지 확인
        existing_tables = inspector.get_table_names()
        
        # Base에 정의된 모든 테이블 가져오기
        metadata_tables = Base.metadata.tables.keys()
        
        # 누락된 테이블 생성
        missing_tables = set(metadata_tables) - set(existing_tables)
        if missing_tables:
            logger.info(f"누락된 테이블 생성 중: {missing_tables}")
            # 누락된 테이블만 생성
            for table_name in missing_tables:
                Base.metadata.tables[table_name].create(engine)
            
        logger.info("데이터베이스 마이그레이션 완료")
        
    except Exception as e:
        logger.error(f"데이터베이스 마이그레이션 중 오류 발생: {e}")
        raise