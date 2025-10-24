"""
Marketing Multi-Agent System
Streamlit 메인 애플리케이션 (Top Bar 버전)
"""
import streamlit as st
from datetime import datetime, timedelta
from loguru import logger
import sys

# 로깅 설정
logger.remove()
logger.add(sys.stderr, level="INFO")

from agents import marketing_graph, AgentState


def main():
    """메인 애플리케이션"""

    st.set_page_config(
        page_title="마케팅 Multi-Agent",
        page_icon="🎯",
        layout="wide"
    )

    st.title("🎯 마케팅 전략 생성 시스템")
    st.caption("Multi-Agent 기반 데이터 중심 전략 수립")

    # ==============================
    # 🔹 상단 입력 바 (Top Control Bar)
    # ==============================
    st.markdown("### ⚙️ 설정")

    # 5열 구성
    col1, col2, col3, col4, col5 = st.columns([1.2, 1.5, 1.2, 1.5, 1.2])

    with col1:
        store_id = st.text_input("점포 ID", value="S123", help="분석할 점포 ID")

    with col2:
        start_date = st.date_input("시작일", value=datetime.now() - timedelta(days=30))

    with col3:
        end_date = st.date_input("종료일", value=datetime.now())

    with col4:
        budget_krw = st.number_input(
            "예산 (원)",
            min_value=0,
            max_value=10000000,
            value=50000,
            step=10000
        )

    with col5:
        preferred_channels = st.multiselect(
            "선호 채널",
            options=["kakao", "instagram", "facebook", "naver", "blog"],
            default=["kakao", "instagram"]
        )

    st.divider()

    # ==============================
    # 🔹 사용자 요청 입력
    # ==============================
    st.markdown("### 💬 전략 요청")
    user_query = st.text_area(
        "무엇을 도와드릴까요?",
        value="평일 점심 매출을 늘리고 싶어. 예산 5만원, 인스타로.",
        height=100,
        help="자연어로 전략 요청을 입력하세요",
        placeholder="예) 주말 저녁 매출 증대를 위한 전략이 필요합니다"
    )

    # 실행 버튼 (상단 중앙 정렬)
    run_col = st.columns([4, 1, 4])[1]
    with run_col:
        run_button = st.button("🚀 전략 생성", type="primary", use_container_width=True)

    # ==============================
    # 🔹 실행 로직
    # ==============================
    if run_button and user_query:
        constraints = {
            "store_id": store_id,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "budget_krw": budget_krw,
            "budget_tier": _determine_budget_tier(budget_krw),
            "preferred_channels": preferred_channels
        }

        initial_state = {
            "user_query": user_query,
            "intent": "strategy",
            "constraints": constraints,
            "context_json": None,
            "situation_json": None,
            "resource_json": None,
            "strategy_cards": [],
            "eval_report": None,
            "batch_eval_result": None,
            "logs": []
        }

        with st.spinner("전략 생성 중..."):
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                status_text.text("🔍 1/5 의도 분석 중...")
                progress_bar.progress(20)

                final_state = marketing_graph.invoke(initial_state)

                progress_bar.progress(100)
                status_text.text("✅ 완료!")

                _display_results(final_state)

            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")
                logger.error(f"그래프 실행 오류: {e}", exc_info=True)


def _determine_budget_tier(budget_krw: int) -> str:
    """예산 등급 판단"""
    if budget_krw < 100000:
        return "low"
    elif budget_krw < 500000:
        return "med"
    else:
        return "high"

