# make_data.py
import pandas as pd
import numpy as np

# 1. 데이터 로드
print("데이터 로딩 중...")
try:
    w1 = pd.read_csv("YP2021_w01.csv")
    w2 = pd.read_csv("YP2021_w02.csv")
    w3 = pd.read_csv("YP2021_w03.csv")
except FileNotFoundError:
    print("오류: 데이터 파일(YP2021_w01.csv 등)이 폴더에 없습니다.")
    exit()

# 2. 필요한 변수 선택 (기본 + 진로/활동)
vars_w1 = [
    'sampid', 'gender', 'birthy', 'w01ecoact', 'w01student', 'w01edu', 'w01region', 'y01e606', # 기본
    'y01a601', 'y01a616_1', 'y01e401', 'y01e501' # 심화(일경험, 진로지도, 계획)
]
w1_sel = w1[vars_w1].copy()
w2_sel = w2[['sampid', 'w02ecoact', 'w02student']].copy()
w3_sel = w3[['sampid', 'w03ecoact', 'w03student']].copy()

# 3. 데이터 병합
df = w1_sel.merge(w2_sel, on='sampid', how='left').merge(w3_sel, on='sampid', how='left')

# 4. NEET 여부 판단 (1차년도)
# NEET: 실업자(2) or 비경제활동(3) AND 학생아님(2)
df['neet_w1'] = df.apply(lambda x: (x['w01ecoact'] in [2, 3]) and (x['w01student'] == 2), axis=1)
neet_df = df[df['neet_w1'] == True].copy()

# 5. 노동시장 진입(취업) 여부 판단 (Outcome)
def check_employment(row):
    w2_emp = (row['w02ecoact'] == 1)
    w3_emp = (row['w03ecoact'] == 1)
    return "취업 성공" if (w2_emp or w3_emp) else "미취업"

neet_df['outcome'] = neet_df.apply(check_employment, axis=1)
neet_df['got_job_flag'] = neet_df['outcome'].apply(lambda x: 1 if x == '취업 성공' else 0) # 상관분석용 숫자 변수

# 6. 변수 전처리 및 라벨링

# [기본] 성별, 나이, 학력, 지역, 건강
neet_df['gender_label'] = neet_df['gender'].map({1: '남성', 2: '여성'})
neet_df['age'] = 2021 - neet_df['birthy']

edu_map = {1: '고졸 미만', 2: '고졸', 3: '전문대졸', 4: '대졸', 5: '대학원졸'}
neet_df['edu_label'] = neet_df['w01edu'].map(edu_map)

region_map = {
    1:'서울', 2:'부산', 3:'대구', 4:'인천', 5:'광주', 6:'대전', 7:'울산', 
    8:'경기', 9:'강원', 10:'충북', 11:'충남', 12:'전북', 13:'전남', 
    14:'경북', 15:'경남', 16:'제주', 17:'세종'
}
neet_df['region_label'] = neet_df['w01region'].map(region_map)

health_map = {1: '매우 나쁨', 2: '나쁜 편', 3: '보통', 4: '좋은 편', 5: '매우 좋음'}
neet_df['health_label'] = neet_df['y01e606'].map(health_map)

# [심화] 활동 경험 (인턴/알바)
# y01a601: 1=있다, 2=없다 / y01a616_1: 1=인턴, 2=현장실습, 3=알바
def clean_experience(row):
    if row['y01a601'] != 1:
        return "경험 없음"
    t = row['y01a616_1']
    if t in [1, 2]: return "인턴/현장실습"
    elif t == 3: return "아르바이트"
    elif t == 4: return "창업 경험"
    else: return "기타"

neet_df['exp_type'] = neet_df.apply(clean_experience, axis=1)

# [심화] 진로지도 경험
neet_df['career_guidance'] = neet_df['y01e401'].map({1: '있음', 2: '없음'})

# [심화] 진로계획 명확성 (1~5점)
neet_df['career_plan_score'] = neet_df['y01e501']

# 7. 파일 저장
neet_df.to_csv("neet_dashboard_data.csv", index=False, encoding='utf-8-sig')
print(f"전처리 완료: {len(neet_df)}명의 통합 데이터 저장됨.")