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
    'y01e606',  # 건강상태
    'y01a601', 'y01a616_1',  # 활동경험
    'y01e401',               # 진로지도
    'y01e501',               # 진로계획 점수
    'w01edu_f', 'w01edu_m',  # 부모 학력
    'y01a439',               # 학자금 대출
    'y01e513', 'y01e514', 'y01e515',  # 자아효능감
    'y01c768a'               # 구직 경로 (1순위)
]

valid_vars = [c for c in target_vars if c in w1.columns]
w1_sel = w1[valid_vars].copy()
w2_sel = w2[['sampid', 'w02ecoact', 'w02student']]
w3_sel = w3[['sampid', 'w03ecoact', 'w03student']]

# 3. 데이터 병합
df = w1_sel.merge(w2_sel, on='sampid', how='left').merge(w3_sel, on='sampid', how='left')

# 4. 1차년도 NEET 여부 판단
df['neet_w1'] = df.apply(lambda x: (x['w01ecoact'] in [2, 3]) and (x['w01student'] == 2), axis=1)
neet_df = df[df['neet_w1'] == True].copy()

# 5. 노동시장 진입 여부
def check_employment(row):
    return "취업 성공" if (row['w02ecoact'] == 1 or row['w03ecoact'] == 1) else "미취업"

neet_df['outcome'] = neet_df.apply(check_employment, axis=1)
neet_df['got_job_flag'] = neet_df['outcome'].map({'취업 성공': 1, '미취업': 0})

# 6. 변수 가공

# (1) 성별, 나이, 학력
neet_df['gender_label'] = neet_df['gender'].map({1: '남성', 2: '여성'})
neet_df['age'] = 2021 - neet_df['birthy']
edu_map = {1: '고졸 미만', 2: '고졸', 3: '전문대졸', 4: '대졸', 5: '대학원졸'}
neet_df['edu_label'] = neet_df['w01edu'].map(edu_map)

# (2) 건강상태 라벨
health_map = {
    1: '매우 나쁨',
    2: '나쁜 편',
    3: '보통',
    4: '좋은 편',
    5: '매우 좋음'
}
neet_df['health_label'] = neet_df['y01e606'].map(health_map)

# (3) 부모 학력
def parent_edu(x):
    if pd.isna(x): return np.nan
    return "대졸 이상" if x >= 4 else "대졸 미만"

neet_df['father_edu'] = neet_df['w01edu_f'].apply(parent_edu)
neet_df['mother_edu'] = neet_df['w01edu_m'].apply(parent_edu)

# (4) 자아효능감 평균
eff_cols = ['y01e513', 'y01e514', 'y01e515']
eff_cols = [c for c in eff_cols if c in neet_df.columns]
neet_df['self_efficacy'] = neet_df[eff_cols].mean(axis=1)

# (5) 학자금 대출
neet_df['student_loan'] = neet_df['y01a439'].map({1: '있음', 2: '없음'})

# (6) 진로 계획
neet_df['career_plan_score'] = neet_df['y01e501']

# (7) 활동 경험
def clean_exp(row):
    if row['y01a601'] != 1: return "경험 없음"
    t = row['y01a616_1']
    if t in [1, 2]: return "인턴/현장실습"
    elif t == 3: return "아르바이트"
    elif t == 4: return "창업 경험"
    return "기타"

neet_df['exp_type'] = neet_df.apply(clean_exp, axis=1)

# (8) 진로지도
neet_df['career_guidance'] = neet_df['y01e401'].map({1: '있음', 2: '없음'})

# (9) 지역
region_map = {
    1:'서울', 2:'부산', 3:'대구', 4:'인천', 5:'광주', 6:'대전', 7:'울산', 
    8:'경기', 9:'강원', 10:'충북', 11:'충남', 12:'전북', 13:'전남', 
    14:'경북', 15:'경남', 16:'제주', 17:'세종'
}
neet_df['region_label'] = neet_df['w01region'].map(region_map)

# (10) 구직 정보 취득 경로
search_map = {
    1: '학교 선생님(교수)', 2: '학교 취업정보센터', 3: '언론매체', 4: '부모/친척',
    5: '지인(친구/선후배)', 6: '공공 취업알선기관', 7: '민간 취업알선기관',
    8: '공공 취업포털(워크넷)', 9: '민간 취업포털(사람인 등)', 10: '커뮤니티',
    11: '기업 홈페이지/SNS', 12: '채용설명회', 13: '학원', 14: '현장실습/인턴십',
    15: '헤드헌터', 97: '기타'
}
neet_df['search_method'] = neet_df['y01c768a'].map(search_map).fillna("응답 없음")

# 7. CSV 저장
neet_df.to_csv("neet_dashboard_data.csv", index=False, encoding="utf-8-sig")
print("전처리 완료! neet_dashboard_data.csv 생성됨.")
