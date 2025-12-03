import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from scipy.stats import ttest_ind
import pydeck as pdk


st.set_page_config(layout="wide", page_title="청년 NEET 노동시장 진입 분석")

# -----------------------------------------------------------------------------
# 1. 데이터 로드
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("neet_dashboard_data.csv")
        # 학력, 건강상태 순서 지정을 위한 Categorical 변환 (그래프 정렬용)
        edu_order = ['고졸 미만', '고졸', '전문대졸', '대졸', '대학원졸']
        health_order = ['매우 나쁨', '나쁜 편', '보통', '좋은 편', '매우 좋음']
        df['edu_label'] = pd.Categorical(df['edu_label'], categories=edu_order, ordered=True)
        df['health_label'] = pd.Categorical(df['health_label'], categories=health_order, ordered=True)
        return df
    except FileNotFoundError:
        st.error("데이터 파일(neet_dashboard_data.csv)이 없습니다. make_data.py를 먼저 실행해주세요.")
        st.stop()

df = load_data()



# seoul = df[df['region_label'] == '서울']

# st.dataframe(
#     seoul[['region_label', 'exp_type']],
#     use_container_width=True
# )


# -----------------------------------------------------------------------------
# 1. 사이트 타이틀
# -----------------------------------------------------------------------------
st.title("🚧 일하지 않는 청년들, 멈춤에서 길을 찾다")
st.markdown("##### : 청년패널(YP2021) NEET 청년의 노동시장 진입 요인 분석")

# -----------------------------------------------------------------------------
# 2. 사이드 바
# -----------------------------------------------------------------------------
# st.sidebar.success("Select a demo above.")

# -----------------------------------------------------------------------------
# 3. 요약 지표
# -----------------------------------------------------------------------------
st.markdown("### 1. 현황 요약")
col1, col2, col3 = st.columns(3)

total_neet = len(df)
success_count = len(df[df['outcome'] == '취업 성공'])
success_rate = (success_count / total_neet * 100) if total_neet > 0 else 0

col1.metric("분석 대상 (2021년 NEET)", f"{total_neet:,} 명")
col2.metric("노동시장 진입 성공 (2~3년차)", f"{success_count:,} 명")
col3.metric("진입 성공률", f"{success_rate:.1f}%")

st.divider()

# -----------------------------------------------------------------------------
# 4. Part: 진로발달
# -----------------------------------------------------------------------------
st.header("진로발달 특성 비교")

tab11, tab13, tab17, tab18, tab14, tab15, tab16 = st.tabs(["진로발달", "🔎 구직 노력(경로)", "지도", '📊 구직 중 가장 어려웠던 점(Top 5)', "📊 인구통계학적 특성", "🏫 학력 및 지역", "💪 건강 상태"])

