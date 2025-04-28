#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
비트코인 자동 거래 프로그램 메인 모듈

이 모듈은 다음 기능을 수행합니다:
1. 설정 파일 로드
2. 데이터 수집기 초기화 및 실행
3. 데이터베이스 연결 관리
4. 지식 베이스 관리
5. 전체 시스템 조정
"""

import os
import sys
import time
import logging
import yaml
import argparse
from datetime import datetime

# 내부 모듈 임포트
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data_collectors.binance_collector import BinanceDataCollector
from data_collectors.news_collector import CryptoPanicCollector
from data_collectors.history_tracker import InvestmentHistoryTracker
from database.db_manager import DatabaseManager
from knowledge_base.kb_manager import KnowledgeBaseManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bitcoin_trading.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config(config_path):
    """설정 파일을 로드합니다."""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"설정 파일 로드 중 오류 발생: {e}")
        sys.exit(1)


def initialize_collectors(config):
    """데이터 수집기를 초기화합니다."""
    # Binance 수집기
    binance_collector = BinanceDataCollector(
        api_key=config['binance']['api_key'],
        api_secret=config['binance']['api_secret'],
        symbols=config['binance']['symbols']
    )
    
    # 뉴스 수집기
    news_collector = CryptoPanicCollector(
        api_key=config['cryptopanic']['api_key'],
        currencies=config['cryptopanic']['currencies']
    )
    
    # 투자 이력 추적기
    history_tracker = InvestmentHistoryTracker(
        db_path=config['database']['path']
    )
    
    return binance_collector, news_collector, history_tracker


def initialize_database(config):
    """데이터베이스 관리자를 초기화합니다."""
    return DatabaseManager(
        db_path=config['database']['path'],
        echo=config['database'].get('echo', False)
    )


def initialize_knowledge_base(config, db_manager):
    """지식 베이스 관리자를 초기화합니다."""
    return KnowledgeBaseManager(
        db_manager=db_manager,
        config=config['knowledge_base']
    )


def run_data_collection(collectors, db_manager, interval=60):
    """데이터 수집 프로세스를 실행합니다."""
    binance_collector, news_collector, history_tracker = collectors
    
    while True:
        try:
            logger.info("데이터 수집 시작...")
            
            # Binance 데이터 수집
            coin_data = binance_collector.collect_data()
            db_manager.save_coin_data(coin_data)
            logger.info(f"{len(coin_data)} 개의 Binance 코인 데이터 수집 완료")
            
            # 뉴스 데이터 수집
            news_data = news_collector.collect_news()
            # 뉴스 데이터를 DB 저장 형식으로 변환
            db_news_data = news_collector.process_news_for_db(news_data)
            db_manager.save_news_data(db_news_data)
            logger.info(f"{len(db_news_data)} 개의 뉴스 데이터 수집 완료")
            
            # 투자 이력 업데이트
            history_data = history_tracker.update_history()
            db_manager.save_history_data(history_data)
            logger.info("투자 이력 업데이트 완료")
            
            logger.info(f"{interval}초 대기 중...")
            time.sleep(interval)
            
        except KeyboardInterrupt:
            logger.info("프로그램 종료 요청됨")
            break
        except Exception as e:
            logger.error(f"데이터 수집 중 오류 발생: {e}")
            time.sleep(10)  # 오류 발생 시 10초 대기 후 재시도


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='비트코인 자동 거래 프로그램')
    parser.add_argument('--config', default='config/config.yaml', help='설정 파일 경로')
    parser.add_argument('--dashboard', action='store_true', help='대시보드 실행 여부')
    parser.add_argument('--dashboard-port', type=int, default=8050, help='대시보드 포트 번호')
    args = parser.parse_args()
    
    logger.info("비트코인 자동 거래 프로그램 시작")
    
    # 설정 로드
    config = load_config(args.config)
    logger.info("설정 로드 완료")
    
    # 데이터베이스 초기화
    db_manager = initialize_database(config)
    logger.info("데이터베이스 초기화 완료")
    
    # 데이터 수집기 초기화
    collectors = initialize_collectors(config)
    logger.info("데이터 수집기 초기화 완료")
    
    # 지식 베이스 초기화
    kb_manager = initialize_knowledge_base(config, db_manager)
    logger.info("지식 베이스 초기화 완료")
    
    # 대시보드 실행 (옵션)
    if args.dashboard:
        try:
            import threading
            from visualization.dashboard import initialize_dashboard, run_dashboard
            
            logger.info("대시보드 초기화 중...")
            initialize_dashboard(config['database']['path'])
            
            # 대시보드를 별도 스레드에서 실행
            dashboard_thread = threading.Thread(
                target=run_dashboard,
                kwargs={"host": "0.0.0.0", "port": args.dashboard_port, "debug": False},
                daemon=True
            )
            dashboard_thread.start()
            logger.info(f"대시보드가 http://localhost:{args.dashboard_port}에서 실행 중입니다.")
        except ImportError as e:
            logger.error(f"대시보드 모듈을 불러올 수 없습니다: {e}")
            logger.info("대시보드 없이 계속 실행합니다.")
        except Exception as e:
            logger.error(f"대시보드 실행 중 오류 발생: {e}")
            logger.info("대시보드 없이 계속 실행합니다.")
    
    # 데이터 수집 실행
    run_data_collection(collectors, db_manager, config['collection']['interval'])
    
    logger.info("프로그램 종료")


if __name__ == "__main__":
    main()





