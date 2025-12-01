import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

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
# 2. 사이드바 필터 & 헤더
# -----------------------------------------------------------------------------
st.title("🚧 일하지 않는 청년들, 멈춤에서 길을 찾다")
st.markdown("##### : 청년패널(YP2021) NEET 청년의 노동시장 진입 요인 분석")

st.sidebar.header("필터 설정")

# 성별 필터
if 'gender_label' in df.columns:
    gender_filter = st.sidebar.multiselect(
        "성별 선택",
        options=df['gender_label'].unique(),
        default=df['gender_label'].unique()
    )
else:
    gender_filter = []

# 지역 필터
if 'region_label' in df.columns:
    region_filter = st.sidebar.multiselect(
        "거주 지역 선택",
        options=sorted(df['region_label'].dropna().unique()),
        default=sorted(df['region_label'].dropna().unique())
    )
else:
    region_filter = []

# 필터링 적용
filtered_df = df[
    (df['gender_label'].isin(gender_filter)) &
    (df['region_label'].isin(region_filter))
]

# -----------------------------------------------------------------------------
# 3. Key Metrics (요약 지표)
# -----------------------------------------------------------------------------
st.markdown("### 1. 현황 요약")
col1, col2, col3 = st.columns(3)

total_neet = len(filtered_df)
success_count = len(filtered_df[filtered_df['outcome'] == '취업 성공'])
success_rate = (success_count / total_neet * 100) if total_neet > 0 else 0

col1.metric("분석 대상 (2021년 NEET)", f"{total_neet:,} 명")
col2.metric("노동시장 진입 성공 (2~3년차)", f"{success_count:,} 명")
col3.metric("진입 성공률", f"{success_rate:.1f}%")

st.divider()

# -----------------------------------------------------------------------------
# 4. Part 1: 기본 특성 분석 (주신 코드 반영)
# -----------------------------------------------------------------------------
st.header("2. 그룹별 특성 비교 (Basic Analysis)")
st.info("2021년(1차년도) 당시의 인구통계학적 특성에 따른 취업 성공률 차이를 분석합니다.")

tab1, tab2, tab3 = st.tabs(["📊 인구통계학적 특성", "🏫 학력 및 지역", "💪 건강 상태"])

with tab1:
    c1, c2 = st.columns(2)
    # 성별 분포
    with c1:
        st.markdown("**성별에 따른 취업 성공률**")
        fig_gender = px.histogram(filtered_df, x="gender_label", color="outcome", 
                                  barmode="group", text_auto=True,
                                  color_discrete_map={"취업 성공": "#2ecc71", "미취업": "#e74c3c"},
                                  labels={"gender_label": "성별", "outcome": "상태"})
        st.plotly_chart(fig_gender, use_container_width=True)

    # 나이 분포
    with c2:
        st.markdown("**나이 분포 (Boxplot)**")
        fig_age = px.box(filtered_df, x="outcome", y="age", color="outcome",
                         color_discrete_map={"취업 성공": "#2ecc71", "미취업": "#e74c3c"},
                         labels={"age": "나이 (2021년 기준)", "outcome": "상태"})
        st.plotly_chart(fig_age, use_container_width=True)

with tab2:
    c1, c2 = st.columns(2)
    # 학력별 분포
    with c1:
        st.markdown("**최종 학력별 비중**")
        fig_edu = px.histogram(filtered_df, x="edu_label", color="outcome", 
                               barmode="group",
                               color_discrete_map={"취업 성공": "#2ecc71", "미취업": "#e74c3c"},
                               labels={"edu_label": "최종 학력"})
        st.plotly_chart(fig_edu, use_container_width=True)
        
    # 지역별 분포
    with c2:
        st.markdown("**지역별 취업 성공 분포**")
        fig_region = px.histogram(filtered_df, y="region_label", color="outcome",
                                  barmode="stack", orientation='h',
                                  color_discrete_map={"취업 성공": "#2ecc71", "미취업": "#e74c3c"},
                                  labels={"region_label": "거주 지역"})
        # 지역명 가나다순 정렬 or 데이터 많은 순 정렬
        fig_region.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_region, use_container_width=True)

