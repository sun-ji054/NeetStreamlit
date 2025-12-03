import pandas as pd
import numpy as np

print("데이터 전처리 시작... (이 작업은 몇 초 정도 걸릴 수 있습니다)")

# 1. 원본 데이터 로드
try:
    w1 = pd.read_csv("YP2021_w01.csv")
    w2 = pd.read_csv("YP2021_w02.csv")
    w3 = pd.read_csv("YP2021_w03.csv")
except FileNotFoundError:
    print("오류: 원본 CSV 파일이 폴더에 없습니다.")
    exit()


# 2. 필요한 변수 선택
target_vars = [
    'sampid', 'gender', 'birthy', 'w01ecoact', 'w01student', 'w01edu', 'w01region',
    'y01e606',
    'y01a601', 'y01a616_1',
    'y01e401',
    'y01e501', 'y01e510', 'y01e511', 'y01e519',
    'w01edu_f', 'w01edu_m',
    'y01a439',
    'y01e513', 'y01e514', 'y01e515',
    'y01c768a',
    'y01a617_1', 'y01a630_1',
    'y01c116', 'y01c136',
    'y01c603d', 'y01c604',
    'y01c771a',
    'y01f508'
]

valid_vars = [c for c in target_vars if c in w1.columns]
w1_sel = w1[valid_vars].copy()

w2_sel = w2[['sampid', 'w02ecoact', 'w02student',
             'y02e501', 'y02e510', 'y02e511', 'y02e519']]

w3_sel = w3[['sampid', 'w03ecoact', 'w03student',
             'y03e501', 'y03e510', 'y03e511', 'y03e519']]


# 3. 병합
neet_df = w1_sel.merge(w2_sel, on='sampid', how='left').merge(w3_sel, on='sampid', how='left')


# 4. NEET 여부
neet_df['neet_w1'] = neet_df.apply(lambda x: (x['w01ecoact'] in [2, 3]) and (x['w01student'] == 2), axis=1)
neet_df = neet_df[neet_df['neet_w1'] == True].copy()


# 5. 노동시장 진입 여부
def check_employment(row):
    return "취업 성공" if (row['w02ecoact'] == 1 or row['w03ecoact'] == 1) else "미취업"

neet_df['outcome'] = neet_df.apply(check_employment, axis=1)
neet_df['got_job_flag'] = neet_df['outcome'].map({'취업 성공': 1, '미취업': 0})


# 6. 기본 변수 처리
neet_df['gender_label'] = neet_df['gender'].map({1: '남성', 2: '여성'})
neet_df['age'] = 2021 - neet_df['birthy']
edu_map = {1: '고졸 미만', 2: '고졸', 3: '전문대졸', 4: '대졸', 5: '대학원졸'}
neet_df['edu_label'] = neet_df['w01edu'].map(edu_map)

health_map = {1: '매우 나쁨', 2: '나쁜 편', 3: '보통', 4: '좋은 편', 5: '매우 좋음'}
neet_df['health_label'] = neet_df['y01e606'].map(health_map)

# 8. 자아효능감
eff_cols = ['y01e513', 'y01e514', 'y01e515']
eff_cols = [c for c in eff_cols if c in neet_df.columns]
neet_df['self_efficacy'] = neet_df[eff_cols].mean(axis=1)


# 9. 학자금 대출
neet_df['student_loan'] = neet_df['y01a439'].map({1: '있음', 2: '없음'})


# 10. 진로 계획 점수
neet_df['career_plan_score'] = neet_df['y01e501']
neet_df['trouble_deciding_career'] = neet_df['y01e510']
neet_df['uncertain_decision_pending'] = neet_df['y01e511']
neet_df['aptitude_not_known'] = neet_df['y01e519']

neet_df['career_plan_score_02'] = neet_df['y02e501']
neet_df['trouble_deciding_career_02'] = neet_df['y02e510']
neet_df['uncertain_decision_pending_02'] = neet_df['y02e511']
neet_df['aptitude_not_known_02'] = neet_df['y02e519']

neet_df['career_plan_score_03'] = neet_df['y03e501']
neet_df['trouble_deciding_career_03'] = neet_df['y03e510']
neet_df['uncertain_decision_pending_03'] = neet_df['y03e511']
neet_df['aptitude_not_known_03'] = neet_df['y03e519']

neet_df['avg_career_plan_score'] = neet_df[
    ['career_plan_score', 'career_plan_score_02', 'career_plan_score_03']
].mean(axis=1)

neet_df['avg_trouble_deciding_career'] = neet_df[
    ['trouble_deciding_career', 'trouble_deciding_career_02', 'trouble_deciding_career_03']
].mean(axis=1)

neet_df['avg_uncertain_decision_pending'] = neet_df[
    ['uncertain_decision_pending', 'uncertain_decision_pending_02', 'uncertain_decision_pending_03']
].mean(axis=1)

neet_df['avg_aptitude_not_known'] = neet_df[
    ['aptitude_not_known', 'aptitude_not_known_02', 'aptitude_not_known_03']
].mean(axis=1)



