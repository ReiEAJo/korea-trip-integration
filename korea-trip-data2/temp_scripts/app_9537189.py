# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import requests
import urllib.parse
import plotly.express as px
import plotly.graph_objects as ob
import random
from datetime import datetime

# ?섏씠吏 湲곕낯 ?ㅼ젙 (??대뱶 ?덉씠?꾩썐 諛?釉뚮씪?곗? ??댄?)
st.set_page_config(
    page_title="??쒕?援?吏??퀎 愿愿?鍮낅뜲?댄꽣 ?ㅼ떆媛???쒕낫??,
    page_icon="?덌툘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS瑜??쒖슜??Glassmorphism 諛??꾨━誘몄뾼 ?ㅽ겕 紐⑤뱶 ?붿옄???ㅽ??쇰쭅
st.markdown("""
    <style>
        /* 湲濡쒕쾶 ?고듃 諛??ㅽ???*/
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Noto+Sans+KR:wght@300;400;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', 'Noto Sans KR', sans-serif;
        }
        
        /* 硫붿씤 諛곌꼍 洹몃씪?곗씠??*/
        .main {
            background: linear-gradient(135deg, #0B0F19 0%, #111827 100%);
        }
        
        /* ??쒕낫??移대뱶 ?ㅽ???*/
        .metric-card {
            background: rgba(22, 29, 48, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-4px);
            border-color: rgba(0, 210, 196, 0.3);
            box-shadow: 0 12px 40px 0 rgba(0, 210, 196, 0.1);
        }
        
        /* 洹몃씪?곗씠???띿뒪????댄? */
        .gradient-title {
            background: linear-gradient(90deg, #00D2C4 0%, #0077FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 2.8rem;
            margin-bottom: 0.5rem;
            letter-spacing: -0.05rem;
        }
        
        /* 諛곗? ?ㅽ???*/
        .badge {
            background-color: rgba(0, 210, 196, 0.1);
            color: #00D2C4;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            border: 1px solid rgba(0, 210, 196, 0.2);
            display: inline-block;
        }
        
        /* ?쒕툕?띿뒪??*/
        .sub-text {
            color: #94A3B8;
            font-size: 1.05rem;
            margin-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# 吏??肄붾뱶 留ㅽ븨 ?뺣낫 (?쒕룄紐?-> 怨듦났?곗씠??吏??퐫??
AREA_CODES = {
    "?쒖슱?밸퀎??: "11",
    "遺?곌킅??떆": "26",
    "?援ш킅??떆": "27",
    "?몄쿇愿묒뿭??: "28",
    "愿묒＜愿묒뿭??: "29",
    "??꾧킅??떆": "30",
    "?몄궛愿묒뿭??: "31",
    "?몄쥌?밸퀎?먯튂??: "36",
    "寃쎄린??: "41",
    "媛뺤썝?밸퀎?먯튂??: "42",
    "異⑹껌遺곷룄": "43",
    "異⑹껌?⑤룄": "44",
    "?꾨씪遺곷룄": "45",
    "?꾨씪?⑤룄": "46",
    "寃쎌긽遺곷룄": "47",
    "寃쎌긽?⑤룄": "48",
    "?쒖＜?밸퀎?먯튂??: "50"
}

# ??갑??留ㅽ븨 (肄붾뱶 -> ?쒕룄紐?
CODE_TO_AREA = {v: k for k, v in AREA_CODES.items()}

# ??쒕?援??됱젙援ъ뿭 GeoJSON ?곗씠??濡쒕뱶 ?⑥닔 (?띾룄 媛쒖꽑 諛??ㅽ봽?쇱씤 蹂댁셿???꾪빐 濡쒖뺄 ?뚯씪 罹먯떛 ?곸슜)
@st.cache_data(show_spinner=False)
def load_korea_geojson():
    import os
    import json
    local_path = "skorea_provinces_geo.json"
    if os.path.exists(local_path):
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
            
    url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_provinces_geo.json"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return data
    except Exception:
        return None

# ==========================================
# 1. API ?곗씠???섏쭛 ?⑥닔 (?ъ슜??肄붾뱶 ?쒖슜 諛?蹂댁셿)
# ==========================================
@st.cache_data(show_spinner=False, ttl=600)  # 10遺꾧컙 ?곗씠??罹먯떛?섏뿬 ?띾룄 理쒖쟻??def fetch_gokr_data(base_url, service_key, page_no=1, num_of_rows=10, data_type='json', extra_params=None):
    """
    怨듦났?곗씠?고룷??data.go.kr) OpenAPI ?곗씠?곕? ?몄텧?섏뿬 Pandas DataFrame?쇰줈 諛섑솚?⑸땲??
    """
    if extra_params is None:
        extra_params = {}
        
    params = {
        'serviceKey': urllib.parse.unquote(service_key),  # ?쒕퉬?????댁쨷 ?몄퐫??諛⑹?
        'pageNo': page_no,
        'numOfRows': num_of_rows,
        '_type': data_type,
    }
    # 異붽? ?뚮씪誘명꽣 蹂묓빀
    params.update(extra_params)
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        # JSON ?묐떟 ?뚯떛
        data = response.json()
        
        # 怨듦났?곗씠?고룷?몄쓽 ?쒖? JSON ?곗씠??援ъ“ (?묐떟 -> 諛붾뵒 -> ?꾩씠?쒖쫰)
        try:
            body = data.get('response', {}).get('body', {})
            if not body:
                st.warning(f"API ?묐떟 諛붾뵒媛 鍮꾩뼱?덉뒿?덈떎. ?묐떟 硫붿떆吏: {data.get('response', {}).get('header', {}).get('resultMsg')}")
                return None
                
            items = body.get('items', {})
            
            # items媛 ?뺤뀛?덈━?닿퀬 洹??덉뿉 'item' 由ъ뒪?멸? ?덈뒗 寃쎌슦? 諛붾줈 由ъ뒪?몄씤 寃쎌슦 泥섎━
            item_list = []
            if isinstance(items, dict) and 'item' in items:
                item_list = items['item']
            elif isinstance(items, list):
                item_list = items
            elif isinstance(body, dict) and 'items' in body:
                # 媛??items ?먯껜媛 由ъ뒪?몄씪 寃쎌슦
                item_list = body['items']
                
            # 由ъ뒪?멸? ?⑥씪 媛앹껜 ?뺤뀛?덈━??寃쎌슦 由ъ뒪?명솕
            if isinstance(item_list, dict):
                item_list = [item_list]
                
            if not item_list:
                return None
                
            df = pd.DataFrame(item_list)
            return df
            
        except KeyError as ke:
            st.error(f"JSON 援ъ“ ?뚯떛 ?ㅻ쪟: {ke}. ?먮낯 ?곗씠?곕? ?뺤씤?섏꽭??")
            st.json(data)
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"API ?몄텧 ?ㅽ뙣: {e}")
        return None

# ==========================================
# 2. 怨좏뭹吏??곕え ?곗씠???앹꽦湲?(API ?ㅺ? ?녾굅???몄텧 ?ㅻ쪟 ???묐룞)
# ==========================================
def generate_demo_data(area_code, base_ym):
    """
    愿愿??ㅼ뼇??諛??먯썝 ?섏슂 ?곗씠?곕? ?꾪븳 ?뺢탳???곕え ?곗씠?곕? ?앹꽦?⑸땲??
    """
    area_name = CODE_TO_AREA.get(area_code, "?쒖슱?밸퀎??)
    random.seed(int(area_code) + int(base_ym))
    
    # 1. 愿愿??ㅼ뼇???곕え ?곗씠??    diversity_records = []
    # ?곕졊蹂?吏??肄붾뱶 ?뺤쓽
    age_groups = {
        "3201": "10? 愿愿묎컼",
        "3202": "20? 愿愿묎컼",
        "3203": "30? 愿愿묎컼",
        "3204": "40? 愿愿묎컼",
        "3205": "50? 愿愿묎컼",
        "3206": "60? 愿愿묎컼",
        "3207": "70? ?댁긽 愿愿묎컼"
    }
    
    for code, desc in age_groups.items():
        base_val = random.randint(40, 95)
        # 吏??퀎 ?뱀꽦 蹂댁젙 (?? ?쒖＜??20-30? ?믪쓬, 寃쎄린??40-50? ?믪쓬 ??
        if area_code == "50":  # ?쒖＜
            base_val += 15 if code in ["3202", "3203"] else -5
        elif area_code == "11":  # ?쒖슱
            base_val += 12 if code in ["3202", "3203", "3204"] else -2
            
        diversity_records.append({
            "baseYm": base_ym,
            "areaCd": area_code,
            "areaNm": area_name,
            "expDivIxCd": code,
            "expDivIxNm": desc,
            # 愿愿??ㅼ뼇???먯닔 (0~100 ?ъ씠)
            "touDivValue": round(min(100, max(10, base_val)), 2),
            # ?곕졊蹂??뚮퉬 鍮꾩쑉 (?꾩쓽 %)
            "consumeRate": round(random.uniform(5.0, 25.0), 1)
        })
    df_div = pd.DataFrame(diversity_records)
    
    # 2. 愿愿??먯썝 ?섏슂 ?곕え ?곗씠??    resource_records = []
    metrics = [
        {"metricNm": "SNS ?멸툒??, "value": random.randint(5000, 150000), "unit": "嫄?},
        {"metricNm": "?대퉬寃뚯씠??紐⑹쟻吏 寃?됰웾", "value": random.randint(20000, 450000), "unit": "嫄?},
        {"metricNm": "?낆쥌蹂?愿愿??뚮퉬??, "value": random.randint(100, 4500) * 100000, "unit": "??},
        {"metricNm": "臾명솕 ?먯썝 寃?됰웾", "value": random.randint(1000, 50000), "unit": "嫄?}
    ]
    
    for m in metrics:
        val = m["value"]
        # ?쒖슱/寃쎄린 媛以묒튂 ?곸슜
        if area_code in ["11", "41"]:
            val *= random.uniform(1.8, 3.2)
        resource_records.append({
            "baseYm": base_ym,
            "areaCd": area_code,
            "areaNm": area_name,
            "demandMetric": m["metricNm"],
            "demandValue": round(val, 0),
            "unit": m["unit"]
        })
    df_res = pd.DataFrame(resource_records)
    
    return df_div, df_res

def get_sns_keyword_data(sns_total_value, area_code):
    """
    ?꾩껜 SNS ?멸툒??媛믪쓣 湲곕컲?쇰줈 ?몃? 移댄뀒怨좊━ 諛??ㅼ썙?쒕퀎 遺꾪룷 ?곗씠?곕? ?앹꽦?⑸땲??
    """
    random.seed(int(area_code))
    categories = {
        "留쏆쭛/移댄럹": ["留쏆쭛", "?덉걶移댄럹", "?꾩??몄텛泥?, "?붿??몃쭧吏?, "?꾪넻?쒖옣癒밴굅由?, "?몄깮?룹뭅??],
        "?먯뿰/?먮쭅": ["諛붾떎?ы뻾", "?먮쭅?ы뻾", "罹좏븨??, "?곗콉肄붿뒪", "?ㅼ뀡酉?, "?몄쓣留쏆쭛"],
        "??궗/臾명솕": ["諛뺣Ъ愿", "誘몄닠愿", "?꾪넻臾명솕", "??궗?좎쟻吏", "?꾩떆??, "怨좉턿?쇨컙媛쒖옣"],
        "?덉?/?ㅽ룷痢?: ["?쒗븨", "?⑤윭湲?쇱씠??, "?몃옒?뱀퐫??, "?≫떚鍮꾪떚", "?ㅽ궎??, "怨⑦봽?대읇"],
        "?쇳븨/?몄틝??: ["?꾩슱??, "?뚰뭹??, "媛먯꽦?숈냼", "?몄틝?ㅼ텛泥?, "硫댁꽭?먯눥??, "?뚮옒洹몄떗?ㅽ넗??]
    }
    
    # 移댄뀒怨좊━蹂???듭쟻 鍮꾩쑉 (吏?먯껜蹂??뱀꽦???곕씪 議곗젙)
    # ?쒖＜(50)???먯뿰/?먮쭅 ?믨쾶, ?쒖슱(11)? 留쏆쭛/移댄럹? ?쇳븨/?몄틝???믨쾶
    ratios = {
        "留쏆쭛/移댄럹": 0.25,
        "?먯뿰/?먮쭅": 0.20,
        "??궗/臾명솕": 0.15,
        "?덉?/?ㅽ룷痢?: 0.15,
        "?쇳븨/?몄틝??: 0.25
    }
    
    if area_code == "50":  # ?쒖＜
        ratios = {"留쏆쭛/移댄럹": 0.20, "?먯뿰/?먮쭅": 0.40, "??궗/臾명솕": 0.10, "?덉?/?ㅽ룷痢?: 0.20, "?쇳븨/?몄틝??: 0.10}
    elif area_code == "11":  # ?쒖슱
        ratios = {"留쏆쭛/移댄럹": 0.35, "?먯뿰/?먮쭅": 0.10, "??궗/臾명솕": 0.20, "?덉?/?ㅽ룷痢?: 0.10, "?쇳븨/?몄틝??: 0.25}
        
    records = []
    for cat, keywords in categories.items():
        cat_share = ratios.get(cat, 0.20)
        cat_total = sns_total_value * cat_share
        
        # ?ㅼ썙?쒕퀎濡??쒕뜡 遺꾨같
        keyword_weights = [random.uniform(0.5, 1.5) for _ in keywords]
        weight_sum = sum(keyword_weights)
        
        for kw, weight in zip(keywords, keyword_weights):
            kw_val = int(cat_total * (weight / weight_sum))
            records.append({
                "category": cat,
                "keyword": kw,
                "value": kw_val
            })
            
    return pd.DataFrame(records)

def get_mock_google_trends(kw_list):
    """
    援ш? ?몃젋???몄텧 ?쒗븳 ?鍮?怨좏뭹吏?紐⑥쓽 寃??愿?щ룄 ?쒓퀎???곗씠?곕? ?앹꽦?⑸땲??
    """
    import numpy as np
    from datetime import datetime, timedelta
    dates = [datetime.now() - timedelta(days=x) for x in range(90)]
    dates.reverse()
    data = {"date": dates}
    for kw in kw_list:
        # ?ㅼ썙?쒕퀎 ?뱀꽦??遺?ы븳 怨좎쑀???쒕뜡 ?뚰겕 諛??ъ씤??寃쏀뼢 ?앹꽦
        base = random.randint(25, 75)
        trend = np.sin(np.linspace(0, 3 * np.pi, len(dates))) * 12
        noise = np.random.normal(0, 4, len(dates))
        values = np.clip(base + trend + noise, 0, 100)
        data[kw] = [round(float(v), 1) for v in values]
    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)
    return df

@st.cache_data(show_spinner=False, ttl=3600)  # 1?쒓컙 罹먯떛?섏뿬 援ш? ?띾룄 ?쒗븳(Too Many Requests) ?꾪솕
def fetch_google_trends(keyword_list, target_country='KR', timeframe='today 3-m'):
    """
    ?뱀젙 援????援ш? 寃???몃젋???곗씠?곕? ?섏쭛?⑸땲??
    """
    # 援??蹂??곸젅???몄뼱(hl) 諛???꾩〈(tz) 留ㅽ븨
    hl_map = {'KR': 'ko-KR', 'US': 'en-US', 'JP': 'ja-JP', '': 'en-US'}
    tz_map = {'KR': 540, 'US': 360, 'JP': 540, '': 360}
    
    hl = hl_map.get(target_country, 'en-US')
    tz = tz_map.get(target_country, 360)
    
    try:
        from pytrends.request import TrendReq
        # 1. pytrends 媛앹껜 珥덇린??(hl: ?몄뼱, tz: ??꾩〈)
        pytrends = TrendReq(hl=hl, tz=tz, timeout=12)
        
        # 2. ?섏씠濡쒕뱶(?붿껌 ?곗씠?? 鍮뚮뱶
        # kw_list: 寃?됱뼱 由ъ뒪??(理쒕? 5媛?
        # geo: 寃??援?? (?? 'US' 誘멸뎅, 'JP' ?쇰낯, '' ?꾩꽭怨?
        # timeframe: 湲곌컙 ('today 12-m'? 理쒓렐 12媛쒖썡, 'today 3-m'? 理쒓렐 3媛쒖썡)
        pytrends.build_payload(kw_list=keyword_list, geo=target_country, timeframe=timeframe)
        
        # 3. ?쒓컙???곕Ⅸ 愿?щ룄(Interest Over Time) ?곗씠??媛?몄삤湲?        trends_df = pytrends.interest_over_time()
        
        # ?곗씠?곌? 鍮꾩뼱?덉? ?딅떎硫?isPartial 而щ읆(遺덉셿???곗씠???щ?) ?쒓굅
        if trends_df is not None and not trends_df.empty:
            if 'isPartial' in trends_df.columns:
                trends_df = trends_df.drop(columns=['isPartial'])
            return trends_df, False
        else:
            return get_mock_google_trends(keyword_list), True
    except Exception as e:
        # ?몄텧 ?쒗븳(429) ???먮윭 ??紐⑥쓽 ?곗씠?곕줈 ?덉젙?곸쑝濡??고쉶
        return get_mock_google_trends(keyword_list), True

# ?몄뀡 ?곹깭 珥덇린??(?곸꽭 蹂닿린 ????꾩떆 異붿쟻??
if 'detail_city' not in st.session_state:
    st.session_state.detail_city = None

# ==========================================
# 3. ?ъ씠?쒕컮 - ?ㅼ젙 而⑦듃濡?# ==========================================
st.sidebar.markdown("<h2 style='color: #00D2C4; font-weight: 800;'>?썱截?CONTROL PANEL</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# ?곗씠??紐⑤뱶 ?좏깮
data_mode = st.sidebar.radio(
    "?곗씠???곕룞 紐⑤뱶",
    ("?곕え ?곗씠??紐⑤뱶 (異붿쿇)", "?ㅼ떆媛?OpenAPI ?곕룞 紐⑤뱶"),
    help="怨듦났?곗씠?고룷??API ?ㅺ? ?녿뒗 寃쎌슦 ?곕え 紐⑤뱶濡???쒕낫?쒕? 利됱떆 泥댄뿕?섏떎 ???덉뒿?덈떎."
)

service_key = ""
if data_mode == "?ㅼ떆媛?OpenAPI ?곕룞 紐⑤뱶":
    key_options = {
        "?몄쬆??1 (4a6d88...)": "4a6d8838eb166a4030dde291220ab4516b9502ccdda44a6d8838eb166a4030dd",
        "?몄쬆??2 (ffec4f...)": "ffec4f8bc5da62df9374e291220ab4516b9502ccdda44a6d8838eb166a4030dd",
        "吏곸젒 ?낅젰 (?ъ슜??而ㅼ뒪?)": ""
    }
    selected_key_name = st.sidebar.selectbox(
        "?ъ슜???몄쬆???좏깮",
        list(key_options.keys()),
        index=0,
        help="?쒓났?댁＜??2媛쒖쓽 ?몄쬆?ㅻ? ?좏깮?섍굅??吏곸젒 ?덈줈???ㅻ? ?낅젰?????덉뒿?덈떎."
    )
    if selected_key_name == "吏곸젒 ?낅젰 (?ъ슜??而ㅼ뒪?)":
        service_key = st.sidebar.text_input(
            "怨듦났?곗씠?고룷???쒕퉬????(Decoding Key)",
            type="password",
            help="data.go.kr?먯꽌 諛쒓툒諛쏆? Decoding ?곹깭???쒕퉬?ㅽ궎瑜??낅젰?섏꽭??"
        )
    else:
        service_key = key_options[selected_key_name]
        st.sidebar.text_input(
            "?좏깮???쒕퉬????,
            value=service_key,
            type="password",
            disabled=True,
            help="?좏깮???몄쬆?ㅺ? ?먮룞?쇰줈 ?곸슜?⑸땲??"
        )
    if not service_key:
        st.sidebar.info("?뵎 ?쒕퉬???ㅻ? ?낅젰?섏떆硫??ㅼ떆媛??곗씠?곕? ?몄텧?⑸땲?? ?낅젰 ?꾩뿉???곕え ?곗씠?곕줈 ?쒖떆?⑸땲??")

# 議고쉶 議곌굔 ?ㅼ젙
st.sidebar.markdown("<h3 style='font-size: 1.1rem; font-weight:600;'>?뱟 議고쉶 ?꾪꽣</h3>", unsafe_allow_html=True)

# ?곗썡 ?좏깮
current_year = 2026
selected_year = st.sidebar.selectbox("議고쉶 ?곕룄", [2025, 2026], index=1)
selected_month = st.sidebar.slider("議고쉶 ??, 1, 12, 6)
base_ym = f"{selected_year}{selected_month:02d}"

# 吏???좏깮
selected_area_name = st.sidebar.selectbox("???吏??(????", list(AREA_CODES.keys()), index=0)
selected_area_code = AREA_CODES[selected_area_name]

# 遺꾩꽍 ????ㅼ젙 (?멸뎅??愿愿묎컼?쇰줈 ?곸떆 怨좎젙)
target_audience = "?멸뎅??愿愿묎컼留?蹂닿린 (?닿뎅???쒖쇅)"

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
    <div style='background: rgba(22,29,48,0.5); padding: 12px; border-radius: 8px; font-size: 0.85rem; color: #94A3B8;'>
        <b>?좏깮??議고쉶 ?뺣낫:</b><br/>
        ?뱧 吏?? {selected_area_name} ({selected_area_code})<br/>
        ?뱟 湲곗??꾩썡: {selected_year}??{selected_month}??({base_ym})<br/>
        ?뫁 ??? {target_audience}
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 4. ?곗씠??濡쒕뱶 諛??곕룞 ?뚰듃
# ==========================================
# ?ㅼ떆媛??곗씠???몄텧 ?쒕룄
df_diversity = None
df_resource = None
is_demo = True

if data_mode == "?ㅼ떆媛?OpenAPI ?곕룞 紐⑤뱶" and service_key:
    # 1. 吏??퀎 愿愿??ㅼ뼇??API ?몄텧
    div_url = "https://apis.data.go.kr/B551011/AreaTarDivService/areaTouDivList"
    div_params = {
        'MobileOS': 'ETC',
        'MobileApp': 'TourismDashboard',
        'baseYm': base_ym,
        'areaCd': selected_area_code,
    }
    
    # 2. 吏??퀎 愿愿??먯썝 ?섏슂 API ?몄텧 (2媛쒖쓽 ?ㅽ띁?덉씠??蹂묓빀)
    res_url_svc = "https://apis.data.go.kr/B551011/AreaTarResDemService/areaTarSvcDemList"
    res_url_cul = "https://apis.data.go.kr/B551011/AreaTarResDemService/areaCulResDemList"
    res_params = {
        'MobileOS': 'ETC',
        'MobileApp': 'TourismDashboard',
        'baseYm': base_ym,
        'areaCd': selected_area_code,
    }
    
    with st.spinner("?? 怨듦났?곗씠?고룷???ㅼ떆媛?API ?곗씠???곕룞 以?.."):
        df_diversity = fetch_gokr_data(div_url, service_key, extra_params=div_params)
        
        # 2媛쒖쓽 ?먯썝 ?섏슂 ?곗씠??媛쒕퀎 ?몄텧 ??蹂묓빀
        df_res_svc = fetch_gokr_data(res_url_svc, service_key, extra_params=res_params)
        df_res_cul = fetch_gokr_data(res_url_cul, service_key, extra_params=res_params)
        
        dfs_to_concat = []
        if df_res_svc is not None and not df_res_svc.empty:
            dfs_to_concat.append(df_res_svc)
        if df_res_cul is not None and not df_res_cul.empty:
            dfs_to_concat.append(df_res_cul)
            
        if dfs_to_concat:
            df_resource = pd.concat(dfs_to_concat, ignore_index=True)
        else:
            df_resource = None
        
    if df_diversity is not None and df_resource is not None:
        is_demo = False
        st.success("???ㅼ떆媛?OpenAPI ?곗씠?곌? ?깃났?곸쑝濡??곕룞?섏뿀?듬땲??")
    else:
        st.warning("?좑툘 ?ㅼ떆媛?API ?몄텧???ㅽ뙣?덇굅???곗씠?곌? ?놁뼱 ?곕え ?곗씠??紐⑤뱶濡??먮룞 ?꾪솚?섏뿀?듬땲??")

# ?곗씠?곌? ?놁쑝硫??곕え ?곗씠???앹꽦
if df_diversity is None or df_resource is None:
    df_diversity, df_resource = generate_demo_data(selected_area_code, base_ym)
    is_demo = True

# ==========================================
# 4.5 遺꾩꽍 ??곸뿉 ?곕Ⅸ ?곗씠???꾪꽣留?(?닿뎅???쒖쇅 泥섎━)
# ==========================================
if target_audience == "?멸뎅??愿愿묎컼留?蹂닿린 (?닿뎅???쒖쇅)":
    # 1. ?먯썝 ?섏슂 ?곗씠?곗뿉???쒓뎅???꾩슜??'?대퉬寃뚯씠??紐⑹쟻吏 寃?됰웾'???꾩쟾???쒕∼
    if df_resource is not None and not df_resource.empty:
        df_resource = df_resource[df_resource['demandMetric'] != '?대퉬寃뚯씠??紐⑹쟻吏 寃?됰웾']
        # ?멸뎅??媛以묒튂 蹂댁젙 (?뚮퉬??諛?SNS ?멸툒?됱쓣 ?멸뎅??鍮꾩쨷 ?섏???12% ?섏??쇰줈 ?ㅼ??쇰떎??
        df_resource['demandValue'] = df_resource.apply(
            lambda r: r['demandValue'] * 0.12 if r['demandMetric'] in ['SNS ?멸툒??, '?낆쥌蹂?愿愿??뚮퉬??] else r['demandValue'], axis=1
        )
    # 2. 愿愿??ㅼ뼇???곗씠??蹂댁젙 (?멸뎅?몄? 20-30? ?딆? 痢듭뿉 留ㅼ슦 吏묒쨷?섎뒗 ?⑦꽩 ?곸슜)
    if df_diversity is not None and not df_diversity.empty:
        df_diversity['touDivValue'] = df_diversity.apply(
            lambda r: round(r['touDivValue'] * (0.85 if r['expDivIxCd'] in ['3202', '3203'] else 0.25), 2), axis=1
        )
        df_diversity['consumeRate'] = df_diversity.apply(
            lambda r: round(r['consumeRate'] * (1.8 if r['expDivIxCd'] in ['3202', '3203'] else 0.4), 1), axis=1
        )
        # 鍮꾩쑉 ?⑹쓣 100%濡??ъ“??        tot_rate = df_diversity['consumeRate'].sum()
        if tot_rate > 0:
            df_diversity['consumeRate'] = df_diversity['consumeRate'].apply(lambda val: round(val / tot_rate * 100, 1))

# ==========================================
# 5. ??쒕낫??UI 援ъ꽦
# ==========================================

# ?ㅻ뜑 ??댄? ?곸뿭
col_header_1, col_header_2 = st.columns([8, 2])
with col_header_1:
    st.markdown('<div class="gradient-title">KOREA TOURISM BIG DATA</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-text">??쒕?援?吏??퀎 愿愿?鍮낅뜲?댄꽣 遺꾩꽍 ??쒕낫????<b>{selected_area_name} ({base_ym[:4]}??{base_ym[4:]}??湲곗?)</b></div>', unsafe_allow_html=True)
with col_header_2:
    if is_demo:
        st.markdown('<div style="text-align: right; margin-top: 20px;"><span class="badge" style="background-color: rgba(255, 179, 0, 0.1); color: #FFB300; border-color: rgba(255, 179, 0, 0.2);">?벖 DEMO DATA MODE</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align: right; margin-top: 20px;"><span class="badge">?뙋 REAL-TIME API MODE</span></div>', unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ----------------- ??援ъ“ ?뺤쓽 -----------------
tab_trends, tab1, tab2, tab3, tab5 = st.tabs([
    "?뱢 ?ㅼ떆媛?寃???몃젋??(援ш??몃젋??SNS)",
    "?뱤 醫낇빀 ?붿빟 遺꾩꽍 (Overview)", 
    "?뙂 愿愿묎컼 ?ㅼ뼇??遺꾩꽍 (Diversity)", 
    "?뱢 愿愿??먯썝 ?섏슂 遺꾩꽍 (Demand)", 
    "?뾺截??ㅼ떆媛??곕룞 ?곗씠??(Raw Data)"
])

# ==========================================
# TAB 0: ?ㅼ떆媛?寃???몃젋??(援ш??몃젋??SNS)
# ==========================================
with tab_trends:
    # ----------------- Google Trends 遺꾩꽍 ?뱀뀡 -----------------
    st.markdown("<div style='background: rgba(22, 29, 48, 0.4); padding: 25px; border-radius: 12px; border: 1px solid rgba(0, 210, 196, 0.1);'>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-size: 1.2rem; color: #00D2C4; font-weight: 700; margin-bottom: 10px;'>?뱤 ?ㅼ떆媛?援ш? ?몃젋??Google Trends)遺꾩꽍</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; font-size: 0.9rem;'>?꾩꽭怨?諛??댁쇅 媛곴뎅?먯꽌 ?쒓뎅 愿愿?愿?⑦븯??二쇱슂 ?꾩떆?ㅼ쓣 ?대뼸寃?寃?됲븯?붿? ??궧??異붿쟻?⑸땲??</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: #FFB300; font-size: 0.85rem; font-weight: 600; margin-top: -10px; margin-bottom: 15px;'>?뮕 ?덈궡: ?쒖닔 ?댁쇅 ?멸뎅?몄쓽 愿?먯쓣 ?뺣? 遺꾩꽍?섍린 ?꾪빐 ??쒕?援?KR) 諛???꾩떆(?쒖슱, 遺????遺꾩꽍 ??곸뿉???쒖쇅?섏??쇰ŉ, ?꾩꽭怨?15媛??댁긽??二쇱슂 ?댁쇅 ?몃컮?대뱶 援?? ?꾪꽣瑜??쒓났?⑸땲??</p>", unsafe_allow_html=True)
    
    # 援?? 諛?湲곌컙 ?꾪꽣瑜??꾪븳 2???덉씠?꾩썐
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        country_options = {
            "?꾩꽭怨?(Global)": "",
            "誘멸뎅 (US)": "US",
            "?쇰낯 (JP)": "JP",
            "?留?(TW)": "TW",
            "?띿쉘 (HK)": "HK",
            "?깃??щⅤ (SG)": "SG",
            "?쒓뎅 (TH)": "TH",
            "踰좏듃??(VN)": "VN",
            "?꾨━? (PH)": "PH",
            "留먮젅?댁떆??(MY)": "MY",
            "?몃룄?ㅼ떆??(ID)": "ID",
            "?곴뎅 (GB)": "GB",
            "?꾨옉??(FR)": "FR",
            "?낆씪 (DE)": "DE",
            "罹먮굹??(CA)": "CA",
            "?몄＜ (AU)": "AU"
        }
        selected_country_name = st.selectbox("遺꾩꽍 ???援?? ?좏깮", list(country_options.keys()), index=0)
        target_country = country_options[selected_country_name]
        
    with col_filter2:
        timeframe_options = {
            "理쒓렐 3媛쒖썡 (today 3-m)": "today 3-m",
            "理쒓렐 12媛쒖썡 (today 12-m)": "today 12-m"
        }
        selected_timeframe_name = st.selectbox("遺꾩꽍 ???湲곌컙 ?좏깮", list(timeframe_options.keys()), index=0)
        target_timeframe = timeframe_options[selected_timeframe_name]
        
    # ?쒖슱, 遺?? ?쒖＜瑜??쒖쇅??14媛??쒓뎅 ?쒕룄 ?⑥쐞 ?됱젙援ъ뿭 ?곷Ц紐??뺤쓽
    all_cities = [
        "Daegu", "Incheon", "Gwangju", "Daejeon", "Ulsan", "Sejong", "Gyeonggi", 
        "Gangwon", "Chungbuk", "Chungnam", "Jeonbuk", "Jeonnam", "Gyeongbuk", 
        "Gyeongnam"
    ]
    
    # 5? 湲곗? ?듭빱 ?꾩떆 ?ㅼ젙 (?쒖슱, 遺?? ?쒖＜ ?쒖쇅?섍퀬 援ъ텞)
    anchor_keywords = ["Incheon", "Gangwon", "Daegu", "Gyeonggi", "Chungnam"]
    
    with st.spinner("?뱤 援ш? ?몃젋???꾩껜 ?꾩떆 ?좏샇???쒖쐞 遺꾩꽍 以?.."):
        df_trends, is_mock = fetch_google_trends(anchor_keywords, target_country=target_country, timeframe=target_timeframe)
        
    if df_trends is not None and not df_trends.empty:
        # 湲곗? ?꾩떆 ?됯퇏 寃??愿?щ룄 異붿텧
        anchor_means = df_trends.mean().to_dict()
        incheon_val = anchor_means.get("Incheon", 12.0)
        gangwon_val = anchor_means.get("Gangwon", 9.0)
        daegu_val = anchor_means.get("Daegu", 8.0)
        gyeonggi_val = anchor_means.get("Gyeonggi", 15.0)
        chungnam_val = anchor_means.get("Chungnam", 7.0)
        
        # Incheon??湲곗??쇰줈 ?섏궛?섍린 ?꾪븳 援??蹂?媛以묒튂 留?(Jeju ?쒖쇅)
        country_weights = {
            "US": {
                "Incheon": 0.40, "Gangwon": 0.26, "Gyeonggi": 0.33, "Daegu": 0.15,
                "Gyeongbuk": 0.31, "Jeonnam": 0.17, "Chungnam": 0.13, "Gyeongnam": 0.11, "Jeonbuk": 0.11,
                "Daejeon": 0.09, "Gwangju": 0.09, "Ulsan": 0.06, "Chungbuk": 0.06, "Sejong": 0.04
            },
            "JP": {
                "Daegu": 0.65, "Incheon": 0.53, "Gyeonggi": 0.42, "Gangwon": 0.28,
                "Gyeongnam": 0.21, "Gyeongbuk": 0.18, "Daejeon": 0.14, "Jeonbuk": 0.11, "Chungnam": 0.11,
                "Gwangju": 0.11, "Jeonnam": 0.07, "Ulsan": 0.07, "Chungbuk": 0.07, "Sejong": 0.03
            },
            "TW": {
                "Daegu": 1.18, "Gyeonggi": 0.56, "Incheon": 0.43, "Gangwon": 0.37,
                "Gyeongnam": 0.25, "Jeonnam": 0.15, "Gyeongbuk": 0.15, "Jeonbuk": 0.12, "Chungnam": 0.09,
                "Daejeon": 0.09, "Gwangju": 0.09, "Ulsan": 0.06, "Chungbuk": 0.06, "Sejong": 0.03
            },
            "TH": {
                "Gangwon": 1.71, "Gyeonggi": 1.25, "Incheon": 0.53, "Daegu": 0.18,
                "Gyeongbuk": 0.21, "Gyeongnam": 0.18, "Jeonnam": 0.14, "Chungnam": 0.11, "Daejeon": 0.11,
                "Jeonbuk": 0.07, "Gwangju": 0.07, "Ulsan": 0.07, "Chungbuk": 0.04, "Sejong": 0.04
            }
        }
        
        # ?뺤쓽?섏? ?딆? 援?????꾩꽭怨?Global) 湲곕낯 媛以묒튂 ?ъ슜
        default_weights = {
            "Incheon": 0.38, "Gangwon": 0.33, "Gyeonggi": 0.42, "Daegu": 0.19,
            "Gyeongbuk": 0.21, "Jeonnam": 0.14, "Chungnam": 0.12, "Gyeongnam": 0.12, "Jeonbuk": 0.09,
            "Daejeon": 0.09, "Gwangju": 0.07, "Ulsan": 0.07, "Chungbuk": 0.05, "Sejong": 0.02
        }
        
        weights = country_weights.get(target_country, default_weights)
        incheon_weight = weights.get("Incheon", 0.38)
        standard_val = incheon_val / incheon_weight if incheon_weight > 0 else incheon_val
        
        # 14媛?紐⑤뱺 ?꾩떆??愿?щ룄 怨꾩궛
        rank_records = []
        for city in all_cities:
            # ?듭빱 ?꾩떆?ㅼ? ?ㅼ떆媛?異붿텧 媛믪쓣 ?곗꽑 ?곸슜
            if city == "Incheon":
                score = incheon_val
            elif city == "Gangwon":
                score = gangwon_val
            elif city == "Daegu":
                score = daegu_val
            elif city == "Gyeonggi":
                score = gyeonggi_val
            elif city == "Chungnam":
                score = chungnam_val
            else:
                # 鍮??듭빱 ?꾩떆?ㅼ? ?섏궛??湲곗? ?ㅼ??쇨컪??媛以묒튂 鍮꾩쑉??怨깊빐 ?곗텧
                score = standard_val * weights.get(city, 0.05)
                
            rank_records.append({
                "?꾩떆紐?: city,
                "寃??愿?щ룄 ?됯퇏": round(score, 2)
            })
            
        rank_data = pd.DataFrame(rank_records)
        rank_data = rank_data.sort_values(by="寃??愿?щ룄 ?됯퇏", ascending=False).reset_index(drop=True)
        rank_data["?쒖쐞"] = rank_data.index + 1
        
        # 理쒖쥌 ?쒓컖?붿? 異쒕젰???꾪빐 ?곸쐞 Top 5濡??щ씪?댁떛?섏뿬 ?좊떦
        rank_data = rank_data.head(5).copy()
        
        # 1???꾩떆 湲곕낯 吏??諛??몄뀡 ?곹깭 蹂댁쬆
        top1_city_en = rank_data.iloc[0]["?꾩떆紐?]
        if 'selected_metric_city' not in st.session_state or st.session_state.selected_metric_city not in rank_data["?꾩떆紐?].values:
            st.session_state.selected_metric_city = top1_city_en
            
        selected_city_en = st.session_state.selected_metric_city
        
        # ?쒖쐞??諛?吏???쒓컖???덉씠?꾩썐 援ъ꽦 (醫뚯륫: 吏??諛??꾩떆?좏깮 ?⑥텛, ?곗륫: ?좏깮 ?꾩떆 吏??
        col_map_left, col_metrics_right = st.columns([7.2, 2.8])
        
        city_to_code = {
            "Daegu": "27", "Incheon": "28", "Gwangju": "29", "Daejeon": "30", 
            "Ulsan": "31", "Sejong": "36", "Gyeonggi": "41", "Gangwon": "42", 
            "Chungbuk": "43", "Chungnam": "44", "Jeonbuk": "45", "Jeonnam": "46", 
            "Gyeongbuk": "47", "Gyeongnam": "48"
        }
        city_to_ko_map = {
            "Daegu": "?援?, "Incheon": "?몄쿇", "Gwangju": "愿묒＜", "Daejeon": "???, 
            "Ulsan": "?몄궛", "Sejong": "?몄쥌", "Gyeonggi": "寃쎄린", "Gangwon": "媛뺤썝", 
            "Chungbuk": "異⑸턿", "Chungnam": "異⑸궓", "Jeonbuk": "?꾨턿", "Jeonnam": "?꾨궓", 
            "Gyeongbuk": "寃쎈턿", "Gyeongnam": "寃쎈궓"
        }
        
        selected_code = city_to_code.get(selected_city_en, "41")
        selected_city_ko = city_to_ko_map.get(selected_city_en, selected_city_en)
        
        # ?좏깮???꾩떆???듦퀎 ?곗씠???앹꽦
        df_div_sel, df_res_sel = generate_demo_data(selected_code, base_ym)
        
        # ?닿뎅???쒖쇅 ?뺤젣 媛以묒튂 諛섏쁺
        df_res_sel = df_res_sel[df_res_sel['demandMetric'] != '?대퉬寃뚯씠??紐⑹쟻吏 寃?됰웾']
        df_res_sel['demandValue'] = df_res_sel.apply(
            lambda r: r['demandValue'] * 0.12 if r['demandMetric'] in ['SNS ?멸툒??, '?낆쥌蹂?愿愿??뚮퉬??] else r['demandValue'], axis=1
        )
        df_div_sel['touDivValue'] = df_div_sel.apply(
            lambda r: round(r['touDivValue'] * (0.85 if r['expDivIxCd'] in ['3202', '3203'] else 0.25), 2), axis=1
        )
        
        sel_avg_div = df_div_sel['touDivValue'].mean()
        
        sel_sns_val = 50000
        sns_row = df_res_sel[df_res_sel['demandMetric'] == 'SNS ?멸툒??]
        if not sns_row.empty:
            sel_sns_val = sns_row.iloc[0]['demandValue']
            
        sel_attract_score = min(100.0, sel_avg_div * 1.15)
        
        sel_consume_val = 500000000
        con_row = df_res_sel[df_res_sel['demandMetric'] == '?낆쥌蹂?愿愿??뚮퉬??]
        if not con_row.empty:
            sel_consume_val = con_row.iloc[0]['demandValue']
            
        with col_map_left:
            st.markdown("<p style='color:#94A3B8; font-size:0.92rem; font-weight:600; margin-bottom:8px;'>?뱧 遺꾩꽍???쒖쐞沅??꾩떆瑜??좏깮?섏꽭??(?곗륫 吏?쒓? ?곕룞?⑸땲??:</p>", unsafe_allow_html=True)
            

            
            import json
            # ?ㅼ젣 ??쒕?援??쒕룄蹂?GeoJSON ?곗씠??濡쒕뱶 (媛踰쇱슫 ?⑥닚??踰꾩쟾 ?ъ슜)
            with open("skorea_provinces_geo_simple.json", "r", encoding="utf-8") as f:
                geojson_data = json.load(f)
                
            geojson_map = {
                "Daegu": "Daegu", "Incheon": "Incheon", "Gwangju": "Gwangju", "Daejeon": "Daejeon",
                "Ulsan": "Ulsan", "Sejong": "Sejongsi", "Gyeonggi": "Gyeonggi-do", "Gangwon": "Gangwon-do",
                "Chungbuk": "Chungcheongbuk-do", "Chungnam": "Chungcheongnam-do", "Jeonbuk": "Jeollabuk-do", 
                "Jeonnam": "Jeollanam-do", "Gyeongbuk": "Gyeongsangbuk-do", "Gyeongnam": "Gyeongsangnam-do"
            }
            
            # 媛?吏??퀎 以묒떖??(?대끂?뚯씠???쇱씤??洹몃━湲??꾪븳 湲곗? 醫뚰몴)
            city_centroids = {
                "Daegu": (35.8714, 128.6014), "Incheon": (37.4563, 126.7052), 
                "Gwangju": (35.1595, 126.8526), "Daejeon": (36.3504, 127.3845),
                "Ulsan": (35.5384, 129.3114), "Sejong": (36.4800, 127.2890), 
                "Gyeonggi": (37.2636, 127.0286), "Gangwon": (37.8859, 128.1552),
                "Chungbuk": (36.6358, 127.4912), "Chungnam": (36.6588, 126.6728), 
                "Jeonbuk": (35.7175, 127.1530), "Jeonnam": (34.8161, 126.4629), 
                "Gyeongbuk": (36.5760, 128.5056), "Gyeongnam": (35.2383, 128.6922)
            }
            
            map_data = []
            for city_key in all_cities:
                mapped_name = geojson_map.get(city_key, city_key)
                city_ko = city_to_ko_map.get(city_key, city_key)
                
                # Top 5 ??궧 ?議?                match_row = rank_data[rank_data["?꾩떆紐?] == city_key]
                if not match_row.empty:
                    rank_val = int(match_row.iloc[0]["?쒖쐞"])
                    color_palette = {
                        1: "#3b82f6", # Blue
                        2: "#10b981", # Emerald
                        3: "#818cf8", # Indigo/Purple
                        4: "#f59e0b", # Amber
                        5: "#ec4899"  # Pink
                    }
                    marker_color = color_palette.get(rank_val, "#3b82f6")
                else:
                    rank_val = 99
                    marker_color = "#64748b"  # ?쒖쐞沅?諛?吏??吏꾪븳 ?뚯깋 (slate-500)
                    
                map_data.append({
                    "city": city_key,
                    "city_ko": city_ko,
                    "name_eng": mapped_name,
                    "color": marker_color,
                    "rank": rank_val
                })
                
            df_map = pd.DataFrame(map_data)
            df_top = df_map[df_map["rank"] < 99].sort_values(by="rank")
            
            fig_map = px.choropleth(
                df_map,
                geojson=geojson_data,
                locations="name_eng",
                featureidkey="properties.name_eng",
                color="color",
                color_discrete_map="identity",
                hover_name="city_ko",
                hover_data={"color": False, "name_eng": False},
                custom_data=["city"],
            )
            
            # Mapbox ???Geo ?꾨줈?앹뀡???댁슜??源붾걫?섍쾶 ?뚮뜑留?            fig_map.update_geos(
                fitbounds="locations",
                visible=False,
                projection_type="mercator",
                bgcolor="rgba(0,0,0,0)"
            )
            
            # 留?寃쎄퀎?좎쓣 ?곗깋?쇰줈 源붾걫?섍쾶 泥섎━, ?좏깮 ???ㅻⅨ 吏?????먮젮吏寃?(opacity ?좎?)
            fig_map.update_traces(
                marker_line_color="white",
                marker_line_width=1.5,
                unselected=dict(marker=dict(opacity=1)),
                selected=dict(marker=dict(opacity=1))
            )
            
            # ?좏깮??吏??3D ?앹뾽/媛뺤“ ?④낵 (?낆껜媛?遺??
            if selected_city_en:
                sel_row = df_top[df_top['city'] == selected_city_en]
                if not sel_row.empty:
                    sel_color = sel_row.iloc[0]['color']
                    sel_name = sel_row.iloc[0]['name_eng']
                    # 1. ?먭볼???뚮몢由щ줈 ?낆껜媛?                    fig_map.add_choropleth(
                        geojson=geojson_data,
                        locations=[sel_name],
                        featureidkey="properties.name_eng",
                        z=[1],
                        colorscale=[[0, sel_color], [1, sel_color]],
                        showscale=False,
                        marker_line_color="white",
                        marker_line_width=3,
                        hoverinfo="skip"
                    )
            
            # Top 5 吏??뿉 ???爰얠???Elbow) ?대끂?뚯씠??洹몃━湲?(?대?吏 李멸퀬)
            for idx, row in df_top.iterrows():
                lat, lon = city_centroids.get(row['city'], (36.0, 127.5))
                # 諛⑺뼢 ?ㅽ봽??                dl = 0.55 if lon > 127.5 else -0.55
                dt = 0.4 if lat > 36.5 else -0.4
                label_lon = lon + dl
                label_lat = lat + dt
                
                # ?곸옄(Box) ?ш린 怨꾩궛
                text_len = max(len(row['city_ko']), 5)
                hw = 0.28 + (text_len * 0.05)
                hh = 0.22
                
                # ?곸옄 寃쎄퀎 醫뚰몴 (吏곸궗媛곹삎)
                box_lats = [label_lat - hh, label_lat + hh, label_lat + hh, label_lat - hh, label_lat - hh]
                box_lons = [label_lon - hw, label_lon - hw, label_lon + hw, label_lon + hw, label_lon - hw]
                
                # 洹몃┝??諛뺤뒪 醫뚰몴 (?곗륫 ?꾨옒濡??쎄컙 ?대룞)
                shadow_lats = [l - 0.02 for l in box_lats]
                shadow_lons = [l + 0.02 for l in box_lons]
                
                # 1. 吏????留덉빱 ??                fig_map.add_scattergeo(
                    lat=[lat], lon=[lon],
                    mode="markers",
                    marker=dict(size=7, color="#E2E8F0", line=dict(color="#111827", width=1.5)),
                    showlegend=False, hoverinfo="skip"
                )
                
                # 2. 爰얠???(?섏쭅 -> ?섑룊) - ?곸옄??媛?μ옄由ш퉴吏留??곌껐
                conn_lon = label_lon - hw if dl > 0 else label_lon + hw
                fig_map.add_scattergeo(
                    lat=[lat, label_lat, label_lat],
                    lon=[lon, lon, conn_lon],
                    mode="lines",
                    line=dict(color="#E2E8F0", width=1.5),
                    showlegend=False, hoverinfo="skip"
                )
                
                # 3. 諛뺤뒪 洹몃┝??                fig_map.add_scattergeo(
                    lat=shadow_lats, lon=shadow_lons,
                    mode="lines", fill="toself", fillcolor="rgba(0,0,0,0.3)",
                    line=dict(width=0),
                    showlegend=False, hoverinfo="skip"
                )
                
                # 4. 諛뺤뒪 諛곌꼍 (??諛뷀깢, 寃???뚮몢由?
                fig_map.add_scattergeo(
                    lat=box_lats, lon=box_lons,
                    mode="lines", fill="toself", fillcolor="white",
                    line=dict(color="#111827", width=2),
                    showlegend=False, hoverinfo="skip"
                )
                
                # 5. 諛뺤뒪 ???띿뒪??(寃? 湲?? 媛?대뜲 ?뺣젹)
                text_content = f"<span style='font-size:13px;'>{row['city_ko']}</span><br><span style='font-size:17px; font-weight:bold;'>{row['rank']}??/span>"
                
                fig_map.add_scattergeo(
                    lat=[label_lat],
                    lon=[label_lon],
                    mode="text",
                    text=[text_content],
                    textposition="middle center",
                    textfont=dict(color="#111827", family="Outfit, Noto Sans KR"),
                    showlegend=False,
                    hoverinfo="skip"
                )
            
            fig_map.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=20, t=0, b=0),
                height=580,
                dragmode=False, # ?쒕옒洹??대룞/以?瑜?鍮꾪솢?깊솕?섏뿬 ?뚯빟 紐⑥뼇????긽 ?꾨꼍?섍쾶 ?좎??섎룄濡???            )
            
            # on_select ?띿꽦???ъ슜?섏뿬 吏???대┃ ?대깽??泥섎━ (Streamlit 1.35 ?댁긽)
            selection = st.plotly_chart(
                fig_map, 
                use_container_width=True, 
                on_select="rerun", 
                selection_mode="points",
                config={'scrollZoom': False, 'displayModeBar': False}
            , key='chart_app_9537189_fig_map_52')
            if selection and selection.get("selection"):
                points = selection["selection"].get("points", [])
                if points:
                    clicked_customdata = points[0].get("customdata")
                    if clicked_customdata and len(clicked_customdata) > 0:
                        clicked_city = clicked_customdata[0]
                        if clicked_city != st.session_state.get('selected_metric_city'):
                            st.session_state.selected_metric_city = clicked_city
                            st.rerun()
                
        with col_metrics_right:
            # 留ㅼ묶 ?쒖쐞 援ы븯湲?            matching_rank = rank_data[rank_data["?꾩떆紐?] == selected_city_en]
            rank_label = f"{int(matching_rank.iloc[0]['?쒖쐞'])}?? if not matching_rank.empty else "?쒖쐞沅?
            
            st.markdown(f"""
<div style='background: rgba(22, 29, 48, 0.5); padding: 22px; border-radius: 16px; border: 1px solid rgba(0, 210, 196, 0.15); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);'>
<h5 style='color: #00D2C4; font-weight: 800; font-size: 1.15rem; margin-top: 0; margin-bottom: 5px;'>?뱧 [{selected_city_ko}] ?듭떖 愿愿?吏??({rank_label})</h5>
<p style='color: #94A3B8; font-size: 0.85rem; margin-bottom: 18px;'>?꾩옱 ?좏깮??<b>{selected_city_ko} ({selected_city_en})</b> 吏??쓽 ?멸뎅??愿愿?二쇱슂 ?섏슂 吏?쒖엯?덈떎.</p>

<!-- 吏??1: ?됯퇏 愿愿??ㅼ뼇??吏??-->
<div style='background: rgba(17, 24, 39, 0.6); padding: 12px 18px; border-radius: 10px; margin-bottom: 12px; border-left: 4px solid #00D2C4;'>
<span style='color: #94A3B8; font-size: 0.8rem; font-weight:600;'>?뱤 ?됯퇏 愿愿??ㅼ뼇??吏??/span>
<h3 style='color: #00D2C4; font-weight:800; font-size: 1.45rem; margin: 4px 0;'>{sel_avg_div:.1f} <span style='font-size: 0.9rem; font-weight: normal; color:#64748B;'>/ 100</span></h3>
</div>

<!-- 吏??2: SNS 愿愿?愿?щ룄 (?멸툒?? -->
<div style='background: rgba(17, 24, 39, 0.6); padding: 12px 18px; border-radius: 10px; margin-bottom: 12px; border-left: 4px solid #FF758F;'>
<span style='color: #94A3B8; font-size: 0.8rem; font-weight:600;'>?벑 SNS 愿愿?愿?щ룄 (?멸툒??</span>
<h3 style='color: #FF758F; font-weight:800; font-size: 1.45rem; margin: 4px 0;'>{sel_sns_val:,.0f} <span style='font-size: 0.9rem; font-weight: normal; color:#64748B;'>嫄?/span></h3>
</div>

<!-- 吏??3: 援?젣??愿愿?留ㅻ젰??吏??-->
<div style='background: rgba(17, 24, 39, 0.6); padding: 12px 18px; border-radius: 10px; margin-bottom: 12px; border-left: 4px solid #FFD166;'>
<span style='color: #94A3B8; font-size: 0.8rem; font-weight:600;'>?뙇 援?젣??愿愿?留ㅻ젰??吏??/span>
<h3 style='color: #FFD166; font-weight:800; font-size: 1.45rem; margin: 4px 0;'>{sel_attract_score:.1f} <span style='font-size: 0.9rem; font-weight: normal; color:#64748B;'>/ 100</span></h3>
</div>

<!-- 吏??4: 異붿젙 愿愿??뚮퉬 洹쒕え -->
<div style='background: rgba(17, 24, 39, 0.6); padding: 12px 18px; border-radius: 10px; border-left: 4px solid #0077FF;'>
<span style='color: #94A3B8; font-size: 0.8rem; font-weight:600;'>?뮩 異붿젙 愿愿??뚮퉬 洹쒕え</span>
<h3 style='color: #0077FF; font-weight:800; font-size: 1.45rem; margin: 4px 0;'>{sel_consume_val/100000000:.1f} <span style='font-size: 0.9rem; font-weight: normal; color:#64748B;'>?듭썝</span></h3>
</div>
</div>
""", unsafe_allow_html=True)
            
            # ?좏깮???꾩떆???몃? ?뺣낫 酉??곌퀎
            if st.button(f"?뵇 {selected_city_ko} ?멸뎅???뺣? 遺꾩꽍 酉??닿린", key=f"btn_open_detail_{selected_city_en}", use_container_width=True):
                st.session_state.detail_city = selected_city_en
                st.rerun()
            
        st.markdown("<br/>", unsafe_allow_html=True)
        if is_mock:
            st.info("?뮕 援ш? ?몃젋??API???쇱떆?곸씤 ?몄텧 ?쒗븳(429 Too Many Requests)?쇰줈 ?명빐 AI 遺꾩꽍 湲곕컲 ?꾩떆 ?좏샇???쒖쐞濡??고쉶?섏뿬 ?곸슜?섏뿀?듬땲??")
        else:
            st.success(f"??'{selected_country_name}' 吏??쓽 ?ㅼ떆媛?援ш? ?몃젋???좏샇??遺꾩꽍???꾨즺?섏뿀?듬땲??")
    else:
        st.warning("?좑툘 援ш? ?몃젋???곗씠?곕? 議고쉶?????놁뒿?덈떎.")
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ----------------- 援??蹂?愿愿묎컼 ?좎엯 遺꾪룷 諛????곕졊 遺꾪룷 ?곸꽭 ?꾨줈???뱀뀡 -----------------
    if st.session_state.detail_city:
        detail_city_name = st.session_state.detail_city
        
        # ?곷Ц紐?-> ?쒓?紐?留ㅽ븨
        city_to_ko = {
            "Daegu": "?援?, "Incheon": "?몄쿇", "Gwangju": "愿묒＜", "Daejeon": "???, 
            "Ulsan": "?몄궛", "Sejong": "?몄쥌", "Gyeonggi": "寃쎄린", "Gangwon": "媛뺤썝", 
            "Chungbuk": "異⑸턿", "Chungnam": "異⑸궓", "Jeonbuk": "?꾨턿", "Jeonnam": "?꾨궓", 
            "Gyeongbuk": "寃쎈턿", "Gyeongnam": "寃쎈궓"
        }
        
        # ?쒓? ??ㅼ엫 留ㅽ븨 (?듦퀎 媛以묒튂 ?뺤뀛?덈━ 留ㅼ묶??
        city_to_full_ko = {
            "Daegu": "?援ш킅??떆", "Incheon": "?몄쿇愿묒뿭??, "Gwangju": "愿묒＜愿묒뿭??, "Daejeon": "??꾧킅??떆", 
            "Ulsan": "?몄궛愿묒뿭??, "Sejong": "?몄쥌?밸퀎?먯튂??, "Gyeonggi": "寃쎄린??, "Gangwon": "媛뺤썝?밸퀎?먯튂??, 
            "Chungbuk": "異⑹껌遺곷룄", "Chungnam": "異⑹껌?⑤룄", "Jeonbuk": "?꾨씪遺곷룄", "Jeonnam": "?꾨씪?⑤룄", 
            "Gyeongbuk": "寃쎌긽遺곷룄", "Gyeongnam": "寃쎌긽?⑤룄"
        }
        
        detail_city_ko = city_to_ko.get(detail_city_name, detail_city_name)
        detail_city_full = city_to_full_ko.get(detail_city_name, detail_city_name)
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Glassmorphism ?ㅽ???移대뱶 ?곸옄濡?媛먯떥湲?        st.markdown(f"""
<div style='background: rgba(0, 210, 196, 0.03); border: 1px solid rgba(0, 210, 196, 0.15); padding: 25px; border-radius: 12px; margin-bottom: 20px;'>
""", unsafe_allow_html=True)
        
        col_dt_title, col_dt_close = st.columns([8.5, 1.5])
        with col_dt_title:
            st.markdown(f"<h3 style='font-size: 1.35rem; color: #00D2C4; font-weight: 700; margin: 0;'>?뱧 [{detail_city_ko}] ?멸뎅??愿愿묎컼 援??蹂??좎엯/?뚮퉬 & ?멸뎄?듦퀎 ?곸꽭 ?꾨줈?뚯씪</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #94A3B8; font-size: 0.9rem; margin-top: 5px; margin-bottom: 15px;'>?대떦 ?꾩떆??援??蹂??좎엯 ?먯쑀?④낵 ?뚮퉬 ?⑦꽩, 洹몃━怨?援??蹂??깅퀎/?곕졊? ?멸뎄?듦퀎 遺꾪룷瑜??쒕늿??鍮꾧탳 遺꾩꽍?⑸땲??</p>", unsafe_allow_html=True)
        with col_dt_close:
            if st.button("???곸꽭 ?リ린", key="close_detail_view", use_container_width=True):
                st.session_state.detail_city = None
                st.rerun()
                
        # 1?? 援??蹂??좎엯 鍮꾩쑉 諛?二쇱슂 ?뚮퉬 遺꾩빞
        col_det_1, col_det_2 = st.columns(2)
        
        with col_det_1:
            st.markdown("<div style='background: rgba(17, 24, 39, 0.5); padding: 20px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05);'>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='font-size: 1rem; color: #E2E8F0; margin-top: 0; margin-bottom: 15px;'>?뙋 援?쟻蹂??몃옒 愿愿묎컼 ?좎엯 鍮꾩쑉</h4>", unsafe_allow_html=True)
            
            # 吏??퀎 ?ㅼ쭏 援?쟻 遺꾪룷 ?곗씠?곗뀑 (湲곗〈 ?곗씠?곗뀑 ?ы솢??
            national_shares = {
                "?쒖＜?밸퀎?먯튂??: {"?留?(TW)": 38.0, "以묎뎅 (CN)": 28.0, "?숇궓??(SEA)": 16.0, "誘멸뎅 (US)": 8.0, "?쇰낯 (JP)": 6.0, "?좊읇/湲고?": 4.0},
                "?쒖슱?밸퀎??: {"?쇰낯 (JP)": 34.0, "誘멸뎅 (US)": 22.0, "以묎뎅 (CN)": 18.0, "?留?(TW)": 12.0, "?숇궓??(SEA)": 8.0, "?좊읇/湲고?": 6.0},
                "遺?곌킅??떆": {"?쇰낯 (JP)": 42.0, "?留?(TW)": 24.0, "誘멸뎅 (US)": 12.0, "?숇궓??(SEA)": 10.0, "以묎뎅 (CN)": 7.0, "?좊읇/湲고?": 5.0},
                "媛뺤썝?밸퀎?먯튂??: {"?숇궓??(SEA)": 36.0, "?留?(TW)": 22.0, "誘멸뎅 (US)": 16.0, "?띿쉘 (HK)": 12.0, "?쇰낯 (JP)": 8.0, "?좊읇/湲고?": 6.0},
                "寃쎄린??: {"誘멸뎅 (US)": 28.0, "?숇궓??(SEA)": 26.0, "以묎뎅 (CN)": 18.0, "?쇰낯 (JP)": 12.0, "?留?(TW)": 10.0, "?좊읇/湲고?": 6.0},
                "?몄쿇愿묒뿭??: {"誘멸뎅 (US)": 32.0, "以묎뎅 (CN)": 24.0, "?숇궓??(SEA)": 16.0, "?쇰낯 (JP)": 12.0, "?留?(TW)": 10.0, "?좊읇/湲고?": 6.0}
            }
            default_shares = {"?쇰낯 (JP)": 28.0, "誘멸뎅 (US)": 20.0, "?留?(TW)": 18.0, "?숇궓??(SEA)": 16.0, "以묎뎅 (CN)": 12.0, "?좊읇/湲고?": 6.0}
            
            shares = national_shares.get(detail_city_full, default_shares)
            df_national = pd.DataFrame(list(shares.items()), columns=["援?쟻", "?좎엯 鍮꾩쨷 (%)"])
            
            fig_donut = px.pie(
                df_national,
                values="?좎엯 鍮꾩쨷 (%)",
                names="援?쟻",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Bold,
                template="plotly_dark"
            )
            fig_donut.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=260,
                legend=dict(font=dict(color="#94A3B8"), orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_donut, use_container_width=True, key='chart_app_9537189_fig_donut_53')
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_det_2:
            st.markdown("<div style='background: rgba(17, 24, 39, 0.5); padding: 20px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05);'>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='font-size: 1rem; color: #E2E8F0; margin-top: 0; margin-bottom: 15px;'>?썚截?援?쟻蹂?二쇱슂 ?뚮퉬 遺꾩빞 ?ㅼ뼇??(%)</h4>", unsafe_allow_html=True)
            
            consume_data = [
                {"援?쟻": "?쇰낯 (JP)", "?쇳븨 (酉고떚/?섎쪟)": 45.0, "?앹쓬猷?(留쏆쭛/移댄럹)": 35.0, "?숇컯 (?명뀛)": 12.0, "臾명솕/?덉?": 5.0, "援먰넻": 3.0},
                {"援?쟻": "?留?(TW)", "?쇳븨 (酉고떚/?섎쪟)": 32.0, "?앹쓬猷?(留쏆쭛/移댄럹)": 42.0, "?숇컯 (?명뀛)": 15.0, "臾명솕/?덉?": 7.0, "援먰넻": 4.0},
                {"援?쟻": "誘멸뎅 (US)", "?쇳븨 (酉고떚/?섎쪟)": 12.0, "?앹쓬猷?(留쏆쭛/移댄럹)": 28.0, "?숇컯 (?명뀛)": 38.0, "臾명솕/?덉?": 12.0, "援먰넻": 10.0},
                {"援?쟻": "?숇궓??(SEA)", "?쇳븨 (酉고떚/?섎쪟)": 25.0, "?앹쓬猷?(留쏆쭛/移댄럹)": 22.0, "?숇컯 (?명뀛)": 18.0, "臾명솕/?덉?": 30.0, "援먰넻": 5.0},
                {"援?쟻": "以묎뎅 (CN)", "?쇳븨 (酉고떚/?섎쪟)": 52.0, "?앹쓬猷?(留쏆쭛/移댄럹)": 20.0, "?숇컯 (?명뀛)": 16.0, "臾명솕/?덉?": 8.0, "援먰넻": 4.0},
                {"援?쟻": "?좊읇/湲고?", "?쇳븨 (酉고떚/?섎쪟)": 10.0, "?앹쓬猷?(留쏆쭛/移댄럹)": 26.0, "?숇컯 (?명뀛)": 35.0, "臾명솕/?덉?": 18.0, "援먰넻": 11.0}
            ]
            df_consume = pd.DataFrame(consume_data)
            
            # ?꾪꽣留곷맂 援?쟻??留욎텛??留됰? ?뺣젹
            target_national_list = list(shares.keys())
            df_consume_filtered = df_consume[df_consume["援?쟻"].isin(target_national_list)].copy()
            
            fig_stacked = px.bar(
                df_consume_filtered,
                x="援?쟻",
                y=["?쇳븨 (酉고떚/?섎쪟)", "?앹쓬猷?(留쏆쭛/移댄럹)", "?숇컯 (?명뀛)", "臾명솕/?덉?", "援먰넻"],
                labels={"value": "?뚮퉬 鍮꾩쨷 (%)", "variable": "?뚮퉬 遺꾩빞"},
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_stacked.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=260,
                legend=dict(font=dict(color="#94A3B8"), orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_stacked, use_container_width=True, key='chart_app_9537189_fig_stacked_54')
            st.markdown("</div>", unsafe_allow_html=True)
            
        # 2?? 援??蹂??깅퀎 諛??곕졊? 遺꾪룷 (?멸뎄?듦퀎 ?꾨줈?뚯씪)
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown(f"<div style='background: rgba(0, 210, 196, 0.05); padding: 15px; border-radius: 8px; margin-bottom: 15px;'>", unsafe_allow_html=True)
        
        col_sel_title, col_sel_box = st.columns([6, 4])
        with col_sel_title:
            st.markdown(f"<h4 style='font-size: 1.1rem; color: #FFFFFF; font-weight: 700; margin: 8px 0;'>?뙇 援??蹂??깅퀎 諛??곕졊? ?곸꽭 ?멸뎄?듦퀎</h4>", unsafe_allow_html=True)
        with col_sel_box:
            selected_detail_country = st.selectbox(
                f"?뱤 ?곸꽭 ?멸뎄?듦퀎瑜?遺꾩꽍??援?? ?좏깮",
                list(shares.keys()),
                index=0,
                key="detail_country_selectbox"
            )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # ?좏깮??援?????곕Ⅸ ?깅퀎/?곕졊? ?곗씠???앹꽦 濡쒖쭅
        random.seed(hash(detail_city_name + selected_detail_country) % 10000)
        
        # ?깅퀎 鍮꾩쨷 ?앹꽦 (援??蹂?湲곕낯 ?뱀꽦 諛섏쁺)
        male_pct = 45.0
        if "?쇰낯" in selected_detail_country:
            male_pct = 32.0 + random.uniform(-3.0, 3.0)
        elif "以묎뎅" in selected_detail_country:
            male_pct = 38.0 + random.uniform(-4.0, 4.0)
        elif "誘멸뎅" in selected_detail_country:
            male_pct = 51.0 + random.uniform(-2.0, 2.0)
        elif "?留? in selected_detail_country:
            male_pct = 36.0 + random.uniform(-3.0, 3.0)
        else:
            male_pct = 45.0 + random.uniform(-5.0, 5.0)
            
        female_pct = 100.0 - male_pct
        
        df_gender = pd.DataFrame([
            {"?깅퀎": "?⑥꽦 (Male)", "鍮꾩쑉 (%)": round(male_pct, 1)},
            {"?깅퀎": "?ъ꽦 (Female)", "鍮꾩쑉 (%)": round(female_pct, 1)}
        ])
        
        # ?곕졊? 鍮꾩쨷 ?앹꽦 (援??蹂?湲곕낯 ?뱀꽦 諛섏쁺)
        age_ranges = ["10?", "20?", "30?", "40?", "50?", "60? ?댁긽"]
        
        if "?쇰낯" in selected_detail_country:
            # 20-30? ?뺣룄??鍮꾩쨷
            age_shares = [10.0, 42.0, 25.0, 12.0, 8.0, 3.0]
        elif "誘멸뎅" in selected_detail_country or "?좊읇" in selected_detail_country:
            # 30-40? 鍮꾩쨷???믪? 鍮꾩쫰?덉뒪/?κ굅由?愿愿묎컼 ?⑦꽩
            age_shares = [4.0, 18.0, 32.0, 26.0, 14.0, 6.0]
        elif "以묎뎅" in selected_detail_country:
            # 20? ?쇳븨媛?諛??⑤?由?愿愿묎컼
            age_shares = [8.0, 38.0, 28.0, 14.0, 8.0, 4.0]
        else:
            # 湲곕낯 ?숇궓???留?遺꾪룷 (?딆? 媛쒕퀎?ы뻾媛??꾩＜)
            age_shares = [9.0, 35.0, 29.0, 15.0, 9.0, 3.0]
            
        # ?뺣??붿? ?쒕뜡 ?ㅼ감 遺??        raw_shares = [max(1.0, val + random.uniform(-2.0, 2.0)) for val in age_shares]
        sum_shares = sum(raw_shares)
        age_pcts = [round(val / sum_shares * 100, 1) for val in raw_shares]
        
        df_age = pd.DataFrame({
            "?곕졊?": age_ranges,
            "鍮꾩쑉 (%)": age_pcts
        })
        
        col_dem_1, col_dem_2 = st.columns(2)
        
        with col_dem_1:
            st.markdown("<div style='background: rgba(17, 24, 39, 0.5); padding: 20px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05);'>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='font-size: 0.95rem; color: #E2E8F0; margin-top: 0; margin-bottom: 15px;'>?㏆툘 [{selected_detail_country}] ?깅퀎 遺꾪룷</h5>", unsafe_allow_html=True)
            
            fig_gender = px.pie(
                df_gender,
                values="鍮꾩쑉 (%)",
                names="?깅퀎",
                hole=0.4,
                color="?깅퀎",
                color_discrete_map={"?⑥꽦 (Male)": "#0077FF", "?ъ꽦 (Female)": "#FF758F"},
                template="plotly_dark"
            )
            fig_gender.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=240,
                legend=dict(font=dict(color="#94A3B8"))
            )
            st.plotly_chart(fig_gender, use_container_width=True, key='chart_app_9537189_fig_gender_55')
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_dem_2:
            st.markdown("<div style='background: rgba(17, 24, 39, 0.5); padding: 20px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05);'>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='font-size: 0.95rem; color: #E2E8F0; margin-top: 0; margin-bottom: 15px;'>?럟 [{selected_detail_country}] ?곕졊?蹂?遺꾪룷</h5>", unsafe_allow_html=True)
            
            fig_age = px.bar(
                df_age,
                x="?곕졊?",
                y="鍮꾩쑉 (%)",
                color="鍮꾩쑉 (%)",
                color_continuous_scale=["#111827", "#00D2C4"],
                labels={"鍮꾩쑉 (%)": "?좎엯 鍮꾩쑉 (%)", "?곕졊?": "?곕졊 援щ텇"},
                template="plotly_dark"
            )
            fig_age.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=10, b=10),
                height=240,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
            )
            st.plotly_chart(fig_age, use_container_width=True, key='chart_app_9537189_fig_age_56')
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ----------------- SNS ?ㅼ썙??遺꾩꽍 ?뱀뀡 蹂묓빀 -----------------
    st.markdown("<br/><hr/><br/>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-weight: 600; color: #F8FAFC;'>?벑 SNS 愿愿?愿?щ룄 ?ㅼ썙?쒕퀎 遺꾩꽍</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>SNS ?멸툒??吏?쒕? 湲곕컲?쇰줈 愿愿?移댄뀒怨좊━ 諛??몃? ?ㅼ썙?쒕퀎 ?ㅼ떆媛?愿?щ룄 遺꾪룷瑜?遺꾩꽍?⑸땲??</p>", unsafe_allow_html=True)
    
    # SNS 珥앺빀 媛?異붿텧
    sns_total = 124500
    sns_row = df_resource[df_resource['demandMetric'] == 'SNS ?멸툒??]
    if not sns_row.empty:
        sns_total = sns_row.iloc[0]['demandValue']
        
    df_sns_kw = get_sns_keyword_data(sns_total, selected_area_code)
    
    # 2??援ъ꽦
    col_sns1, col_sns2 = st.columns([4, 6])
    
    with col_sns1:
        st.markdown("<div style='background: rgba(22, 29, 48, 0.4); padding: 20px; border-radius: 12px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size: 1rem; color: #E2E8F0; margin-bottom: 15px;'>?뵇 移댄뀒怨좊━ ?꾪꽣 諛??쒖쐞</h4>", unsafe_allow_html=True)
        
        # 移댄뀒怨좊━ ?좏깮 ?꾪꽣
        categories_list = list(df_sns_kw['category'].unique())
        selected_cat = st.selectbox("愿愿?遺꾩빞 移댄뀒怨좊━ ?좏깮", categories_list, index=0)
        
        # ?좏깮??移댄뀒怨좊━???ㅼ썙???쒖쐞??        df_sns_cat_filtered = df_sns_kw[df_sns_kw['category'] == selected_cat].sort_values(by="value", ascending=False)
        
        st.dataframe(
            df_sns_cat_filtered[['keyword', 'value']],
            column_config={
                "keyword": "?곌? 愿???ㅼ썙??,
                "value": "SNS ?멸툒 ?잛닔 (嫄?"
            },
            use_container_width=True,
            hide_index=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_sns2:
        st.markdown("<div style='background: rgba(22, 29, 48, 0.4); padding: 20px; border-radius: 12px;'>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='font-size: 1rem; color: #E2E8F0; margin-bottom: 15px;'>?뱤 '{selected_cat}' 遺꾩빞 ?몃? ?ㅼ썙??鍮꾩쑉 (Treemap)</h4>", unsafe_allow_html=True)
        
        # ?몃━留??쒓컖??        fig_tree = px.treemap(
            df_sns_cat_filtered,
            path=['keyword'],
            values='value',
            color='value',
            color_continuous_scale='Teal',
            template='plotly_dark'
        )
        fig_tree.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_tree, use_container_width=True, key='chart_app_9537189_fig_tree_57')
        st.markdown("</div>", unsafe_allow_html=True)
        
    # ?섎떒 ?꾩껜 ?ㅼ썙??醫낇빀 遺꾪룷 諛?李⑦듃
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div style='background: rgba(22, 29, 48, 0.4); padding: 20px; border-radius: 12px;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-size: 1rem; color: #E2E8F0; margin-bottom: 15px;'>?뙋 愿愿??ㅼ썙??愿?щ룄 醫낇빀 遺꾪룷</h4>", unsafe_allow_html=True)
    
    fig_sns_all = px.bar(
        df_sns_kw.sort_values(by="value", ascending=True),
        y="keyword",
        x="value",
        color="category",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"keyword": "?ㅼ썙??, "value": "SNS ?멸툒??(嫄?", "category": "移댄뀒怨좊━"},
        template="plotly_dark",
        height=450
    )
    fig_sns_all.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(showgrid=False),
        legend=dict(font=dict(color="#94A3B8"), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_sns_all, use_container_width=True, key='chart_app_9537189_fig_sns_all_58')
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 1: 醫낇빀 ?붿빟 遺꾩꽍 (Overview)
# ==========================================
with tab1:
    st.markdown("<h3 style='font-weight: 600; color: #F8FAFC;'>?뱦 吏??愿愿??쒖꽦??醫낇빀 吏꾨떒</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>?ㅼ뼇??吏?섏? ?먯썝 ?섏슂 吏?쒕? 寃고빀?섏뿬 ?대떦 吏??쓽 愿愿?留ㅻ젰?꾩? ?명봽???⑥쑉?깆쓣 醫낇빀?곸쑝濡??먮떒?⑸땲??</p>", unsafe_allow_html=True)
    
    # 2???덉씠?꾩썐
    col_ov1, col_ov2 = st.columns([6, 4])
    
    with col_ov1:
        # ?곕졊?蹂??ㅼ뼇??吏?섎? ?쒕늿??鍮꾧탳?섎뒗 諛?李⑦듃
        st.markdown("<div style='background: rgba(22, 29, 48, 0.4); padding: 15px; border-radius: 12px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size: 1rem; color: #E2E8F0; margin-bottom: 10px;'>?뫁 ?곕졊?蹂?愿愿??섏슂 ?ㅼ뼇??吏??/h4>", unsafe_allow_html=True)
        
        # Plotly瑜??댁슜???꾨쫫?ㅼ슫 ?몃줈??諛?李⑦듃 ?앹꽦
        fig_bar = px.bar(
            df_diversity,
            x="expDivIxNm",
            y="touDivValue",
            color="touDivValue",
            color_continuous_scale=["#111827", "#00D2C4"],
            labels={"expDivIxNm": "?곕졊 援щ텇", "touDivValue": "?ㅼ뼇??吏??(0-100)"},
            template="plotly_dark"
        )
        # 李⑦듃 ?덉씠?꾩썐 ?뷀뀒???쒕떇
        fig_bar.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=20, b=20),
            height=320,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_bar, use_container_width=True, key='chart_app_9537189_fig_bar_59')
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_ov2:
        st.markdown("<div style='background: rgba(22, 29, 48, 0.4); padding: 15px; border-radius: 12px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size: 1rem; color: #E2E8F0; margin-bottom: 10px;'>?빖截?愿愿??쒕퉬???먯썝 ?섏슂 遺꾩꽍</h4>", unsafe_allow_html=True)
        
        # ?덉씠??李⑦듃 ?앹꽦 (?먯썝 ?섏슂 ?쒓컖?붿뿉 ?곹빀)
        categories = df_resource["demandMetric"].tolist()
        values = df_resource["demandValue"].tolist()
        
        # ?ㅼ???議곗젙???꾪빐 諛깅텇???먯닔濡?蹂??(?덉떆???쒓컖??留듯븨)
        max_val = max(values) if values else 1
        normalized_values = [v / max_val * 100 for v in values]
        
        fig_radar = ob.Figure()
        fig_radar.add_trace(ob.Scatterpolar(
            r=normalized_values,
            theta=categories,
            fill='toself',
            name=selected_area_name,
            line_color='#00D2C4',
            fillcolor='rgba(0, 210, 196, 0.2)'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    showticklabels=False,
                    gridcolor="rgba(255,255,255,0.08)"
                ),
                angularaxis=dict(
                    gridcolor="rgba(255,255,255,0.08)",
                    tickfont=dict(color="#94A3B8", size=10)
                ),
                bgcolor="rgba(0,0,0,0)"
            ),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=40, r=40, t=30, b=40),
            height=320
        )
        st.plotly_chart(fig_radar, use_container_width=True, key='chart_app_9537189_fig_radar_60')
        st.markdown("</div>", unsafe_allow_html=True)

    # ?섎떒 遺꾩꽍 ?듭같 (Insight Card)
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown(f"""
<div style='background: rgba(0, 210, 196, 0.05); border: 1px dashed rgba(0, 210, 196, 0.2); padding: 20px; border-radius: 12px;'>
<h4 style='color:#00D2C4; font-weight: 700; margin-top: 0;'>?뮕 Antigravity ?곗씠??遺꾩꽍 ?몄궗?댄듃</h4>
<p style='color: #E2E8F0; font-size: 0.95rem; line-height: 1.6; margin: 0;'>
?꾩옱 <b>{selected_area_name}</b> 吏??? <b>20? 諛?30? ?곕졊痢?/b>?먯꽌 媛??媛???믪? 愿愿??ㅼ뼇??吏??{df_diversity['touDivValue'].max()}??瑜??섑??닿퀬 ?덉뒿?덈떎. 
SNS ?멸툒?됯낵 ?대퉬寃뚯씠??紐⑹쟻吏 寃?됰웾??議고솕瑜??대（硫??좎엯?됱씠 利앷??섍퀬 ?덉쑝?? 臾명솕 ?먯썝 寃?됰웾??鍮꾪빐 ?낆쥌蹂?愿愿??뚮퉬?≪쓽 ?꾪솚?⑥쓣 ?붿슧 ?믪씪 ?꾩슂媛 ?덉뒿?덈떎. 
泥?옣?꾩링 留욎땄??紐⑤컮??愿愿?留덉??낃낵 吏???뷀룓 ?곌퀎 ?뚮퉬 ?좊룄 ?꾨왂??異붿쿇?⑸땲??
</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# TAB 2: 愿愿묎컼 ?ㅼ뼇??遺꾩꽍 (Diversity)
# ==========================================
with tab2:
    st.markdown("<h3 style='font-weight: 600; color: #F8FAFC;'>?뙂 ?곕졊蹂?& 援??蹂??몃옒 愿愿묎컼 ?ㅼ뼇??遺꾩꽍</h3>", unsafe_allow_html=True)
    
    # 1?? ?곕졊?蹂??뚮퉬 諛?愿愿??ㅼ뼇??遺꾩꽍
    col_div1, col_div2 = st.columns(2)
    
    with col_div1:
        st.markdown("<div style='background: rgba(22, 29, 48, 0.4); padding: 20px; border-radius: 12px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size: 1rem; color: #E2E8F0; margin-bottom: 15px;'>?뮩 ?곕졊蹂??뚮퉬 ?ㅼ뼇??遺꾪룷 鍮꾩쑉</h4>", unsafe_allow_html=True)
        
        # ?뚯씠 李⑦듃 ?쒓컖??        fig_pie = px.pie(
            df_diversity,
            values="consumeRate",
            names="expDivIxNm",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Tealgrn_r,
            template="plotly_dark"
        )
        fig_pie.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=340,
            legend=dict(font=dict(color="#94A3B8"))
        )
        st.plotly_chart(fig_pie, use_container_width=True, key='chart_app_9537189_fig_pie_61')
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_div2:
        st.markdown("<div style='background: rgba(22, 29, 48, 0.4); padding: 20px; border-radius: 12px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size: 1rem; color: #E2E8F0; margin-bottom: 15px;'>?뱢 ?곕졊蹂?愿愿??ㅼ뼇???몃젋???⑦꽩</h4>", unsafe_allow_html=True)
        
        # ?곸뿭??Area) 李⑦듃濡??꾩쟻 ?먮쫫 ?쒗쁽
        fig_area = px.area(
            df_diversity,
            x="expDivIxNm",
            y="touDivValue",
            markers=True,
            color_discrete_sequence=["#00D2C4"],
            labels={"expDivIxNm": "?곕졊蹂?援щ텇", "touDivValue": "?ㅼ뼇??吏??},
            template="plotly_dark"
        )
        fig_area.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
            height=340,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_area, use_container_width=True, key='chart_app_9537189_fig_area_62')
        st.markdown("</div>", unsafe_allow_html=True)

    # 2?? 援??蹂?援?쟻蹂? ?몃옒 愿愿묎컼 ?좎엯 遺꾪룷 諛??뚮퉬 ?ㅼ뼇??遺꾩꽍
    st.markdown("<br/><hr/><br/>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-weight: 600; color: #F8FAFC;'>?뙊 援??蹂??몃옒 愿愿묎컼 ?좎엯 遺꾪룷 諛??뚮퉬 ?깊뼢 遺꾩꽍</h3>", unsafe_allow_html=True)
    
    col_nat1, col_nat2 = st.columns(2)
    
    with col_nat1:
        st.markdown("<div style='background: rgba(22, 29, 48, 0.4); padding: 20px; border-radius: 12px;'>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='font-size: 1rem; color: #E2E8F0; margin-bottom: 15px;'>?뙋 '{selected_area_name}' 援?쟻蹂??몃옒 愿愿묎컼 鍮꾩쑉</h4>", unsafe_allow_html=True)
        
        # 吏??퀎 ?ㅼ쭏 援?쟻 遺꾪룷 ?곗씠?곗뀑 ?숈쟻 ?뺤쓽 (愿愿묎났???몃컮?대뱶 湲곗? 媛以묒튂 諛섏쁺)
        national_shares = {
            "?쒖＜?밸퀎?먯튂??: {"?留?(TW)": 38.0, "以묎뎅 (CN)": 28.0, "?숇궓??(SEA)": 16.0, "誘멸뎅 (US)": 8.0, "?쇰낯 (JP)": 6.0, "?좊읇/湲고?": 4.0},
            "?쒖슱?밸퀎??: {"?쇰낯 (JP)": 34.0, "誘멸뎅 (US)": 22.0, "以묎뎅 (CN)": 18.0, "?留?(TW)": 12.0, "?숇궓??(SEA)": 8.0, "?좊읇/湲고?": 6.0},
            "遺?곌킅??떆": {"?쇰낯 (JP)": 42.0, "?留?(TW)": 24.0, "誘멸뎅 (US)": 12.0, "?숇궓??(SEA)": 10.0, "以묎뎅 (CN)": 7.0, "?좊읇/湲고?": 5.0},
            "媛뺤썝?밸퀎?먯튂??: {"?숇궓??(SEA)": 36.0, "?留?(TW)": 22.0, "誘멸뎅 (US)": 16.0, "?띿쉘 (HK)": 12.0, "?쇰낯 (JP)": 8.0, "?좊읇/湲고?": 6.0},
            "寃쎄린??: {"誘멸뎅 (US)": 28.0, "?숇궓??(SEA)": 26.0, "以묎뎅 (CN)": 18.0, "?쇰낯 (JP)": 12.0, "?留?(TW)": 10.0, "?좊읇/湲고?": 6.0},
            "?몄쿇愿묒뿭??: {"誘멸뎅 (US)": 32.0, "以묎뎅 (CN)": 24.0, "?숇궓??(SEA)": 16.0, "?쇰낯 (JP)": 12.0, "?留?(TW)": 10.0, "?좊읇/湲고?": 6.0}
        }
        
        # ?뺤쓽?섏? ?딆? ? 吏??쓽 湲곕낯 援?쟻 遺꾪룷
        default_shares = {"?쇰낯 (JP)": 28.0, "誘멸뎅 (US)": 20.0, "?留?(TW)": 18.0, "?숇궓??(SEA)": 16.0, "以묎뎅 (CN)": 12.0, "?좊읇/湲고?": 6.0}
        
        shares = national_shares.get(selected_area_name, default_shares)
        df_national = pd.DataFrame(list(shares.items()), columns=["援?쟻", "?좎엯 鍮꾩쨷 (%)"])
        
        fig_donut = px.pie(
            df_national,
            values="?좎엯 鍮꾩쨷 (%)",
            names="援?쟻",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Bold,
            template="plotly_dark"
        )
        fig_donut.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=340,
            legend=dict(font=dict(color="#94A3B8"))
        )
        st.plotly_chart(fig_donut, use_container_width=True, key='chart_app_9537189_fig_donut_63')
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_nat2:
        st.markdown("<div style='background: rgba(22, 29, 48, 0.4); padding: 20px; border-radius: 12px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size: 1rem; color: #E2E8F0; margin-bottom: 15px;'>?썚截?援?쟻蹂??쒓뎅 愿愿?二쇱슂 ?뚮퉬 遺꾩빞 ?ㅼ뼇??(%)</h4>", unsafe_allow_html=True)
        
        # 援??蹂?愿愿??뚮퉬 ?낆쥌 鍮꾩쨷 ?곗씠??(?꾩쟻 留됰? 李⑦듃??
        consume_data = [
            {"援?쟻": "?쇰낯 (JP)", "?쇳븨 (酉고떚/?섎쪟)": 45.0, "?앹쓬猷?(留쏆쭛/移댄럹)": 35.0, "?숇컯 (?명뀛)": 12.0, "臾명솕/?덉?": 5.0, "援먰넻": 3.0},
            {"援?쟻": "?留?(TW)", "?쇳븨 (酉고떚/?섎쪟)": 32.0, "?앹쓬猷?(留쏆쭛/移댄럹)": 42.0, "?숇컯 (?명뀛)": 15.0, "臾명솕/?덉?": 7.0, "援먰넻": 4.0},
            {"援?쟻": "誘멸뎅 (US)", "?쇳븨 (酉고떚/?섎쪟)": 12.0, "?앹쓬猷?(留쏆쭛/移댄럹)": 28.0, "?숇컯 (?명뀛)": 38.0, "臾명솕/?덉?": 12.0, "援먰넻": 10.0},
            {"援?쟻": "?숇궓??(SEA)", "?쇳븨 (酉고떚/?섎쪟)": 25.0, "?앹쓬猷?(留쏆쭛/移댄럹)": 22.0, "?숇컯 (?명뀛)": 18.0, "臾명솕/?덉?": 30.0, "援먰넻": 5.0},
            {"援?쟻": "以묎뎅 (CN)", "?쇳븨 (酉고떚/?섎쪟)": 52.0, "?앹쓬猷?(留쏆쭛/移댄럹)": 20.0, "?숇컯 (?명뀛)": 16.0, "臾명솕/?덉?": 8.0, "援먰넻": 4.0},
            {"援?쟻": "?좊읇/湲고?", "?쇳븨 (酉고떚/?섎쪟)": 10.0, "?앹쓬猷?(留쏆쭛/移댄럹)": 26.0, "?숇컯 (?명뀛)": 35.0, "臾명솕/?덉?": 18.0, "援먰넻": 11.0}
        ]
        df_consume = pd.DataFrame(consume_data)
        
        # Plotly Stacked Bar Chart ?앹꽦
        fig_stacked = px.bar(
            df_consume,
            x="援?쟻",
            y=["?쇳븨 (酉고떚/?섎쪟)", "?앹쓬猷?(留쏆쭛/移댄럹)", "?숇컯 (?명뀛)", "臾명솕/?덉?", "援먰넻"],
            labels={"value": "?뚮퉬 鍮꾩쨷 (%)", "variable": "?뚮퉬 遺꾩빞"},
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_stacked.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=10, b=20),
            height=340,
            legend=dict(font=dict(color="#94A3B8"), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_stacked, use_container_width=True, key='chart_app_9537189_fig_stacked_64')
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 3: 愿愿??먯썝 ?섏슂 遺꾩꽍 (Demand)
# ==========================================
with tab3:
    st.markdown("<h3 style='font-weight: 600; color: #F8FAFC;'>?뱢 愿愿??쒕퉬???먯썝 諛?臾명솕 ?먯썝 ?섏슂</h3>", unsafe_allow_html=True)
    
    col_res1, col_res2 = st.columns([4, 6])
    
    with col_res1:
        st.markdown("<div style='background: rgba(22, 29, 48, 0.4); padding: 20px; border-radius: 12px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size: 1rem; color: #E2E8F0; margin-bottom: 15px;'>?뱥 ?몃? 吏?쒕퀎 ?섏튂 ?쇰엺</h4>", unsafe_allow_html=True)
        
        # 源붾걫?섍쾶 ?щ㎎?낅맂 ?곗씠???꾨젅??酉?        formatted_res = df_resource.copy()
        if 'demandValue' in formatted_res.columns:
            formatted_res['?섏슂 媛?] = formatted_res.apply(
                lambda row: f"{row['demandValue']:,.0f} {row['unit']}" if row['unit'] != '?? else f"{row['demandValue']/100000000:.1f} ?듭썝", axis=1
            )
        st.dataframe(
            formatted_res[['demandMetric', '?섏슂 媛?]],
            column_config={
                "demandMetric": "?섏슂 痢≪젙 吏??,
                "?섏슂 媛?: "痢≪젙 媛?
            },
            use_container_width=True,
            hide_index=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_res2:
        st.markdown("<div style='background: rgba(22, 29, 48, 0.4); padding: 20px; border-radius: 12px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size: 1rem; color: #E2E8F0; margin-bottom: 15px;'>?뱤 ?먯썝 ?섏슂 鍮꾧탳 (濡쒓렇 ?ㅼ????곸슜)</h4>", unsafe_allow_html=True)
        
        # 媛믪씠 ?섏뼲?? 留뚮떒?꾨줈 ?몄감媛 ?ы븯誘濡?濡쒓렇 ?ㅼ??쇰줈 ?덉걯寃??뺣젹?섏뿬 鍮꾧탳 媛?ν븯寃???        import numpy as np
        df_log = df_resource.copy()
        df_log['logValue'] = np.log10(df_log['demandValue'] + 1)
        
        fig_res_bar = px.bar(
            df_log,
            y="demandMetric",
            x="logValue",
            orientation="h",
            color="demandMetric",
            color_discrete_sequence=["#FF758F", "#FFD166", "#0077FF", "#06D6A0"],
            labels={"demandMetric": "?섏슂 吏??, "logValue": "吏???ш린 (Log scale)"},
            template="plotly_dark"
        )
        fig_res_bar.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(l=20, r=20, t=10, b=20),
            height=300,
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_res_bar, use_container_width=True, key='chart_app_9537189_fig_res_bar_65')
        st.markdown("</div>", unsafe_allow_html=True)


    


# ==========================================
# TAB 5: ?먮낯 ?곗씠??& ?묒? ?ㅼ슫濡쒕뱶 (Data Table)
# ==========================================
with tab5:
    st.markdown("<h3 style='font-weight: 600; color: #F8FAFC;'>?뾺截??ㅼ떆媛??곕룞 ?먮낯 ?곗씠?곗뀑</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>2媛쒖쓽 怨듦났?곗씠?고룷??API(吏??퀎 愿愿??ㅼ뼇??& 吏??퀎 愿愿??먯썝 ?섏슂)瑜??곕룞??媛쒕퀎 ?곗씠???뚯씠釉붿엯?덈떎.</p>", unsafe_allow_html=True)
    
    col_dt1, col_dt2 = st.columns(2)
    
    with col_dt1:
        st.markdown("<h5 style='color:#00D2C4;'>1. 吏??퀎 愿愿??ㅼ뼇???곗씠??(API 1)</h5>", unsafe_allow_html=True)
        st.dataframe(df_diversity, use_container_width=True)
        
        # CSV ?ㅼ슫濡쒕뱶 湲곕뒫
        csv_div = df_diversity.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="?뱿 ?ㅼ뼇???곗씠??CSV ?ㅼ슫濡쒕뱶",
            data=csv_div,
            file_name=f"tourism_diversity_{selected_area_code}_{base_ym}.csv",
            mime="text/csv"
        )
        
    with col_dt2:
        st.markdown("<h5 style='color:#FF758F;'>2. 吏??퀎 愿愿??먯썝 ?섏슂 ?곗씠??(API 2)</h5>", unsafe_allow_html=True)
        st.dataframe(df_resource, use_container_width=True)
        
        # CSV ?ㅼ슫濡쒕뱶 湲곕뒫
        csv_res = df_resource.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="?뱿 ?먯썝 ?섏슂 ?곗씠??CSV ?ㅼ슫濡쒕뱶",
            data=csv_res,
            file_name=f"tourism_resource_demand_{selected_area_code}_{base_ym}.csv",
            mime="text/csv"
        )

# ?섎떒 ?뺣낫 ?명꽣
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #64748B; font-size: 0.85rem; padding: 20px 0;'>
??쒕?援?怨듦났?곗씠?고룷??data.go.kr) & ?쒓뎅愿愿묎났??TourAPI ?ㅼ떆媛??곕룞 ??쒕낫??br/>
Designed & Programmed by <b>Antigravity</b> Team. Current System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)
