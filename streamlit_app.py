import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from scipy.stats import ttest_ind


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

# -----------------------------------------------------------------------------
# 1. 사이트 타이틀
# -----------------------------------------------------------------------------
st.title("🚧 일하지 않는 청년들, 멈춤에서 길을 찾다")
st.markdown("##### : 청년패널(YP2021) NEET 청년의 노동시장 진입 요인 분석")

# -----------------------------------------------------------------------------
# 2. 사이드 바
# -----------------------------------------------------------------------------
st.sidebar.success("Select a demo above.")

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
st.info("""니트족과 취업군의 진로발달 특성을 비교분석합니다.\n
        e501(진로발달_나는 내 또래에 비해서 뚜렷한 진로 계획을 가지고 있다)\n
        e510(나는 직업들 중에서 하나를 결정하느라고 애를 먹고 있다)\n
        e511(진로선택에 관한 것이 너무 불확실해서 결정하는 것을 보류하고 싶다)""")

tab11, tab12 = st.tabs(["진로발달", "진로발달 상세"])

# ==============================
# 📌 TAB 11 — 레이더 차트
# ==============================
with tab11:

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
        title="3개년 평균 진로발달 요인 비교"
    )

    st.plotly_chart(fig_radar_psych, use_container_width=True)

# ==============================
# 📌 TAB 12 — 상세 박스플롯 + T-test
# ==============================
with tab12:

    common_box_opts = {
        "x": "outcome",
        "color": "outcome",
        "category_orders": {"outcome": ["취업 성공", "미취업"]},
        "color_discrete_map": {"취업 성공": "#2ecc71", "미취업": "#e74c3c"}
    }

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


# -----------------------------------------------------------------------------
# 4. Part 1: 기본 특성 분석 (주신 코드 반영)
# -----------------------------------------------------------------------------
st.header("2. 그룹별 특성 비교 (Basic Analysis)")
st.info("2021년(1차년도) 당시의 인구통계학적 특성에 따른 취업 성공률 차이를 분석합니다.")

tab1, tab2, tab3, tab10 = st.tabs(["📊 인구통계학적 특성", "🏫 학력 및 지역", "💪 건강 상태", '지도'])

with tab1:
    c1, c2 = st.columns(2)
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

    # --- [추가된 부분] 성별 X 나이 교차 분석 ---
    st.divider() # 구분선 추가
    st.subheader("📊 심화: 나이대와 성별에 따른 취업률 차이")
    
    # 3. 나이 그룹 생성 (데이터에 없는 경우 즉석에서 생성)
    if 'age_group' not in df.columns:
        df['age_group'] = pd.cut(df['age'], 
                                          bins=[18, 24, 29], 
                                          labels=['19-24세 (초반)', '25-29세 (후반)'])

    # 4. 데이터 집계 (나이대/성별별 취업 성공률)
    # got_job_flag가 1(성공), 0(실패)이므로 mean()이 성공률이 됨
    grouped_stats = df.groupby(['age_group', 'gender_label'], observed=False)['got_job_flag'].mean().reset_index()
    grouped_stats['success_rate'] = grouped_stats['got_job_flag'] * 100 # % 변환

    col_new1, col_new2 = st.columns([2, 1])

    with col_new1:
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

    with col_new2:
        st.markdown("**💡 상세 수치표**")
        st.caption("각 나이대에서 남성과 여성의 취업률(%)을 비교합니다.")
        
        # 보기 좋게 피벗 테이블로 변환
        pivot_table = grouped_stats.pivot(index='age_group', columns='gender_label', values='success_rate')
        # 색상 입혀서 표 출력
        st.dataframe(pivot_table.style.format("{:.1f}%").background_gradient(cmap="Blues", axis=None))

with tab2:
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

with tab3:
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

with tab10:
    # -----------------------------------------------------------------------------
# [Interactive] 지역별 심층 특성 지도 + 클릭 상세 리포트 (오류 수정됨)
# -----------------------------------------------------------------------------
    st.header("4. 지역별 심층 특성 지도 (Interactive Map)")
st.info("👇 **지도 위의 원을 클릭**해보세요! 하단에 해당 지역의 상세 분석 리포트가 나타납니다.")

# 1. 데이터 집계
agg_funcs = {
    'self_efficacy': 'mean',        # 자아효능감
    'career_plan_score': 'mean',    # 진로계획 명확성
    'got_job_flag': 'mean',         # 취업 성공률
    'sampid': 'count'               # 표본 수
}

# 부모님 대졸 비율 & 진로지도 경험률 추가
if 'father_edu' in df.columns:
    df['father_high_edu'] = df['father_edu'].apply(lambda x: 1 if x == '대졸 이상' else 0)
    agg_funcs['father_high_edu'] = 'mean'
