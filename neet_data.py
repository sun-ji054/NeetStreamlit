import pandas as pd
import numpy as np

print("데이터 전처리 시작...")

# 1. 원본 데이터 로드
try:
    w1 = pd.read_csv("YP2021_w01.csv")
    w2 = pd.read_csv("YP2021_w02.csv")
    w3 = pd.read_csv("YP2021_w03.csv")
except FileNotFoundError:
    print("오류: 'YP2021_w01.csv' 등의 원본 파일이 폴더에 없습니다.")
    exit()

# 2. 필요한 변수 선택 (기본 변수 + 심화 분석 변수 모두 포함)
# y01a439: 학자금 대출, w01edu_f/m: 부모 학력, y01e513~515: 자아효능감
target_vars = [
    'sampid', 'gender', 'birthy', 'w01ecoact', 'w01student', 'w01edu', 'w01region', 'y01e606',
    'y01a601', 'y01a616_1', 'y01e401', 'y01e501', 
    'w01edu_f', 'w01edu_m', 'y01a439', 'y01e513', 'y01e514', 'y01e515'
]

# 실제로 존재하는 컬럼만 선택 (오류 방지)
valid_vars = [c for c in target_vars if c in w1.columns]
w1_sel = w1[valid_vars].copy()
w2_sel = w2[['sampid', 'w02ecoact', 'w02student']].copy()
w3_sel = w3[['sampid', 'w03ecoact', 'w03student']].copy()

# 3. 데이터 병합
df = w1_sel.merge(w2_sel, on='sampid', how='left').merge(w3_sel, on='sampid', how='left')

# 4. NEET 여부 판단 (1차년도)
df['neet_w1'] = df.apply(lambda x: (x['w01ecoact'] in [2, 3]) and (x['w01student'] == 2), axis=1)
neet_df = df[df['neet_w1'] == True].copy()

# 5. 취업 여부 (Outcome)
def check_employment(row):
    w2_emp = (row['w02ecoact'] == 1)
    w3_emp = (row['w03ecoact'] == 1)
    return "취업 성공" if (w2_emp or w3_emp) else "미취업"

neet_df['outcome'] = neet_df.apply(check_employment, axis=1)
neet_df['got_job_flag'] = neet_df['outcome'].map({'취업 성공': 1, '미취업': 0})

# 6. 변수 가공 및 라벨링

# (1) 기본 정보
neet_df['gender_label'] = neet_df['gender'].map({1: '남성', 2: '여성'})
neet_df['age'] = 2021 - neet_df['birthy']
edu_map = {1: '고졸 미만', 2: '고졸', 3: '전문대졸', 4: '대졸', 5: '대학원졸'}
neet_df['edu_label'] = neet_df['w01edu'].map(edu_map)


# (2) 부모 학력 (대졸 이상 여부)
def check_parent_edu(code):
    if pd.isna(code): return np.nan
    return "대졸 이상" if (code >= 4 and code < 10) else "대졸 미만"

if 'w01edu_f' in neet_df.columns:
    neet_df['father_edu'] = neet_df['w01edu_f'].apply(check_parent_edu)
if 'w01edu_m' in neet_df.columns:
    neet_df['mother_edu'] = neet_df['w01edu_m'].apply(check_parent_edu)

# (3) 구직 효능감 (평균)
eff_cols = [c for c in ['y01e513', 'y01e514', 'y01e515'] if c in neet_df.columns]
if eff_cols:
    neet_df['self_efficacy'] = neet_df[eff_cols].mean(axis=1)

# (4) 학자금 대출 (핵심 원인 해결)
if 'y01a439' in neet_df.columns:
    neet_df['student_loan'] = neet_df['y01a439'].map({1: '있음', 2: '없음'})
else:
    neet_df['student_loan'] = '데이터 없음' # 컬럼이 없어도 생성해서 에러 방지

# (5) 진로 계획
neet_df['career_plan_score'] = neet_df['y01e501']

# (6) 활동 경험
def clean_experience(row):
    if row.get('y01a601') != 1: return "경험 없음"
    t = row.get('y01a616_1')
    if t in [1, 2]: return "인턴/현장실습"
    elif t == 3: return "아르바이트"
    elif t == 4: return "창업 경험"
    else: return "기타"

neet_df['exp_type'] = neet_df.apply(clean_experience, axis=1)
neet_df['career_guidance'] = neet_df['y01e401'].map({1: '있음', 2: '없음'})
neet_df['region_label'] = neet_df['w01region'].map({
    1:'서울', 2:'부산', 3:'대구', 4:'인천', 5:'광주', 6:'대전', 7:'울산', 8:'경기', 
    9:'강원', 10:'충북', 11:'충남', 12:'전북', 13:'전남', 14:'경북', 15:'경남', 16:'제주', 17:'세종'
})


# 8. 파일 저장
neet_df.to_csv("neet_dashboard_data.csv", index=False, encoding='utf-8-sig')
print("전처리 완료! 'neet_dashboard_data.csv' 파일이 업데이트되었습니다.")