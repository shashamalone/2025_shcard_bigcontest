"""
Marketing Multi-Agent System
Streamlit 메인 애플리케이션
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
    
    # 사이드바: 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 점포 선택
        store_id = st.text_input("점포 ID", value="S123", help="분석할 점포 ID")
        
        # 기간 선택
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "시작일",
                value=datetime.now() - timedelta(days=30)
            )
        with col2:
            end_date = st.date_input(
                "종료일",
                value=datetime.now()
            )
        
        # 예산
        budget_krw = st.number_input(
            "예산 (원)",
            min_value=0,
            max_value=10000000,
            value=50000,
            step=10000
        )
        
        # 채널
        preferred_channels = st.multiselect(
            "선호 채널",
            options=["kakao", "instagram", "facebook", "naver", "blog"],
            default=["kakao", "instagram"]
        )
        
        st.divider()
        
        # 실행 버튼
        run_button = st.button("🚀 전략 생성", type="primary", use_container_width=True)
    
    # 메인 영역: 쿼리 입력
    st.header("💬 전략 요청")
    user_query = st.text_area(
        "무엇을 도와드릴까요?",
        value="평일 점심 매출을 늘리고 싶어. 예산 5만원, 인스타로.",
        height=100,
        help="자연어로 전략 요청을 입력하세요"
    )
    
    # 실행
    if run_button and user_query:
        
        # 제약 조건 구성
        constraints = {
            "store_id": store_id,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "budget_krw": budget_krw,
            "budget_tier": _determine_budget_tier(budget_krw),
            "preferred_channels": preferred_channels
        }
        
        # 초기 상태
        initial_state = AgentState(
            user_query=user_query,
            constraints=constraints
        )
        
        # 진행 상황
        with st.spinner("전략 생성 중..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # 그래프 실행
                status_text.text("1/5 의도 분석 중...")
                progress_bar.progress(20)
                
                final_state = marketing_graph.invoke(initial_state)
                
                progress_bar.progress(100)
                status_text.text("✅ 완료!")
                
                # 결과 표시
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


def _display_results(state: AgentState):
    """결과 표시"""
    
    st.success("전략 생성이 완료되었습니다!")
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 전략 카드",
        "📈 컨텍스트",
        "✅ 평가 결과",
        "📝 로그"
    ])
    
    # 전략 카드
    with tab1:
        st.header("생성된 전략")
        
        if state.strategy_cards:
            for idx, card in enumerate(state.strategy_cards):
                with st.expander(f"**전략 {idx+1}: {card.get('title', 'N/A')}**", expanded=True):
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**가설**: {card.get('hypothesis', 'N/A')}")
                        st.markdown(f"**타겟**: {card.get('target_segment', 'N/A')}")
                        st.markdown(f"**제안**: {card.get('offer', 'N/A')}")
                        
                        st.markdown("**근거**:")
                        for why in card.get("why", []):
                            st.markdown(f"- {why}")
                    
                    with col2:
                        budget = card.get("budget", {})
                        st.metric("예산", f"{budget.get('cap', 0):,}원")
                        
                        timeline = card.get("timeline", {})
                        st.metric("기간", f"{timeline.get('start', '')} ~ {timeline.get('end', '')}")
                        
                        kpi = card.get("kpi_targets", {}).get("primary", {})
                        st.metric("목표 KPI", f"{kpi.get('metric', 'N/A')}: {kpi.get('target', 'N/A')}")
                    
                    st.markdown("---")
                    st.markdown("**채널**: " + ", ".join(card.get("channel_hints", [])))
                    st.markdown("**위험**: " + " / ".join(card.get("risks", ["없음"])))
        else:
            st.warning("생성된 전략이 없습니다.")
    
    # 컨텍스트
    with tab2:
        st.header("점포/상권 컨텍스트")
        
        if state.context_json:
            ctx = state.context_json
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                sales = ctx.get("metrics", {}).get("kpi", {}).get("sales_sum", 0)
                st.metric("총 매출", f"{sales:,.0f}원")
            with col2:
                visits = ctx.get("metrics", {}).get("kpi", {}).get("visits_sum", 0)
                st.metric("총 방문", f"{visits:,}회")
            with col3:
                aov = ctx.get("metrics", {}).get("kpi", {}).get("aov", 0)
                st.metric("객단가", f"{aov:,.0f}원")
            with col4:
                repeat = ctx.get("metrics", {}).get("kpi", {}).get("repeat_rate", 0)
                st.metric("재방문율", f"{repeat:.1%}")
            
            st.markdown("---")
            
            st.subheader("파생 지표")
            derived = ctx.get("metrics", {}).get("derived", {})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("경쟁강도", f"{derived.get('comp_intensity', 0):.2f}")
                st.metric("런치비중", f"{derived.get('lunch_share', 0):.1%}")
            with col2:
                st.metric("주말편중", f"{derived.get('weekend_share', 0):.1%}")
                st.metric("유동지수", f"{derived.get('foot_traffic_proxy', 0):.2f}")
            with col3:
                st.metric("업종대비", f"{derived.get('same_industry_sales_ratio', 0):.2f}")
                st.metric("매출변동", f"{derived.get('sales_volatility_4w', 0):.2f}")
            
            st.markdown("---")
            
            st.subheader("위험 평가")
            risk = ctx.get("risk", {})
            st.metric("위험점수", f"{risk.get('score', 0):.2f}")
            st.markdown(f"**유형**: {risk.get('typology', 'N/A')}")
            st.markdown("**요인**: " + ", ".join(risk.get("reasons", [])))
        else:
            st.warning("컨텍스트 데이터가 없습니다.")
    
    # 평가 결과
    with tab3:
        st.header("전략 평가")
        
        if state.eval_report:
            report = state.eval_report
            
            severity_color = {
                "low": "🟢",
                "medium": "🟡",
                "high": "🔴"
            }
            
            st.markdown(f"**요약**: {report.get('summary', 'N/A')}")
            st.markdown(f"**심각도**: {severity_color.get(report.get('severity'), '⚪')} {report.get('severity', 'N/A')}")
            
            st.markdown("---")
            
            checks = report.get("checks", [])
            for check in checks:
                card_idx = check.get("card_idx", 0)
                
                with st.expander(f"카드 {card_idx + 1} 검증 결과"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        constraint_fit = check.get("constraint_fit", False)
                        st.markdown(f"**제약 부합**: {'✅' if constraint_fit else '❌'}")
                    
                    with col2:
                        evidence_match = check.get("evidence_match", False)
                        st.markdown(f"**근거 매칭**: {'✅' if evidence_match else '❌'}")
                    
                    risk_notes = check.get("risk_notes", [])
                    if risk_notes:
                        st.markdown("**위험 노트**:")
                        for note in risk_notes:
                            st.markdown(f"- {note}")
                    
                    fix_suggestion = check.get("fix_suggestion")
                    if fix_suggestion:
                        st.info(f"💡 수정 제안: {fix_suggestion}")
            
            st.markdown("---")
            
            st.subheader("권장 액션")
            actions = report.get("recommended_actions", [])
            for action in actions:
                st.markdown(f"- **{action.get('action', 'N/A')}**: {action.get('impact', 'N/A')}")
        else:
            st.warning("평가 결과가 없습니다.")
    
    # 로그
    with tab4:
        st.header("실행 로그")
        
        logs = state.logs
        if logs:
            for log in logs:
                st.text(log)
        else:
            st.info("로그가 없습니다.")


if __name__ == "__main__":
    main()
