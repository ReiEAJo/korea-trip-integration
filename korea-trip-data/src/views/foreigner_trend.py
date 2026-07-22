"""
방한 외래객 추이 분석 모듈입니다.
주요 기능:
- 성별/연령대별 교차 분포, 국적 점유율
- 방문자/입국자 국적 집중화 현상 분석
"""
import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def render_foreigner_trend():
    st.title("📈 방한 외래관광객 트렌드 분석")
    st.markdown("글로벌 외래 관광객의 입국 트렌드와 인구통계학적 세그먼트 분석을 제공합니다.")
    st.caption("🔹 **자료 출처:** 한국관광공사(한국관광 데이터랩), 공공데이터포털(ODCloud)")
    st.markdown("---")

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
    
    @st.cache_data
    def load_real_data():
        try:
            df_monthly = pd.read_csv(os.path.join(data_dir, '20260702201956_전체 외국인 방문자수 및 증감률 CSV 다운로드.csv'), encoding='utf-8')
        except:
            df_monthly = pd.read_csv(os.path.join(data_dir, '20260702201956_전체 외국인 방문자수 및 증감률 CSV 다운로드.csv'), encoding='cp949')
            
        try:
            df_gender_age = pd.read_csv(os.path.join(data_dir, '20260702211925_성_연령별 입국현황.csv'), encoding='utf-8')
        except:
            df_gender_age = pd.read_csv(os.path.join(data_dir, '20260702211925_성_연령별 입국현황.csv'), encoding='cp949')
            
        try:
            df_purpose = pd.read_csv(os.path.join(data_dir, '20260702211937_목적별 입국현황.csv'), encoding='utf-8')
        except:
            df_purpose = pd.read_csv(os.path.join(data_dir, '20260702211937_목적별 입국현황.csv'), encoding='cp949')
            
        try:
            df_entry = pd.read_csv(os.path.join(data_dir, '20260620155533_입국자 국적별 입국현황.csv'), encoding='utf-8')
        except:
            df_entry = pd.read_csv(os.path.join(data_dir, '20260620155533_입국자 국적별 입국현황.csv'), encoding='cp949')
            
        return df_monthly, df_gender_age, df_purpose, df_entry

    try:
        df_monthly, df_gender_age, df_purpose, df_entry = load_real_data()
    except Exception as e:
        st.warning(f"로컬 입국자 데이터를 불러올 수 없습니다: {e}")
        return

    # 데이터 타입 캐스팅 및 파생 변수 처리
    # '202506' 같은 숫자형태 문자열을 '2025-06' 형태로 변환하여 Plotly가 숫자로 자동 해석(예: 202.5k)하지 않도록 방지
    df_monthly['기준년월'] = df_monthly['기준년월'].astype(str)
    df_monthly['기준년월'] = df_monthly['기준년월'].str[:4] + '-' + df_monthly['기준년월'].str[4:]
    
    # 2026년 총 방문자 수 계산
    df_2026 = df_monthly[df_monthly['기준년월'].str.startswith('2026')]
    total_foreigner_2026 = df_2026['조회기간 방문자 수'].sum()
    
    # 대표 목적 및 연령 산출
    top_purpose = df_purpose.loc[df_purpose['방문자 수(명)'].idxmax(), '목적 유형']
    
    df_gender_age['총 승객 수'] = df_gender_age['남성 승객 수(명)'] + df_gender_age['여성 승객 수(명)']
    top_age = df_gender_age.loc[df_gender_age['총 승객 수'].idxmax(), '연령 구분']

    # 메인 요약 KPI
    st.markdown("### 📊 방한 외래객 유입 현황 요약")
    
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.metric(
            label="방한 외래객 총수(2026년 기준 누적)", 
            value=f"{total_foreigner_2026:,.0f} 명"
        )
    with kpi_col2:
        st.metric(label="핵심 입국 목적", value=top_purpose)
    with kpi_col3:
        st.metric(label="주요 방문 연령층", value=top_age)

    # 1-1. 왜 관심이 많을까? 주요 키워드 분석
    with st.container():
        st.markdown("### 🔤 1-1. 왜 관심이 많을까? 주요 키워드 분석")
        st.caption("외국인 관광객들의 관심이 높은 한국 주요 로컬 도시별 키워드 및 워드클라우드 분석입니다.")
        
        cities_list = ["경주", "강릉", "안동", "수원", "양양", "남해", "울산", "평택", "창원", "춘천", "여수", "전주"]
        keywords_list = [
            "역사 템플스테이 불국사 한옥 문화재 첨성대 전통",
            "바다 서핑 카페거리 해변 순두부 힐링 동해",
            "하회탈 전통 한옥 고택 역사 서원 안동찜닭",
            "수원화성 성곽 갈비 당일치기 역사 근교 지하철",
            "서핑 양양 서피비치 클럽 젊음 바다 인스타",
            "독일마을 다랭이마을 남해대교 힐링 바다 드라이브",
            "비즈니스 출장 공업 공장 바이어 현대 산업",
            "미군기지 비즈니스 산업단지 평택항 일자리 근로자",
            "산업 비즈니스 출장 창원공단 벚꽃 군항제 기계",
            "닭갈비 남이섬 호수 엠티 가평 근교 ITX",
            "여수밤바다 낭만포차 돌산대교 케이블카 간장게장",
            "한옥마을 먹방 전주비빔밥 막걸리 한복 성당"
        ]
        df_kw = pd.DataFrame({"도시": cities_list, "관심_키워드": keywords_list})
        
        col_kw1, col_kw2 = st.columns([2, 3])
        with col_kw1:
            st.markdown("#### **도시별 키워드 선택**")
            selected_city_ft = st.selectbox("키워드를 확인하고 싶은 도시를 선택하세요:", df_kw["도시"].unique(), key="ft_city_select")
            text_data_ft = df_kw[df_kw["도시"] == selected_city_ft]["관심_키워드"].values[0]
            st.info(f"💡 **{selected_city_ft}**의 인기 태그: {text_data_ft}")

        with col_kw2:
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
            
            font_path = "C:/Windows/Fonts/malgun.ttf"
            if not os.path.exists(font_path):
                font_path = None
                
            wordcloud = WordCloud(
                width=500, height=320, 
                background_color='white',
                font_path=font_path
            ).generate(text_data_ft)
            
            fig_wc, ax_wc = plt.subplots(figsize=(6, 3.8))
            ax_wc.imshow(wordcloud, interpolation='bilinear')
            ax_wc.axis("off")
            st.pyplot(fig_wc)
            plt.close(fig_wc)

    st.markdown("---")


    
    st.header("🗺️ 국적 집중화 현상")
    st.markdown("특정 국가에 편중된 의존도를 분석합니다.")
    
    if df_entry is not None and not df_entry.empty:
        st.subheader("방한 주요 국적별 입국자 총량")
        
        iso_mapping = {
            '중국': 'CHN', '일본': 'JPN', '대만': 'TWN', '미국': 'USA',
            '홍콩': 'HKG', '베트남': 'VNM', '싱가포르': 'SGP', '필리핀': 'PHL',
            '태국': 'THA', '말레이시아': 'MYS', '인도네시아': 'IDN', '러시아': 'RUS',
            '영국': 'GBR', '캐나다': 'CAN', '프랑스': 'FRA', '독일': 'DEU', '호주': 'AUS'
        }
        df_entry['ISO_CODE'] = df_entry['입국자 국적'].map(iso_mapping)
        
        # 각 국가별 중심 위경도
        base_coords = {
            'CHN': [104.195, 35.861], 'JPN': [138.252, 36.204], 'TWN': [120.960, 23.697], 
            'USA': [-95.712, 37.090], 'HKG': [114.109, 22.396], 'VNM': [108.277, 14.058], 
            'SGP': [103.819, 1.352], 'PHL': [121.774, 12.879], 'THA': [100.992, 15.870], 
            'MYS': [101.975, 4.210], 'IDN': [113.921, -0.789], 'RUS': [105.318, 61.524],
            'GBR': [-3.435, 55.378], 'CAN': [-106.346, 56.130], 'FRA': [2.213, 46.227], 
            'DEU': [10.451, 51.165], 'AUS': [133.775, -25.274]
        }
        
        df_entry['lon'] = df_entry['ISO_CODE'].map(lambda x: base_coords.get(x, [0,0])[0])
        df_entry['lat'] = df_entry['ISO_CODE'].map(lambda x: base_coords.get(x, [0,0])[1])

        # 돌링 카토그램을 위한 충돌 방지 로직 (Force-directed)
        max_val = df_entry['입국자 수(명)'].max()
        # 원의 논리적 반지름을 도(degree) 단위로 대략 환산 (최대 10도 수준)
        size_factor = 10.0 / np.sqrt(max_val) if max_val > 0 else 1
        df_entry['radius'] = np.sqrt(df_entry['입국자 수(명)']) * size_factor

        positions = df_entry[['lon', 'lat']].values.astype(float)
        radii = df_entry['radius'].values.astype(float)
        orig_positions = positions.copy()

        n = len(positions)
        for _ in range(150): # 겹침을 방지하기 위한 물리 엔진 반복
            for i in range(n):
                for j in range(i+1, n):
                    dx = positions[i, 0] - positions[j, 0]
                    dy = positions[i, 1] - positions[j, 1]
                    dist = np.sqrt(dx**2 + dy**2)
                    min_dist = radii[i] + radii[j]
                    
                    if dist < min_dist and dist > 0:
                        overlap = min_dist - dist
                        nx, ny = dx / dist, dy / dist
                        
                        # 가중치 (크기가 작은 원이 더 많이 움직이도록)
                        w_i = radii[j] / (radii[i] + radii[j])
                        w_j = radii[i] / (radii[i] + radii[j])
                        
                        positions[i, 0] += nx * overlap * w_i * 0.5
                        positions[i, 1] += ny * overlap * w_i * 0.5
                        positions[j, 0] -= nx * overlap * w_j * 0.5
                        positions[j, 1] -= ny * overlap * w_j * 0.5
                        
            # 원래 지리적 위치로 돌아가려는 힘
            for i in range(n):
                positions[i, 0] += (orig_positions[i, 0] - positions[i, 0]) * 0.05
                positions[i, 1] += (orig_positions[i, 1] - positions[i, 1]) * 0.05

        df_entry['lon_adj'] = positions[:, 0]
        df_entry['lat_adj'] = positions[:, 1]
        
        fig4 = px.scatter_geo(
            df_entry, 
            lon="lon_adj",
            lat="lat_adj",
            size="입국자 수(명)",
            color="입국자 수(명)", 
            hover_name="입국자 국적",
            hover_data={"lon_adj": False, "lat_adj": False, "ISO_CODE": False, "입국자 수(명)": True, "입국자 비율(%)": True},
            title="국적별 입국자 수 돌링 카토그램",
            color_continuous_scale="Blues",
            projection="equirectangular",
            size_max=60
        )
        
        fig4.update_traces(marker_line_color="white", marker_line_width=1)
        fig4.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor="black",
                showcountries=True,
                countrycolor="black",
                bgcolor="rgba(0,0,0,0)",
                fitbounds="locations"  # 데이터가 있는 위치를 기준으로 줌인 (여백 제거)
            ),
            height=600,  # 차트 높이를 키워 좌우로 더 확장되도록 유도
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
            hoverlabel=dict(bgcolor="#E2E8F0", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig4, use_container_width=True, key='chart_foreigner_trend_fig4_16')
        with st.expander("📊 국적별 입국자 통계 및 데이터"):
            st.caption("🔹 **자료 출처:** 한국관광공사(한국관광데이터랩) - 입국자 국적별 입국현황")
            st.dataframe(df_entry[['입국자 수(명)', '입국자 비율(%)']].describe().astype(str), use_container_width=True)
            st.dataframe(df_entry[['입국자 국적', '입국자 수(명)', '입국자 비율(%)']], use_container_width=True)
    else:
        st.warning("입국자 국적 데이터를 확인할 수 없습니다.")
