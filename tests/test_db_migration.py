#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
데이터베이스 마이그레이션 테스트

이 모듈은 데이터베이스 마이그레이션 기능을 테스트합니다.
"""

import os
import sys
import unittest
import sqlite3
import tempfile
import shutil
from datetime import datetime

# 상위 디렉토리 추가하여 모듈 임포트 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from database.models import NewsData
from database.db_migration import migrate_database


class TestDatabaseMigration(unittest.TestCase):
    """데이터베이스 마이그레이션 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 임시 디렉토리 생성
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_migration.db")
        
        # 테스트용 데이터베이스 생성 (이전 스키마 버전)
        self.create_old_schema_db()
        
    def tearDown(self):
        """테스트 정리"""
        # 임시 디렉토리 삭제
        shutil.rmtree(self.test_dir)
        
    def create_old_schema_db(self):
        """이전 버전의 스키마를 가진 데이터베이스를 생성합니다."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 이전 버전의 news_data 테이블 생성 (content와 summary 컬럼 없음)
        cursor.execute('''
        CREATE TABLE news_data (
            id INTEGER PRIMARY KEY,
            external_id VARCHAR(100) NOT NULL UNIQUE,
            title VARCHAR(500) NOT NULL,
            url VARCHAR(1000) NOT NULL,
            source_title VARCHAR(200),
            source_domain VARCHAR(200),
            currency VARCHAR(20) NOT NULL,
            published_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP NOT NULL,
            votes TEXT,
            sentiment VARCHAR(20),
            importance FLOAT,
            collected_at TIMESTAMP
        )
        ''')
        
        # 테스트 데이터 삽입
        cursor.execute('''
        INSERT INTO news_data (
            external_id, title, url, source_title, source_domain, 
            currency, published_at, created_at, votes, sentiment, 
            importance, collected_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            '775c4e5f1d1256fa41fb48245d1b5aa0',
            'Test News Title',
            'https://example.com/news/1',
            'Test Source',
            'example.com',
            'BTC',
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            '{}',
            'neutral',
            0.5,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
    def test_migration_adds_missing_columns(self):
        """마이그레이션이 누락된 컬럼을 추가하는지 테스트합니다."""
        # 마이그레이션 실행
        migrate_database(self.db_path)
        
        # 데이터베이스 연결
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 테이블 정보 가져오기
        cursor.execute("PRAGMA table_info(news_data)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # content와 summary 컬럼이 추가되었는지 확인
        self.assertIn('content', columns, "content 컬럼이 추가되지 않았습니다")
        self.assertIn('summary', columns, "summary 컬럼이 추가되지 않았습니다")
        
        conn.close()
        
    def test_db_manager_with_migration(self):
        """DatabaseManager가 마이그레이션을 올바르게 실행하는지 테스트합니다."""
        # DatabaseManager 초기화 (마이그레이션 자동 실행)
        db_manager = DatabaseManager(db_path=self.db_path, echo=False)
        
        # 세션 가져오기
        session = db_manager.get_session()
        
        try:
            # NewsData 모델을 사용하여 데이터 조회
            news = session.query(NewsData).filter_by(external_id='775c4e5f1d1256fa41fb48245d1b5aa0').first()
            
            # 데이터가 존재하는지 확인
            self.assertIsNotNone(news, "뉴스 데이터를 찾을 수 없습니다")
            
            # content와 summary 속성에 접근 가능한지 확인
            self.assertIsNone(news.content, "content 필드가 None이어야 합니다")
            self.assertIsNone(news.summary, "summary 필드가 None이어야 합니다")
            
            # 새 데이터 추가 테스트
            new_news = NewsData(
                external_id='test123',
                title='New Test Title',
                content='This is test content',
                summary='This is test summary',
                url='https://example.com/news/2',
                source_title='Test Source',
                source_domain='example.com',
                currency='ETH',
                published_at=datetime.now(),
                created_at=datetime.now(),
                votes='{}',
                sentiment='positive',
                importance=0.8,
                collected_at=datetime.now()
            )
            session.add(new_news)
            session.commit()
            
            # 추가한 데이터 조회
            added_news = session.query(NewsData).filter_by(external_id='test123').first()
            self.assertIsNotNone(added_news, "새로 추가한 뉴스 데이터를 찾을 수 없습니다")
            self.assertEqual(added_news.content, 'This is test content', "content 필드가 올바르게 저장되지 않았습니다")
            self.assertEqual(added_news.summary, 'This is test summary', "summary 필드가 올바르게 저장되지 않았습니다")
            
        finally:
            session.close()
            db_manager.close()


if __name__ == "__main__":
    unittest.main()