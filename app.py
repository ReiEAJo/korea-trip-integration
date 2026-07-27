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
/* 사이드바 상단 여백 축소 및 연한 파란색 바탕 */
[data-testid="stSidebarUserContent"] {
    padding-top: 1rem !important;
}

section[data-testid="stSidebar"] {
    background-color: #EFF6FF !important;
    background: linear-gradient(180deg, #EFF6FF 0%, #F0F9FF 100%) !important;
    border-right: 1px solid #DBEAFE !important;
}

/* 로고 이미지 원형 및 중앙 정렬 스타일 */
[data-testid="stSidebar"] img {
    border-radius: 50% !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15) !important;
    margin-bottom: 16px !important;
    display: block !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* 라디오 메뉴 가로/세로 레이아웃 규격화 */
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

/* 각 라디오 메뉴 캡슐 버튼 */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    box-sizing: border-box !important;
    background-color: #FFFFFF !important;
    border: 1px solid #DBEAFE !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all 0.15s ease-in-out !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
}

/* 라디오 동그라미 아이콘 제거 */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

/* 마우스 호버 효과 */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {
    background-color: #DBEAFE !important;
    border-color: #93C5FD !important;
}

/* 선택된 메뉴 항목 스타일 (파란색 활성화 캡슐) */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked),
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] {
    background-color: #2563EB !important;
    border-color: #1D4ED8 !important;
    box-shadow: 0 3px 8px rgba(37, 99, 235, 0.3) !important;
}

/* 메뉴 텍스트 폰트 스타일 */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label p {
    font-family: 'Pretendard', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: #334155 !important;
    margin: 0 !important;
    white-space: nowrap !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p,
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* 사이드바 expander 및 하단 데이터 목록 바탕 순백색(#FFFFFF) 설정 */
div[data-testid="stSidebar"] div[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 10px !important;
    margin-top: 16px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    overflow: hidden !important;
}

div[data-testid="stSidebar"] div[data-testid="stExpander"] details summary p {
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: #334155 !important;
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
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    with st.expander("📁 수집 데이터 출처"):
        st.markdown("""
        <div style="font-size:0.78rem; color:#475569; line-height:1.7; font-family:'Pretendard', sans-serif; background-color: #FFFFFF;">
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
            <div style="margin-top: 8px; font-weight: 600; color: #334155; border-top: 1px solid #E2E8F0; padding-top: 6px;">
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
