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