import streamlit as st
import os
from dotenv import load_dotenv
from agents.agent_graph_simple import run_marketing_agent
import pandas as pd

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="마케팅 AI 어시스턴트",
    page_icon="🎯",
    layout="wide"
)

# 세션 상태 초기화
if 'store_data' not in st.session_state:
    st.session_state.store_data = None
if 'selected_store' not in st.session_state:
    st.session_state.selected_store = None
if 'filtered_stores' not in st.session_state:
    st.session_state.filtered_stores = None

# 제목
st.title("🎯 소상공인을 위한 마케팅 AI 어시스턴트")
st.markdown("---")

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    
    # API 키 확인
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    
    if openai_key:
        st.success("✅ OpenAI API 연결됨")
    else:
        st.error("❌ OpenAI API 키 필요")
    
    if tavily_key:
        st.success("✅ Tavily API 연결됨")
    else:
        st.warning("⚠️ Tavily API 키 권장")
    
    if pinecone_key:
        st.success("✅ Pinecone 연결됨")
    else:
        st.warning("⚠️ Pinecone 키 권장")
    
    st.markdown("---")
    st.markdown("""
    ### 💡 사용 방법
    1. 가맹점 검색 및 선택
    2. 비즈니스 정보 확인
    3. 타겟 고객 설명
    4. AI 분석 실행
    5. 맞춤 전략 확인
    """)

# === 1단계: 가맹점 검색 ===
st.header("🔍 1단계: 가맹점 검색")

col_search1, col_search2 = st.columns([3, 1])

with col_search1:
    store_search = st.text_input(
        "가맹점명 검색",
        placeholder="예: 10월의 하늘",
        help="가맹점명의 일부만 입력해도 검색됩니다"
    )

with col_search2:
    search_button = st.button("🔍 검색", use_container_width=True)

# 가맹점 데이터 로드 (Fast MCP에서 가져온다고 가정)
def load_store_data():
    """실제로는 Fast MCP를 통해 데이터를 가져옴"""
    # 예시 데이터 (실제로는 MCP API 호출)
    data = {
        '가맹점구분번호': ['7162A93F6B', '24AA9CA0A5', 'D395BA1A40', '9C1036E322', '1A8BA43A9D', 'E8E75C90BA', 'DD406CC456'],
        '가맹점명': ['10월의 하늘', '포차명가', '10월의 하늘', '10월의 하늘 왕십리점', '19세기 피렌체', '20세기 바다', '20세기 레스토랑'],
        '가맹점주소': [
            '서울특별시 성동구 살곶이길 200',
            '서울특별시 성동구 용답중앙길 80',
            '서울 성동구 뚝섬로 341-8',
            '서울특별시 성동구 왕십리광장로 17',
            '서울특별시 성동구 왕십리로 106',
            '서울 성동구 성수동2가',
            '서울특별시 성동구 성수일로1길 12-12'
        ],
        '브랜드구분코드': ['오****', '포***', '10**', '10*******', '19******', '20****', '20****'],
        '가맹점지역': ['서울 성동구', '서울 성동구', '서울 성동구', '서울 성동구', '서울 성동구', '서울 성동구', '서울 성동구'],
        '업종': ['카페', '중식당', '일식당', '일식-덮밥/돈가스', '양식', '한식-해물/생선', '양식'],
        '상권': ['한양대', '답십리', '성수', '왕십리', '뚝섬', '성수', ''],
        '개설일': ['20221024', '20240829', '20100607', '20190107', '20220527', '20090804', '20230530'],
        '폐업일': ['', '', '', '', '', '', '']
    }
    return pd.DataFrame(data)

# 검색 실행
if search_button and store_search:
    st.session_state.store_data = load_store_data()
    df = st.session_state.store_data
    
    # 가맹점명 검색 (부분 일치)
    filtered = df[df['가맹점명'].str.contains(store_search, case=False, na=False)]
    st.session_state.filtered_stores = filtered
    
    if len(filtered) == 0:
        st.warning(f"'{store_search}'에 해당하는 가맹점을 찾을 수 없습니다.")
    elif len(filtered) == 1:
        st.session_state.selected_store = filtered.iloc[0].to_dict()
        st.success(f"✅ 가맹점이 선택되었습니다: {filtered.iloc[0]['가맹점명']}")
    else:
        st.info(f"🔎 '{store_search}' 검색 결과: {len(filtered)}개의 가맹점이 있습니다. 아래에서 선택하세요.")

