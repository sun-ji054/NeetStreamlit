import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import ttest_ind

# -----------------------------------------------------------------------------
# 0. 페이지 설정 (가장 먼저 실행)
# -----------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="청년 NEET 노동시장 진입 분석",
    page_icon="🧭",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 🎨 [디자인 커스텀] CSS 주입 (배경색, 폰트, 카드 스타일)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
        /* 1. 전체 배경 그라데이션 (Deep Blue & Teal) */
        .stApp {
            background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
            background-attachment: fixed;
            color: #ffffff;
        }
        
        /* 2. 상단 헤더 숨기기 및 여백 조정 */
        header {visibility: hidden;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
        }

        /* 3. 메트릭(Metric) 카드 스타일링 */
        div[data-testid="stMetric"] {
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: white;
            transition: transform 0.2s;
        }
        div[data-testid="stMetric"]:hover {
            transform: scale(1.02);
            background-color: rgba(255, 255, 255, 0.15);
        }
        div[data-testid="stMetricLabel"] {
            color: #dcdcdc !important; /* 라벨 색상 연하게 */
            font-size: 0.9rem !important;
        }
        div[data-testid="stMetricValue"] {
            color: #ffffff !important; /* 값 색상 밝게 */
            font-weight: 700 !important;
        }

        /* 4. 탭(Tab) 스타일링 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
            color: #ffffff;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(46, 204, 113, 0.2) !important;
            border: 1px solid #2ecc71;
            color: #2ecc71 !important;
        }

        /* 5. 텍스트 및 헤더 색상 강제 지정 */
        h1, h2, h3, h4, h5, h6, p, span, div {
            font-family: 'Pretendard', 'Malgun Gothic', sans-serif;
            color: #ffffff;
        }
        
        /* 6. 경고창 등 메시지 박스 스타일 */
        .stAlert {
            background-color: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 🛠 [유틸리티] 차트 테마 통일 함수
# -----------------------------------------------------------------------------
def update_chart_design(fig):
    """모든 Plotly 차트에 다크 테마와 투명 배경을 적용"""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  # 전체 배경 투명
        plot_bgcolor="rgba(0,0,0,0)",   # 플롯 배경 투명
        font=dict(color="#e0e0e0"),     # 폰트 색상 밝게
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color="white")
        ),
        xaxis=dict(showgrid=False, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
    )
    return fig

# -----------------------------------------------------------------------------
# 1. 데이터 로드
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("neet_dashboard_data.csv")
        edu_order = ['고졸 미만', '고졸', '전문대졸', '대졸', '대학원졸']
        health_order = ['매우 나쁨', '나쁜 편', '보통', '좋은 편', '매우 좋음']
        df['edu_label'] = pd.Categorical(df['edu_label'], categories=edu_order, ordered=True)
        df['health_label'] = pd.Categorical(df['health_label'], categories=health_order, ordered=True)
        return df
    except FileNotFoundError:
        st.error("🚨 데이터 파일(neet_dashboard_data.csv)이 없습니다.")
        st.stop()

df = load_data()

# -----------------------------------------------------------------------------
# 2. 사이트 헤더
# -----------------------------------------------------------------------------
c1, c2 = st.columns([0.8, 0.2])
with c1:
    st.title("🚀 청년 NEET, 멈춤에서 길을 찾다")
    st.markdown("#### : 청년패널(YP2021) 데이터를 활용한 노동시장 진입 요인 심층 분석")
with c2:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=80) # 장식용 아이콘

st.divider()

# -----------------------------------------------------------------------------
# 3. 핵심 성과 지표 (KPI)
# -----------------------------------------------------------------------------
total_neet = len(df)
success_count = len(df[df['outcome'] == '취업 성공'])
success_rate = (success_count / total_neet * 100) if total_neet > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("📌 분석 대상 (2021년 NEET)", f"{total_neet:,} 명", delta="청년패널 기반")
col2.metric("💼 진입 성공 (2~3년차)", f"{success_count:,} 명", delta=f"{success_count/total_neet*100:.1f}% 전환")
col3.metric("📈 취업 성공률", f"{success_rate:.1f}%", delta_color="normal")

st.markdown("<br>", unsafe_allow_html=True) # 여백 추가