def _display_results(state):
    """결과 표시 (탭 스타일 버튼 + 세로 카드형 평가결과)"""

    st.success("✅ 전략 생성이 완료되었습니다!")

    # ==============================
    # 💅 CSS 커스터마이징 (탭 스타일)
    # ==============================
    st.markdown(
        """
        <style>
        /* 전체 탭 영역 스타일 */
        div[data-baseweb="tab-list"] {
            display: flex;
            justify-content: center;
            gap: 1rem;
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 8px;
            margin-bottom: 1rem;
        }
        /* 각 탭 버튼 스타일 */
        button[data-baseweb="tab"] {
            border-radius: 12px;
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #dcdcdc;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.2s ease-in-out;
        }
        /* 탭 hover 효과 */
        button[data-baseweb="tab"]:hover {
            background-color: #f0f0f0;
            color: #000000;
            transform: translateY(-1px);
        }
        /* 활성화된 탭 스타일 */
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #007BFF;
            color: white !important;
            border: none;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
        }
        /* 카드 스타일 */
        .card {
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            background-color: #ffffff;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            height: 100%;
            transition: transform 0.2s;
            margin-bottom: 10px;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .card-header {
            font-size: 18px;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 15px;
            border-bottom: 2px solid #1f77b4;
            padding-bottom: 10px;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 14px;
            margin: 5px 5px 5px 0;
        }
        .badge-success {
            background-color: #d4edda;
            color: #155724;
        }
        .badge-danger {
            background-color: #f8d7da;
            color: #721c24;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ==============================
    # 📊 탭 구조
    # ==============================
    tab1, tab2, tab3 = st.tabs([
        "📊 전략 카드",
        "📈 컨텍스트",
        "✅ 평가 결과"
    ])

    # --- 1️⃣ 전략 카드 ---
    with tab1:
        st.markdown("## 📋 생성된 전략")
        strategy_cards = state.get("strategy_cards", [])
        if strategy_cards:
            for idx, card in enumerate(strategy_cards):
                with st.expander(f"**💡 전략 {idx+1}: {card.get('title', 'N/A')}**", expanded=(idx==0)):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**🎯 가설**: {card.get('hypothesis', 'N/A')}")
                        st.markdown(f"**👥 타겟**: {card.get('target_segment', 'N/A')}")
                        st.markdown(f"**🎁 제안**: {card.get('offer', 'N/A')}")
                        st.markdown("**📌 근거:**")
                        for why in card.get("why", []):
                            st.markdown(f"  • {why}")
                    with col2:
                        budget = card.get("budget", {})
                        st.metric("💰 예산", f"{budget.get('cap', 0):,}원")
                        timeline = card.get("timeline", {})
                        st.metric("📅 기간", f"{timeline.get('start', '')} ~ {timeline.get('end', '')}")
                        kpi = card.get("kpi_targets", {}).get("primary", {})
                        st.metric("🎯 목표 KPI", f"{kpi.get('metric', 'N/A')}: {kpi.get('target', 'N/A')}")
                    
                    st.markdown("---")
                    col_ch, col_risk = st.columns(2)
                    with col_ch:
                        st.markdown("**📢 채널**: " + ", ".join(card.get("channel_hints", [])))
                    with col_risk:
                        st.markdown("**⚠️ 위험**: " + " / ".join(card.get("risks", ["없음"])))
        else:
            st.info("⚠️ 생성된 전략이 없습니다.")

    # --- 2️⃣ 컨텍스트 ---
    with tab2:
        st.markdown("## 🏪 점포/상권 컨텍스트")
        ctx = state.get("context_json")
        if ctx:
            st.markdown("### 📊 핵심 지표")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💵 총 매출", f"{ctx.get('metrics', {}).get('kpi', {}).get('sales_sum', 0):,.0f}원")
            with col2:
                st.metric("👥 총 방문", f"{ctx.get('metrics', {}).get('kpi', {}).get('visits_sum', 0):,}회")
            with col3:
                st.metric("🛒 객단가", f"{ctx.get('metrics', {}).get('kpi', {}).get('aov', 0):,.0f}원")
            with col4:
                st.metric("🔄 재방문율", f"{ctx.get('metrics', {}).get('kpi', {}).get('repeat_rate', 0):.1%}")
            
            st.markdown("---")
            st.markdown("### 📈 파생 지표")
            derived = ctx.get("metrics", {}).get("derived", {})
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("⚔️ 경쟁강도", f"{derived.get('comp_intensity', 0):.2f}")
            with col2:
                st.metric("📅 주말편중", f"{derived.get('weekend_share', 0):.1%}")
            with col3:
                st.metric("📊 매출변동", f"{derived.get('sales_volatility_4w', 0):.2f}")
        else:
            st.info("⚠️ 컨텍스트 데이터가 없습니다.")

    # --- 3️⃣ 평가 결과 ---
    with tab3:
        # 하드코딩 샘플 데이터
        checks = [
            {
                "card_idx": 0,
                "constraint_fit": True,
                "evidence_match": True,
                "risk_notes": ["시장 변동성 주의", "경쟁사 동향 모니터링 필요"],
                "fix_suggestion": "분기별 KPI 검토 주기 단축 권장",
                "details": {
                    "strategy_name": "시장 확대 전략",
                    "target_metric": "매출 30% 증가",
                    "timeline": "6개월",
                    "resources": "마케팅 예산 2억",
                    "success_rate": "85%"
                }
            },
            {
                "card_idx": 1,
                "constraint_fit": False,
                "evidence_match": True,
                "risk_notes": ["예산 초과 가능성", "인력 부족"],
                "fix_suggestion": "우선순위 재조정 및 단계별 실행 필요",
                "details": {
                    "strategy_name": "제품 다각화",
                    "target_metric": "신제품 3종 출시",
                    "timeline": "12개월",
                    "resources": "R&D 인력 10명",
                    "success_rate": "65%"
                }
            },
            {
                "card_idx": 2,
                "constraint_fit": True,
                "evidence_match": False,
                "risk_notes": ["데이터 근거 부족"],
                "fix_suggestion": "사전 테스트 및 파일럿 프로그램 실시",
                "details": {
                    "strategy_name": "고객 충성도 향상",
                    "target_metric": "재구매율 20% 증가",
                    "timeline": "9개월",
                    "resources": "CRM 시스템 구축",
                    "success_rate": "75%"
                }
            }
        ]
        
        st.markdown("## 🔍 전략 평가 결과")
        report = state.get("eval_report")
        
        if report:
            severity_color = {"low": "🟢", "medium": "🟡", "high": "🔴"}
            
            # 요약 정보를 컬럼으로 표시
            sum_col1, sum_col2 = st.columns([3, 1])
            with sum_col1:
                st.markdown(f"**📝 요약**: {report.get('summary', 'N/A')}")
            with sum_col2:
                st.markdown(f"**🚨 심각도**: {severity_color.get(report.get('severity'), '⚪')} {report.get('severity', 'N/A').upper()}")
            
            st.markdown("---")

        # 가로 카드 레이아웃
        if checks:
            cols = st.columns(3)
            
            for idx, check in enumerate(checks):
                with cols[idx]:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    
                    # 카드 헤더
                    st.markdown(f'<div class="card-header">🧩 전략 카드 {check.get("card_idx", 0)+1}</div>', 
                               unsafe_allow_html=True)
                    
                    # 상태 배지
                    constraint_status = "✅ 부합" if check.get('constraint_fit') else "❌ 불일치"
                    evidence_status = "✅ 일치" if check.get('evidence_match') else "❌ 불일치"
                    
                    st.markdown(f"""
                    <div class="status-badge {'badge-success' if check.get('constraint_fit') else 'badge-danger'}">
                        제약조건: {constraint_status}
                    </div>
                    <div class="status-badge {'badge-success' if check.get('evidence_match') else 'badge-danger'}">
                        근거자료: {evidence_status}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 수정 제안
                    if check.get("fix_suggestion"):
                        st.info(f"💡 {check['fix_suggestion']}")
                    
                    # 세부사항 토글
                    with st.expander("📋 세부 정보"):
                        details = check.get("details", {})
                        st.markdown(f"**전략명**: {details.get('strategy_name', 'N/A')}")
                        st.markdown(f"**목표 지표**: {details.get('target_metric', 'N/A')}")
                        st.markdown(f"**기간**: {details.get('timeline', 'N/A')}")
                        st.markdown(f"**필요 자원**: {details.get('resources', 'N/A')}")
                        st.markdown(f"**성공 확률**: {details.get('success_rate', 'N/A')}")
                        
                        if check.get("risk_notes"):
                            st.markdown("**⚠️ 위험 요소**:")
                            for note in check["risk_notes"]:
                                st.markdown(f"  • {note}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("⚠️ 세부 카드 검증 결과가 없습니다.")


if __name__ == "__main__":
    main()