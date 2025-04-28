#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CryptoPanic 뉴스 수집기

이 모듈은 CryptoPanic API를 사용하여 암호화폐 관련 뉴스를 수집합니다.
- 코인별 뉴스 수집
- 최근 3시간 내 뉴스 필터링
- 뉴스 경과 시간 계산
"""

import logging
import time
import requests
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class CryptoPanicCollector:
    """CryptoPanic API를 사용하여 암호화폐 뉴스를 수집하는 클래스"""
    
    BASE_URL = "https://cryptopanic.com/api/v1/posts/"
    
    def __init__(self, api_key: str, currencies: List[str]):
        """
        CryptoPanic 뉴스 수집기 초기화
        
        Args:
            api_key: CryptoPanic API 키
            currencies: 뉴스를 수집할 통화 목록 (예: ["BTC", "ETH"])
        """
        self.api_key = api_key
        self.currencies = currencies
        self.session = requests.Session()
        
    def collect_news(self, posts_per_page: int = 50, filter_: str = "hot") -> List[Dict[str, Any]]:
        """
        모든 설정된 통화에 대한 뉴스를 수집합니다.
        
        Args:
            posts_per_page: 페이지당 가져올 뉴스 수
            filter_: 뉴스 필터 (예: "hot", "rising", "bullish", "bearish")
            
        Returns:
            수집된 뉴스 데이터 목록
        """
        all_news = []
        
        for currency in self.currencies:
            try:
                news_data = self.get_bitcoin_news(currency, posts_per_page)
                if news_data:
                    summary = self.summarize_news(news_data)
                    if summary:
                        all_news.append({
                            "currency": currency,
                            "summary": summary,
                            "collected_at": datetime.now(timezone.utc).isoformat()
                        })
                        logger.debug(f"{currency} 뉴스 {summary['news_count']}개 수집 완료")
                
                # API 속도 제한 방지를 위한 대기
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"{currency} 뉴스 수집 중 오류 발생: {e}")
                
        return all_news
    
    def get_bitcoin_news(self, currency: str = "BTC", posts_per_page: int = 50) -> Dict[str, Any]:
        """
        특정 통화에 대한 뉴스를 가져옵니다.
        
        Args:
            currency: 뉴스를 가져올 통화 (예: "BTC")
            posts_per_page: 페이지당 가져올 뉴스 수
            
        Returns:
            뉴스 데이터
        """
        params = {
            "auth_token": self.api_key,
            "currencies": currency,
            "per_page": posts_per_page
        }
        
        try:
            response = self.session.get(self.BASE_URL, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"오류 발생: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"CryptoPanic API 요청 실패: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"CryptoPanic API 응답 파싱 실패: {e}")
            return None
    
    def format_time_delta(self, published_at, now):
        """
        Returns a string representing the time elapsed between 'now' and 'published_at'
        in the format "X hours Y minutes ago".
        
        Args:
            published_at: 게시 시간 (datetime 객체)
            now: 현재 시간 (datetime 객체)
            
        Returns:
            경과 시간 문자열
        """
        delta = now - published_at
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours} hours {minutes} minutes ago"
    
    def summarize_news(self, news_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        최근 3시간 내의 모든 포스트(뉴스, 트윗 등) 항목에서 제목과 함께
        'X hours Y minutes ago' 형식의 시간을 출력합니다.
        
        Args:
            news_data: 뉴스 데이터
            
        Returns:
            뉴스 요약 데이터 또는 None
        """
        now = datetime.now(timezone.utc)
        news_items = news_data.get("results", [])
        
        recent_posts = []
        for item in news_items:
            published_str = item.get("published_at")
            if published_str:
                # ISO 형식 날짜 문자열을 UTC offset-aware datetime 객체로 변환
                published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                if (now - published_at).total_seconds() <= 3 * 3600:  # 최근 3시간 내
                    title = item.get("title", "")
                    if title:
                        time_ago = self.format_time_delta(published_at, now)
                        recent_posts.append({
                            "title": title,
                            "time_ago": time_ago,
                            "url": item.get("url", ""),
                            "source": item.get("source", {}).get("title", ""),
                            "published_at": published_str
                        })

        news_count = len(recent_posts)
        if news_count == 0:
            return None

        summary = {
            "news_count": news_count,
            "posts": recent_posts
        }
        return summary
    
    def process_news_for_db(self, all_news: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        수집된 뉴스 데이터를 데이터베이스 저장용 형식으로 변환합니다.
        
        Args:
            all_news: 수집된 뉴스 데이터 목록
            
        Returns:
            데이터베이스 저장용 뉴스 데이터 목록
        """
        db_news = []
        
        for news_item in all_news:
            currency = news_item["currency"]
            summary = news_item["summary"]
            
            for post in summary["posts"]:
                # 고유 ID 생성 (URL 기반)
                import hashlib
                post_id = hashlib.md5(post["url"].encode()).hexdigest()
                
                # 기본 내용 설정 (실제로는 웹 스크래핑이나 API를 통해 가져와야 함)
                content = f"This is the content for the news article titled '{post['title']}'. " \
                          f"This article was published {post['time_ago']} by {post['source']}."
                
                # 요약 생성 (실제로는 NLP 모델을 사용하여 생성해야 함)
                news_summary = f"Summary of '{post['title']}'. Published {post['time_ago']}."
                
                db_news.append({
                    "id": post_id,
                    "title": post["title"],
                    "content": content,  # 내용 추가
                    "summary": news_summary,  # 요약 추가
                    "url": post["url"],
                    "source_title": post["source"],
                    "source_domain": post["url"].split("/")[2] if len(post["url"].split("/")) > 2 else "",
                    "currency": currency,
                    "published_at": post["published_at"],
                    "created_at": post["published_at"],  # 같은 값 사용
                    "votes": {},  # 투표 정보 없음
                    "sentiment": "neutral",  # 기본값
                    "importance": 0.5,  # 기본값
                    "collected_at": news_item["collected_at"]
                })
                
        return db_news