# -----------------------------------------------------------------------------
# 4. 메인 탭 구성
# -----------------------------------------------------------------------------
tab_titles = [
    "🧠 진로 심리", 
    "🗺️ 인터랙티브 지도", 
    "🔎 구직 경로", 
    "😫 어려움 Top 5", 
    "👫 인구통계", 
    "🏫 학력/지역", 
    "💪 건강"
]
tabs = st.tabs(tab_titles)

# 색상 팔레트 정의 (성공/실패) - 네온 느낌
COLOR_SUCCESS = "#00E676" # Bright Green
COLOR_FAIL = "#FF5252"    # Bright Red
COLOR_MAP = {"취업 성공": COLOR_SUCCESS, "미취업": COLOR_FAIL}

# ==============================
# 📌 TAB 1: 진로 심리 (Radar Chart)
# ==============================
with tabs[0]:
    st.subheader("💡 심리적 요인과 진로 발달")
    col_radar, col_desc = st.columns([1, 1])

    radar_cols = [
        'avg_career_plan_score', 'avg_trouble_deciding_career',
        'avg_uncertain_decision_pending', 'avg_aptitude_not_known'
    ]
    categories = ['계획 명확성', '결정 어려움', '진로 불확실성', '적성 모름']

    with col_radar:
        avg_diff = df.groupby('outcome')[radar_cols].mean().reset_index()
        fig_radar_psych = go.Figure()

        # 취업 성공 군
        if '취업 성공' in avg_diff['outcome'].values:
            success_vals = avg_diff[avg_diff['outcome'] == '취업 성공'][radar_cols].values[0].tolist()
            fig_radar_psych.add_trace(go.Scatterpolar(
                r=success_vals + [success_vals[0]], theta=categories + [categories[0]],
                fill='toself', name='취업 성공', line_color=COLOR_SUCCESS, opacity=0.8
            ))

        # 미취업 군
        if '미취업' in avg_diff['outcome'].values:
            fail_vals = avg_diff[avg_diff['outcome'] == '미취업'][radar_cols].values[0].tolist()
            fig_radar_psych.add_trace(go.Scatterpolar(
                r=fail_vals + [fail_vals[0]], theta=categories + [categories[0]],
                fill='toself', name='미취업', line_color=COLOR_FAIL, opacity=0.6
            ))

        fig_radar_psych.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[1, 5], showticklabels=False, gridcolor="rgba(255,255,255,0.2)"),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.2)", tickfont=dict(color="white", size=12))
            ),
            margin=dict(t=30, b=30)
        )
        st.plotly_chart(update_chart_design(fig_radar_psych), use_container_width=True)

    with col_desc:
        st.markdown("""
        > **인사이트** > **취업 성공 그룹(초록색)**은 상대적으로 **'진로 계획 명확성'**이 높고, 
        > **미취업 그룹(빨간색)**은 **'결정 어려움'**과 **'불확실성'** 수치가 넓게 분포합니다.
        > 
        > 즉, *스킬보다 방향성* 설정이 NEET 탈출의 핵심일 수 있습니다.
        """)
        
        # 박스플롯 3개 작은 사이즈로
        sub_c1, sub_c2, sub_c3 = st.columns(3)
        common_box_opts = {"x": "outcome", "color": "outcome", 
                           "color_discrete_map": COLOR_MAP}
        
        with sub_c1:
            st.caption("① 계획 명확성")
            fig = px.box(df, y="avg_career_plan_score", **common_box_opts)
            fig.update_layout(showlegend=False, margin=dict(l=0,r=0,t=0,b=0), height=200)
            st.plotly_chart(update_chart_design(fig), use_container_width=True)
        with sub_c2:
            st.caption("② 결정 어려움")
            fig = px.box(df, y="avg_trouble_deciding_career", **common_box_opts)
            fig.update_layout(showlegend=False, margin=dict(l=0,r=0,t=0,b=0), height=200)
            st.plotly_chart(update_chart_design(fig), use_container_width=True)
        with sub_c3:
            st.caption("③ 불확실성")
            fig = px.box(df, y="avg_uncertain_decision_pending", **common_box_opts)
            fig.update_layout(showlegend=False, margin=dict(l=0,r=0,t=0,b=0), height=200)
            st.plotly_chart(update_chart_design(fig), use_container_width=True)