# === 중복 가맹점 선택 UI ===
if st.session_state.filtered_stores is not None and len(st.session_state.filtered_stores) > 1:
    st.subheader("📍 가맹점 선택")
    
    filtered = st.session_state.filtered_stores
    
    # 선택 옵션 생성
    store_options = []
    for idx, row in filtered.iterrows():
        option = f"{row['가맹점명']} | {row['가맹점주소']} | {row['업종']} | {row['상권']}"
        store_options.append(option)
    
    selected_option = st.radio(
        "가맹점을 선택하세요:",
        store_options,
        key="store_selector"
    )
    
    # 선택 확인 버튼
    if st.button("✅ 이 가맹점으로 선택", type="primary"):
        selected_idx = store_options.index(selected_option)
        st.session_state.selected_store = filtered.iloc[selected_idx].to_dict()
        st.success(f"✅ 선택 완료: {st.session_state.selected_store['가맹점명']}")
        st.rerun()

# === 2단계: 선택된 가맹점 정보 표시 ===
if st.session_state.selected_store:
    st.markdown("---")
    st.header("📋 2단계: 선택된 가맹점 정보")
    
    store = st.session_state.selected_store
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("가맹점명", store['가맹점명'])
        st.metric("업종", store['업종'])
    
    with col2:
        st.metric("지역", store['가맹점지역'])
        st.metric("상권", store['상권'] if store['상권'] else "정보 없음")
    
    with col3:
        st.metric("개설일", store['개설일'])
        st.text(f"주소: {store['가맹점주소']}")
    
    # 가맹점 변경 버튼
    if st.button("🔄 다른 가맹점 선택"):
        st.session_state.selected_store = None
        st.session_state.filtered_stores = None
        st.rerun()

# === 3단계: 마케팅 정보 입력 (가맹점 선택 후에만 표시) ===
if st.session_state.selected_store:
    st.markdown("---")
    st.header("🎯 3단계: 마케팅 목표 설정")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        target_audience = st.text_area(
            "타겟 고객",
            placeholder="예: 20-30대 직장인, 건강에 관심 많은 여성",
            height=100
        )
        
        business_goal = st.text_area(
            "마케팅 목표",
            placeholder="예: 신규 고객 유치, 브랜드 인지도 향상, 매출 증대",
            height=100
        )
        
        budget = st.selectbox(
            "월 마케팅 예산",
            ["50만원 미만", "50-100만원", "100-200만원", "200만원 이상"]
        )
    
    with col2:
        channels = st.multiselect(
            "선호 마케팅 채널",
            ["Instagram", "Facebook", "네이버 블로그", "YouTube", "카카오톡", "이메일"],
            default=["Instagram", "네이버 블로그"]
        )
        
        campaign_type = st.radio(
            "캠페인 유형",
            ["신규 고객 유치", "기존 고객 유지", "브랜드 인지도", "프로모션/할인"]
        )
        
        timeline = st.selectbox(
            "캠페인 기간",
            ["1주", "2주", "1개월", "3개월", "6개월"]
        )
    
    additional_info = st.text_area(
        "추가 정보 (선택사항)",
        placeholder="특별히 강조하고 싶은 점이나 제약사항을 입력하세요",
        height=80
    )
    
    # === 실행 버튼 ===
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn2:
        run_button = st.button("🚀 AI 마케팅 전략 생성", type="primary", use_container_width=True)
    
    # === 결과 생성 ===
    if run_button:
        if not target_audience:
            st.error("❌ 타겟 고객 정보를 입력해주세요!")
        elif not openai_key:
            st.error("❌ OpenAI API 키가 설정되지 않았습니다.")
        else:
            store = st.session_state.selected_store
            
            # 비즈니스 정보 종합 (선택된 가맹점 정보 포함)
            business_info = f"""
            === 가맹점 정보 ===
            가맹점명: {store['가맹점명']}
            가맹점구분번호: {store['가맹점구분번호']}
            주소: {store['가맹점주소']}
            업종: {store['업종']}
            지역: {store['가맹점지역']}
            상권: {store['상권']}
            개설일: {store['개설일']}
            
            === 마케팅 설정 ===
            타겟 고객: {target_audience}
            마케팅 목표: {business_goal}
            예산: {budget}
            선호 채널: {', '.join(channels)}
            캠페인 유형: {campaign_type}
            기간: {timeline}
            추가 정보: {additional_info if additional_info else '없음'}
            """
            
            with st.spinner("🤖 AI가 맞춤 마케팅 전략을 분석 중입니다..."):
                try:
                    # 에이전트 실행
                    result = run_marketing_agent(business_info)
                    
                    if result:
                        st.session_state['result'] = result
                        st.success("✅ 마케팅 전략이 생성되었습니다!")
                        st.balloons()
                
                except Exception as e:
                    st.error(f"❌ 오류가 발생했습니다: {str(e)}")
                    st.info("💡 API 키 설정을 확인하거나, 입력 내용을 수정해보세요.")

