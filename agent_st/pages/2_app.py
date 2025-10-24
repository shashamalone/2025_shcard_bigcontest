"""
Streamlit UI for Marketing MultiAgent System
=============================================
사용자 친화적인 마케팅 전략 수립 인터페이스
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys

# 메인 시스템 임포트
sys.path.append(str(Path(__file__).parent))
from marketing_multiagent_system_improved import (
    run_marketing_strategy_system,
    STPDataLoader,
    TrendRAGSystem
)

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
# Custom CSS
# ============================================================================

st.markdown("""
<style>
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
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Helper Functions
# ============================================================================

@st.cache_data
def load_store_list():
    """가맹점 목록 로드"""
    loader = STPDataLoader()
    loader.load_all_data()
    df = loader.store_positioning[['가맹점구분번호', '가맹점명', '업종', '상권']].dropna()
    return df

def create_positioning_map(stp_output, recommended_ws):
    """포지셔닝 맵 시각화"""
    fig = go.Figure()
    
    # 클러스터별 색상
    colors = px.colors.qualitative.Set3
    
    # 각 클러스터 표시
    for i, cluster in enumerate(stp_output.cluster_profiles):
        fig.add_trace(go.Scatter(
            x=[cluster.pc1_mean],
            y=[cluster.pc2_mean],
            mode='markers+text',
            name=cluster.cluster_name,
            text=[cluster.cluster_name],
            textposition="top center",
            marker=dict(
                size=cluster.store_count / 2,  # 크기는 가맹점 수에 비례
                color=colors[i % len(colors)],
                opacity=0.6,
                line=dict(width=2, color='white')
            ),
            hovertemplate=f"<b>{cluster.cluster_name}</b><br>"
                         f"PC1: {cluster.pc1_mean:.2f}<br>"
                         f"PC2: {cluster.pc2_mean:.2f}<br>"
                         f"가맹점 수: {cluster.store_count}<br>"
                         f"{cluster.characteristics}<extra></extra>"
        ))
    
    # 우리 가맹점 현재 위치
    current_pos = stp_output.store_current_position
    fig.add_trace(go.Scatter(
        x=[current_pos.pc1_score],
        y=[current_pos.pc2_score],
        mode='markers+text',
        name='현재 위치',
        text=['현재'],
        textposition="top center",
        marker=dict(
            size=20,
            color='red',
            symbol='star',
            line=dict(width=2, color='darkred')
        ),
        hovertemplate=f"<b>현재 위치</b><br>"
                     f"PC1: {current_pos.pc1_score:.2f}<br>"
                     f"PC2: {current_pos.pc2_score:.2f}<extra></extra>"
    ))
    
    # 추천 포지션
    if recommended_ws:
        fig.add_trace(go.Scatter(
            x=[recommended_ws.pc1_coord],
            y=[recommended_ws.pc2_coord],
            mode='markers+text',
            name='추천 포지션',
            text=['목표'],
            textposition="top center",
            marker=dict(
                size=20,
                color='gold',
                symbol='diamond',
                line=dict(width=2, color='orange')
            ),
            hovertemplate=f"<b>추천 포지션</b><br>"
                         f"PC1: {recommended_ws.pc1_coord:.2f}<br>"
                         f"PC2: {recommended_ws.pc2_coord:.2f}<br>"
                         f"기회 점수: {recommended_ws.opportunity_score:.2f}<br>"
                         f"{recommended_ws.reasoning}<extra></extra>"
        ))
    
    # 레이아웃
    pc1_interp = stp_output.pc_axis_interpretation['PC1'].interpretation
    pc2_interp = stp_output.pc_axis_interpretation['PC2'].interpretation
    
    fig.update_layout(
        title={
            'text': '시장 포지셔닝 맵',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#1f77b4'}
        },
        xaxis_title=f'PC1: {pc1_interp}',
        yaxis_title=f'PC2: {pc2_interp}',
        hovermode='closest',
        showlegend=True,
        height=600,
        plot_bgcolor='rgba(240, 242, 246, 0.5)'
    )
    
    return fig

