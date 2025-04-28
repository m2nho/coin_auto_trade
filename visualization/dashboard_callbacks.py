#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
데이터 수집 시각화 대시보드 콜백

이 모듈은 대시보드의 인터랙티브 기능을 위한 콜백 함수들을 정의합니다.
"""

import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import dash
from dash import html, dcc, Input, Output, callback, dash_table, State
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

# 상태 카드 업데이트 콜백
def register_status_callbacks(app, data_cache):
    @app.callback(
        [
            Output("binance-status", "children"),
            Output("binance-last-update", "children"),
            Output("binance-count", "children"),
            Output("news-status", "children"),
            Output("news-last-update", "children"),
            Output("news-count", "children")
        ],
        [Input("interval-component", "n_intervals")]
    )
    def update_status_cards(n):
        binance_status = data_cache["collection_status"]["binance"]
        news_status = data_cache["collection_status"]["news"]
        
        # Binance 상태
        binance_status_text = f"상태: {binance_status['status']}"
        binance_last_update = f"마지막 업데이트: {binance_status['last_update'] if binance_status['last_update'] else '없음'}"
        binance_count = f"수집된 데이터 수: {binance_status['count']}"
        
        # 뉴스 상태
        news_status_text = f"상태: {news_status['status']}"
        news_last_update = f"마지막 업데이트: {news_status['last_update'] if news_status['last_update'] else '없음'}"
        news_count = f"수집된 데이터 수: {news_status['count']}"
        
        return (
            binance_status_text, binance_last_update, binance_count,
            news_status_text, news_last_update, news_count
        )

# 거래량 차트 업데이트 콜백
def register_volume_chart_callback(app, data_cache):
    @app.callback(
        Output("volume-chart", "figure"),
        [Input("interval-component", "n_intervals"),
         Input("coin-selector", "value"),
         Input("candle-interval", "value")]
    )
    def update_volume_chart(n, selected_coin, interval):
        # 선택된 코인에 해당하는 심볼 찾기
        binance_symbol = f"{selected_coin}USDT"
        
        # 빈 차트 초기화
        fig = go.Figure()
        
        # 캔들스틱 데이터 가져오기
        if "candle_data" in data_cache and binance_symbol in data_cache["candle_data"]:
            # 새로운 구조: 심볼 -> 간격 -> 데이터
            symbol_candles = data_cache["candle_data"][binance_symbol]
            
            # 선택된 간격의 데이터가 있는지 확인
            if interval in symbol_candles and not symbol_candles[interval].empty:
                df_candles = symbol_candles[interval]
                
                # 거래량 바 차트 추가
                fig.add_trace(go.Bar(
                    x=df_candles["timestamp"],
                    y=df_candles["volume"],
                    name="거래량",
                    marker=dict(
                        color='rgba(58, 71, 80, 0.6)',
                        line=dict(color='rgba(58, 71, 80, 1.0)', width=1)
                    )
                ))
            else:
                # 선택된 간격의 데이터가 없는 경우
                fig.add_annotation(
                    text=f"{selected_coin}에 대한 {interval} 거래량 데이터가 없습니다",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=20)
                )
        else:
            # 데이터가 없는 경우 빈 차트 표시
            fig.add_annotation(
                text=f"{selected_coin}에 대한 거래량 데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
        
        # 차트 레이아웃 설정
        fig.update_layout(
            title=f"{selected_coin}/USDT {interval} 거래량",
            xaxis_title="시간",
            yaxis_title="거래량",
            template="plotly_white",
            showlegend=False,
            margin=dict(l=40, r=40, t=40, b=40),
            xaxis=dict(
                type="date",
                rangeslider=dict(visible=False)
            )
        )
        
        # 차트 스타일 개선
        fig.update_xaxes(
            gridcolor='rgba(200, 200, 200, 0.2)',
            showgrid=True,
            zeroline=False
        )
        
        fig.update_yaxes(
            gridcolor='rgba(200, 200, 200, 0.2)',
            showgrid=True,
            zeroline=False
        )
        
        return fig

# 캔들스틱 차트 업데이트 콜백
def register_candle_chart_callback(app, data_cache):
    @app.callback(
        Output("candle-chart", "figure"),
        [Input("interval-component", "n_intervals"),
         Input("coin-selector", "value"),
         Input("candle-interval", "value"),
         Input("indicator-toggles", "value")]
    )
    def update_candle_chart(n, selected_coin, interval, indicators):
        # 선택된 코인에 해당하는 심볼 찾기
        binance_symbol = f"{selected_coin}USDT"
        
        # 빈 차트 초기화
        fig = go.Figure()
        
        # 캔들스틱 데이터 가져오기
        if "candle_data" in data_cache and binance_symbol in data_cache["candle_data"]:
            # 새로운 구조: 심볼 -> 간격 -> 데이터
            symbol_candles = data_cache["candle_data"][binance_symbol]
            
            # 선택된 간격의 데이터가 있는지 확인
            if interval in symbol_candles and not symbol_candles[interval].empty:
                df_candles = symbol_candles[interval]
                
                # 캔들스틱 차트 추가
                fig.add_trace(go.Candlestick(
                    x=df_candles["timestamp"],
                    open=df_candles["open"],
                    high=df_candles["high"],
                    low=df_candles["low"],
                    close=df_candles["close"],
                    name=f"{selected_coin}/USDT"
                ))
                
                # 볼린저 밴드 추가 (선택된 경우)
                if "bollinger" in indicators:
                    from visualization.dashboard import calculate_bollinger_bands
                    
                    # 볼린저 밴드 계산 (20일 이동평균, 2 표준편차)
                    df_with_bands = calculate_bollinger_bands(df_candles, window=20, num_std=2.0)
                    
                    # 중간 밴드 (20일 이동평균)
                    fig.add_trace(go.Scatter(
                        x=df_with_bands["timestamp"],
                        y=df_with_bands["middle_band"],
                        line=dict(color='rgba(255, 207, 0, 0.7)', width=1),
                        name="MA(20)"
                    ))
                    
                    # 상단 밴드
                    fig.add_trace(go.Scatter(
                        x=df_with_bands["timestamp"],
                        y=df_with_bands["upper_band"],
                        line=dict(color='rgba(0, 128, 255, 0.7)', width=1),
                        name="Upper Band"
                    ))
                    
                    # 하단 밴드
                    fig.add_trace(go.Scatter(
                        x=df_with_bands["timestamp"],
                        y=df_with_bands["lower_band"],
                        line=dict(color='rgba(0, 128, 255, 0.7)', width=1),
                        name="Lower Band",
                        fill='tonexty',
                        fillcolor='rgba(0, 128, 255, 0.05)'
                    ))
                
                # 이동평균선 추가 (선택된 경우)
                if "ma" in indicators:
                    # 7일 이동평균
                    ma7 = df_candles["close"].rolling(window=7).mean()
                    fig.add_trace(go.Scatter(
                        x=df_candles["timestamp"],
                        y=ma7,
                        line=dict(color='rgba(255, 0, 0, 0.7)', width=1),
                        name="MA(7)"
                    ))
                    
                    # 25일 이동평균
                    ma25 = df_candles["close"].rolling(window=25).mean()
                    fig.add_trace(go.Scatter(
                        x=df_candles["timestamp"],
                        y=ma25,
                        line=dict(color='rgba(0, 255, 0, 0.7)', width=1),
                        name="MA(25)"
                    ))
                    
                    # 99일 이동평균
                    ma99 = df_candles["close"].rolling(window=99).mean()
                    fig.add_trace(go.Scatter(
                        x=df_candles["timestamp"],
                        y=ma99,
                        line=dict(color='rgba(128, 0, 128, 0.7)', width=1),
                        name="MA(99)"
                    ))
            else:
                # 선택된 간격의 데이터가 없는 경우
                fig.add_annotation(
                    text=f"{selected_coin}에 대한 {interval} 캔들 데이터가 없습니다",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=20)
                )
        else:
            # 데이터가 없는 경우 빈 차트 표시
            fig.add_annotation(
                text=f"{selected_coin}에 대한 캔들 데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
        
        # 시간 범위 설정
        time_range = None
        if interval == "1m":
            time_range = [datetime.now() - timedelta(hours=12), datetime.now()]
        elif interval == "3m":
            time_range = [datetime.now() - timedelta(hours=18), datetime.now()]
        elif interval == "5m":
            time_range = [datetime.now() - timedelta(days=1), datetime.now()]
        elif interval == "15m":
            time_range = [datetime.now() - timedelta(days=3), datetime.now()]
        elif interval == "30m":
            time_range = [datetime.now() - timedelta(days=5), datetime.now()]
        elif interval == "1h":
            time_range = [datetime.now() - timedelta(days=10), datetime.now()]
        elif interval == "4h":
            time_range = [datetime.now() - timedelta(days=20), datetime.now()]
        elif interval == "1d":
            time_range = [datetime.now() - timedelta(days=60), datetime.now()]
        
        # 차트 레이아웃 설정
        fig.update_layout(
            title=f"{selected_coin}/USDT {interval} 캔들스틱 차트",
            xaxis_title="시간",
            yaxis_title="가격 (USDT)",
            template="plotly_white",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=40, r=40, t=80, b=40),
            xaxis=dict(
                rangeslider=dict(visible=False),  # 하단 슬라이더 비활성화
                type="date"
            )
        )
        
        # 시간 범위 설정 (있는 경우)
        if time_range:
            fig.update_xaxes(range=time_range)
        
        # 차트 스타일 개선
        fig.update_xaxes(
            gridcolor='rgba(200, 200, 200, 0.2)',
            showgrid=True,
            zeroline=False
        )
        
        fig.update_yaxes(
            gridcolor='rgba(200, 200, 200, 0.2)',
            showgrid=True,
            zeroline=False
        )
        
        return fig
# 뉴스 테이블 업데이트 콜백
def register_news_table_callback(app, data_cache):
    @app.callback(
        Output("news-table", "children"),
        [Input("interval-component", "n_intervals"),
         Input("coin-selector", "value"),
         Input("news-page", "data")]
    )
    def update_news_table(n, selected_coin, page):
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
            card = dbc.Card(
                [
                    dbc.CardHeader(
                        html.H5(title, className="card-title")
                    ),
                    dbc.CardBody(
                        [
                            html.H6("내용:", className="card-subtitle mb-2 text-muted"),
                            html.P(content[:200] + "..." if len(content) > 200 else content, className="card-text"),
                            html.H6("요약:", className="card-subtitle mb-2 text-muted mt-3"),
                            html.P(summary, className="card-text"),
                            html.Div(
                                [
                                    html.Small(f"출처: {source}", className="text-muted"),
                                    html.Small(f"발행일: {published_at}", className="text-muted ml-3")
                                ],
                                className="d-flex justify-content-between mt-3"
                            )
                        ]
                    ),
                    dbc.CardFooter(
                        dbc.Button("원문 보기", href=url, target="_blank", color="primary", size="sm")
                    )
                ],
                className="mb-3 shadow-sm"
            )
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

# 페이지 이동 콜백
def register_pagination_callbacks(app):
    @app.callback(
        Output("news-page", "data"),
        [Input("prev-page", "n_clicks"),
         Input("next-page", "n_clicks")],
        [State("news-page", "data")]
    )
    def update_page(prev_clicks, next_clicks, current_page):
        # 콜백 컨텍스트 가져오기
        ctx = dash.callback_context
        
        # 기본값 설정
        if current_page is None:
            current_page = 1
        
        # 어떤 버튼이 클릭되었는지 확인
        if not ctx.triggered:
            return current_page
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "prev-page":
            return max(1, current_page - 1)
        elif button_id == "next-page":
            return current_page + 1
        
        return current_page

# 데이터 수집 통계 차트 업데이트 콜백
def register_collection_stats_callback(app, data_cache):
    @app.callback(
        Output("collection-stats-chart", "figure"),
        [Input("interval-component", "n_intervals")]
    )
    def update_collection_stats_chart(n):
        # 데이터 수집 통계 준비 (Upbit 제외)
        collection_stats = {
            "Binance": data_cache["collection_status"]["binance"]["count"],
            "News": data_cache["collection_status"]["news"]["count"]
        }
        
        # 색상 매핑
        colors = {
            "Binance": "#F0B90B",  # Binance 노란색
            "News": "#28a745"      # 뉴스 녹색
        }
        
        # 바 차트 생성
        fig = px.bar(
            x=list(collection_stats.keys()),
            y=list(collection_stats.values()),
            color=list(collection_stats.keys()),
            color_discrete_map=colors,
            labels={"x": "데이터 소스", "y": "수집된 데이터 수"}
        )
        
        # 차트 레이아웃 설정
        fig.update_layout(
            title="데이터 소스별 수집 통계",
            template="plotly_white",
            showlegend=False,
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        return fig

# 모든 콜백 등록
def register_all_callbacks(app, data_cache):
    register_status_callbacks(app, data_cache)
    register_volume_chart_callback(app, data_cache)
    register_candle_chart_callback(app, data_cache)
    register_news_table_callback(app, data_cache)
    register_pagination_callbacks(app)
    register_collection_stats_callback(app, data_cache)
















