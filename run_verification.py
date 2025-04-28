#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
수정사항 검증 실행 스크립트
"""

import os
import sys
import subprocess
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_verification():
    """검증 스크립트를 실행합니다."""
    logger.info("수정사항 검증 스크립트 실행 중...")
    
    # 현재 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 검증 스크립트 실행
    verify_script = os.path.join(current_dir, "verify_fixes.py")
    result = subprocess.run([sys.executable, verify_script], capture_output=True, text=True)
    
    # 결과 출력
    logger.info("검증 스크립트 출력:")
    for line in result.stdout.splitlines():
        print(line)
    
    if result.stderr:
        logger.error("검증 스크립트 오류:")
        for line in result.stderr.splitlines():
            print(line)
    
    # 종료 코드 반환
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_verification())