if 'career_guidance' in df.columns:
    df['has_guidance'] = df['career_guidance'].apply(lambda x: 1 if x == '있음' else 0)
    agg_funcs['has_guidance'] = 'mean'
if 'y01a616_1' in df.columns: 
    df['has_intern'] = df['y01a616_1'].apply(lambda x: 1 if x in [1, 2] else 0)
    agg_funcs['has_intern'] = 'mean'

# 집계 실행
map_deep_df = df.groupby('region_label', observed=False).agg(agg_funcs).reset_index()

# 표시용 데이터 가공 (점수 및 % 변환)
map_deep_df['취업 성공률(%)'] = (map_deep_df['got_job_flag'] * 100).round(1)
map_deep_df['자아효능감(점)'] = map_deep_df['self_efficacy'].round(2)
map_deep_df['진로계획 명확성(점)'] = map_deep_df['career_plan_score'].round(2)

if 'father_high_edu' in map_deep_df.columns:
    map_deep_df['부모 대졸비율(%)'] = (map_deep_df['father_high_edu'] * 100).round(1)
if 'has_guidance' in map_deep_df.columns:
    map_deep_df['진로지도 경험률(%)'] = (map_deep_df['has_guidance'] * 100).round(1)
if 'has_intern' in map_deep_df.columns:
    map_deep_df['인턴 경험률(%)'] = (map_deep_df['has_intern'] * 100).round(1)

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

# 2. 지도 그리기 (Interactive)
metric_options = {
    '취업 성공률(%)': 'RdYlGn',     
    '자아효능감(점)': 'Blues',      
    '진로계획 명확성(점)': 'Purples', 
    '부모 대졸비율(%)': 'Oranges',  
    '진로지도 경험률(%)': 'Teal'    
}
valid_metrics = [m for m in metric_options.keys() if m in map_deep_df.columns]

col_sel, _ = st.columns([1, 2])
with col_sel:
    selected_metric = st.selectbox("🎨 지도 색상 기준 (지표 선택)", valid_metrics)

# [수정 포인트 1] 지도용 데이터프레임을 따로 정의 (인덱스 참조를 위해)
plot_df = map_deep_df.dropna(subset=['lat', 'lon']).reset_index(drop=True)

if not plot_df.empty:
    fig_deep_map = px.scatter_mapbox(
        plot_df,
        lat="lat", lon="lon",
        size="sampid",                  
        color=selected_metric,          
        color_continuous_scale=metric_options[selected_metric],
        size_max=40, zoom=5.5,
        center={"lat": 36.5, "lon": 127.8},
        mapbox_style="carto-positron",
        title=f"지역별 '{selected_metric}' 분포 (클릭하여 상세 보기)",
        hover_name="region_label",
        hover_data={'lat': False, 'lon': False, 'sampid': True}
    )
    fig_deep_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

    # 클릭 이벤트 활성화
    event = st.plotly_chart(fig_deep_map, use_container_width=True, on_select="rerun", selection_mode="points")
else:
    st.warning("지도 데이터가 없습니다.")
    event = None

# 3. 클릭 시 상세 리포트
selected_region = None

# [수정 포인트 2] point_index를 사용하여 안전하게 데이터 조회
if event and event['selection']['points']:
    point_idx = event['selection']['points'][0]['point_index']
    # plot_df에서 해당 인덱스의 지역명을 가져옴
    selected_region = plot_df.iloc[point_idx]['region_label']

if selected_region:
    st.divider()
    st.subheader(f"🔍 [{selected_region}] 상세 분석 리포트")
    
    # 해당 지역 데이터 추출
    region_data = map_deep_df[map_deep_df['region_label'] == selected_region].iloc[0]
    national_avg = map_deep_df.mean(numeric_only=True)
    
    # (1) 핵심 지표 비교
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("대상 인원", f"{int(region_data['sampid']):,}명")
    
    val_job = region_data['취업 성공률(%)']
    avg_job = national_avg['취업 성공률(%)']
    c2.metric("취업 성공률", f"{val_job}%", f"{val_job - avg_job:.1f}%p")
    
    val_eff = region_data['자아효능감(점)']
    avg_eff = national_avg['자아효능감(점)']
    c3.metric("자아효능감", f"{val_eff}점", f"{val_eff - avg_eff:.2f}점")
    
    val_plan = region_data['진로계획 명확성(점)']
    avg_plan = national_avg['진로계획 명확성(점)']
    c4.metric("진로계획 명확성", f"{val_plan}점", f"{val_plan - avg_plan:.2f}점")

    # (2) 레이더 차트
    st.markdown("##### 🕸️ 영역별 강점/약점 분석 (전국 평균=100 기준)")
    
    radar_metrics = {
        '취업 성공률': 'got_job_flag',
        '자아효능감': 'self_efficacy',
        '진로계획': 'career_plan_score',
        '부모 학력(대졸↑)': 'father_high_edu',
        '인턴 경험률': 'has_intern'
    }
    
    radar_data = []
    categories = []
    
    for label, col in radar_metrics.items():
        if col in map_deep_df.columns:
            reg_val = map_deep_df.loc[map_deep_df['region_label'] == selected_region, col].values[0]
            nat_val = map_deep_df[col].mean()
            ratio = (reg_val / nat_val) * 100 if nat_val > 0 else 0
            radar_data.append(ratio)
            categories.append(label)
    
    if radar_data:
        radar_df = pd.DataFrame(dict(r=radar_data, theta=categories))
        
        fig_radar = px.line_polar(radar_df, r='r', theta='theta', line_close=True,
                                  title=f"{selected_region} vs 전국 평균(100)")
        fig_radar.update_traces(fill='toself', line_color='#3498db')
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max(max(radar_data), 120)])))
        st.plotly_chart(fig_radar, use_container_width=True)
        
        max_idx = radar_data.index(max(radar_data))
        min_idx = radar_data.index(min(radar_data))
        
        strong_point = categories[max_idx]
        weak_point = categories[min_idx]
        st.success(f"💡 **{selected_region}**의 강점은 **'{strong_point}'**이며, 상대적으로 **'{weak_point}'** 수치가 낮습니다.")