def display_4p_strategy(strategy_4p):
    """4P 전략 카드 표시"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎨 Product (제품)")
        st.markdown(f"<div class='metric-card'>{strategy_4p.product}</div>", unsafe_allow_html=True)
        
        st.markdown("#### 📍 Place (유통)")
        st.markdown(f"<div class='metric-card'>{strategy_4p.place}</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 💰 Price (가격)")
        st.markdown(f"<div class='metric-card'>{strategy_4p.price}</div>", unsafe_allow_html=True)
        
        st.markdown("#### 📢 Promotion (프로모션)")
        st.markdown(f"<div class='metric-card'>{strategy_4p.promotion}</div>", unsafe_allow_html=True)

# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=Marketing+AI", width="stretch")
    
    st.markdown("### 📋 가맹점 선택")
    
    # 가맹점 리스트 로드
    try:
        store_df = load_store_list()
        
        # 업종 필터
        industries = ['전체'] + sorted(store_df['업종'].unique().tolist())
        selected_industry = st.selectbox("업종 필터", industries)
        
        if selected_industry != '전체':
            filtered_df = store_df[store_df['업종'] == selected_industry]
        else:
            filtered_df = store_df
        
        # 가맹점 선택
        store_options = filtered_df.apply(
            lambda x: f"{x['가맹점명']} ({x['업종']}, {x['상권']})",
            axis=1
        ).tolist()
        
        selected_store_display = st.selectbox(
            "가맹점 선택",
            store_options,
            index=0 if store_options else None
        )
        
        if selected_store_display:
            idx = store_options.index(selected_store_display)
            selected_store_id = filtered_df.iloc[idx]['가맹점구분번호']
            selected_store_name = filtered_df.iloc[idx]['가맹점명']
        else:
            selected_store_id = None
            selected_store_name = None
    
    except Exception as e:
        st.error(f"데이터 로딩 실패: {e}")
        selected_store_id = None
        selected_store_name = None
    
    st.markdown("---")
    
    st.markdown("### ⚙️ 분석 옵션")
    
    enable_rag = st.checkbox("외부 트렌드 데이터 활용", value=True)
    detail_level = st.radio(
        "상세도",
        ["간단", "보통", "상세"],
        index=1
    )
    
    st.markdown("---")
    
    analyze_button = st.button("🚀 전략 분석 시작", type="primary", width="stretch")

# ============================================================================
# Main Content
# ============================================================================

st.markdown("<div class='main-header'>🎯 마케팅 전략 수립 시스템</div>", unsafe_allow_html=True)

# 분석 실행
if analyze_button and selected_store_id:
    
    with st.spinner("🔄 마케팅 전략을 분석하고 있습니다... (약 30초 소요)"):
        
        try:
            # 시스템 실행
            result = run_marketing_strategy_system(
                target_store_id=selected_store_id,
                target_store_name=selected_store_name
            )
            
            st.success("✅ 분석 완료!")
            
            # ================================================================
            # Tab Layout
            # ================================================================
            
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 STP 분석",
                "🎯 전략 수립",
                "📅 실행 계획",
                "📄 최종 보고서"
            ])
            
            # ---- Tab 1: STP 분석 ----
            with tab1:
                st.markdown("<div class='section-header'>Segmentation (시장 세분화)</div>", unsafe_allow_html=True)
                
                stp_output = result['stp_output']
                
                # 클러스터 정보
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("전체 군집 수", len(stp_output.cluster_profiles))
                with col2:
                    st.metric("타겟 군집", stp_output.target_cluster_name)
                with col3:
                    total_stores = sum(c.store_count for c in stp_output.cluster_profiles)
                    st.metric("전체 가맹점 수", total_stores)
                
                # 클러스터 상세
                st.markdown("##### 군집별 특성")
                cluster_data = []
                for cluster in stp_output.cluster_profiles:
                    cluster_data.append({
                        "군집 ID": cluster.cluster_id,
                        "군집명": cluster.cluster_name,
                        "가맹점 수": cluster.store_count,
                        "PC1 평균": f"{cluster.pc1_mean:.2f}",
                        "PC2 평균": f"{cluster.pc2_mean:.2f}",
                        "특성": cluster.characteristics
                    })
                
                st.dataframe(
                    pd.DataFrame(cluster_data),
                    width="stretch",
                    hide_index=True
                )
                
                # PC축 해석
                st.markdown("##### PC축 해석")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**PC1 (X축)**")
                    pc1 = stp_output.pc_axis_interpretation['PC1']
                    st.info(f"**의미:** {pc1.interpretation}")
                    
                    st.markdown("주요 영향 요인:")
                    for feat in pc1.top_features:
                        st.markdown(f"- {feat['속성']}: {feat['가중치']} ({feat['설명']})")
                
                with col2:
                    st.markdown("**PC2 (Y축)**")
                    pc2 = stp_output.pc_axis_interpretation['PC2']
                    st.info(f"**의미:** {pc2.interpretation}")
                    
                    st.markdown("주요 영향 요인:")
                    for feat in pc2.top_features:
                        st.markdown(f"- {feat['속성']}: {feat['가중치']} ({feat['설명']})")
                
                st.markdown("<div class='section-header'>Targeting & Positioning</div>", unsafe_allow_html=True)
                
                # 포지셔닝 맵
                fig = create_positioning_map(stp_output, stp_output.recommended_white_space)
                st.plotly_chart(fig, width="stretch")
                
                # 현재 위치 vs 추천 위치
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 📍 현재 포지션")
                    current = stp_output.store_current_position
                    st.markdown(f"""
                    - **PC1:** {current.pc1_score:.2f}
                    - **PC2:** {current.pc2_score:.2f}
                    - **소속 군집:** {current.cluster_name}
                    """)
                
                with col2:
                    st.markdown("##### 🎯 추천 포지션")
                    recommended = stp_output.recommended_white_space
                    if recommended:
                        st.markdown(f"""
                        - **PC1:** {recommended.pc1_coord:.2f}
                        - **PC2:** {recommended.pc2_coord:.2f}
                        - **기회 점수:** {recommended.opportunity_score:.2f}
                        """)
                        st.success(f"💡 {recommended.reasoning}")
                    else:
                        st.warning("추천 포지션을 찾을 수 없습니다.")
            
            # ---- Tab 2: 전략 수립 ----
            with tab2:
                st.markdown("<div class='section-header'>포지셔닝 컨셉</div>", unsafe_allow_html=True)
                
                positioning_concept = result['positioning_concept']
                st.markdown(f"""
                <div class='success-box'>
                    <h4>🎯 {selected_store_name}의 차별화 메시지</h4>
                    <p style='font-size:1.1rem;'>{positioning_concept}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<div class='section-header'>4P 마케팅 전략</div>", unsafe_allow_html=True)
                
                strategy_4p = result['strategy_4p']
                display_4p_strategy(strategy_4p)
            
            # ---- Tab 3: 실행 계획 ----
            with tab3:
                st.markdown("<div class='section-header'>주차별 실행 계획</div>", unsafe_allow_html=True)
                
                execution_plan = result['execution_plan']
                st.markdown(execution_plan)
                
                # 타임라인 시각화 (간단한 Gantt 차트)
                st.markdown("##### 📅 실행 타임라인")
                
                weeks = ["1주차", "2주차", "3주차", "4주차"]
                tasks = [
                    "Product 전략 실행",
                    "Price 전략 실행",
                    "Place 전략 실행",
                    "Promotion 전략 실행"
                ]
                
                timeline_data = []
                for i, task in enumerate(tasks):
                    timeline_data.append({
                        "Task": task,
                        "Start": i,
                        "End": i + 1
                    })

                fig = px.timeline(
                    timeline_data,
                    x_start="Start",
                    x_end="End",
                    y="Task",
                    title="실행 타임라인"
                )
                fig.update_yaxes(categoryorder="total ascending")
                st.plotly_chart(fig, width="stretch")
            
            # ---- Tab 4: 최종 보고서 ----
            with tab4:
                st.markdown("<div class='section-header'>최종 마케팅 전략 보고서</div>", unsafe_allow_html=True)
                
                final_report = result['final_report']
                
                # 다운로드 버튼
                st.download_button(
                    label="📥 보고서 다운로드 (TXT)",
                    data=final_report,
                    file_name=f"marketing_strategy_{selected_store_name}.txt",
                    mime="text/plain"
                )
                
                st.markdown("---")
                
                # 보고서 내용
                st.markdown(final_report)
        
        except Exception as e:
            st.error(f"❌ 분석 중 오류가 발생했습니다: {e}")
            st.exception(e)