# ==============================
# 📌 TAB 11 — 레이더 차트
# ==============================
with tab11:
    st.subheader("3개년 평균 진로발달 요인 비교")
    radar_cols = [
        'avg_career_plan_score',
        'avg_trouble_deciding_career',
        'avg_uncertain_decision_pending',
        'avg_aptitude_not_known'
    ]

    categories = ['진로 계획 명확성', '진로결정 어려움', '진로 불확실성', '적성을 모름']

    # 그룹별 평균 계산
    avg_diff = df.groupby('outcome')[radar_cols].mean().reset_index()

    fig_radar_psych = go.Figure()

    # 취업 성공 군
    if '취업 성공' in avg_diff['outcome'].values:
        success_vals = avg_diff[avg_diff['outcome'] == '취업 성공'][radar_cols].values[0].tolist()
        fig_radar_psych.add_trace(go.Scatterpolar(
            r=success_vals + [success_vals[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='취업 성공',
            line_color='#2ecc71'
        ))

    # 미취업 군
    if '미취업' in avg_diff['outcome'].values:
        fail_vals = avg_diff[avg_diff['outcome'] == '미취업'][radar_cols].values[0].tolist()
        fig_radar_psych.add_trace(go.Scatterpolar(
            r=fail_vals + [fail_vals[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='미취업',
            line_color='#e74c3c'
        ))

    fig_radar_psych.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[1, 5])),
        # title="3개년 평균 진로발달 요인 비교"
    )

    st.plotly_chart(fig_radar_psych, use_container_width=True)

    common_box_opts = {
        "x": "outcome",
        "color": "outcome",
        "category_orders": {"outcome": ["취업 성공", "미취업"]},
        "color_discrete_map": {"취업 성공": "#2ecc71", "미취업": "#e74c3c"}
    }

    st.divider()
    st.subheader("진로발달 상세")

    b_col1, b_col2, b_col3 = st.columns(3)

    # -------------------
    # ① 진로 계획 명확성
    # -------------------
    with b_col1:
        st.markdown("**① 진로 계획 명확성**")
        fig_b1 = px.box(df, y="avg_career_plan_score", **common_box_opts)
        fig_b1.update_layout(showlegend=False)
        st.plotly_chart(fig_b1, use_container_width=True)

        # T-test
        g1 = df[df['outcome'] == '취업 성공']['avg_career_plan_score'].dropna()
        g2 = df[df['outcome'] == '미취업']['avg_career_plan_score'].dropna()
        t_stat, p_val = ttest_ind(g1, g2, equal_var=False)
        st.markdown(f"📌 **t-test p-value:** `{p_val:.4f}`")

    # -------------------
    # ② 진로결정 어려움
    # -------------------
    with b_col2:
        st.markdown("**② 진로결정 어려움**")
        fig_b2 = px.box(df, y="avg_trouble_deciding_career", **common_box_opts)
        fig_b2.update_layout(showlegend=False)
        st.plotly_chart(fig_b2, use_container_width=True)

        # T-test
        g1 = df[df['outcome'] == '취업 성공']['avg_trouble_deciding_career'].dropna()
        g2 = df[df['outcome'] == '미취업']['avg_trouble_deciding_career'].dropna()
        t_stat, p_val = ttest_ind(g1, g2, equal_var=False)
        st.markdown(f"📌 **t-test p-value:** `{p_val:.4f}`")

    # -------------------
    # ③ 진로 불확실성
    # -------------------
    with b_col3:
        st.markdown("**③ 진로 불확실성**")
        fig_b3 = px.box(df, y="avg_uncertain_decision_pending", **common_box_opts)
        fig_b3.update_layout(showlegend=False)
        st.plotly_chart(fig_b3, use_container_width=True)

        # T-test
        g1 = df[df['outcome'] == '취업 성공']['avg_uncertain_decision_pending'].dropna()
        g2 = df[df['outcome'] == '미취업']['avg_uncertain_decision_pending'].dropna()
        t_stat, p_val = ttest_ind(g1, g2, equal_var=False)
        st.markdown(f"📌 **t-test p-value:** `{p_val:.4f}`")


# ==============================
# 📌 TAB 13 — 구직 정보 취득 경로
# ==============================
with tab13:
    st.subheader("📢 구직 정보 취득 경로 (1순위)")

    # '응답 없음' 제거한 데이터만 분석
    if 'search_method' in df.columns:
        search_df = df[df['search_method'] != '응답 없음']

        # 응답자가 0명일 때
        if search_df.empty:
            st.warning("구직 경로에 응답한 사람이 없습니다. (대부분 무응답)")
            st.stop()

        c_path1, c_path2 = st.columns([1, 1])

        # -----------------------
        # 1) 구직 경로 사용량 히스토그램
        # -----------------------
        with c_path1:
            st.markdown("**구직 경로별 활용 비중 (인기 순위)**")

            path_counts = search_df['search_method'].value_counts().reset_index()
            path_counts.columns = ['구직 경로', '인원수']

            fig_path = px.bar(
                path_counts, x='인원수', y='구직 경로', orientation='h',
                text='인원수', title="NEET 청년들이 가장 많이 사용한 구직 경로"
            )
            fig_path.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_path, use_container_width=True)

        # -----------------------
        # 2) 경로별 취업 성공률
        # -----------------------
        with c_path2:
            st.markdown("**경로별 취업 성공률 (%)**")

            # 최소 5명 이상 응답한 경로만 사용 (표본 너무 작으면 왜곡됨)
            method_counts = search_df['search_method'].value_counts()
            valid_methods = method_counts[method_counts >= 5].index
            valid_df = search_df[search_df['search_method'].isin(valid_methods)]

            if valid_df.empty:
                st.info("응답자가 너무 적어 의미 있는 통계가 없습니다.")
            else:
                path_succ = valid_df.groupby('search_method')['got_job_flag'].mean().reset_index()
                path_succ['성공률'] = path_succ['got_job_flag'] * 100
                path_succ = path_succ.sort_values(by='성공률', ascending=False)

                fig_succ_path = px.bar(
                    path_succ, x='성공률', y='search_method', orientation='h',
                    text_auto='.1f', color='성공률', color_continuous_scale='Greens',
                    title="실제 취업 성공률이 높은 구직 경로 (Top)"
                )
                fig_succ_path.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_succ_path, use_container_width=True)