# ==============================
# 📌 TAB 2: 지도 (Interactive Map)
# ==============================
with tabs[1]:
    st.subheader("🗺️ 지역별 심층 분석 (Interactive Map)")
    st.caption("👇 지도 위의 원을 클릭하면 하단에 상세 분석 리포트가 펼쳐집니다.")

    # -------------------------------------------------------------------------
    # 1. 데이터 집계 및 준비
    # -------------------------------------------------------------------------
    agg_funcs = {
        'sampid': 'count', 
        'got_job_flag': 'mean', 
        'self_efficacy': 'mean', 
        'career_plan_score': 'mean'
    }
    # 경험 유무 컬럼 생성
    df['experience'] = df['exp_type'].apply(lambda x: 1 if x in ['인턴/현장실습', '아르바이트', '창업 경험'] else 0)
    agg_funcs['experience'] = 'mean'

    # 지역별 그룹화
    map_deep_df = df.groupby('region_label', observed=False).agg(agg_funcs).reset_index()
    
    # 표시용 컬럼 계산
    map_deep_df['취업 성공률(%)'] = (map_deep_df['got_job_flag'] * 100).round(1)
    map_deep_df['자아효능감(점)'] = map_deep_df['self_efficacy'].round(2)
    map_deep_df['진로계획 명확성(점)'] = map_deep_df['career_plan_score'].round(2)
    map_deep_df['일 경험률(%)'] = (map_deep_df['experience'] * 100).round(1)
    
    # 전국 평균 계산 (비교용)
    national_avg = map_deep_df.mean(numeric_only=True)

    # 좌표 매핑
    region_coords = {
        '서울': [37.5665, 126.9780], '부산': [35.1796, 129.0756], '대구': [35.8714, 128.6014],
        '인천': [37.4563, 126.7052], '광주': [35.1601, 126.8517], '대전': [36.3504, 127.3845],
        '울산': [35.5384, 129.3114], '세종': [36.4800, 127.2890], '경기': [37.4138, 127.5183],
        '강원': [37.8228, 128.1555], '충북': [36.6350, 127.4914], '충남': [36.5184, 126.8000],
        '전북': [35.7175, 127.1530], '전남': [34.8161, 126.4629], '경북': [36.5783, 128.5093],
        '경남': [35.2383, 128.6925], '제주': [33.4996, 126.5312]
    }
    map_deep_df['lat'] = map_deep_df['region_label'].map(lambda x: region_coords.get(x, [None, None])[0])
    map_deep_df['lon'] = map_deep_df['region_label'].map(lambda x: region_coords.get(x, [None, None])[1])
    
    plot_df = map_deep_df.dropna(subset=['lat', 'lon']).reset_index(drop=True)

    # -------------------------------------------------------------------------
    # 2. 지도 그리기
    # -------------------------------------------------------------------------
    if not plot_df.empty:
        fig_map = px.scatter_mapbox(
            plot_df, 
            lat="lat", lon="lon", 
            size="sampid",
            color="취업 성공률(%)",
            color_continuous_scale="Tealgrn", # 디자인 테마에 맞춘 컬러
            size_max=40, 
            zoom=6,
            center={"lat": 36.5, "lon": 127.8},
            mapbox_style="carto-darkmatter", # 다크 모드 지도
            hover_name="region_label",
            hover_data={"lat":False, "lon":False, "sampid":True, "취업 성공률(%)":True}
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)")
        
        # 클릭 이벤트 감지
        event = st.plotly_chart(
            fig_map, 
            use_container_width=True, 
            on_select="rerun", 
            selection_mode="points"
        )
    else:
        st.warning("지도 데이터가 없습니다.")
        event = None

    # -------------------------------------------------------------------------
    # 3. 클릭 시 상세 분석 로직
    # -------------------------------------------------------------------------
    selected_region = None
    
    # 클릭된 포인트가 있는지 확인
    if event and event['selection']['points']:
        idx = event['selection']['points'][0]['point_index']
        selected_region = plot_df.iloc[idx]['region_label']

    if selected_region:
        st.divider()
        st.markdown(f"### 🔍 [{selected_region}] 지역 상세 분석")
        
        region_data = map_deep_df[map_deep_df['region_label'] == selected_region].iloc[0]

        # 🔹 [Section 1] 핵심 지표 카드
        # (CSS 스타일이 적용된 Metric 카드)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("대상 인원", f"{int(region_data['sampid'])}명")
        c2.metric("취업 성공률", f"{region_data['취업 성공률(%)']}%")
        c3.metric("자아효능감(5점 만점)", f"{region_data['자아효능감(점)']}점")
        c4.metric("진로계획 명확성(5점 만점)", f"{region_data['진로계획 명확성(점)']}점")
        c5.metric("일 경험률", f"{region_data['일 경험률(%)']}%")
        
        st.write("") # 여백

        # 🔹 [Section 2] 일 경험률 상세 (Toggle & Pie Chart)
        show_exp = st.toggle("🔍 일 경험률 상세 보기", value=False)
        
        if show_exp:
            st.markdown("##### 🥧 활동경험 분포")
            region_subset = df[df['region_label'] == selected_region]
            exp_counts = region_subset['exp_type'].value_counts().reindex(
                ["인턴/현장실습", "아르바이트", "창업 경험", "기타", "경험 없음"],
                fill_value=0
            )

            fig_pie = px.pie(
                names=exp_counts.index,
                values=exp_counts.values,
                hole=0.4,
                title=f"{selected_region} 활동경험 비율",
                color_discrete_sequence=px.colors.sequential.Teal
            )
            fig_pie.update_traces(textinfo='percent+label')
            # 파이 차트 디자인 (투명 배경)
            fig_pie.update_layout(
                title_font_color="#ffffff",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                showlegend=True
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        st.divider()
        
        # 🔹 [Section 3] 레이더 차트 (지역 vs 전국 평균)
        col_radar_chart, col_radar_text = st.columns([2, 1])

        with col_radar_chart:
            st.markdown("#### 🕸️ 지역 강점/약점 분석 (전국 평균=100 기준)")
            
            radar_metrics = {
                '취업 성공률':'got_job_flag',
                '자아효능감':'self_efficacy',
                '진로계획':'career_plan_score',
                '일 경험률': 'experience'
            }

            radar_r = []
            categories = []

            for label, col in radar_metrics.items():
                reg = region_data[col]
                nat = national_avg[col]
                # 전국 평균 대비 % 계산
                score = (reg / nat * 100) if nat > 0 else 0
                radar_r.append(score)
                categories.append(label)

            radar_df = pd.DataFrame(dict(r=radar_r, theta=categories))

            fig_radar = px.line_polar(
                radar_df,
                r='r', theta='theta',
                line_close=True,
                title=f"{selected_region} vs 전국 평균(100)"
            )
            
            # 레이더 차트 디자인 (다크 모드 최적화)
            fig_radar.update_traces(fill='toself', line_color='#00E676') # 형광 초록
            fig_radar.update_layout(
                title_font_color="#ffffff",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,0.2)", tickfont=dict(color="gray")),
                    angularaxis=dict(gridcolor="rgba(255,255,255,0.2)", tickfont=dict(color="white", size=13))
                ),
                font=dict(color="white")
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        # 🔹 [Section 4] 자동 분석 텍스트
        with col_radar_text:
            st.markdown("<br><br>", unsafe_allow_html=True) # 줄바꿈으로 위치 조정
            
            max_val = max(radar_r)
            min_val = min(radar_r)
            max_idx = radar_r.index(max_val)
            min_idx = radar_r.index(min_val)
            
            strong_point = categories[max_idx]
            weak_point = categories[min_idx]

            st.info(f"""
            **💡 AI Insight**
            
            **{selected_region}** 지역은 전국 평균 대비
            **'{strong_point}'** 수치가 **{max_val:.1f}**점으로 가장 우수합니다.
            
            반면, **'{weak_point}'** 수치는 상대적으로 보완이 필요해 보입니다.
            """)