elif analyze_button and not selected_store_id:
    st.warning("⚠️ 가맹점을 먼저 선택해주세요.")

else:
    # 초기 화면
    st.markdown("""
    ### 👋 환영합니다!
    
    이 시스템은 **STP 분석**과 **AI 에이전트 팀**을 활용하여 
    소상공인을 위한 맞춤형 마케팅 전략을 자동으로 수립합니다.
    
    #### 🔄 분석 프로세스
    
    1. **Segmentation (시장 세분화)**
       - K-Means 클러스터링으로 경쟁 그룹 정의
       - PCA 기반 포지셔닝 맵 생성
    
    2. **Targeting (타겟 선정)**
       - 우리 가맹점의 현재 포지션 파악
       - 공략 대상 군집 선정
    
    3. **Positioning (차별화 전략)**
       - White Space (빈 포지션) 탐지
       - 최적 포지셔닝 좌표 추천
    
    4. **4P 전략 수립**
       - Product, Price, Place, Promotion 전략
       - 외부 트렌드 데이터 통합 (RAG)
    
    5. **실행 계획 생성**
       - 주차별 액션 플랜
       - 타임라인 시각화
    
    #### 🚀 시작하기
    
    왼쪽 사이드바에서 가맹점을 선택하고 **전략 분석 시작** 버튼을 눌러주세요!
    """)
    
    # 데모 이미지 (선택사항)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://via.placeholder.com/300x200/2ca02c/ffffff?text=STP+Analysis", width="stretch")
        st.caption("STP 분석")
    with col2:
        st.image("https://via.placeholder.com/300x200/ff7f0e/ffffff?text=4P+Strategy", width="stretch")
        st.caption("4P 전략")
    with col3:
        st.image("https://via.placeholder.com/300x200/d62728/ffffff?text=Action+Plan", width="stretch")
        st.caption("실행 계획")

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>Powered by Langchain, Langgraph, and Gemini 2.5 Pro</p>
    <p>© 2025 Marketing AI Team. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