# 11. 활동 경험 exp_type
def clean_exp(row):
    if row['y01a601'] != 1: return "경험 없음"
    t = row['y01a616_1']
    if t in [1, 2]: return "인턴/현장실습"
    elif t == 3: return "아르바이트"
    elif t == 4: return "창업 경험"
    return "기타"

neet_df['exp_type'] = neet_df.apply(clean_exp, axis=1)

# ⭐ 지도 표시용 더미 변수 생성 (비율 계산용)
neet_df['is_intern'] = neet_df['exp_type'].apply(lambda x: 1 if x == '인턴/현장실습' else 0)
neet_df['is_parttime'] = neet_df['exp_type'].apply(lambda x: 1 if x == '아르바이트' else 0)
neet_df['is_startup'] = neet_df['exp_type'].apply(lambda x: 1 if x == '창업 경험' else 0)


# 12. 진로지도
neet_df['career_guidance'] = neet_df['y01e401'].map({1: '있음', 2: '없음'})


# 13. 지역
region_map = {
    1:'서울', 2:'부산', 3:'대구', 4:'인천', 5:'광주', 6:'대전', 7:'울산', 
    8:'경기', 9:'강원', 10:'충북', 11:'충남', 12:'전북', 13:'전남', 
    14:'경북', 15:'경남', 16:'제주', 17:'세종'
}
neet_df['region_label'] = neet_df['w01region'].map(region_map)


# 14. 구직정보 취득 경로
search_map = {
    1:'학교 선생님(교수)', 2:'학교 취업정보센터', 3:'언론매체', 4:'부모/친척',
    5:'지인(친구/선후배)', 6:'공공 취업알선기관', 7:'민간 취업알선기관',
    8:'공공 취업포털(워크넷)', 9:'민간 취업포털(사람인 등)', 10:'커뮤니티',
    11:'기업 홈페이지/SNS', 12:'채용설명회', 13:'학원', 14:'현장실습/인턴십',
    15:'헤드헌터', 97:'기타'
}
neet_df['search_method'] = neet_df['y01c768a'].map(search_map).fillna("응답 없음")


# 15. 기타 구직 관련 변수
neet_df['work_exp_type'] = neet_df['y01a616_1'].map({
    1:'체험형 인턴', 2:'채용형 인턴', 3:'아르바이트',
    4:'창업', 5:'프리랜서', 97:'기타'
}).fillna("경험없음")

neet_df['job_type_code'] = neet_df['y01a617_1'].fillna(0)

neet_df['program_help_score'] = pd.to_numeric(neet_df['y01a630_1'], errors='coerce')

neet_df['fail_exp_flag'] = neet_df['y01c116'].apply(lambda x: 1 if x == 1 else 0)
neet_df['difficult_flag'] = neet_df['y01c136'].apply(lambda x: 1 if x == 1 else 0)

neet_df['search_duration_month'] = pd.to_numeric(neet_df['y01c603d'], errors='coerce').fillna(0)
neet_df['search_count'] = pd.to_numeric(neet_df['y01c604'], errors='coerce').fillna(0)

neet_df['main_difficulty'] = neet_df['y01c771a'].map({
    1:'일자리 부족', 2:'정보 부족', 3:'적성 불일치', 4:'자격요건 미달',
    5:'임금/조건 불일치', 6:'면접 기술 부족', 7:'자신감 결여', 97:'기타'
}).fillna('해당없음')

# y01f508: 금융자산 총액 (단위: 만원). 결측치나 응답거절(999999 등) 처리 필요
# 여기서는 NaN을 0으로 처리 (자산 없음)하고 극단적 이상치는 그대로 둠 (분석 시 주의)
if 'y01f508' in neet_df.columns:
    # 1. 숫자형으로 변환 (문자열 등 오류 방지)
    neet_df['total_asset_amount'] = pd.to_numeric(neet_df['y01f508'], errors='coerce')
    
    # 2. 무응답/거절 코드 제거 (NaN 처리)
    # 999999, 9090908, 9090909 등 설문조사 특유의 코드를 제거
    error_codes = [999999, 9090908, 9090909]
    neet_df.loc[neet_df['total_asset_amount'].isin(error_codes), 'total_asset_amount'] = np.nan
    
    # 3. '자산 없음(y01f507=2)' 응답자는 확실하게 0원으로 처리
    if 'y01f507' in neet_df.columns:
        neet_df.loc[neet_df['y01f507'] == 2, 'total_asset_amount'] = 0
    
    # 4. 결측치(NaN)는 0으로 채울지, 제외할지 결정
    # 분석의 정확성을 위해 일단 NaN으로 둡니다. (0으로 채우면 평균이 왜곡될 수 있음)
    # 단, Streamlit에서 fillna(0)이 필요하면 그때 처리합니다.
    # 여기서는 "자산이 있다고 했는데 액수를 모르는 경우"는 제외하는 것이 깔끔합니다.
    
else:
    neet_df['total_asset_amount'] = np.nan # 컬럼이 아예 없으면 NaN

# 16. CSV 저장
neet_df.to_csv("neet_dashboard_data.csv", index=False, encoding="utf-8-sig")
print("전처리 완료! neet_dashboard_data.csv 생성됨.")
