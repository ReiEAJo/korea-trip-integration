import os
import sys
import streamlit as st

# 1. 페이지 환경설정 (최상단에서 단 한 번만 실행)
st.set_page_config(
    page_title="Korea Trip 통합 관광 대시보드 메인 앱",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 프로젝트 검색 경로 설정
workspace_root = os.path.dirname(os.path.abspath(__file__))

# korea-trip-data 경로 추가
korea_trip_data_path = os.path.join(workspace_root, "korea-trip-data")
sys.path.append(korea_trip_data_path)

# 3. 대시보드 진입점 함수 임포트
from src.app import (
    apply_custom_style,
    render_home,
    render_foreigner_trend,
    render_tourism_diversity,
    render_demand_analysis,
    render_eda_insights
)

# 두 번째 대시보드 (korea-trip-data2/app.py) 동적 임포트
import importlib.util
korea_trip_data2_path = os.path.join(workspace_root, "korea-trip-data2")
spec = importlib.util.spec_from_file_location(
    "korea_trip_data2_app", 
    os.path.join(korea_trip_data2_path, "app.py")
)
korea_trip_data2_app = importlib.util.module_from_spec(spec)
sys.modules["korea_trip_data2_app"] = korea_trip_data2_app
spec.loader.exec_module(korea_trip_data2_app)

# 4. 공통 라이트 모드 스타일 적용
apply_custom_style()

import base64

# 5. 통합 사이드바 구성 (로고 및 텍스트 메뉴)
logo_path = os.path.join(workspace_root, "korea_trip_logo_circle.png")
if not os.path.exists(logo_path):
    logo_path = os.path.join(workspace_root, "korea trip project_logo.jpeg")

logo_b64 = ""
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")

menu_options = [
    "📈 방한 외래객 추이", 
    "🔍 지역별 관심도 분석",
    "🚶 지역별 방문도 분석",
    "⚖️ 관심도 vs 방문도 격차",
    "🏗️ 지역별 관광 인프라",
    "💡 관광 인사이트 및 제언"
]

if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = menu_options[0]

# 텍스트 형태 메뉴 커스텀 CSS (연한 파란색 사이드바, 가로 길이 통일, 깔끔한 캡슐 라벨, 흰색 펼침목록)
st.markdown("""
<style>
/* 1. 사이드바 상단 여백 및 배경 */
[data-testid="stSidebarUserContent"] {
    padding-top: 1rem !important;
}

section[data-testid="stSidebar"] {
    background-color: #F8FAFC !important;
    background: linear-gradient(180deg, #EFF6FF 0%, #F8FAFC 100%) !important;
    border-right: 1px solid #E2E8F0 !important;
}

/* 2. 원형 로고 이미지 중앙 정렬 */
[data-testid="stSidebar"] img {
    border-radius: 50% !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.15) !important;
    margin-bottom: 20px !important;
    display: block !important;
    margin-left: auto !important;
    margin-right: auto !important;
    width: 100% !important;
    object-fit: cover !important;
}

/* 3. 라디오 메뉴 컨테이너 */
[data-testid="stSidebar"] [data-testid="stRadio"] {
    width: 100% !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] > label {
    display: none !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
    width: 100% !important;
}

/* 4. 라디오 메뉴 각 버튼 캡슐 카드 스타일 */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    box-sizing: border-box !important;
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all 0.15s ease-in-out !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03) !important;
}

/* 라디오 마크다운 텍스트 컨테이너 정렬 */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label p {
    font-family: 'Pretendard', sans-serif !important;
    font-size: 0.90rem !important;
    font-weight: 600 !important;
    color: #334155 !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.3 !important;
    white-space: nowrap !important;
}

/* 마우스 호버 효과 */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {
    background-color: #F1F5F9 !important;
    border-color: #CBD5E1 !important;
}

/* 5. 선택된 라디오 메뉴 (파란색 캡슐 하이라이트) */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked),
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] {
    background-color: #2563EB !important;
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
    border-color: #1D4ED8 !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p,
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* 선택된 라디오의 원형 서클 스타일링 (파란 배경 시 흰색 동그라미) */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) div[data-baseweb="radio"] > div,
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] div[data-baseweb="radio"] > div {
    border-color: #FFFFFF !important;
    background-color: transparent !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) div[data-baseweb="radio"] > div > div,
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] div[data-baseweb="radio"] > div > div {
    background-color: #FFFFFF !important;
}

/* 6. 수집 데이터 출처 expander 스타일 */
div[data-testid="stSidebar"] div[data-testid="stExpander"] {
    width: 100% !important;
    box-sizing: border-box !important;
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    margin-top: 14px !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03) !important;
    overflow: hidden !important;
}

div[data-testid="stSidebar"] div[data-testid="stExpander"] summary {
    padding: 10px 14px !important;
    min-height: auto !important;
}

div[data-testid="stSidebar"] div[data-testid="stExpander"] details summary p {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: #334155 !important;
    margin: 0 !important;
}

div[data-testid="stSidebar"] div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    padding: 10px 14px !important;
}
</style>
""", unsafe_allow_html=True)

# 사이드바 내용 렌더링
with st.sidebar:
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)

    if "main_menu_selection" not in st.session_state:
        st.session_state.main_menu_selection = menu_options[0]

    selected_menu = st.radio(
        label="대시보드 메뉴 선택",
        options=menu_options,
        key="main_menu_selection",
        label_visibility="collapsed"
    )

    # 사이드바 하단 수집 데이터 출처 펼침메뉴(expander)
    st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)
    with st.expander("📁 수집 데이터 출처"):
        st.markdown("""
        <div style="font-size:0.75rem; color:#475569; line-height:1.6; font-family:'Pretendard', sans-serif; background-color: #FFFFFF;">
            <div>· 한국관광공사(KTO) 통계 & 데이터랩</div>
            <div>· 한국문화관광연구원 외래관광객 실태조사</div>
            <div>· 신한카드 & BC카드 소비 빅데이터</div>
            <div>· 문화체육관광부 & 공공데이터포털(ODCloud)</div>
            <div>· 문화공공데이터광장 (축제/여행지 정보)</div>
            <div>· 글로벌 OTA (Klook, KKday, GetYourGuide)</div>
            <div>· 인스타그램 리뷰 및 해시태그 버즈</div>
            <div>· 캐치테이블 글로벌 예약/리뷰</div>
            <div>· 네이버 지도 외국인 리뷰</div>
            <div>· 구글 트렌드 분석</div>
            <div>· TripAdvisor 평점 및 리뷰</div>
            <div>· Tumblr 포럼 리뷰 데이터</div>
            <div style="margin-top: 6px; font-weight: 600; color: #334155; border-top: 1px solid #E2E8F0; padding-top: 4px;">
                · 기준기간: 2025.06 ~ 2026.05
            </div>
        </div>
        """, unsafe_allow_html=True)

selected_menu = st.session_state.main_menu_selection

# 6. 메인 페이지 콘텐츠 렌더링
if selected_menu == menu_options[0]:
    render_foreigner_trend()
elif selected_menu == menu_options[1]:
    korea_trip_data2_app.render_korea_trip_data2_dashboard(active_page="interest", show_sidebar=False)
elif selected_menu == menu_options[2]:
    korea_trip_data2_app.render_korea_trip_data2_dashboard(active_page="visit", show_sidebar=False)
elif selected_menu == menu_options[3]:
    korea_trip_data2_app.render_korea_trip_data2_dashboard(active_page="vs", show_sidebar=False)
elif selected_menu == menu_options[4]:
    render_demand_analysis()
elif selected_menu == menu_options[5]:
    render_eda_insights()
