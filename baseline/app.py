import streamlit as st
import os
from dotenv import load_dotenv
from agents.agent_graph_simple import run_marketing_agent

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="마케팅 AI 어시스턴트",
    page_icon="🎯",
    layout="wide"
)

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
    1. 비즈니스 정보 입력
    2. 타겟 고객 설명
    3. AI 분석 실행
    4. 맞춤 전략 확인
    """)

# 메인 컨텐츠
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 비즈니스 정보 입력")
    
    business_name = st.text_input("비즈니스 이름", placeholder="예: 강남 베이커리")
    
    business_type = st.selectbox(
        "업종",
        ["음식점/카페", "소매업", "서비스업", "온라인 쇼핑몰", "교육", "기타"]
    )
    
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
    st.header("🎯 마케팅 목표 설정")
    
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
    
    st.markdown("---")
    
    additional_info = st.text_area(
        "추가 정보 (선택사항)",
        placeholder="특별히 강조하고 싶은 점이나 제약사항을 입력하세요",
        height=100
    )

# 실행 버튼
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn2:
    run_button = st.button("🚀 AI 마케팅 전략 생성", type="primary", use_container_width=True)

# 결과 표시
if run_button:
    if not business_name or not target_audience:
        st.error("❌ 비즈니스 이름과 타겟 고객 정보를 입력해주세요!")
    elif not openai_key:
        st.error("❌ OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    else:
        # 비즈니스 정보 종합
        business_info = f"""
        비즈니스 이름: {business_name}
        업종: {business_type}
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
                
                # 결과 저장
                if result:
                    st.session_state['result'] = result
                    st.success("✅ 마케팅 전략이 생성되었습니다!")
                    st.balloons()
            
            except Exception as e:
                st.error(f"❌ 오류가 발생했습니다: {str(e)}")
                st.info("💡 API 키 설정을 확인하거나, 입력 내용을 수정해보세요.")

# 결과가 있으면 표시
if 'result' in st.session_state:
    result = st.session_state['result']
    
    st.markdown("---")
    st.header("📊 AI 생성 마케팅 전략")
    
    # 탭으로 결과 구분
    tab1, tab2, tab3, tab4 = st.tabs(["📋 종합 전략", "📈 데이터 분석", "✍️ 콘텐츠", "🎨 디자인"])
    
    with tab1:
        st.subheader("🎯 최종 마케팅 전략")
        
        # 최종 전략 표시
        final_key = None
        for key in result.keys():
            if 'brand_manager' in key:
                final_key = key
                break
        
        if final_key and 'final_strategy' in result[final_key]:
            st.markdown(result[final_key]['final_strategy'])
        else:
            st.info("최종 전략이 아직 생성되지 않았습니다.")
        
        # 다운로드 버튼
        if final_key and 'final_strategy' in result[final_key]:
            st.download_button(
                label="📥 전략 다운로드 (TXT)",
                data=result[final_key]['final_strategy'],
                file_name=f"{business_name}_마케팅전략.txt",
                mime="text/plain"
            )
    
    with tab2:
        st.subheader("📈 시장 분석 결과")
        
        # 데이터 분석 결과 찾기
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
        
        # 콘텐츠 작가 결과 찾기
        writer_key = None
        for key in result.keys():
            if 'content_writer' in key:
                writer_key = key
                break
        
        if writer_key and 'content_draft' in result[writer_key]:
            st.markdown(result[writer_key]['content_draft'])
            
            # 복사 버튼
            st.code(result[writer_key]['content_draft'], language=None)
        else:
            st.info("콘텐츠 초안이 없습니다.")
    
    with tab4:
        st.subheader("🎨 디자인 컨셉")
        
        # 디자이너 결과 찾기
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
    <p>🤖 Powered by LangChain & LangGraph | 소상공인 마케팅 AI 어시스턴트 v1.0</p>
</div>
""", unsafe_allow_html=True)