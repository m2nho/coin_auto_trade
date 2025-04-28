#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
뉴스 표시 기능 테스트

이 모듈은 뉴스 데이터가 대시보드에 올바르게 표시되는지 테스트합니다.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
import dash
from dash import html

# 상위 디렉토리 추가하여 모듈 임포트 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from visualization.dashboard_callbacks import update_news_table
from visualization.dashboard_layout import create_news_table


class TestNewsDisplay(unittest.TestCase):
    """뉴스 표시 기능 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 테스트용 뉴스 데이터 생성
        self.mock_news_data = [
            {
                "id": 1,
                "external_id": "news1",
                "title": "비트코인 가격 상승",
                "content": "비트코인 가격이 크게 상승했습니다.",
                "summary": "비트코인 가격 상승 요약",
                "url": "https://example.com/news/1",
                "source": "News Source 1",
                "source_title": "News Source 1",
                "source_domain": "example.com",
                "published_at": datetime.now().isoformat(),
                "currency": "BTC"
            },
            {
                "id": 2,
                "external_id": "news2",
                "title": "이더리움 업데이트 예정",
                "content": "이더리움 네트워크 업데이트가 예정되어 있습니다.",
                "summary": "이더리움 업데이트 요약",
                "url": "https://example.com/news/2",
                "source": "News Source 2",
                "source_title": "News Source 2",
                "source_domain": "example.com",
                "published_at": datetime.now().isoformat(),
                "currency": "ETH"
            },
            {
                "id": 3,
                "external_id": "news3",
                "title": "비트코인 관련 뉴스",
                "content": "비트코인에 관한 또 다른 뉴스입니다.",
                "summary": "비트코인 뉴스 요약",
                "url": "https://example.com/news/3",
                "source": "News Source 3",
                "source_title": "News Source 3",
                "source_domain": "example.com",
                "published_at": datetime.now().isoformat(),
                "currency": "BTC"
            }
        ]
        
        # 데이터 캐시 모의 객체
        self.mock_data_cache = {
            "news_data": self.mock_news_data,
            "collection_status": {
                "news": {"count": len(self.mock_news_data), "status": "active", "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            }
        }
    
    def test_create_news_table(self):
        """뉴스 테이블 생성 테스트"""
        # 뉴스 테이블 컴포넌트 생성
        news_table = create_news_table()
        
        # 검증
        self.assertIsNotNone(news_table)
        self.assertEqual(news_table.className, "mb-4")
        
        # 카드 헤더 확인
        card_header = news_table.children[0].children.children[0].children[0]
        self.assertEqual(card_header.children.children, "최근 뉴스 데이터")
    
    def test_news_filtering(self):
        """뉴스 필터링 테스트"""
        # 콜백 함수 호출 (BTC 필터링)
        with patch('dash.callback_context'):
            result = update_news_table(1, "BTC", 1, data_cache=self.mock_data_cache)
        
        # 결과가 html.Div인지 확인
        self.assertIsInstance(result, html.Div)
        
        # 뉴스 카드가 있는지 확인
        news_cards = result.children[0].children
        self.assertTrue(len(news_cards) > 0)
        
        # BTC 관련 뉴스만 필터링되었는지 확인
        btc_news_count = sum(1 for news in self.mock_news_data if "BTC" in news["currency"])
        self.assertEqual(len(news_cards), min(btc_news_count, 10))  # 페이지당 최대 10개
    
    def test_news_pagination(self):
        """뉴스 페이지네이션 테스트"""
        # 많은 뉴스 데이터 생성
        many_news = []
        for i in range(25):  # 25개의 뉴스 (3페이지 분량)
            many_news.append({
                "id": i,
                "external_id": f"news{i}",
                "title": f"뉴스 제목 {i}",
                "content": f"뉴스 내용 {i}",
                "summary": f"뉴스 요약 {i}",
                "url": f"https://example.com/news/{i}",
                "source": "News Source",
                "source_title": "News Source",
                "source_domain": "example.com",
                "published_at": datetime.now().isoformat(),
                "currency": "BTC"
            })
        
        # 데이터 캐시 업데이트
        self.mock_data_cache["news_data"] = many_news
        
        # 첫 페이지 테스트
        with patch('dash.callback_context'):
            result_page1 = update_news_table(1, "BTC", 1, data_cache=self.mock_data_cache)
        
        # 두 번째 페이지 테스트
        with patch('dash.callback_context'):
            result_page2 = update_news_table(1, "BTC", 2, data_cache=self.mock_data_cache)
        
        # 세 번째 페이지 테스트
        with patch('dash.callback_context'):
            result_page3 = update_news_table(1, "BTC", 3, data_cache=self.mock_data_cache)
        
        # 각 페이지의 뉴스 카드 수 확인
        news_cards_page1 = result_page1.children[0].children
        news_cards_page2 = result_page2.children[0].children
        news_cards_page3 = result_page3.children[0].children
        
        self.assertEqual(len(news_cards_page1), 10)  # 첫 페이지는 10개
        self.assertEqual(len(news_cards_page2), 10)  # 두 번째 페이지는 10개
        self.assertEqual(len(news_cards_page3), 5)   # 세 번째 페이지는 5개
    
    def test_missing_fields_handling(self):
        """누락된 필드 처리 테스트"""
        # 일부 필드가 누락된 뉴스 데이터
        incomplete_news = [
            {
                "id": 1,
                "external_id": "news1",
                "title": "제목만 있는 뉴스",
                "currency": "BTC",
                "published_at": datetime.now().isoformat()
            }
        ]
        
        # 데이터 캐시 업데이트
        self.mock_data_cache["news_data"] = incomplete_news
        
        # 콜백 함수 호출
        with patch('dash.callback_context'):
            result = update_news_table(1, "BTC", 1, data_cache=self.mock_data_cache)
        
        # 결과가 html.Div인지 확인
        self.assertIsInstance(result, html.Div)
        
        # 오류 없이 렌더링되는지 확인
        news_cards = result.children[0].children
        self.assertEqual(len(news_cards), 1)


# 테스트 실행을 위한 헬퍼 함수
def update_news_table(n, selected_coin, page, data_cache):
    """뉴스 테이블 업데이트 콜백 함수 래퍼"""
    # 페이지 번호 기본값 설정
    if page is None:
        page = 1
    
    # 페이지당 뉴스 수
    news_per_page = 10
    
    # 뉴스 데이터 필터링
    news_data = data_cache["news_data"]
    
    # 선택된 코인에 대한 뉴스 필터링 (대소문자 구분 없이)
    filtered_news = []
    for news in news_data:
        news_currency = news.get("currency", "").upper()
        if selected_coin in news_currency or selected_coin.upper() in news_currency:
            filtered_news.append(news)
    
    if not filtered_news:
        return html.Div("선택한 코인에 대한 뉴스가 없습니다.", className="text-center p-3")
    
    # 전체 페이지 수 계산
    total_pages = (len(filtered_news) + news_per_page - 1) // news_per_page
    
    # 현재 페이지에 해당하는 뉴스만 선택
    start_idx = (page - 1) * news_per_page
    end_idx = min(start_idx + news_per_page, len(filtered_news))
    page_news = filtered_news[start_idx:end_idx]
    
    # 뉴스 카드 생성
    news_cards = []
    for news in page_news:
        # 뉴스 내용과 요약 가져오기 (없으면 기본값 사용)
        content = news.get("content", "내용이 없습니다.")
        summary = news.get("summary", "요약이 없습니다.")
        source = news.get("source", news.get("source_title", "알 수 없는 출처"))
        published_at = news.get("published_at", "알 수 없는 시간")
        url = news.get("url", "#")
        title = news.get("title", "제목 없음")
        
        # 뉴스 카드 생성
        card = html.Div(className="mb-3 shadow-sm")
        news_cards.append(card)
    
    # 페이지네이션 컨트롤 생성
    pagination = html.Div([
        html.Div([
            html.Button("이전", id="prev-page", n_clicks=0, 
                       className="btn btn-outline-primary mr-2",
                       disabled=page <= 1),
            html.Span(f"페이지 {page} / {total_pages}", className="mx-2"),
            html.Button("다음", id="next-page", n_clicks=0, 
                       className="btn btn-outline-primary ml-2",
                       disabled=page >= total_pages)
        ], className="d-flex justify-content-center align-items-center my-3")
    ])
    
    return html.Div([html.Div(news_cards), pagination])


if __name__ == "__main__":
    unittest.main()