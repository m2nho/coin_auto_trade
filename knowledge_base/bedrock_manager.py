#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AWS Bedrock 관리 모듈

이 모듈은 AWS Bedrock 연결 및 AI 기능을 제공합니다:
- AWS Bedrock 연결 설정
- 텍스트 생성 및 분석
- 임베딩 생성
- 감성 분석
"""

import logging
import json
import os
from typing import List, Dict, Any, Optional, Union, Tuple

import boto3
from botocore.config import Config

logger = logging.getLogger(__name__)


class BedrockManager:
    """AWS Bedrock 연결 및 AI 기능을 담당하는 클래스"""
    
    def __init__(self, region: str, models: Dict[str, str] = None, parameters: Dict[str, Any] = None):
        """
        AWS Bedrock 관리자 초기화
        
        Args:
            region: AWS 리전
            models: 사용할 모델 ID 매핑
            parameters: 모델 파라미터 설정
        """
        self.region = region
        self.models = models or {
            "text_generation": "anthropic.claude-3-sonnet-20240229-v1:0",
            "embeddings": "amazon.titan-embed-text-v1"
        }
        self.parameters = parameters or {
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9
        }
        self.client = None
        self.connect()
        
    def connect(self) -> None:
        """AWS Bedrock에 연결합니다."""
        try:
            # AWS 설정
            config = Config(
                region_name=self.region,
                retries={
                    'max_attempts': 10,
                    'mode': 'standard'
                }
            )
            
            # Bedrock 클라이언트 생성
            self.client = boto3.client('bedrock-runtime', config=config)
            logger.info("AWS Bedrock 연결 성공")
                
        except Exception as e:
            logger.error(f"AWS Bedrock 연결 중 오류 발생: {e}")
            raise
            
    def analyze_news_sentiment(self, news_text: str) -> Dict[str, Any]:
        """
        뉴스 텍스트의 감성을 분석합니다.
        
        Args:
            news_text: 분석할 뉴스 텍스트
            
        Returns:
            감성 분석 결과
        """
        try:
            prompt = f"""
            다음 암호화폐 관련 뉴스 텍스트의 감성을 분석해주세요.
            감성은 'positive', 'neutral', 'negative' 중 하나로 분류하고, 
            중요도를 0.0에서 1.0 사이의 값으로 평가해주세요.
            
            뉴스 텍스트:
            {news_text}
            
            JSON 형식으로 다음 정보를 반환해주세요:
            {{
                "sentiment": "positive/neutral/negative",
                "importance": 0.0-1.0,
                "reasoning": "분석 근거"
            }}
            """
            
            # Claude 모델 호출
            response = self.client.invoke_model(
                modelId=self.models["text_generation"],
                body=json.dumps({
                    "prompt": prompt,
                    "max_tokens": self.parameters["max_tokens"],
                    "temperature": self.parameters["temperature"],
                    "top_p": self.parameters["top_p"]
                })
            )
            
            # 응답 처리
            response_body = json.loads(response['body'].read())
            result_text = response_body.get('completion', '')
            
            # JSON 추출
            try:
                # JSON 부분만 추출
                json_str = result_text.strip()
                if json_str.startswith('```json'):
                    json_str = json_str.split('```json')[1].split('```')[0].strip()
                result = json.loads(json_str)
            except:
                # JSON 파싱 실패 시 기본값 반환
                result = {
                    "sentiment": "neutral",
                    "importance": 0.5,
                    "reasoning": "Failed to parse model response"
                }
                
            return result
            
        except Exception as e:
            logger.error(f"뉴스 감성 분석 중 오류 발생: {e}")
            # 오류 발생 시 기본값 반환
            return {
                "sentiment": "neutral",
                "importance": 0.5,
                "reasoning": f"Error: {str(e)}"
            }
            
    def create_text_embeddings(self, text: str) -> List[float]:
        """
        텍스트의 임베딩 벡터를 생성합니다.
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터
        """
        try:
            # Titan Embeddings 모델 호출
            response = self.client.invoke_model(
                modelId=self.models["embeddings"],
                body=json.dumps({
                    "inputText": text
                })
            )
            
            # 응답 처리
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding', [])
            
            return embedding
            
        except Exception as e:
            logger.error(f"텍스트 임베딩 생성 중 오류 발생: {e}")
            raise
            
    def generate_market_insights(self, data: Dict[str, Any]) -> str:
        """
        시장 데이터를 기반으로 인사이트를 생성합니다.
        
        Args:
            data: 시장 데이터
            
        Returns:
            생성된 인사이트 텍스트
        """
        try:
            # 데이터를 문자열로 변환
            data_str = json.dumps(data, indent=2)
            
            prompt = f"""
            다음은 암호화폐 시장 데이터입니다:
            
            {data_str}
            
            이 데이터를 분석하여 시장 동향, 주요 패턴, 그리고 투자자에게 유용한 인사이트를 제공해주세요.
            다음 형식으로 응답해주세요:
            
            1. 시장 요약
            2. 주요 동향
            3. 위험 요소
            4. 투자 기회
            5. 단기 전망
            """
            
            # Claude 모델 호출
            response = self.client.invoke_model(
                modelId=self.models["text_generation"],
                body=json.dumps({
                    "prompt": prompt,
                    "max_tokens": self.parameters["max_tokens"],
                    "temperature": self.parameters["temperature"],
                    "top_p": self.parameters["top_p"]
                })
            )
            
            # 응답 처리
            response_body = json.loads(response['body'].read())
            insights = response_body.get('completion', '')
            
            return insights
            
        except Exception as e:
            logger.error(f"시장 인사이트 생성 중 오류 발생: {e}")
            return f"인사이트 생성 실패: {str(e)}"
            
    def predict_market_trend(self, symbol: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        시장 동향을 예측합니다.
        
        Args:
            symbol: 코인 심볼
            features: 예측에 사용할 특성
            
        Returns:
            예측 결과
        """
        try:
            # 특성을 문자열로 변환
            features_str = json.dumps(features, indent=2)
            
            prompt = f"""
            다음은 {symbol} 코인의 특성 데이터입니다:
            
            {features_str}
            
            이 데이터를 기반으로 향후 24시간 동안의 시장 동향을 예측해주세요.
            다음 JSON 형식으로 응답해주세요:
            
            {{
                "trend": "bullish/bearish/neutral",
                "confidence": 0.0-1.0,
                "price_change_prediction": "예상 가격 변동 비율(%)",
                "reasoning": "예측 근거"
            }}
            """
            
            # Claude 모델 호출
            response = self.client.invoke_model(
                modelId=self.models["text_generation"],
                body=json.dumps({
                    "prompt": prompt,
                    "max_tokens": self.parameters["max_tokens"],
                    "temperature": self.parameters["temperature"],
                    "top_p": self.parameters["top_p"]
                })
            )
            
            # 응답 처리
            response_body = json.loads(response['body'].read())
            result_text = response_body.get('completion', '')
            
            # JSON 추출
            try:
                # JSON 부분만 추출
                json_str = result_text.strip()
                if json_str.startswith('```json'):
                    json_str = json_str.split('```json')[1].split('```')[0].strip()
                result = json.loads(json_str)
            except:
                # JSON 파싱 실패 시 기본값 반환
                result = {
                    "trend": "neutral",
                    "confidence": 0.5,
                    "price_change_prediction": "0.0",
                    "reasoning": "Failed to parse model response"
                }
                
            return result
            
        except Exception as e:
            logger.error(f"시장 동향 예측 중 오류 발생: {e}")
            # 오류 발생 시 기본값 반환
            return {
                "trend": "neutral",
                "confidence": 0.5,
                "price_change_prediction": "0.0",
                "reasoning": f"Error: {str(e)}"
            }