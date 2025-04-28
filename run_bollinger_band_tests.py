#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
볼린저 밴드 및 이동평균선 수정사항 테스트 실행 스크립트
"""

import unittest
import sys

# 테스트 모듈 임포트
from tests.test_dashboard import TestDashboard
from tests.test_dashboard_callbacks import TestDashboardCallbacks
from tests.test_smooth_lines import TestSmoothLines

if __name__ == "__main__":
    # 테스트 스위트 생성
    suite = unittest.TestSuite()
    
    # 각 테스트 클래스에서 테스트 로드
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDashboard))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDashboardCallbacks))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSmoothLines))
    
    # 테스트 실행
    result = unittest.TextTestRunner().run(suite)
    
    # 결과 출력
    if result.wasSuccessful():
        print("\n모든 테스트가 성공적으로 완료되었습니다.")
        print("볼린저 밴드와 이동평균선 수정이 성공적으로 적용되었습니다.")
        sys.exit(0)
    else:
        print("\n일부 테스트가 실패했습니다.")
        print("볼린저 밴드와 이동평균선 수정에 문제가 있을 수 있습니다.")
        sys.exit(1)