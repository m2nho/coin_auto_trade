#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI 변경사항 테스트 실행 스크립트
"""

import unittest
from test_ui_changes import TestUIChanges

if __name__ == "__main__":
    # 테스트 실행
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUIChanges)
    result = unittest.TextTestRunner().run(suite)
    
    # 결과 출력
    if result.wasSuccessful():
        print("\n모든 테스트가 성공적으로 완료되었습니다.")
        print("UI에서 Upbit 관련 요소가 성공적으로 제거되었습니다.")
    else:
        print("\n일부 테스트가 실패했습니다.")
        print("UI에서 Upbit 관련 요소가 완전히 제거되지 않았을 수 있습니다.")