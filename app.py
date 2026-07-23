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

# 5. 통합 사이드바 구성 (라이트 모드 테마)
st.sidebar.markdown("""
<div style="padding:15px; text-align:center; background: linear-gradient(135deg, #1D4ED8 0%, #059669 100%); border-radius: 14px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
    <h2 style="color:white; margin:0; font-size:1.35rem; font-weight:800; font-family:'Pretendard', sans-serif;">🗺️ Korea Trip</h2>
    <span style="color:#F1F5F9; font-size:0.78rem; font-weight:600; display:block; margin-top:5px;">통합 관광 분석 대시보드</span>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎯 연령대 분석 그룹")
    st.markdown("""
    <div style="margin-bottom:10px;">
        <span style="display:inline-block; background: linear-gradient(90deg, #1D4ED8, #2563EB); color: white; font-weight:700; font-size:0.85rem; padding:4px 14px; border-radius:20px; margin-right:6px;">청년층 (10대~40대)</span>
    </div>
    <div>
        <span style="display:inline-block; background: linear-gradient(90deg, #059669, #10B981); color: white; font-weight:700; font-size:0.85rem; padding:4px 14px; border-radius:20px; margin-right:6px;">중장년층 (50대~90대)</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### ℹ️ 분석 범위")
    st.info("💡 서울특별시, 부산광역시, 제주특별자치도는 분석 대상에서 제외되었습니다 (내국인 검색 제외 14개 시도 대상).")

    st.markdown("---")

    st.markdown("### 📁 수집 데이터 출처")
    st.markdown("""
    <div style="font-size:0.82rem; color:#475569; line-height:1.75; font-family:'Pretendard', sans-serif;">
    · 한국관광공사(KTO) 외래객 통계 & 데이터랩<br>
    · 한국문화관광연구원 외래관광객 실태조사<br>
    · 신한카드 & BC카드 소비 빅데이터<br>
    · 문화체육관광부 & 공공데이터포털(ODCloud)<br>
    · 문화공공데이터광장 (지역축제/여행지 정보)<br>
    · 글로벌 OTA (Klook, KKday, GetYourGuide, Creatrip)<br>
    · 인스타그램 리뷰 및 해시태그 버즈<br>
    · 캐치테이블 글로벌 예약/리뷰<br>
    · 네이버 지도 외국인 리뷰<br>
    · 구글 트렌드 분석<br>
    · TripAdvisor 평점 및 리뷰<br>
    · Tumblr 포럼 리뷰 데이터<br>
    · 기준기간: 2025.06 ~ 2026.05
    </div>
    """, unsafe_allow_html=True)

# 6. 메인 페이지 탭 구성
tabs = st.tabs([
    "📈 방한 외래객 추이", 
    "🔍 지역별 관심도 분석",
    "🚶 지역별 방문도 분석",
    "🏛️ 지역별 관광 인프라", 
    "⚖️ 관심도 vs 방문도 격차",
    "💡 관광 인사이트 및 제언",
    "🗺️ 외국인 방문 트렌드 지도"
])

with tabs[0]:
    render_foreigner_trend()

with tabs[1]:
    korea_trip_data2_app.render_korea_trip_data2_dashboard(active_page="interest", show_sidebar=False)

with tabs[2]:
    korea_trip_data2_app.render_korea_trip_data2_dashboard(active_page="visit", show_sidebar=False)

with tabs[3]:
    render_demand_analysis()

with tabs[4]:
    korea_trip_data2_app.render_korea_trip_data2_dashboard(active_page="vs", show_sidebar=False)

with tabs[5]:
    render_eda_insights()

with tabs[6]:
    import importlib.util
    test_app_path = os.path.join(korea_trip_data2_path, "test", "app.py")
    if os.path.exists(test_app_path):
        spec_test = importlib.util.spec_from_file_location("test_map_app", test_app_path)
        test_map_app = importlib.util.module_from_spec(spec_test)
        spec_test.loader.exec_module(test_map_app)
        if hasattr(test_map_app, "main"):
            test_map_app.main()
    else:
        st.warning("외국인 방문 트렌드 지도 모듈을 찾을 수 없습니다.")
