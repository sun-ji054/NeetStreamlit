import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(layout="wide", page_title="청년 NEET 노동시장 진입 분석")

# 제목
st.title("🚧 일하지 않는 청년들, 멈춤에서 길을 찾다")
st.subheader(": 청년패널조사(YP2021) 기반 NEET 청년의 노동시장 진입 분석")

# 데이터 로드 함수
@st.cache_data
def load_data():
    df = pd.read_csv("neet_dashboard_data.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("데이터 파일(neet_dashboard_data.csv)을 찾을 수 없습니다. 전처리 코드를 먼저 실행해주세요.")
    st.stop()

# --- 사이드바 필터 ---
st.sidebar.header("필터 설정")
gender_filter = st.sidebar.multiselect(
    "성별 선택",
    options=df['gender_label'].unique(),
    default=df['gender_label'].unique()
)

region_filter = st.sidebar.multiselect(
    "거주 지역 선택",
    options=df['region_label'].unique(),
    default=df['region_label'].unique()
)

# 데이터 필터링
filtered_df = df[
    (df['gender_label'].isin(gender_filter)) &
    (df['region_label'].isin(region_filter))
]

# --- Key Metrics ---
st.markdown("### 1. 현황 요약")
col1, col2, col3 = st.columns(3)

total_neet = len(filtered_df)
success_count = len(filtered_df[filtered_df['outcome'] == '취업 성공'])
success_rate = (success_count / total_neet * 100) if total_neet > 0 else 0

col1.metric("분석 대상 (2021년 NEET)", f"{total_neet:,} 명")
col2.metric("노동시장 진입 성공 (2~3년차)", f"{success_count:,} 명")
col3.metric("진입 성공률", f"{success_rate:.1f}%")

st.divider()

# --- 비교 분석 ---
st.markdown("### 2. 취업 성공 그룹 vs 미취업 그룹 특성 비교")
st.info("2021년(1차년도) 당시의 특성을 기준으로, 향후 취업 여부에 따른 차이를 분석합니다.")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["인구통계학적 특성", "학력 및 지역", "건강 상태"])

with tab1:
    c1, c2 = st.columns(2)
    
    # 성별 분포 비교
    with c1:
        st.markdown("**성별에 따른 취업 성공률**")
        fig_gender = px.histogram(filtered_df, x="gender_label", color="outcome", 
                                  barmode="group", text_auto=True,
                                  color_discrete_map={"취업 성공": "#2ecc71", "미취업": "#e74c3c"},
                                  labels={"gender_label": "성별", "outcome": "상태"})
        st.plotly_chart(fig_gender, use_container_width=True)

    # 나이 분포 비교
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
        # 학력 순서 정렬
        edu_order = ['고졸 미만', '고졸', '전문대졸', '대졸', '대학원졸']
        fig_edu = px.histogram(filtered_df, x="edu_label", color="outcome", 
                               barmode="group", category_orders={"edu_label": edu_order},
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
        fig_region.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_region, use_container_width=True)

with tab3:
    st.markdown("**주관적 건강 상태와 취업의 관계**")
    st.markdown("1차년도에 느낀 주관적 건강 상태가 향후 취업에 미치는 영향을 보여줍니다.")
    
    # 건강 상태 순서
    health_order = ['매우 나쁨', '나쁜 편', '보통', '좋은 편', '매우 좋음']
    
    # 비율 계산
    health_counts = filtered_df.groupby(['health_label', 'outcome']).size().reset_index(name='count')
    health_total = filtered_df.groupby('health_label').size().reset_index(name='total')
    health_merged = health_counts.merge(health_total, on='health_label')
    health_merged['ratio'] = health_merged['count'] / health_merged['total'] * 100
    
    fig_health = px.bar(health_merged, x="health_label", y="ratio", color="outcome",
                        category_orders={"health_label": health_order},
                        text_auto='.1f',
                        color_discrete_map={"취업 성공": "#2ecc71", "미취업": "#e74c3c"},
                        labels={"ratio": "비율(%)", "health_label": "건강 상태"})
    st.plotly_chart(fig_health, use_container_width=True)

# --- Raw Data 보기 ---
with st.expander("원본 데이터 샘플 보기"):
    st.dataframe(filtered_df.head(100))