with tab3:
    st.markdown("**주관적 건강 상태와 취업의 관계**")
    
    # 비율 계산 후 그래프 생성
    health_counts = filtered_df.groupby(['health_label', 'outcome'], observed=False).size().reset_index(name='count')
    health_total = filtered_df.groupby('health_label', observed=False).size().reset_index(name='total')
    health_merged = health_counts.merge(health_total, on='health_label')
    health_merged['ratio'] = health_merged['count'] / health_merged['total'] * 100
    
    fig_health = px.bar(health_merged, x="health_label", y="ratio", color="outcome",
                        text_auto='.1f',
                        color_discrete_map={"취업 성공": "#2ecc71", "미취업": "#e74c3c"},
                        labels={"ratio": "비율(%)", "health_label": "건강 상태"})
    st.plotly_chart(fig_health, use_container_width=True)

st.divider()

# -----------------------------------------------------------------------------
# 5. Part 2: 진로 및 활동 경험 분석 (심화 분석)
# -----------------------------------------------------------------------------
st.header("3. 진로 발달 및 경험 요인 (Deep Dive)")
st.markdown("단순 스펙 외에 **인턴/알바 경험, 진로지도, 진로계획 명확성**이 실제 취업에 어떤 영향을 미치는지 봅니다.")

tab4, tab5, tab6 = st.tabs(["🛠️ 재학 중 활동 경험", "🧭 진로지도 및 계획", "🔗 요인 상관관계"])

with tab4:
    st.subheader("인턴 및 아르바이트 경험의 영향")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**경험 유형별 분포**")
        exp_counts = filtered_df['exp_type'].value_counts().reset_index()
        exp_counts.columns = ['유형', '인원수']
        fig_pie = px.pie(exp_counts, values='인원수', names='유형', hole=0.4, title="NEET 청년들의 재학 중 경험")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.markdown("**경험 유무에 따른 취업 성공률 (%)**")
        # 성공률 계산
        exp_succ = filtered_df.groupby('exp_type')['got_job_flag'].mean().reset_index()
        exp_succ['성공률'] = exp_succ['got_job_flag'] * 100
        
        fig_exp_bar = px.bar(exp_succ, x='exp_type', y='성공률', 
                             color='exp_type', text_auto='.1f',
                             labels={'성공률': '취업 성공률 (%)', 'exp_type': '경험 유형'})
        fig_exp_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_exp_bar, use_container_width=True)
    
    st.info("📌 **참고**: '경험 없음' 그룹 대비 '인턴/현장실습' 경험자의 취업 성공률이 유의미하게 높은지 확인해보세요.")

with tab5:
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("**진로지도(상담) 경험 유무**")
        # Stacked Bar
        fig_guide = px.histogram(filtered_df, x="career_guidance", color="outcome", 
                                 barmode="group", text_auto=True,
                                 color_discrete_map={"취업 성공": "#2ecc71", "미취업": "#e74c3c"},
                                 labels={"career_guidance": "진로지도 경험"})
        st.plotly_chart(fig_guide, use_container_width=True)
        
    with c2:
        st.markdown("**진로계획 명확성 점수 (5점 만점)**")
        # Boxplot
        fig_plan = px.box(filtered_df, x="outcome", y="career_plan_score", color="outcome",
                          color_discrete_map={"취업 성공": "#2ecc71", "미취업": "#e74c3c"},
                          labels={"career_plan_score": "진로계획 명확성(점)"})
        st.plotly_chart(fig_plan, use_container_width=True)

with tab6:
    st.markdown("**취업 성공(Got Job)과의 상관관계 분석**")
    st.caption("빨간색(양의 상관관계)이 진할수록 취업 성공과 관련이 높습니다.")
    
    # 상관분석용 데이터 준비
    if len(filtered_df) > 10:
        corr_df = filtered_df[['got_job_flag', 'age', 'career_plan_score']].copy()
        corr_df['is_male'] = filtered_df['gender'].apply(lambda x: 1 if x==1 else 0)
        corr_df['has_intern'] = filtered_df['exp_type'].apply(lambda x: 1 if '인턴' in x else 0)
        corr_df['has_guidance'] = filtered_df['career_guidance'].apply(lambda x: 1 if x=='있음' else 0)
        corr_df['is_univ_grad'] = filtered_df['edu_label'].apply(lambda x: 1 if x in ['대졸', '대학원졸'] else 0)
        
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
    st.dataframe(filtered_df.head(100))