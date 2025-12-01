import pandas as pd

# 1. 데이터 로드
w1 = pd.read_csv("YP2021_w01.csv")
w2 = pd.read_csv("YP2021_w02.csv")
w3 = pd.read_csv("YP2021_w03.csv")

# 2. 필요한 변수 선택 (1차년도 특성 + 2,3차년도 상태)
# sampid: 패널ID, gender: 성별, birthy: 출생년도
# ecoact: 경제활동상태, student: 학생여부
# edu: 최종학력, region: 거주지, y01e606: 주관적 건강상태
w1_sel = w1[['sampid', 'gender', 'birthy', 'w01ecoact', 'w01student', 'w01edu', 'w01region', 'y01e606']].copy()
w2_sel = w2[['sampid', 'w02ecoact', 'w02student']].copy()
w3_sel = w3[['sampid', 'w03ecoact', 'w03student']].copy()

# 3. 데이터 병합 (Left Join)
df = w1_sel.merge(w2_sel, on='sampid', how='left').merge(w3_sel, on='sampid', how='left')

# 4. NEET 여부 판단 함수
def is_neet(ecoact, student):
    # 실업자(2) 혹은 비경제활동(3) AND 학생아님(2)
    if pd.isna(ecoact) or pd.isna(student):
        return False
    return (ecoact in [2, 3]) and (student == 2)

# 각 차수별 NEET 상태 정의
df['neet_w1'] = df.apply(lambda x: is_neet(x['w01ecoact'], x['w01student']), axis=1)

# 5. 1차년도 NEET 족 필터링
neet_df = df[df['neet_w1'] == True].copy()

# 6. 노동시장 진입(취업) 여부 판단 (Outcome)
# 2차나 3차 중 한 번이라도 취업(1) 상태가 되면 '취업 성공'으로 간주
def check_employment(row):
    w2_emp = (row['w02ecoact'] == 1)
    w3_emp = (row['w03ecoact'] == 1)
    if w2_emp or w3_emp:
        return "취업 성공"
    else:
        return "미취업"

neet_df['outcome'] = neet_df.apply(check_employment, axis=1)

# 7. 분석을 위한 변수 매핑 (코드북 기준)
# 성별
neet_df['gender_label'] = neet_df['gender'].map({1: '남성', 2: '여성'})

# 나이 (2021년 기준)
neet_df['age'] = 2021 - neet_df['birthy']

# 학력
edu_map = {1: '고졸 미만', 2: '고졸', 3: '전문대졸', 4: '대졸', 5: '대학원졸'}
neet_df['edu_label'] = neet_df['w01edu'].map(edu_map)

# 거주지
region_map = {
    1:'서울', 2:'부산', 3:'대구', 4:'인천', 5:'광주', 6:'대전', 7:'울산', 
    8:'경기', 9:'강원', 10:'충북', 11:'충남', 12:'전북', 13:'전남', 
    14:'경북', 15:'경남', 16:'제주', 17:'세종'
}
neet_df['region_label'] = neet_df['w01region'].map(region_map)

# 건강상태 (1:아주안좋음 ~ 5:매우좋음)
health_map = {1: '매우 나쁨', 2: '나쁜 편', 3: '보통', 4: '좋은 편', 5: '매우 좋음'}
neet_df['health_label'] = neet_df['y01e606'].map(health_map)

# 8. 파일 저장
neet_df.to_csv("neet_dashboard_data.csv", index=False, encoding='utf-8-sig')
print("전처리 완료: neet_dashboard_data.csv 생성됨")