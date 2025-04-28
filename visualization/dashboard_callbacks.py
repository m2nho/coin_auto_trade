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

# 가격 차트 업데이트 콜백
def register_price_chart_callback(app, data_cache):
    @app.callback(
        Output("price-chart", "figure"),
        [Input("interval-component", "n_intervals"),
         Input("coin-selector", "value"),
         Input("bollinger-toggle", "value")]
    )
    def update_price_chart(n, selected_coin, show_bollinger):
        # 선택된 코인에 해당하는 심볼 찾기
        binance_symbol = f"{selected_coin}USDT"
        
        # 빈 차트 초기화
        fig = go.Figure()
        
        # 데이터 존재 여부 플래그
        has_data = False
        
        # 웹소켓 데이터 확인
        if binance_symbol in data_cache["websocket_data"] and data_cache["websocket_data"][binance_symbol]:
            # 웹소켓 데이터를 DataFrame으로 변환
            ws_data = data_cache["websocket_data"][binance_symbol]
            df_ws = pd.DataFrame(ws_data)
            
            if not df_ws.empty:
                has_data = True
                # 실시간 데이터 추가
                fig.add_trace(go.Scatter(
                    x=df_ws["timestamp"],
                    y=df_ws["price"],
                    mode="lines",
                    name=f"Binance {selected_coin}/USDT (실시간)",
                    line=dict(color="#F0B90B", width=2)
                ))
                
                # 볼린저 밴드 계산 및 추가
                if show_bollinger and "on" in show_bollinger and len(df_ws) > 20:
                    from visualization.dashboard import calculate_bollinger_bands
                    df_bb = calculate_bollinger_bands(df_ws.copy())
                    
                    # 중간 밴드 (20일 이동평균)
                    fig.add_trace(go.Scatter(
                        x=df_bb["timestamp"],
                        y=df_bb["middle_band"],
                        mode="lines",
                        name="중간 밴드 (20일 MA)",
                        line=dict(color="rgba(0, 0, 255, 0.5)", width=1)
                    ))
                    
                    # 상단 밴드
                    fig.add_trace(go.Scatter(
                        x=df_bb["timestamp"],
                        y=df_bb["upper_band"],
                        mode="lines",
                        name="상단 밴드",
                        line=dict(color="rgba(0, 255, 0, 0.5)", width=1)
                    ))
                    
                    # 하단 밴드
                    fig.add_trace(go.Scatter(
                        x=df_bb["timestamp"],
                        y=df_bb["lower_band"],
                        mode="lines",
                        name="하단 밴드",
                        line=dict(color="rgba(255, 0, 0, 0.5)", width=1),
                        fill='tonexty',
                        fillcolor='rgba(200, 200, 255, 0.2)'
                    ))
        
        # 기존 데이터베이스 데이터 추가
        if not has_data and "coin_data" in data_cache and binance_symbol in data_cache["coin_data"]:
            df_binance = data_cache["coin_data"][binance_symbol]
            if not df_binance.empty:
                has_data = True
                fig.add_trace(go.Scatter(
                    x=df_binance["timestamp"],
                    y=df_binance["price"],
                    mode="lines",
                    name=f"Binance {selected_coin}/USDT",
                    line=dict(color="#F0B90B", width=2)
                ))
                
                # 볼린저 밴드 계산 및 추가
                if show_bollinger and "on" in show_bollinger and len(df_binance) > 20:
                    from visualization.dashboard import calculate_bollinger_bands
                    df_bb = calculate_bollinger_bands(df_binance.copy())
                    
                    # 중간 밴드 (20일 이동평균)
                    fig.add_trace(go.Scatter(
                        x=df_bb["timestamp"],
                        y=df_bb["middle_band"],
                        mode="lines",
                        name="중간 밴드 (20일 MA)",
                        line=dict(color="rgba(0, 0, 255, 0.5)", width=1)
                    ))
                    
                    # 상단 밴드
                    fig.add_trace(go.Scatter(
                        x=df_bb["timestamp"],
                        y=df_bb["upper_band"],
                        mode="lines",
                        name="상단 밴드",
                        line=dict(color="rgba(0, 255, 0, 0.5)", width=1)
                    ))
                    
                    # 하단 밴드
                    fig.add_trace(go.Scatter(
                        x=df_bb["timestamp"],
                        y=df_bb["lower_band"],
                        mode="lines",
                        name="하단 밴드",
                        line=dict(color="rgba(255, 0, 0, 0.5)", width=1),
                        fill='tonexty',
                        fillcolor='rgba(200, 200, 255, 0.2)'
                    ))
        
        # 데이터가 없는 경우 메시지 표시
        if not has_data:
            fig.add_annotation(
                text="가격 데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
        
        # 차트 레이아웃 설정
        fig.update_layout(
            title=f"{selected_coin} 가격 추이 (24시간)",
            xaxis_title="시간",
            yaxis_title="가격 (USD)",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=60, b=40),
            height=500  # 차트 높이 증가
        )
        
        # X축 범위 설정 (최근 24시간)
        fig.update_xaxes(
            range=[datetime.now() - timedelta(hours=24), datetime.now()],
            rangeslider_visible=False
        )
        
        return fig

