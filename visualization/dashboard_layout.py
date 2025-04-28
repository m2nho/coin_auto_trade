#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
데이터 수집 시각화 대시보드 레이아웃

이 모듈은 대시보드의 레이아웃과 UI 컴포넌트를 정의합니다.
"""

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px

# 대시보드 헤더 컴포넌트
def create_header():
    return dbc.Row(
        dbc.Col(
            html.Div(
                [
                    html.H1("암호화폐 데이터 수집 대시보드", className="display-4"),
                    html.P("실시간 데이터 수집 현황 및 시각화", className="lead")
                ],
                className="p-4 bg-light rounded-3"
            ),
            width=12
        ),
        className="mb-4"
    )

# 데이터 수집 상태 카드 컴포넌트
def create_status_cards():
    return dbc.Row(
        [
            # Binance 데이터 수집 상태 카드
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H4("Binance 데이터 수집", className="card-title")),
                        dbc.CardBody(
                            [
                                html.P("상태: ", className="card-text", id="binance-status"),
                                html.P("마지막 업데이트: ", className="card-text", id="binance-last-update"),
                                html.P("수집된 데이터 수: ", className="card-text", id="binance-count")
                            ]
                        )
                    ],
                    className="mb-4 shadow-sm"
                ),
                md=6
            ),
            
            # 뉴스 데이터 수집 상태 카드
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H4("뉴스 데이터 수집", className="card-title")),
                        dbc.CardBody(
                            [
                                html.P("상태: ", className="card-text", id="news-status"),
                                html.P("마지막 업데이트: ", className="card-text", id="news-last-update"),
                                html.P("수집된 데이터 수: ", className="card-text", id="news-count")
                            ]
                        )
                    ],
                    className="mb-4 shadow-sm"
                ),
                md=6
            )
        ],
        className="mb-4"
    )

# 코인 가격 차트 컴포넌트
def create_price_charts():
    return dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            dbc.Row(
                                [
                                    dbc.Col(html.H4("코인 가격 차트", className="card-title"), width=6),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id="coin-selector",
                                            options=[
                                                {"label": "Bitcoin (BTC)", "value": "BTC"},
                                                {"label": "Ethereum (ETH)", "value": "ETH"},
                                                {"label": "Binance Coin (BNB)", "value": "BNB"},
                                                {"label": "Cardano (ADA)", "value": "ADA"},
                                                {"label": "Dogecoin (DOGE)", "value": "DOGE"}
                                            ],
                                            value="BTC",
                                            clearable=False
                                        ),
                                        width=4
                                    ),
                                    dbc.Col(
                                        dbc.Checklist(
                                            options=[
                                                {"label": "볼린저 밴드 표시", "value": "on"}
                                            ],
                                            value=[],
                                            id="bollinger-toggle",
                                            switch=True,
                                        ),
                                        width=2
                                    )
                                ]
                            )
                        ),
                        dbc.CardBody(
                            [
                                dcc.Graph(id="price-chart", style={"height": "500px"})
                            ]
                        )
                    ],
                    className="mb-4 shadow-sm"
                ),
                md=12
            )
        ],
        className="mb-4"
    )

# 거래량 차트 컴포넌트
def create_volume_charts():
    return dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H4("Binance 거래량 차트", className="card-title")),
                        dbc.CardBody(
                            [
                                dcc.Graph(id="volume-chart", style={"height": "300px"})
                            ]
                        )
                    ],
                    className="mb-4 shadow-sm"
                ),
                md=6
            ),
            
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H4("캔들스틱 차트", className="card-title")),
                        dbc.CardBody(
                            [
                                dcc.Graph(id="candle-chart", style={"height": "300px"})
                            ]
                        )
                    ],
                    className="mb-4 shadow-sm"
                ),
                md=6
            )
        ],
        className="mb-4"
    )

# 뉴스 데이터 테이블 컴포넌트
def create_news_table():
    return dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H4("최근 뉴스 데이터", className="card-title")),
                        dbc.CardBody(
                            [
                                html.Div(id="news-table")
                            ]
                        )
                    ],
                    className="mb-4 shadow-sm"
                ),
                md=12
            )
        ],
        className="mb-4"
    )

# 데이터 수집 통계 컴포넌트
def create_collection_stats():
    return dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H4("데이터 수집 통계", className="card-title")),
                        dbc.CardBody(
                            [
                                dcc.Graph(id="collection-stats-chart", style={"height": "300px"})
                            ]
                        )
                    ],
                    className="mb-4 shadow-sm"
                ),
                md=12
            )
        ],
        className="mb-4"
    )

# 전체 대시보드 레이아웃 생성
def create_layout():
    return dbc.Container(
        [
            create_header(),
            create_status_cards(),
            create_price_charts(),
            create_volume_charts(),
            create_news_table(),
            create_collection_stats(),
            
            # 데이터 자동 업데이트를 위한 인터벌 컴포넌트
            dcc.Interval(
                id="interval-component",
                interval=30 * 1000,  # 30초마다 업데이트
                n_intervals=0
            ),
            
            # 뉴스 페이지 상태를 저장하기 위한 숨겨진 컴포넌트
            dcc.Store(id="news-page", data=1)
        ],
        fluid=True,
        className="p-4"
    )