else:
    st.info("👆 지도에서 지역(원)을 클릭하면 상세 비교 분석 결과가 여기에 표시됩니다.")
# -----------------------------------------------------------------------------
# 5. Part 2: 진로 및 활동 경험 분석 (심화 분석)
# -----------------------------------------------------------------------------
st.header("3. 진로 발달 및 경험 요인 (Deep Dive)")
st.markdown("단순 스펙 외에 **인턴/알바 경험, 진로지도, 진로계획 명확성**이 실제 취업에 어떤 영향을 미치는지 봅니다.")

tab4, tab5, tab6, tab7 = st.tabs(["🛠️ 재학 중 활동 경험", "🔎 구직 노력(경로)", "🧭 진로지도 및 계획", "🔗 요인 상관관계"])

with tab4:
    st.subheader("인턴 및 아르바이트 경험의 영향")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**경험 유형별 분포**")
        exp_counts = df['exp_type'].value_counts().reset_index()
        exp_counts.columns = ['유형', '인원수']
        fig_pie = px.pie(exp_counts, values='인원수', names='유형', hole=0.4, title="NEET 청년들의 재학 중 경험")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.markdown("**경험 유무에 따른 취업 성공률 (%)**")
        # 성공률 계산
        exp_succ = df.groupby('exp_type')['got_job_flag'].mean().reset_index()
        exp_succ['성공률'] = exp_succ['got_job_flag'] * 100
        
        fig_exp_bar = px.bar(exp_succ, x='exp_type', y='성공률', 
                             color='exp_type', text_auto='.1f',
                             labels={'성공률': '취업 성공률 (%)', 'exp_type': '경험 유형'})
        fig_exp_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_exp_bar, use_container_width=True)
    
    st.info("📌 **참고**: '경험 없음' 그룹 대비 '인턴/현장실습' 경험자의 취업 성공률이 유의미하게 높은지 확인해보세요.")

with tab5:
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

        # -----------------------
        # 3) 상세 교차표
        # -----------------------
        st.markdown("---")
        st.markdown("### 📋 경로별 상세 데이터 표")

        cross_tab = pd.crosstab(search_df['search_method'], search_df['outcome'])
        cross_tab['합계'] = cross_tab.sum(axis=1)
        cross_tab['취업 성공률(%)'] = (cross_tab['취업 성공'] / cross_tab['합계'] * 100).round(1)

        cross_tab_sorted = cross_tab.sort_values(by='취업 성공률(%)', ascending=False)

        st.dataframe(
            cross_tab_sorted.style.background_gradient(cmap="Greens", subset=['취업 성공률(%)'])
        )
        st.caption("※ ‘응답 없음’은 제외했습니다. 표본 수가 너무 적은 경로는 왜곡될 수 있습니다.")

    else:
        st.warning("구직 경로 데이터가 없습니다. make_data.py를 다시 실행해주세요.")