# === 결과 표시 ===
if 'result' in st.session_state:
    result = st.session_state['result']
    
    st.markdown("---")
    st.header("📊 AI 생성 마케팅 전략")
    
    # 탭으로 결과 구분
    tab1, tab2, tab3, tab4 = st.tabs(["📋 종합 전략", "📈 데이터 분석", "✍️ 콘텐츠", "🎨 디자인"])
    
    with tab1:
        st.subheader("🎯 최종 마케팅 전략")
        
        final_key = None
        for key in result.keys():
            if 'brand_manager' in key:
                final_key = key
                break
        
        if final_key and 'final_strategy' in result[final_key]:
            st.markdown(result[final_key]['final_strategy'])
            
            # 다운로드 버튼
            store = st.session_state.selected_store
            st.download_button(
                label="📥 전략 다운로드 (TXT)",
                data=result[final_key]['final_strategy'],
                file_name=f"{store['가맹점명']}_마케팅전략.txt",
                mime="text/plain"
            )
        else:
            st.info("최종 전략이 아직 생성되지 않았습니다.")
    
    with tab2:
        st.subheader("📈 시장 분석 결과")
        
        analyst_key = None
        for key in result.keys():
            if 'data_analyst' in key:
                analyst_key = key
                break
        
        if analyst_key and 'analysis_result' in result[analyst_key]:
            st.markdown(result[analyst_key]['analysis_result'])
        else:
            st.info("분석 결과가 없습니다.")
    
    with tab3:
        st.subheader("✍️ 콘텐츠 초안")
        
        writer_key = None
        for key in result.keys():
            if 'content_writer' in key:
                writer_key = key
                break
        
        if writer_key and 'content_draft' in result[writer_key]:
            st.markdown(result[writer_key]['content_draft'])
            st.code(result[writer_key]['content_draft'], language=None)
        else:
            st.info("콘텐츠 초안이 없습니다.")
    
    with tab4:
        st.subheader("🎨 디자인 컨셉")
        
        designer_key = None
        for key in result.keys():
            if 'graphic_designer' in key:
                designer_key = key
                break
        
        if designer_key and 'design_concept' in result[designer_key]:
            st.markdown(result[designer_key]['design_concept'])
        else:
            st.info("디자인 컨셉이 없습니다.")
    
    # 프로세스 로그
    with st.expander("🔍 AI 에이전트 작업 과정 보기"):
        st.subheader("Agent 실행 로그")
        
        for key, value in result.items():
            if 'messages' in value:
                for msg in value['messages']:
                    st.text(msg)

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🤖 Powered by LangChain & LangGraph | 소상공인 마케팅 AI 어시스턴트 v1.1</p>
</div>
""", unsafe_allow_html=True)