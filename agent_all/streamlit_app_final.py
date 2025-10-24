# streamlit_app_improved.py
"""
Streamlit UI - Marketing MultiAgent System (Improved)
======================================================
✅ 기존 디자인 요소 유지
✅ 전략 카드 3개 가로 배치 추가
✅ 데이터 근거 시각화
✅ 4P별 상세 표시
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
from datetime import date, timedelta
import typing as Any


# 메인 시스템 임포트
sys.path.append(str(Path(__file__).parent))
from marketing_multiagent_system import (
    run_marketing_system,
    PrecomputedPositioningLoader
)

# 🔥 Intent 분류기 (내장)
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from typing import Literal
import json

class IntentClassification(BaseModel):
    """Intent 분류 결과"""
    task_type: Literal["종합_전략_수립", "상황_전술_제안", "콘텐츠_생성_가이드"]
    confidence: float
    reasoning: str

def classify_user_intent(user_input: str) -> IntentClassification:
    """사용자 입력 의도 분류 (초고속)"""

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.0,
        max_output_tokens=150
    )

    prompt = f"""사용자 요청을 3가지 중 분류:

1. 종합_전략_수립: 장기 전략, STP 분석, 종합 컨설팅
2. 상황_전술_제안: 날씨/이벤트 대응, 긴급 프로모션
3. 콘텐츠_생성_가이드: SNS 콘텐츠, 인스타/블로그

입력: "{user_input}"