# ==============================
# 📌 TAB 3: 구직 경로
# ==============================
with tabs[2]:
    st.subheader("📢 어떻게 일자리를 찾았을까?")
    
    if 'search_method' in df.columns:
        search_df = df[df['search_method'] != '응답 없음']
        
        c1, c2 = st.columns([1, 1])
        with c1:
            path_counts = search_df['search_method'].value_counts().reset_index()
            path_counts.columns = ['구직 경로', '인원수']
            fig = px.bar(path_counts, x='인원수', y='구직 경로', orientation='h', text='인원수',
                         color='인원수', color_continuous_scale='Bluyl')
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}, title={
                    'text': "가장 많이 시도한 방법",
                    'font': {'color': '#ffffff', 'size': 17} 
                })
            st.plotly_chart(update_chart_design(fig), use_container_width=True)

        with c2:
            method_counts = search_df['search_method'].value_counts()
            valid_methods = method_counts[method_counts >= 5].index
            valid_df = search_df[search_df['search_method'].isin(valid_methods)]
            
            path_succ = valid_df.groupby('search_method')['got_job_flag'].mean().reset_index()
            path_succ['성공률'] = path_succ['got_job_flag'] * 100
            path_succ = path_succ.sort_values(by='성공률', ascending=False)
            
            fig2 = px.bar(path_succ, x='성공률', y='search_method', orientation='h', text_auto='.1f',
                          color='성공률', color_continuous_scale='Greens')
            fig2.update_layout(yaxis={'categoryorder': 'total ascending'}, title={
                    'text': "실제 성공률이 높은 방법",
                    'font': {'color': '#ffffff', 'size': 17} 
                })
            st.plotly_chart(update_chart_design(fig2), use_container_width=True)