with tab6:
    c1, c_g2 = st.columns(2)
    
    with c1:
        fig_guide = px.histogram(
            df, 
            x="outcome",            # X축을 결과(취업 성공/미취업)로 변경
            color="career_guidance", # 색상을 원인(경험 있음/없음)으로 변경
            barmode="group", 
            text_auto=True,
            category_orders={
                "outcome": ["취업 성공", "미취업"],    # X축 순서 고정
                "career_guidance": ["있음", "없음"]    # 범례 순서 고정
            },
            color_discrete_map={
                "있음": "#2ecc71", # 경험 있음: 초록색
                "없음": "#95a5a6"  # 경험 없음: 회색 (중립적 색상 사용)
            },
            labels={
                "outcome": "취업 여부",
                "career_guidance": "진로지도(상담) 경험",
                "count": "인원 수"
            },
            title="취업 성공/실패 그룹 내 진로지도 경험 분포"
        )
        
        # 텍스트 위치 및 포맷 조정
        fig_guide.update_traces(textposition='outside')
        st.plotly_chart(fig_guide, use_container_width=True)
        
    with c_g2:
        st.markdown("**진로 결정 어려움 요인 분석 (3개년 평균 Radar Chart)**")

    radar_cols = [
        'avg_career_plan_score',
        'avg_trouble_deciding_career',
        'avg_uncertain_decision_pending',
        'avg_aptitude_not_known'
    ]

    categories = ['진로 계획 명확성','진로결정 어려움', '진로 불확실성', '적성을 모름']

    # 그룹별 평균 계산
    avg_diff = df.groupby('outcome')[radar_cols].mean().reset_index()

    fig_radar_psych = go.Figure()

    # 취업 성공
    if '취업 성공' in avg_diff['outcome'].values:
        success_vals = avg_diff[avg_diff['outcome'] == '취업 성공'][radar_cols].values[0].tolist()
        fig_radar_psych.add_trace(go.Scatterpolar(
            r=success_vals + [success_vals[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='취업 성공',
            line_color='#2ecc71'
        ))

    # 미취업
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
        title="3개년 평균 진로 어려움 요인 비교 (높을수록 어려움 ↑)"
    )

    st.plotly_chart(fig_radar_psych, use_container_width=True)
    # 박스플롯 상세
    st.markdown("#### 📦 상세 분포 확인")
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    common_box_opts = {
        "x": "outcome", "color": "outcome",
        "category_orders": {"outcome": ["취업 성공", "미취업"]},
        "color_discrete_map": {"취업 성공": "#2ecc71", "미취업": "#e74c3c"}
    }
    
    st.markdown("#### 📦 상세 분포 확인 (3개년 평균)")

b_col1, b_col2, b_col3 = st.columns(3)

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

with b_col2:
    st.markdown("**② 진로결정 어려움 평균**")
    fig_b2 = px.box(df, y="avg_trouble_deciding_career", **common_box_opts)
    fig_b2.update_layout(showlegend=False)
    st.plotly_chart(fig_b2, use_container_width=True)

    # T-test
    g1 = df[df['outcome'] == '취업 성공']['avg_trouble_deciding_career'].dropna()
    g2 = df[df['outcome'] == '미취업']['avg_trouble_deciding_career'].dropna()
    t_stat, p_val = ttest_ind(g1, g2, equal_var=False)
    st.markdown(f"📌 **t-test p-value:** `{p_val:.4f}`")

with b_col3:
    st.markdown("**③ 결정 보류/불확실 평균**")
    fig_b3 = px.box(df, y="avg_uncertain_decision_pending", **common_box_opts)
    fig_b3.update_layout(showlegend=False)
    st.plotly_chart(fig_b3, use_container_width=True)

    # T-test
    g1 = df[df['outcome'] == '취업 성공']['avg_uncertain_decision_pending'].dropna()
    g2 = df[df['outcome'] == '미취업']['avg_uncertain_decision_pending'].dropna()
    t_stat, p_val = ttest_ind(g1, g2, equal_var=False)
    st.markdown(f"📌 **t-test p-value:** `{p_val:.4f}`")


with tab7:
    st.markdown("**취업 성공(Got Job)과의 상관관계 분석**")
    st.caption("빨간색(양의 상관관계)이 진할수록 취업 성공과 관련이 높습니다.")
    
    # 상관분석용 데이터 준비
    if len(df) > 10:
        corr_df = df[['got_job_flag', 'age', 'career_plan_score']].copy()
        corr_df['is_male'] = df['gender'].apply(lambda x: 1 if x==1 else 0)
        corr_df['has_intern'] = df['exp_type'].apply(lambda x: 1 if '인턴' in x else 0)
        corr_df['has_guidance'] = df['career_guidance'].apply(lambda x: 1 if x=='있음' else 0)
        corr_df['is_univ_grad'] = df['edu_label'].apply(lambda x: 1 if x in ['대졸', '대학원졸'] else 0)
        
        corr_matrix = corr_df.corr()
        
        fig_corr, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='RdBu_r', center=0, ax=ax)
        st.pyplot(fig_corr)
    else:
        st.warning("데이터가 너무 적어 상관분석을 수행할 수 없습니다.")

# -----------------------------------------------------------------------------
# 6. Raw Data 보기
# -----------------------------------------------------------------------------
st.divider()
with st.expander("원본 데이터 샘플 보기"):
    st.dataframe(df.head(100))