JSON 출력 (예시):
{{"task_type": "상황_전술_제안", "confidence": 0.9, "reasoning": "날씨 키워드 감지"}}"""

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()

        # JSON 파싱
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        data = json.loads(content)
        return IntentClassification(**data)

    except Exception as e:
        print(f"⚠️ LLM 분류 실패: {e}, 룰 베이스 사용")
        # 폴백: 키워드 기반
        user_lower = user_input.lower()
        if any(k in user_lower for k in ['날씨', '비', '눈', '행사', '이벤트', '긴급', '오늘', '내일']):
            return IntentClassification(task_type="상황_전술_제안", confidence=0.7, reasoning="키워드 매칭")
        elif any(k in user_lower for k in ['콘텐츠', '인스타', '블로그', '포스팅', 'sns', '해시태그']):
            return IntentClassification(task_type="콘텐츠_생성_가이드", confidence=0.7, reasoning="키워드 매칭")
        else:
            return IntentClassification(task_type="종합_전략_수립", confidence=0.6, reasoning="기본값")

HAS_INTENT_CLASSIFIER = True

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="마케팅 전략 수립 시스템",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Custom CSS - 기존 디자인 + 전략 카드 스타일
# ============================================================================

st.markdown("""
<style>
    /* ============================== */
    /* 기존 디자인 요소 */
    /* ============================== */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2ca02c;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-left: 0.5rem;
        border-left: 5px solid #2ca02c;
    }
    
    .task-card {
        background-color: #f8f9fa;
        border: 2px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .task-card:hover {
        border-color: #1f77b4;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .signal-card {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.3rem;
    }
    
    .channel-card {
        background-color: #ffffff;
        border: 2px solid #4caf50;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    
    /* ============================== */
    /* 🔥 전략 카드 스타일 (추가) */
    /* ============================== */
    .strategy-card {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        height: 100%;
        transition: all 0.3s;
    }
    .strategy-card:hover {
        border-color: #1f77b4;
        box-shadow: 0 4px 16px rgba(31,119,180,0.2);
        transform: translateY(-2px);
    }
    
    .card-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.8rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    
    .card-priority {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .priority-high {
        background-color: #ff6b6b;
        color: white;
    }
    .priority-medium {
        background-color: #ffa500;
        color: white;
    }
    .priority-low {
        background-color: #95e1d3;
        color: #333;
    }
    
    .card-section {
        margin: 1rem 0;
    }
    .card-section-title {
        font-size: 1rem;
        font-weight: bold;
        color: #555;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
    }
    .card-section-content {
        font-size: 0.95rem;
        color: #333;
        line-height: 1.6;
        padding-left: 1.5rem;
        border-left: 3px solid #e0e0e0;
    }
    
    .card-concept {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 0.8rem;
        margin: 1rem 0;
        font-style: italic;
        border-radius: 4px;
    }
    
    .card-outcome {
        background-color: #d1ecf1;
        border-left: 4px solid #0c5460;
        padding: 0.8rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    
    .evidence-tag {
        display: inline-block;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        padding: 0.3rem 0.6rem;
        margin: 0.2rem;
        font-size: 0.85rem;
        color: #495057;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Helper Functions
# ============================================================================

@st.cache_data
def load_store_list():
    """가맹점 목록 로드"""
    try:
        data_dir = "/mnt/c/Users/rladl/Desktop/bigcontest_2025/2025_shcard_bigcontest/data"
        df = pd.read_csv(
            f"{data_dir}/store_segmentation_final_re.csv",
            encoding='utf-8-sig'
        )

        df = df[['가맹점구분번호', '가맹점명', '업종', '상권']].copy()
        df = df.dropna(subset=['가맹점구분번호', '가맹점명', '업종'])
        df['상권'] = df['상권'].fillna('미분류')

        return df

    except Exception as e:
        st.error(f"❌ 데이터 로드 실패: {e}")
        return pd.DataFrame(columns=['가맹점구분번호', '가맹점명', '업종', '상권'])

def create_positioning_map(stp_output):
    """포지셔닝 맵 시각화"""
    if not stp_output or not hasattr(stp_output, 'cluster_profiles'):
        return None
        
    fig = go.Figure()
    colors = px.colors.qualitative.Set3
    
    for i, cluster in enumerate(stp_output.cluster_profiles):
        fig.add_trace(go.Scatter(
            x=[cluster.pc1_mean],
            y=[cluster.pc2_mean],
            mode='markers+text',
            name=cluster.cluster_name,
            text=[cluster.cluster_name],
            textposition="top center",
            marker=dict(
                size=cluster.store_count / 2,
                color=colors[i % len(colors)],
                opacity=0.6
            )
        ))
    
    if stp_output.store_current_position:
        current = stp_output.store_current_position
        fig.add_trace(go.Scatter(
            x=[current.pc1_score],
            y=[current.pc2_score],
            mode='markers+text',
            name='현재 위치',
            text=['현재'],
            marker=dict(size=20, color='red', symbol='star')
        ))
    
    fig.update_layout(
        title='시장 포지셔닝 맵',
        xaxis_title='PC1',
        yaxis_title='PC2',
        height=500
    )
    
    return fig

def render_strategy_card(card, card_index):
    """
    🔥 전략 카드 HTML 렌더링
    
    Args:
        card: StrategyCard 객체
        card_index: 카드 번호 (1, 2, 3)
    """
    priority_class = f"priority-{card.priority.lower()}"
    
    # 데이터 근거 태그
    evidence_html = ""
    for ev in card.data_evidence[:5]:  # 상위 5개만
        evidence_html += f"<span class='evidence-tag'>{ev}</span>"
    
    card_html = f"""
    <div class='strategy-card'>
        <div class='card-title'>
            전략 카드 {card_index}: {card.title}
        </div>
        
        <span class='card-priority {priority_class}'>
            우선순위: {card.priority}
        </span>
        
        <div class='card-concept'>
            💡 <strong>포지셔닝 컨셉</strong><br>
            {card.positioning_concept}
        </div>
        
        <div class='card-section'>
            <div class='card-section-title'>
                📦 Product
            </div>
            <div class='card-section-content'>
                {card.strategy_4p.get('product', 'N/A')}
            </div>
        </div>
        
        <div class='card-section'>
            <div class='card-section-title'>
                💰 Price
            </div>
            <div class='card-section-content'>
                {card.strategy_4p.get('price', 'N/A')}
            </div>
        </div>
        
        <div class='card-section'>
            <div class='card-section-title'>
                🏪 Place
            </div>
            <div class='card-section-content'>
                {card.strategy_4p.get('place', 'N/A')}
            </div>
        </div>
        
        <div class='card-section'>
            <div class='card-section-title'>
                📢 Promotion
            </div>
            <div class='card-section-content'>
                {card.strategy_4p.get('promotion', 'N/A')}
            </div>
        </div>
        
        <div class='card-outcome'>
            📈 <strong>예상 효과</strong><br>
            {card.expected_outcome}
        </div>
        
        <div class='card-section'>
            <div class='card-section-title'>
                📊 데이터 근거
            </div>
            <div style='margin-top: 0.5rem;'>
                {evidence_html}
            </div>
        </div>
    </div>
    """
    
    return card_html

# ============================================================================
# Main App
# ============================================================================

st.markdown("<h1 class='main-header'>🎯 마케팅 전략 수립 시스템</h1>", unsafe_allow_html=True)

# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.title("🎯 설정")
    
    st.markdown("### 📍 가맹점 선택")

    store_df = load_store_list()

    # 🔍 검색 기능
    search_query = st.text_input(
        "🔍 가맹점 검색",
        placeholder="가맹점명 또는 업종으로 검색...",
        help="예: 축산, 성우, 한식 등"
    )

    # 검색 필터링
    if search_query:
        search_lower = search_query.lower()
        filtered_df = store_df[
            store_df['가맹점명'].str.lower().str.contains(search_lower, na=False) |
            store_df['업종'].str.lower().str.contains(search_lower, na=False)
        ]
        st.info(f"🔍 검색 결과: {len(filtered_df)}개 가맹점")
    else:
        # 업종 필터 (검색이 없을 때만)
        industries = ['전체'] + sorted(store_df['업종'].unique().tolist())
        selected_industry = st.selectbox("업종 필터", industries)

        if selected_industry != '전체':
            filtered_df = store_df[store_df['업종'] == selected_industry]
        else:
            filtered_df = store_df

    # 가맹점 선택
    if len(filtered_df) == 0:
        st.warning("⚠️ 검색 결과가 없습니다.")
        selected_store_id = None
        selected_store_name = None
    else:
        store_options = filtered_df.apply(
            lambda x: f"{x['가맹점명']} ({x['업종']}) - {x['상권']}",
            axis=1
        ).tolist()

        selected_store_display = st.selectbox(
            "가맹점",
            store_options,
            help=f"총 {len(store_options)}개 가맹점"
        )

        if selected_store_display:
            idx = store_options.index(selected_store_display)
            selected_store_id = filtered_df.iloc[idx]['가맹점구분번호']
            selected_store_name = filtered_df.iloc[idx]['가맹점명']
        else:
            selected_store_id = None
            selected_store_name = None
    
    st.markdown("---")
    
    # === 🆕 사용자 자유 입력 + 작업 유형 선택 ===
    st.markdown("### 💬 요청 사항")
    
    input_mode = st.radio(
        "입력 방식 선택",
        ["자유 입력 (AI가 작업 유형 판단)", "수동 선택 (작업 유형 직접 선택)"],
        index=0
    )
    
    user_input = None
    task_type = None
    
    if input_mode == "자유 입력 (AI가 작업 유형 판단)":
        st.markdown("#### 📝 원하시는 내용을 자유롭게 입력하세요")
        user_input = st.text_area(
            "예시: '비 오는 날 매출을 높일 방법을 알려줘', '인스타그램 콘텐츠 아이디어가 필요해'",
            height=100,
            placeholder="원하는 마케팅 전략이나 고민을 자유롭게 적어주세요..."
        )
        
        if user_input:
            # 🤖 LLM 기반 Intent 분류
            with st.spinner("🤖 AI가 의도를 분석 중..."):
                intent_result = classify_user_intent(user_input)

            task_type = intent_result.task_type

            # 판단 결과 표시
            task_type_display = {
                "종합_전략_수립": "📊 종합 전략 수립",
                "상황_전술_제안": "⚡ 상황 전술 제안",
                "콘텐츠_생성_가이드": "📱 콘텐츠 생성 가이드"
            }[task_type]

            st.info(f"🤖 **AI 판단**: {task_type_display}이 필요한 것 같아요!")
            st.success(f"✅ 선택된 작업 유형: **{task_type_display}** (확신도: {intent_result.confidence:.0%})")

            # 판단 근거 표시
            with st.expander("📊 AI 판단 근거"):
                st.write(f"**분석 결과**: {intent_result.reasoning}")
            
            # 사용자가 변경 원할 경우
            with st.expander("🔄 작업 유형을 변경하고 싶으신가요?"):
                override_task = st.selectbox(
                    "다른 작업 유형 선택",
                    ["종합_전략_수립", "상황_전술_제안", "콘텐츠_생성_가이드"],
                    format_func=lambda x: {
                        "종합_전략_수립": "📊 종합 전략 수립",
                        "상황_전술_제안": "⚡ 상황 전술 제안",
                        "콘텐츠_생성_가이드": "📱 콘텐츠 생성 가이드"
                    }[x]
                )
                if st.button("변경 적용"):
                    task_type = override_task
                    changed_display = {
                        "종합_전략_수립": "📊 종합 전략 수립",
                        "상황_전술_제안": "⚡ 상황 전술 제안",
                        "콘텐츠_생성_가이드": "📱 콘텐츠 생성 가이드"
                    }[task_type]
                    st.success(f"✅ 작업 유형이 변경되었습니다: **{changed_display}**")
    
    else:  # 수동 선택
        st.markdown("#### 🎨 작업 유형을 직접 선택하세요")
        task_type = st.radio(
            "선택하세요",
            ["종합_전략_수립", "상황_전술_제안", "콘텐츠_생성_가이드"],
            format_func=lambda x: {
                "종합_전략_수립": "📊 종합 전략 수립",
                "상황_전술_제안": "⚡ 상황 전술 제안",
                "콘텐츠_생성_가이드": "📱 콘텐츠 생성 가이드"
            }[x]
        )
        
        st.markdown("#### 📝 추가 요청 사항 (선택)")
        user_input = st.text_area(
            "원하는 내용을 자유롭게 입력하세요 (선택사항)",
            height=80,
            placeholder="예: 20대 고객을 타겟으로 한 전략이 필요해요"
        )
    
    st.markdown("---")
    
    # 추가 입력 (작업 유형별)
    target_market_id = None
    period_start = None
    period_end = None
    content_channels = []

    if task_type == "상황_전술_제안":
        st.markdown("### ⚡ 상황 정보")

        # 상황 분석 모드 선택 (필수)
        situation_mode = st.radio(
            "📊 상황 분석 모드",
            ["🌤️ 날씨 기반", "📅 이벤트 기반"],
            horizontal=True,
            help="날씨 또는 이벤트 중 하나를 선택하세요"
        )

        # 상권 정보 (필수)
        target_market_id = st.text_input(
            "📍 상권 ID 또는 지역명",
            value="성수동",
            placeholder="예: 성수동, 강남, 홍대 등",
            help="상황 정보를 수집할 지역을 입력하세요"
        )

        # 기간 설정 (필수)
        col1, col2 = st.columns(2)
        with col1:
            period_start = st.date_input("기간 시작", date.today())
        with col2:
            period_end = st.date_input("기간 종료", date.today() + timedelta(days=7))

        # 상황별 힌트 입력
        st.markdown("#### 📝 상황 설명 (선택사항)")

        if "날씨" in situation_mode:
            situation_hint = st.text_area(
                "날씨 상황",
                placeholder="예: 이번 주 폭염 예보, 주말에 강한 비 예상",
                height=80,
                help="예상되는 날씨 상황을 자유롭게 입력하세요"
            )
        else:  # 이벤트
            situation_hint = st.text_area(
                "이벤트 상황",
                placeholder="예: 성수동에서 대규모 축제 개최 예정, 주변 팝업스토어 오픈",
                height=80,
                help="예상되는 이벤트나 행사를 자유롭게 입력하세요"
            )

        # user_query 구성 (모드 + 힌트)
        mode_mapping = {
            "🌤️ 날씨 기반": "날씨",
            "📅 이벤트 기반": "이벤트"
        }
        mode_keyword = mode_mapping.get(situation_mode, "")

        if situation_hint:
            user_input = f"{mode_keyword} 분석: {situation_hint}"
        else:
            user_input = f"{mode_keyword} 분석"
    
    elif task_type == "콘텐츠_생성_가이드":
        st.markdown("### 📱 채널 선택")
        
        content_channels = st.multiselect(
            "콘텐츠 채널",
            ["Instagram", "Naver Blog", "YouTube Shorts", "TikTok", "카카오톡"],
            default=["Instagram"]
        )
        
        period_start = st.date_input("기간 시작", date.today())
        period_end = st.date_input("기간 종료", date.today() + timedelta(days=30))

    # 분석 시작 버튼 - task_type이 있을 때만 활성화
    if task_type:
        analyze_button = st.button("🚀 분석 시작", type="primary", use_container_width=True)
    else:
        st.warning("⚠️ 입력을 작성해주세요.")
        analyze_button = False

# ============================================================================
# Main Content
# ============================================================================

if analyze_button and selected_store_id:
    
    with st.spinner(f"📊 {task_type} 진행 중..."):
        
        try:
            # 사용자 입력이 있으면 표시
            if user_input and user_input.strip():
                st.info(f"💬 **사용자 요청**: {user_input}")
            
            # 시스템 실행
            result = run_marketing_system(
                target_store_id=selected_store_id,
                target_store_name=selected_store_name,
                task_type=task_type,
                user_query=user_input,  # 사용자 쿼리 전달 (날씨/행사 키워드 분석용)
                target_market_id=target_market_id,
                period_start=str(period_start) if period_start else None,
                period_end=str(period_end) if period_end else None,
                content_channels=content_channels
            )
            
            st.success("✅ 분석 완료!")
            
            # ================================================================
            # 🔥 작업 유형별 탭 구성 (전략 카드 포함)
            # ================================================================
            
            if task_type == "종합_전략_수립":
                # === 종합 전략: 4개 탭 (원본 구조 유지) ===
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📊 STP 분석",
                    "🎯 전략 카드 (3개)",  # 🔥 변경: 전략 수립 → 전략 카드
                    "📅 실행 계획",
                    "📄 최종 보고서"
                ])
                
                with tab1:
                    st.markdown("## 📊 STP 분석")
                    stp = result.get('stp_output')
                    
                    if stp:
                        # 포지셔닝 맵
                        fig = create_positioning_map(stp)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # 클러스터 정보
                        st.markdown("### 군집 정보")
                        for cluster in stp.cluster_profiles:
                            st.info(f"**{cluster.cluster_name}**: {cluster.characteristics}")
                    else:
                        st.warning("STP 데이터가 없습니다.")
                
                with tab2:
                    st.markdown("## 🎯 데이터 기반 3가지 전략 카드")
                    
                    strategy_cards = result.get('strategy_cards', [])
                    
                    if strategy_cards and len(strategy_cards) >= 3:
                        # 🔥 3개 카드 가로 배치
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(render_strategy_card(strategy_cards[0], 1), unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(render_strategy_card(strategy_cards[1], 2), unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(render_strategy_card(strategy_cards[2], 3), unsafe_allow_html=True)
                        
                        # 선택된 전략 표시
                        st.markdown("---")
                        selected_strategy = result.get('selected_strategy')
                        if selected_strategy:
                            st.success(f"✅ **추천 전략**: {selected_strategy.title} (우선순위: {selected_strategy.priority})")
                    
                    else:
                        st.warning("⚠️ 전략 카드가 생성되지 않았습니다.")
                        
                        # Fallback: 기존 4P 전략 표시 (원본 스타일 유지)
                        strategy = result.get('strategy_4p')
                        if strategy:
                            st.markdown("### 📋 4P 전략")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("#### 🎨 Product")
                                st.write(strategy.product)
                                st.markdown("#### 📍 Place")
                                st.write(strategy.place)
                            with col2:
                                st.markdown("#### 💰 Price")
                                st.write(strategy.price)
                                st.markdown("#### 📢 Promotion")
                                st.write(strategy.promotion)
                
                with tab3:
                    st.markdown("## 📅 실행 계획")
                    st.markdown(result.get('execution_plan', '계획 없음'))
                
                with tab4:
                    st.markdown("## 📄 최종 보고서")
                    st.download_button(
                        "📥 보고서 다운로드",
                        data=result.get('final_report', ''),
                        file_name=f"report_{selected_store_name}.txt"
                    )
                    st.markdown(result.get('final_report', '보고서 없음'))
            
            elif task_type == "상황_전술_제안":
                # === 상황 전술: 2개 탭 ===
                tab1, tab2 = st.tabs(["📡 상황 분석", "⚡ 전술 카드"])
                
                with tab1:
                    st.markdown("## 📡 상황 분석")
                    situation = result.get('situation', {})
                    
                    st.info(f"**요약**: {situation.get('summary', 'N/A')}")
                    
                    # 신호 카드
                    signals = situation.get('signals', [])
                    if signals:
                        st.markdown("### 🔔 수집된 신호")
                        for sig in signals:
                            st.markdown(f"""
                            <div class='signal-card'>
                                <h4>{sig.get('description', 'N/A')}</h4>
                                <p><strong>유형</strong>: {sig.get('signal_type', 'N/A')}</p>
                                <p><strong>관련도</strong>: {sig.get('relevance', 0):.2f}</p>
                                <p><em>{sig.get('reason', '')}</em></p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("신호 없음")
                
                with tab2:
                    st.markdown("## ⚡ 긴급 전술 카드")
                    
                    # 전략 카드가 있으면 표시
                    strategy_cards = result.get('strategy_cards', [])
                    if strategy_cards:
                        for i, card in enumerate(strategy_cards[:3], 1):
                            st.markdown(render_strategy_card(card, i), unsafe_allow_html=True)
                    else:
                        # Fallback
                        strategy = result.get('strategy_4p')
                        if strategy:
                            st.success(f"**Product**: {strategy.product}")
                            st.warning(f"**Price**: {strategy.price}")
                            st.info(f"**Place**: {strategy.place}")
                            st.error(f"**Promotion**: {strategy.promotion}")
            
            else:  # 콘텐츠_생성_가이드
                # === 콘텐츠 가이드: 2개 탭 ===
                tab1, tab2 = st.tabs(["📱 콘텐츠 가이드", "📄 보고서"])
                
                with tab1:
                    st.markdown("## 📱 채널별 콘텐츠 가이드")
                    content_guide = result.get('content_guide', {})

                    if content_guide:
                        # 🎨 무드보드 섹션
                        st.markdown("### 🎨 무드보드")
                        mood_board = content_guide.get('mood_board', [])
                        if mood_board:
                            # 무드보드 키워드를 박스로 표시
                            cols = st.columns(min(len(mood_board), 5))
                            for i, keyword in enumerate(mood_board):
                                with cols[i % 5]:
                                    st.info(f"**{keyword}**")
                        else:
                            st.write("무드보드 정보 없음")

                        # 브랜드 톤앤매너
                        st.markdown("### 🎭 브랜드 톤앤매너")
                        brand_tone = content_guide.get('brand_tone', 'N/A')
                        st.success(f"**{brand_tone}**")

                        # 타겟 고객
                        st.markdown("### 🎯 타겟 고객")
                        target_audience = content_guide.get('target_audience', 'N/A')
                        st.write(target_audience)

                        st.markdown("---")

                        # 전체 전략
                        st.markdown("### 📊 전체 콘텐츠 전략")
                        st.info(content_guide.get('overall_strategy', 'N/A'))

                        st.markdown("---")

                        # 채널별
                        st.markdown("### 📺 채널별 가이드")
                        channels = content_guide.get('channels', [])
                        for ch in channels:
                            with st.expander(f"📱 {ch.get('channel_name', 'N/A')}", expanded=True):
                                # 기본 정보
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**포스팅 형식**: {ch.get('post_format', 'N/A')}")
                                    st.write(f"**게시 빈도**: {ch.get('posting_frequency', 'N/A')}")
                                with col2:
                                    st.write(f"**최적 시간**: {ch.get('best_time', 'N/A')}")

                                # 시각적 방향
                                visual_direction = ch.get('visual_direction', [])
                                if visual_direction:
                                    st.markdown("**🎬 시각적 방향**")
                                    st.write(", ".join(visual_direction))

                                # 카피 예시
                                st.markdown("**✍️ 카피 예시**")
                                for i, ex in enumerate(ch.get('copy_examples', []), 1):
                                    st.write(f"{i}. {ex}")

                                # 해시태그
                                tags = ch.get('hashtags', [])
                                if tags:
                                    st.markdown("**#️⃣ 해시태그**")
                                    st.code(" ".join([f"#{t}" for t in tags[:15]]))

                                # 콘텐츠 팁
                                tips = ch.get('content_tips', [])
                                if tips:
                                    st.markdown("**💡 콘텐츠 팁**")
                                    for tip in tips:
                                        st.write(f"• {tip}")

                        # 금기 사항
                        do_not_list = content_guide.get('do_not_list', [])
                        if do_not_list:
                            st.markdown("---")
                            st.markdown("### ⚠️ 금기 사항")
                            for item in do_not_list:
                                st.warning(f"• {item}")
                    else:
                        st.warning("콘텐츠 가이드가 없습니다.")
                
                with tab2:
                    st.markdown("## 📄 보고서")
                    st.markdown(result.get('final_report', '보고서 없음'))
        
        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")
            st.exception(e)

elif analyze_button and not selected_store_id:
    st.warning("⚠️ 가맹점을 먼저 선택해주세요.")

else:
    # 초기 화면 (원본 스타일 유지)
    st.markdown("""
    <div class='task-card'>
        <h3>📊 종합 전략 수립</h3>
        <p><strong>목적</strong>: STP 분석 기반 장기 전략</p>
        <ul>
            <li>포지셔닝 맵 분석</li>
            <li>4P 전략 (Product, Price, Place, Promotion)</li>
            <li>실행 계획 수립</li>
            <li>🔥 <strong>NEW: 데이터 기반 전략 카드 3개</strong></li>
        </ul>
    </div>
    
    <div class='task-card'>
        <h3>⚡ 상황 전술 제안</h3>
        <p><strong>목적</strong>: 즉각 대응 전술</p>
        <ul>
            <li>날씨 기반 전술 (비, 폭염, 한파)</li>
            <li>이벤트 연계 프로모션</li>
            <li>긴급 Flash Sale</li>
        </ul>
    </div>
    
    <div class='task-card'>
        <h3>📱 콘텐츠 생성 가이드</h3>
        <p><strong>목적</strong>: 채널별 콘텐츠 템플릿</p>
        <ul>
            <li>Instagram 릴스 스크립트</li>
            <li>Naver Blog 포스팅 가이드</li>
            <li>카피 예시</li>
            <li>해시태그 전략</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# Footer
# ============================================================================

st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>Powered by Langchain, Langgraph, and Gemini 2.5 Flash</p>
    <p>© 2025 Marketing AI Team</p>
</div>
""", unsafe_allow_html=True)