# ==============================
# 📌 TAB 14 — 인구통계학적 특성
# ==============================
with tab14:
    c1, c2, c3 = st.columns(3)
    # 성별 분포
    with c1:
        st.markdown("**성별에 따른 취업 성공률**")
        fig_gender = px.histogram(df, x="gender_label", color="outcome", 
                                  barmode="group", text_auto=True,
                                  color_discrete_map={"취업 성공": "#2ecc71", "미취업": "#e74c3c"},
                                  labels={"gender_label": "성별", "outcome": "상태"})
        st.plotly_chart(fig_gender, use_container_width=True)

    # 나이 분포
    with c2:
        st.markdown("**나이 분포 (Boxplot)**")
        fig_age = px.box(df, x="outcome", y="age", color="outcome",
                         color_discrete_map={"취업 성공": "#2ecc71", "미취업": "#e74c3c"},
                         labels={"age": "나이 (2021년 기준)", "outcome": "상태"})
        st.plotly_chart(fig_age, use_container_width=True)

    with c3:
        # 3. 나이 그룹 생성 (데이터에 없는 경우 즉석에서 생성)
        if 'age_group' not in df.columns:
            df['age_group'] = pd.cut(df['age'], 
                                            bins=[18, 24, 29], 
                                            labels=['19-24세 (초반)', '25-29세 (후반)'])

        # 4. 데이터 집계 (나이대/성별별 취업 성공률)
        # got_job_flag가 1(성공), 0(실패)이므로 mean()이 성공률이 됨
        grouped_stats = df.groupby(['age_group', 'gender_label'], observed=False)['got_job_flag'].mean().reset_index()
        grouped_stats['success_rate'] = grouped_stats['got_job_flag'] * 100 # % 변환

            # 그룹 막대 그래프 (Grouped Bar Chart)
        fig_cross = px.bar(grouped_stats, 
                            x='age_group', 
                            y='success_rate', 
                            color='gender_label',
                            barmode='group', # 남/녀 막대를 옆으로 나란히
                            text_auto='.1f',
                            title="20대 초반 vs 후반 남녀 취업 성공률 비교",
                            labels={'success_rate': '취업 성공률(%)', 'age_group': '나이대', 'gender_label': '성별'},
                            color_discrete_map={'남성': '#3498db', '여성': '#e74c3c'}) # 파랑/빨강 구분
        st.plotly_chart(fig_cross, use_container_width=True)

# ==============================
# 📌 TAB 15 — 학력 및 지역
# ==============================
with tab15:
    c1, c2 = st.columns(2)
    # 학력별 분포
    with c1:
        st.markdown("**최종 학력별 비중**")
        fig_edu = px.histogram(df, x="edu_label", color="outcome", 
                               barmode="group",
                               color_discrete_map={"취업 성공": "#2ecc71", "미취업": "#e74c3c"},
                               labels={"edu_label": "최종 학력"})
        st.plotly_chart(fig_edu, use_container_width=True)
        
    # 지역별 분포
    with c2:
        st.markdown("**지역별 취업 성공 분포**")
        fig_region = px.histogram(df, y="region_label", color="outcome",
                                  barmode="stack", orientation='h',
                                  color_discrete_map={"취업 성공": "#2ecc71", "미취업": "#e74c3c"},
                                  labels={"region_label": "거주 지역"})
        # 지역명 가나다순 정렬 or 데이터 많은 순 정렬
        fig_region.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_region, use_container_width=True)

# ==============================
# 📌 TAB 16 — 건강상태
# ==============================
with tab16:
    st.markdown("**주관적 건강 상태와 취업의 관계**")
    
    # 비율 계산 후 그래프 생성
    health_counts = df.groupby(['health_label', 'outcome'], observed=False).size().reset_index(name='count')
    health_total = df.groupby('health_label', observed=False).size().reset_index(name='total')
    health_merged = health_counts.merge(health_total, on='health_label')
    health_merged['ratio'] = health_merged['count'] / health_merged['total'] * 100
    
    fig_health = px.bar(health_merged, x="health_label", y="ratio", color="outcome",
                        text_auto='.1f',
                        color_discrete_map={"취업 성공": "#2ecc71", "미취업": "#e74c3c"},
                        labels={"ratio": "비율(%)", "health_label": "건강 상태"})
    st.plotly_chart(fig_health, use_container_width=True)