# 거래량 차트 업데이트 콜백
def register_volume_chart_callback(app, data_cache):
    @app.callback(
        Output("volume-chart", "figure"),
        [Input("interval-component", "n_intervals"),
         Input("coin-selector", "value")]
    )
    def update_volume_chart(n, selected_coin):
        # 선택된 코인에 해당하는 심볼 찾기
        binance_symbol = f"{selected_coin}USDT"
        
        # Binance 거래량 데이터 준비
        volume = 0
        
        # Binance 거래량 합산
        if binance_symbol in data_cache["coin_data"]:
            df_binance = data_cache["coin_data"][binance_symbol]
            if not df_binance.empty:
                volume = df_binance["volume"].sum()
        
        # 바 차트 생성
        fig = px.bar(
            x=["Binance"],
            y=[volume],
            color=["Binance"],
            color_discrete_map={"Binance": "#F0B90B"},
            labels={"x": "거래소", "y": "24시간 거래량"}
        )
        
        # 차트 레이아웃 설정
        fig.update_layout(
            title=f"{selected_coin} 거래량",
            template="plotly_white",
            showlegend=False,
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        return fig

# 캔들스틱 차트 업데이트 콜백
def register_candle_chart_callback(app, data_cache):
    @app.callback(
        Output("candle-chart", "figure"),
        [Input("interval-component", "n_intervals"),
         Input("coin-selector", "value")]
    )
    def update_candle_chart(n, selected_coin):
        # 선택된 코인에 해당하는 심볼 찾기
        binance_symbol = f"{selected_coin}USDT"
        
        # 빈 차트 초기화
        fig = go.Figure()
        
        # 캔들스틱 데이터 가져오기 (예시 데이터)
        # 실제로는 데이터베이스에서 캔들스틱 데이터를 가져와야 함
        if "candle_data" in data_cache and binance_symbol in data_cache["candle_data"]:
            df_candles = data_cache["candle_data"][binance_symbol]
            
            fig.add_trace(go.Candlestick(
                x=df_candles["timestamp"],
                open=df_candles["open"],
                high=df_candles["high"],
                low=df_candles["low"],
                close=df_candles["close"],
                name=f"{selected_coin} 캔들"
            ))
        else:
            # 데이터가 없는 경우 빈 차트 표시
            fig.add_annotation(
                text="캔들스틱 데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
        
        # 차트 레이아웃 설정
        fig.update_layout(
            title=f"{selected_coin} 캔들스틱 차트",
            xaxis_title="시간",
            yaxis_title="가격 (USD)",
            template="plotly_white",
            xaxis_rangeslider_visible=False,
            margin=dict(l=40, r=40, t=60, b=40)
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
    register_price_chart_callback(app, data_cache)
    register_volume_chart_callback(app, data_cache)
    register_candle_chart_callback(app, data_cache)
    register_news_table_callback(app, data_cache)
    register_pagination_callbacks(app)
    register_collection_stats_callback(app, data_cache)
















