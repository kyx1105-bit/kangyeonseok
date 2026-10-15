import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 데이터 불러오기 (스트림릿 캐시를 사용하여 앱 속도 향상)
@st.cache_data
def load_data():
    # 첨부된 압축 CSV 파일을 판다스로 읽어옵니다.
    df = pd.read_csv('population_ts_yearly_gender.csv')
    return df

df = load_data()

# 2. 가장 최신 연도 데이터만 필터링
latest_year = df['연도'].max()
df_latest = df[df['연도'] == latest_year]

st.title(f"🏘️ {latest_year}년 동네별 인구 피라미드")
st.write("원하는 동네를 선택하면 해당 지역의 인구 구조를 따뜻한 톤의 피라미드 그래프로 보여줍니다.")

# 3. 화면 상단 드롭다운 (시도 -> 시군구 -> 동)
col1, col2, col3 = st.columns(3)

with col1:
    sido_list = df_latest['시도'].unique()
    selected_sido = st.selectbox('시도 선택', sido_list)

with col2:
    sigungu_list = df_latest[df_latest['시도'] == selected_sido]['시군구'].unique()
    selected_sigungu = st.selectbox('시군구 선택', sigungu_list)

with col3:
    dong_list = df_latest[(df_latest['시도'] == selected_sido) & (df_latest['시군구'] == selected_sigungu)]['동'].unique()
    selected_dong = st.selectbox('동 선택', dong_list)

# 4. 선택된 동네의 데이터 추출
selected_data = df_latest[
    (df_latest['시도'] == selected_sido) & 
    (df_latest['시군구'] == selected_sigungu) & 
    (df_latest['동'] == selected_dong)
].iloc[0]

# 5. 나이 라벨 0세~100세 이상까지 순서대로 생성
ages = [f"{i}세" for i in range(100)] + ["100세 이상"]

# 남녀 컬럼명 생성 및 데이터 추출
male_cols = [f"남_{age}" for age in ages]
female_cols = [f"여_{age}" for age in ages]

# 남자는 왼쪽으로 그려야 하므로 음수로 변환합니다.
male_values = selected_data[male_cols].values * -1
female_values = selected_data[female_cols].values

# 6. Plotly 가로 막대그래프(인구 피라미드) 그리기
fig = go.Figure()

# 남자 데이터 추가 (따뜻한 노란/주황 톤)
fig.add_trace(go.Bar(
    y=ages,
    x=male_values,
    orientation='h',
    name='남성',
    marker_color='#F4A261', 
    hoverinfo='y+text',
    text=[f"{abs(v):,}명" for v in male_values] # 마우스 오버 시 양수로 표시
))

# 여자 데이터 추가 (따뜻한 붉은/코랄 톤)
fig.add_trace(go.Bar(
    y=ages,
    x=female_values,
    orientation='h',
    name='여성',
    marker_color='#E76F51',
    hoverinfo='y+text',
    text=[f"{v:,}명" for v in female_values]
))

# 7. 그래프 축 및 레이아웃 설정
fig.update_layout(
    title=f"{selected_sido} {selected_sigungu} {selected_dong} 인구 피라미드",
    barmode='relative', # 막대를 좌우로 배치하기 위한 설정
    bargap=0.1,
    height=800,
    yaxis=dict(
        title="나이",
        type='category',
        categoryorder='array', # 축 뒤집기 옵션 없이 배열 순서 그대로 고정
        categoryarray=ages     # 0세부터 100세 이상까지 명시된 리스트 순서 적용
    ),
    xaxis=dict(
        title="인구 수(명)",
        tickformat="d" # 정수 형태로 표시
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# 스트림릿 화면에 그래프 출력
st.plotly_chart(fig, use_container_width=True)
