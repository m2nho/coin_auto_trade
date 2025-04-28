#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI 변경사항 테스트 스크립트

이 스크립트는 UI에서 Upbit 관련 요소가 제거되었는지 확인합니다.
"""

import os
import sys
import unittest

# 상위 디렉토리 추가하여 모듈 임포트 가능하게 함
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from visualization.dashboard import data_cache
from visualization.dashboard_layout import create_layout
import dash

class TestUIChanges(unittest.TestCase):
    """UI 변경사항 테스트 클래스"""
    
    def test_no_upbit_in_data_cache(self):
        """데이터 캐시에 Upbit 관련 정보가 없는지 확인"""
        # 데이터 캐시의 collection_status에 upbit가 없는지 확인
        self.assertNotIn("upbit", data_cache["collection_status"])
    
    def test_no_upbit_in_layout(self):
        """레이아웃에 Upbit 관련 요소가 없는지 확인"""
        # 대시보드 레이아웃 생성
        layout = create_layout()
        
        # 레이아웃을 문자열로 변환
        layout_str = str(layout)
        
        # 레이아웃에 'upbit'나 'Upbit'가 포함되어 있지 않은지 확인
        self.assertNotIn("upbit", layout_str.lower())
        
        print("UI에서 Upbit 관련 요소가 성공적으로 제거되었습니다.")

if __name__ == "__main__":
    unittest.main()