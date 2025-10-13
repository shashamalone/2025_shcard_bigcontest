import streamlit as st
import os
from dotenv import load_dotenv
from agents.graph import run_marketing_agent

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="마케팅 AI 어시스턴트",
    page_icon="🎯",
    layout="wide"
)

# 제목
st.title("🎯 소상공인 마케팅 MultiAgent 시스템")
st.markdown("LangGraph 기반 지능형 마케팅 전략 생성")
st.markdown("---")

# 사이드바
with st.sidebar:
    st.header("⚙️ API 설정")
    
    # API 키 확인
    gemini_key = os.getenv("GOOGLE_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    
    if gemini_key:
        st.success("✅ Gemini API 연결됨")
    else:
        st.error("❌ Gemini API 키 필요")
    
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
    ### 🔄 Agent 흐름
    
    **strategy_supervisor**
    ↓
    **{context, situation, resource}** (병렬)
    ↓
    **merge_supervisor**
    ↓
    **evaluation_agent**
    ↓
    **END**
    """)
    
    st.markdown("---")
    st.markdown("""
    ### 📋 사전 질문 예시
    
    1. 카페 - 고객 특성별 채널 추천
    2. 재방문율 30% 이하 - 개선 방안
    3. 요식업 - 문제점 진단
    4. 상권 특화 - 이벤트/날씨 활용
    """)

# 메인 컨텐츠
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 비즈니스 정보")
    
    business_name = st.text_input(
        "가맹점명",
        placeholder="예: 강남 카페",
        help="비공개 가능"
    )
    
    business_type = st.selectbox(
        "업종",
        ["카페", "요식업", "소매업", "서비스업", "온라인몰"]
    )
    
    user_query = st.text_area(
        "마케팅 질문",
        placeholder="예: 평일 매출을 늘리고 싶어요\n재방문율을 높이는 방법을 알려주세요",
        height=120,
        help="구체적일수록 정확한 답변을 받을 수 있습니다"
    )

with col2:
    st.header("🎯 제약 조건")
    
    budget = st.selectbox(
        "월 마케팅 예산",
        ["5만원 미만", "5-10만원", "10-20만원", "20만원 이상"]
    )
    
    budget_map = {
        "5만원 미만": 50000,
        "5-10만원": 100000,
        "10-20만원": 200000,
        "20만원 이상": 500000
    }
    
    channels = st.multiselect(
        "선호 채널",
        ["Instagram", "네이버 블로그", "카카오톡", "Facebook", "YouTube"],
        default=["Instagram"]
    )
    
    duration = st.selectbox(
        "실행 기간",
        ["1주", "2주", "1개월", "3개월"]
    )
    
    duration_map = {
        "1주": 1,
        "2주": 2,
        "1개월": 4,
        "3개월": 12
    }

# 실행 버튼
st.markdown("---")
col_btn = st.columns([1, 2, 1])

with col_btn[1]:
    run_button = st.button(
        "🚀 AI 전략 생성 시작",
        type="primary",
        use_container_width=True
    )

# 결과 표시
if run_button:
    if not user_query:
        st.error("❌ 마케팅 질문을 입력해주세요!")
    elif not gemini_key:
        st.error("❌ Gemini API 키가 설정되지 않았습니다.")
    else:
        # 제약조건 구성
        constraints = {
            "budget_krw": budget_map[budget],
            "channels": channels,
            "duration_weeks": duration_map[duration]
        }
        
        # 비즈니스 정보 추가
        full_query = f"""
비즈니스: {business_name} ({business_type})
질문: {user_query}
"""
        
        with st.spinner("🤖 MultiAgent 시스템이 전략을 생성 중입니다..."):
            try:
                # 에이전트 실행
                result = run_marketing_agent(full_query, constraints)
                
                if result:
                    st.session_state['result'] = result
                    st.success("✅ 전략 생성 완료!")
                    st.balloons()
            
            except Exception as e:
                st.error(f"❌ 오류: {str(e)}")
                st.info("💡 API 키를 확인하거나 질문을 수정해보세요")

# 결과 출력
if 'result' in st.session_state:
    result = st.session_state['result']
    
    st.markdown("---")
    st.header("📊 생성된 마케팅 전략")
    
    # 탭 구성
    tabs = st.tabs([
        "🎯 전략 카드",
        "📈 컨텍스트 분석",
        "🌤️ 상황 분석",
        "💰 리소스 분석",
        "✅ 평가 리포트",
        "📝 실행 로그"
    ])
    
    # 전략 카드
    with tabs[0]:
        st.subheader("🎯 최종 전략 카드")
        
        if result.strategy_cards:
            for idx, card in enumerate(result.strategy_cards):
                with st.expander(f"전략 {idx+1}: {card.get('title', '제목없음')}", expanded=True):
                    st.markdown(f"**유형:** {card.get('card_type', 'N/A')}")
                    
                    st.markdown("**📌 근거 (Why)**")
                    for reason in card.get('why', []):
                        st.markdown(f"- {reason}")
                    
                    st.markdown("**📋 실행 내용 (What)**")
                    for item in card.get('what', []):
                        st.markdown(f"- {item}")
                    
                    st.markdown("**🔧 실행 방법 (How)**")
                    for step in card.get('how', []):
                        st.markdown(f"- {step.get('step', 'N/A')} "
                                  f"(담당: {step.get('owner', 'N/A')}, "
                                  f"예상 시간: {step.get('eta_min', 0)}분)")
                    
                    st.markdown("**📈 예상 효과**")
                    effect = card.get('expected_effect', {})
                    st.markdown(f"- KPI: {effect.get('kpi', 'N/A')}")
                    st.markdown(f"- 예상 효과: {effect.get('lift_hypothesis', 'N/A')}")
        else:
            st.info("생성된 전략 카드가 없습니다.")
    
    # 컨텍스트 분석
    with tabs[1]:
        st.subheader("📈 점포/상권 컨텍스트")
        
        if result.context_json:
            st.json(result.context_json)
        else:
            st.info("컨텍스트 정보가 없습니다.")
    
    # 상황 분석
    with tabs[2]:
        st.subheader("🌤️ 날씨/이벤트 상황")
        
        if result.situation_json:
            st.json(result.situation_json)
        else:
            st.info("상황 정보가 없습니다.")
    
    # 리소스 분석
    with tabs[3]:
        st.subheader("💰 예산/채널/도구")
        
        if result.resource_json:
            st.json(result.resource_json)
        else:
            st.info("리소스 정보가 없습니다.")
    
    # 평가 리포트
    with tabs[4]:
        st.subheader("✅ 전략 평가 결과")
        
        if result.eval_report:
            eval_report = result.eval_report
            
            # 요약
            st.metric(
                "전체 품질",
                eval_report.get('overall_quality', 'N/A'),
                f"{eval_report.get('pass_rate', 0)*100:.0f}% 적합"
            )
            
            st.markdown(f"**요약:** {eval_report.get('summary', 'N/A')}")
            
            # 세부 검증
            st.markdown("**세부 검증 결과:**")
            for check in eval_report.get('checks', []):
                status_emoji = "✅" if check.get('status') == 'PASS' else "❌"
                st.markdown(f"{status_emoji} **{check.get('card_title', 'N/A')}**")
                
                if check.get('issues'):
                    for issue in check['issues']:
                        st.markdown(f"  - ⚠️ {issue}")
            
            # 권고사항
            if eval_report.get('recommendations'):
                st.markdown("**개선 권고사항:**")
                for rec in eval_report['recommendations']:
                    st.warning(f"🔔 [{rec.get('priority', 'N/A')}] {rec.get('action', 'N/A')}")
        else:
            st.info("평가 리포트가 없습니다.")
    
    # 실행 로그
    with tabs[5]:
        st.subheader("📝 Agent 실행 로그")
        
        if result.logs:
            for log in result.logs:
                st.text(log)
        else:
            st.info("로그가 없습니다.")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🤖 Powered by LangChain & LangGraph | Gemini 2.0 Flash | v2.0</p>
</div>
""", unsafe_allow_html=True)