# ==============================
# 📌 TAB 4: 어려움 Top 5 (Clean Bar)
# ==============================
with tabs[3]:
    st.subheader("😫 구직 중 가장 큰 장벽은?")
    
    diff_counts = df['main_difficulty'].value_counts().drop("해당없음", errors='ignore').head(5)
    diff_df = pd.DataFrame({"항목": diff_counts.index, "빈도": diff_counts.values})
    diff_df["비율"] = (diff_df["빈도"] / len(df) * 100).round(1)

    fig = px.bar(diff_df, x="항목", y="비율", text="비율", color="항목",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(showlegend=False, height=500, font=dict(size=14))
    st.plotly_chart(update_chart_design(fig), use_container_width=True)

# ==============================
# 📌 TAB 5: 인구통계
# ==============================
with tabs[4]:
    st.subheader("👫 성별 및 나이 분포")
    c1, c2 = st.columns(2)
    
    with c1:
        fig = px.histogram(df, x="gender_label", color="outcome", barmode="group", text_auto=True,
                           color_discrete_map=COLOR_MAP, title="성별 취업 성공 현황")
        st.plotly_chart(update_chart_design(fig), use_container_width=True)
        
    with c2:
        if 'age_group' not in df.columns:
            df['age_group'] = pd.cut(df['age'], bins=[18, 24, 29], labels=['19-24세', '25-29세'])
        
        grouped = df.groupby(['age_group', 'gender_label'], observed=False)['got_job_flag'].mean().reset_index()
        grouped['rate'] = grouped['got_job_flag'] * 100
        
        fig2 = px.bar(grouped, x='age_group', y='rate', color='gender_label', barmode='group',
                      text_auto='.1f', title="연령대/성별 성공률 (%)",
                      color_discrete_map={'남성': '#29B6F6', '여성': '#FF7043'})
        st.plotly_chart(update_chart_design(fig2), use_container_width=True)

# ==============================
# 📌 TAB 6: 학력 및 지역
# ==============================
with tabs[5]:
    st.subheader("🏫 학력과 거주지")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(df, x="edu_label", color="outcome", barmode="group",
                           color_discrete_map=COLOR_MAP, title="학력별 분포")
        st.plotly_chart(update_chart_design(fig), use_container_width=True)
    with c2:
        fig2 = px.histogram(df, y="region_label", color="outcome", barmode="stack", orientation='h',
                            color_discrete_map=COLOR_MAP, title="지역별 분포")
        fig2.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(update_chart_design(fig2), use_container_width=True)

# ==============================
# 📌 TAB 7: 건강
# ==============================
with tabs[6]:
    st.subheader("💪 건강 상태와 취업")
    
    health_counts = df.groupby(['health_label', 'outcome'], observed=False).size().reset_index(name='count')
    health_total = df.groupby('health_label', observed=False).size().reset_index(name='total')
    merged = health_counts.merge(health_total, on='health_label')
    merged['ratio'] = merged['count'] / merged['total'] * 100
    
    fig = px.bar(merged, x="health_label", y="ratio", color="outcome", text_auto='.1f',
                 color_discrete_map=COLOR_MAP, title="주관적 건강 상태별 취업률")
    st.plotly_chart(update_chart_design(fig), use_container_width=True)