# st.header("2. 그룹별 특성 비교 (Basic Analysis)")
# st.info("2021년(1차년도) 당시의 인구통계학적 특성에 따른 취업 성공률 차이를 분석합니다.")

# ==============================
# 📌 TAB 17 — 지도
# ==============================
with tab17:

    # -------------------------------------------------------------------------
    # 1. 상단 제목
    # -------------------------------------------------------------------------
    st.subheader("지역별 심층 특성 지도 (Interactive Map)")
    st.info("👇 지도 위의 원을 클릭하면 해당 지역의 상세 분석 리포트가 제공됩니다.")

    # -------------------------------------------------------------------------
    # 2. 집계할 함수 정의
    # -------------------------------------------------------------------------
    agg_funcs = {
        'sampid': 'count',
        'got_job_flag': 'mean',
        'self_efficacy': 'mean',
        'career_plan_score': 'mean',
    }

    # 활동경험 가중치용 더미변수 (is_intern, is_parttime, is_startup, is_other, is_none)
    df['is_intern'] = df['exp_type'].apply(lambda x: 1 if x == '인턴/현장실습' else 0)
    df['is_parttime'] = df['exp_type'].apply(lambda x: 1 if x == '아르바이트' else 0)
    df['is_startup'] = df['exp_type'].apply(lambda x: 1 if x == '창업 경험' else 0)
    df['is_other'] = df['exp_type'].apply(lambda x: 1 if x == '기타' else 0)
    df['is_none'] = df['exp_type'].apply(lambda x: 1 if x == '경험 없음' else 0)
    df['experience'] = df['exp_type'].apply(
    lambda x: 1 if x in ['인턴/현장실습', '아르바이트', '창업 경험'] else 0)

    # 지도용 집계 추가
    agg_funcs.update({
        'is_intern': 'mean',
        'is_parttime': 'mean',
        'is_startup': 'mean',
        'is_other': 'mean',
        'is_none': 'mean',
        'experience': 'mean'
    })

    map_deep_df = df.groupby('region_label', observed=False).agg(agg_funcs).reset_index()

    # 시각용 비율 컬럼
    map_deep_df['취업 성공률(%)'] = (map_deep_df['got_job_flag'] * 100).round(1)
    map_deep_df['자아효능감(점)'] = map_deep_df['self_efficacy'].round(2)
    map_deep_df['진로계획 명확성(점)'] = map_deep_df['career_plan_score'].round(2)
    map_deep_df['일 경험률(%)'] = (map_deep_df['experience'] * 100).round(1)

    # -------------------------------
    # 4. 지역 좌표 설정
    # -------------------------------
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

    # 지도용 데이터프레임
    plot_df = map_deep_df.dropna(subset=['lat', 'lon']).reset_index(drop=True)

    # -------------------------------
    # 5. 지도 색상 기준 선택 옵션 — 취업 성공률만 사용
    # -------------------------------
    metric_options = {
        '취업 성공률(%)': 'RdYlGn',
    }

    selected_metric = '취업 성공률(%)'   # 선택박스 없애고 바로 사용해도 됨

    # -------------------------------
    # 6. 지도 생성
    # -------------------------------
    if not plot_df.empty:
        fig_deep_map = px.scatter_mapbox(
            plot_df,
            lat="lat", lon="lon",
            size="sampid",
            color=selected_metric,
            color_continuous_scale=metric_options[selected_metric],
            size_max=45,
            zoom=6,
            center={"lat": 36.5, "lon": 127.8},
            mapbox_style="carto-positron",
            title="지역별 취업 성공률 지도"
        )
        fig_deep_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

        event = st.plotly_chart(
            fig_deep_map, use_container_width=True,
            on_select="rerun", selection_mode="points"
        )
    else:
        st.warning("지도 데이터가 없습니다.")
        event = None

    # -------------------------------------------------------------------------
    # 7. 지도 클릭 → 상세 리포트 생성
    # -------------------------------------------------------------------------
    selected_region = None

    if event and event['selection']['points']:
        idx = event['selection']['points'][0]['point_index']
        selected_region = plot_df.iloc[idx]['region_label']

    if selected_region:
        st.divider()
        st.subheader(f"🔍 [{selected_region}] 지역 상세 분석")

        region_data = map_deep_df[map_deep_df['region_label'] == selected_region].iloc[0]
        national_avg = map_deep_df.mean(numeric_only=True)

        # 🔹 핵심 지표 비교
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("대상 인원", f"{int(region_data['sampid'])}명")
        c2.metric("취업 성공률", f"{region_data['취업 성공률(%)']}%")
        c3.metric("자아효능감", f"{region_data['자아효능감(점)']}점")
        c4.metric("진로계획 명확성", f"{region_data['진로계획 명확성(점)']}점")
        c5.metric("일 경험률", f"{region_data['일 경험률(%)']}%")

        # -------------------------------------------------------------------------
        # 🔍 일 경험률 상세 보기 토글
        # -------------------------------------------------------------------------
        show_exp = st.toggle("🔍 일 경험률 상세 보기")

        # -------------------------------------------------------------------------
        # 8. 활동경험 분포 파이 차트 (토글 On일 때만 표시)
        # -------------------------------------------------------------------------
        if show_exp:
            st.markdown("### 🥧 활동경험 분포")

            region_subset = df[df['region_label'] == selected_region]

            exp_counts = region_subset['exp_type'].value_counts().reindex(
                ["인턴/현장실습", "아르바이트", "창업 경험", "기타", "경험 없음"],
                fill_value=0
            )

            fig_pie = px.pie(
                names=exp_counts.index,
                values=exp_counts.values,
                hole=0.4,
                title=f"{selected_region} 활동경험 비율"
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        # -------------------------------------------------------------------------
        # 9. 레이더 차트
        # -------------------------------------------------------------------------
        st.markdown("#### 🕸️ 지역 강점/약점 분석 (전국 평균=100 기준)")

        radar_metrics = {
            '취업 성공률':'got_job_flag',
            '자아효능감':'self_efficacy',
            '진로계획':'career_plan_score',
            '일 경험률': 'experience'
        }

        radar_data = []
        categories = []

        for label, col in radar_metrics.items():
            reg = region_data[col]
            nat = national_avg[col]
            score = (reg / nat * 100) if nat > 0 else 0
            radar_data.append(score)
            categories.append(label)

        radar_df = pd.DataFrame(dict(r=radar_data, theta=categories))

        fig_radar = px.line_polar(
            radar_df,
            r='r', theta='theta',
            line_close=True,
            title=f"{selected_region} 지역 특성 vs 전국 평균"
        )
        fig_radar.update_traces(fill='toself', line_color='#2980b9')
        st.plotly_chart(fig_radar, use_container_width=True)

        # -------------------------------------------------------------------------
        # 🔎 레이더 차트 자동 분석 텍스트
        # -------------------------------------------------------------------------
        max_idx = radar_data.index(max(radar_data))
        min_idx = radar_data.index(min(radar_data))
                
        strong_point = categories[max_idx]
        weak_point = categories[min_idx]
        st.success(f"💡 **{selected_region}**의 강점은 '**{strong_point}**'이며, 상대적으로 **'{weak_point}'** 수치가 낮습니다.")

# ==============================
# 📌 TAB 18 — 구직 중 가장 어려웠던 점(Top 5)
# ==============================
with tab18:
    st.markdown("### 😥 전체 청년 NEET: 구직 중 가장 어려웠던 점 (Top 5)")

    # 전체 데이터를 사용 (지역 조건 제거)
    all_subset = df.copy()

    # 항목별 빈도 계산 (해당없음 제거)
    diff_counts = all_subset['main_difficulty'].value_counts().drop("해당없음", errors='ignore')

    # 가장 많이 선택된 항목 상위 5개
    diff_top5 = diff_counts.head(5)

    # 데이터프레임 생성
    diff_df = pd.DataFrame({
        "항목": diff_top5.index,
        "빈도": diff_top5.values
    })

    # 전체 표본 수
    total_people = len(all_subset)

    # 비율 계산
    diff_df["비율(%)"] = (diff_df["빈도"] / total_people * 100).round(1)

    # Plotly Bar Chart
    fig_diff = px.bar(
        diff_df,
        x="항목",
        y="비율(%)",
        text="비율(%)",
        color="항목",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="전국 NEET: 구직 중 가장 어려웠던 점 (Top 5)"
    )

    # 스타일 업데이트
    fig_diff.update_traces(
        textposition='outside',
        marker_line_color="black",
        marker_line_width=1.5
    )

    fig_diff.update_layout(
        xaxis_title="",
        yaxis_title="비율 (%)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
        showlegend=False,
        height=420
    )

    st.plotly_chart(fig_diff, use_container_width=True)



