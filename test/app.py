"""
Marketing MultiAgent System for Small Businesses
개선된 STP 기반 마케팅 전략 자동화 시스템
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
from typing import TypedDict, List, Annotated, Literal, Dict, Any
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
import json
from datetime import datetime

# ============================================================================
# 환경 설정
# ============================================================================

# Gemini API 키 설정 (환경 변수 또는 Streamlit secrets 사용)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")

# Gemini 2.5 Pro 모델 초기화
def get_gemini_model(temperature=0.7):
    """Gemini 2.5 Pro 모델 인스턴스 생성"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",  # 최신 모델명으로 업데이트 필요
        google_api_key=GOOGLE_API_KEY,
        temperature=temperature
    )


# ============================================================================
# 상태 정의
# ============================================================================

class SuperGraphState(TypedDict):
    """최상위 그래프 상태"""
    messages: Annotated[List[BaseMessage], operator.add]
    user_input: str
    business_data: Dict[str, Any]  # CSV 업로드 데이터
    intent_tags: List[str]
    next: str
    final_output: str


class AnalysisTeamState(TypedDict):
    """분석팀 상태 (STP 분석)"""
    messages: Annotated[List[BaseMessage], operator.add]
    business_data: Dict[str, Any]
    
    # Segmentation 결과
    cluster_features: Dict[int, Dict[str, Any]]  # 각 클러스터의 특징
    pca_components: Dict[str, Any]  # PCA 축 해석
    
    # Targeting 결과
    target_cluster: int  # 선정된 타겟 클러스터
    our_position: Dict[str, float]  # 우리 가맹점의 PC1, PC2 좌표
    
    # Positioning 결과
    white_space_position: Dict[str, float]  # 빈 포지션 좌표
    nearby_competitors: List[Dict[str, Any]]  # 인근 경쟁사 정보
    
    team_members: List[str]
    next: str
    stp_report: str


class StrategyTeamState(TypedDict):
    """전략팀 상태"""
    messages: Annotated[List[BaseMessage], operator.add]
    
    # 분석팀으로부터 받은 STP 결과
    stp_results: Dict[str, Any]
    
    # Strategy Agent 출력
    positioning_concept: str  # 포지셔닝 컨셉
    four_p_strategy: Dict[str, str]  # Product, Price, Place, Promotion
    
    # Situation Agent 출력 (단기 전술)
    situational_tactics: List[Dict[str, Any]]
    
    # Content Agent 출력
    execution_content: str
    
    team_members: List[str]
    next: str
    strategy_document: str


# ============================================================================
# 분석팀 에이전트들
# ============================================================================

class DataCruncherAgent:
    """데이터 분석가 - K-Means 클러스터링 및 PCA 수행"""
    
    def __init__(self):
        self.llm = get_gemini_model(temperature=0.3)
    
    def run(self, state: AnalysisTeamState) -> AnalysisTeamState:
        """데이터 분석 실행"""
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        from sklearn.decomposition import PCA
        
        business_data = state["business_data"]
        df = pd.DataFrame(business_data)
        
        # 분석용 특성 선택
        feature_columns = [col for col in df.columns if df[col].dtype in ['float64', 'int64']]
        X = df[feature_columns].fillna(df[feature_columns].mean())
        
        # 표준화
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # K-Means 클러스터링 (k=4로 설정)
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        df['cluster'] = clusters
        
        # PCA (2차원으로 축소)
        pca = PCA(n_components=2)
        pca_coords = pca.fit_transform(X_scaled)
        df['PC1'] = pca_coords[:, 0]
        df['PC2'] = pca_coords[:, 1]
        
        # 클러스터별 특징 추출
        cluster_features = {}
        for cluster_id in range(4):
            cluster_data = df[df['cluster'] == cluster_id]
            cluster_features[cluster_id] = {
                'size': len(cluster_data),
                'mean_features': cluster_data[feature_columns].mean().to_dict(),
                'centroid_pc1': cluster_data['PC1'].mean(),
                'centroid_pc2': cluster_data['PC2'].mean()
            }
        
        # PCA 성분 해석 (LLM 활용)
        pca_variance = pca.explained_variance_ratio_
        pca_components_values = pca.components_
        
        interpretation_prompt = f"""
다음은 가맹점 데이터의 PCA 분석 결과입니다.

특성 목록: {feature_columns}
PC1 설명 분산: {pca_variance[0]:.2%}
PC2 설명 분산: {pca_variance[1]:.2%}

PC1 가중치: {dict(zip(feature_columns, pca_components_values[0]))}
PC2 가중치: {dict(zip(feature_columns, pca_components_values[1]))}

각 주성분(PC1, PC2)이 무엇을 의미하는지 비즈니스 관점에서 해석하세요.
예: PC1은 '객단가 수준', PC2는 '재방문율 안정성' 등
"""
        
        interpretation_response = self.llm.invoke([HumanMessage(content=interpretation_prompt)])
        
        state["cluster_features"] = cluster_features
        state["pca_components"] = {
            'variance_explained': pca_variance.tolist(),
            'interpretation': interpretation_response.content,
            'feature_weights': {
                'PC1': dict(zip(feature_columns, pca_components_values[0])),
                'PC2': dict(zip(feature_columns, pca_components_values[1]))
            }
        }
        
        # 업데이트된 데이터프레임 저장
        state["business_data"]["df_with_clusters"] = df.to_dict('records')
        
        msg = AIMessage(content=f"✅ K-Means 클러스터링 완료 (4개 클러스터)\n✅ PCA 차원축소 완료\n\nPC 해석:\n{interpretation_response.content}")
        state["messages"].append(msg)
        
        return state


class InsightExtractorAgent:
    """인사이트 추출가 - Targeting & Positioning"""
    
    def __init__(self):
        self.llm = get_gemini_model(temperature=0.5)
    
    def run(self, state: AnalysisTeamState) -> AnalysisTeamState:
        """타겟 선정 및 포지셔닝 기회 발견"""
        
        cluster_features = state["cluster_features"]
        df_records = state["business_data"]["df_with_clusters"]
        df = pd.DataFrame(df_records)
        
        # 1. Targeting: 가장 매력적인 클러스터 선정 (LLM 판단)
        cluster_summary = "\n".join([
            f"클러스터 {cid}: 규모={info['size']}, PC1평균={info['centroid_pc1']:.2f}, PC2평균={info['centroid_pc2']:.2f}"
            for cid, info in cluster_features.items()
        ])
        
        targeting_prompt = f"""
다음 클러스터 중 소규모 사업자가 공략하기 가장 적합한 타겟을 선정하세요.

{cluster_summary}

PC 해석: {state['pca_components']['interpretation']}

선정 기준:
- 시장 규모가 적절한가?
- 경쟁 강도가 적절한가?
- 성장 가능성이 있는가?

JSON 형식으로 응답:
{{"target_cluster": <숫자>, "reason": "<이유>"}}
"""
        
        targeting_response = self.llm.invoke([HumanMessage(content=targeting_prompt)])
        try:
            targeting_result = json.loads(targeting_response.content.strip().replace("```json", "").replace("```", ""))
            target_cluster = targeting_result["target_cluster"]
        except:
            target_cluster = 0  # 기본값
        
        state["target_cluster"] = target_cluster
        
        # 우리 가맹점 위치 (임의로 타겟 클러스터 내 점 선택)
        our_data = df[df['cluster'] == target_cluster].iloc[0]
        state["our_position"] = {
            'PC1': float(our_data['PC1']),
            'PC2': float(our_data['PC2'])
        }
        
        # 2. Positioning: White Space 탐지
        # 그리드 기반으로 빈 공간 찾기
        pc1_range = (df['PC1'].min(), df['PC1'].max())
        pc2_range = (df['PC2'].min(), df['PC2'].max())
        
        # 10x10 그리드 생성
        grid_pc1 = np.linspace(pc1_range[0], pc1_range[1], 10)
        grid_pc2 = np.linspace(pc2_range[0], pc2_range[1], 10)
        
        # 각 그리드 셀의 밀도 계산
        min_density = float('inf')
        white_space_pos = {'PC1': 0, 'PC2': 0}
        
        for i in range(len(grid_pc1) - 1):
            for j in range(len(grid_pc2) - 1):
                cell_df = df[
                    (df['PC1'] >= grid_pc1[i]) & (df['PC1'] < grid_pc1[i+1]) &
                    (df['PC2'] >= grid_pc2[j]) & (df['PC2'] < grid_pc2[j+1])
                ]
                if len(cell_df) < min_density:
                    min_density = len(cell_df)
                    white_space_pos = {
                        'PC1': (grid_pc1[i] + grid_pc1[i+1]) / 2,
                        'PC2': (grid_pc2[j] + grid_pc2[j+1]) / 2
                    }
        
        state["white_space_position"] = white_space_pos
        
        # 빈 포지션 인근 경쟁사 탐색 (거리 기준 상위 5개)
        df['distance_to_white_space'] = np.sqrt(
            (df['PC1'] - white_space_pos['PC1'])**2 + 
            (df['PC2'] - white_space_pos['PC2'])**2
        )
        nearby = df.nsmallest(5, 'distance_to_white_space')
        
        state["nearby_competitors"] = nearby.to_dict('records')
        
        msg = AIMessage(content=f"""
✅ 타겟 클러스터 선정: 클러스터 {target_cluster}
✅ 우리 포지션: PC1={state['our_position']['PC1']:.2f}, PC2={state['our_position']['PC2']:.2f}
✅ White Space 발견: PC1={white_space_pos['PC1']:.2f}, PC2={white_space_pos['PC2']:.2f}
""")
        state["messages"].append(msg)
        
        return state


class AnalysisTeamSupervisor:
    """분석팀 감독자"""
    
    def __init__(self):
        self.llm = get_gemini_model(temperature=0.3)
    
    def run(self, state: AnalysisTeamState) -> AnalysisTeamState:
        """작업 할당 및 완료 판단"""
        
        # 필요한 작업 체크
        has_clusters = "cluster_features" in state and state["cluster_features"]
        has_targeting = "target_cluster" in state
        has_positioning = "white_space_position" in state
        
        if not has_clusters:
            state["next"] = "DataCruncher"
        elif not (has_targeting and has_positioning):
            state["next"] = "InsightExtractor"
        else:
            # STP 보고서 생성
            report = f"""
# STP 분석 보고서

## Segmentation (시장 세분화)
- 총 {len(state['cluster_features'])} 개의 시장 군집 발견
- PCA 분석: {state['pca_components']['interpretation']}

{chr(10).join([f"### 클러스터 {cid}\n- 규모: {info['size']}개 가맹점\n- 중심: PC1={info['centroid_pc1']:.2f}, PC2={info['centroid_pc2']:.2f}" 
               for cid, info in state['cluster_features'].items()])}

## Targeting (목표 시장 선정)
- **선정된 타겟 클러스터**: {state['target_cluster']}
- **우리 가맹점 현재 위치**: PC1={state['our_position']['PC1']:.2f}, PC2={state['our_position']['PC2']:.2f}

## Positioning (포지셔닝)
- **White Space (차별화 기회 지점)**: PC1={state['white_space_position']['PC1']:.2f}, PC2={state['white_space_position']['PC2']:.2f}
- **인근 경쟁사 수**: {len(state['nearby_competitors'])}개

---
분석팀 작업 완료. 전략팀으로 이관.
"""
            state["stp_report"] = report
            state["next"] = "FINISH"
        
        return state


# ============================================================================
# 전략팀 에이전트들
# ============================================================================

class StrategyAgent:
    """전략 에이전트 - STP 결과 기반 4P 전략 수립"""
    
    def __init__(self):
        self.llm = get_gemini_model(temperature=0.7)
    
    def run(self, state: StrategyTeamState) -> StrategyTeamState:
        """4P 전략 생성"""
        
        stp_results = state["stp_results"]
        
        # RAG 시뮬레이션 (실제로는 벡터DB 검색)
        industry_trends = """
[트렌드 데이터베이스]
- 2025년 외식업 트렌드: 건강식, 비건 옵션, 로컬 푸드
- 고객 선호: 프리미엄 경험, SNS 인증샷
- 배달 서비스 확대: 배달 전용 메뉴 필요
"""
        
        strategy_prompt = f"""
당신은 소규모 사업자를 위한 마케팅 전략가입니다.

## STP 분석 결과
{json.dumps(stp_results, indent=2, ensure_ascii=False)}

## 업계 트렌드
{industry_trends}

위 정보를 바탕으로 다음을 제안하세요:

1. **Positioning Concept**: White Space로 이동하기 위한 핵심 컨셉 (한 문장)
2. **4P 전략**:
   - Product: 시그니처 메뉴 또는 서비스 개선 제안
   - Price: 객단가 전략 (PC1 좌표 기반)
   - Place: 유통 채널 전략
   - Promotion: 타겟 고객 대상 프로모션

JSON 형식으로 응답:
{{
  "positioning_concept": "<컨셉>",
  "four_p": {{
    "product": "<제안>",
    "price": "<제안>",
    "place": "<제안>",
    "promotion": "<제안>"
  }}
}}
"""
        
        response = self.llm.invoke([HumanMessage(content=strategy_prompt)])
        try:
            result = json.loads(response.content.strip().replace("```json", "").replace("```", ""))
            state["positioning_concept"] = result["positioning_concept"]
            state["four_p_strategy"] = result["four_p"]
        except:
            state["positioning_concept"] = "프리미엄 가치 제공"
            state["four_p_strategy"] = {
                "product": "시그니처 메뉴 개발",
                "price": "중상급 가격대",
                "place": "배달 채널 확대",
                "promotion": "SNS 마케팅"
            }
        
        msg = AIMessage(content=f"✅ 포지셔닝 컨셉: {state['positioning_concept']}\n✅ 4P 전략 수립 완료")
        state["messages"].append(msg)
        
        return state


class SituationAgent:
    """상황 분석 에이전트 - 단기 전술 제안"""
    
    def __init__(self):
        self.llm = get_gemini_model(temperature=0.6)
    
    def run(self, state: StrategyTeamState) -> StrategyTeamState:
        """즉시 실행 가능한 전술 제안"""
        
        tactics_prompt = f"""
다음 장기 전략을 고려하여, 이번 주/이번 달 즉시 실행 가능한 단기 전술 3가지를 제안하세요.

장기 전략:
- 포지셔닝: {state.get('positioning_concept', 'N/A')}
- Product: {state.get('four_p_strategy', {}).get('product', 'N/A')}
- Promotion: {state.get('four_p_strategy', {}).get('promotion', 'N/A')}

조건:
- 소규모 사업자가 혼자 실행 가능해야 함
- 비용이 적게 들어야 함
- 측정 가능한 결과가 나와야 함

JSON 배열로 응답:
[
  {{"tactic": "<전술명>", "action": "<구체적 행동>", "timeline": "<기간>"}},
  ...
]
"""
        
        response = self.llm.invoke([HumanMessage(content=tactics_prompt)])
        try:
            tactics = json.loads(response.content.strip().replace("```json", "").replace("```", ""))
            state["situational_tactics"] = tactics
        except:
            state["situational_tactics"] = [
                {"tactic": "SNS 포스팅", "action": "주 3회 인스타그램 업로드", "timeline": "이번 주"},
                {"tactic": "단골 이벤트", "action": "재방문 고객 10% 할인", "timeline": "이번 달"},
                {"tactic": "리뷰 독려", "action": "리뷰 작성 시 음료 무료", "timeline": "상시"}
            ]
        
        msg = AIMessage(content=f"✅ 단기 전술 {len(state['situational_tactics'])}개 제안 완료")
        state["messages"].append(msg)
        
        return state


class ContentAgent:
    """콘텐츠 에이전트 - 실행 가능한 포맷으로 변환"""
    
    def __init__(self):
        self.llm = get_gemini_model(temperature=0.5)
    
    def run(self, state: StrategyTeamState) -> StrategyTeamState:
        """최종 실행 문서 작성"""
        
        content = f"""
# 🎯 마케팅 실행 계획서

## 1. 포지셔닝 방향
**컨셉**: {state.get('positioning_concept', 'N/A')}

## 2. 4P 전략

### 📦 Product (제품/서비스)
{state.get('four_p_strategy', {}).get('product', 'N/A')}

### 💰 Price (가격)
{state.get('four_p_strategy', {}).get('price', 'N/A')}

### 📍 Place (유통)
{state.get('four_p_strategy', {}).get('place', 'N/A')}

### 📣 Promotion (프로모션)
{state.get('four_p_strategy', {}).get('promotion', 'N/A')}

## 3. 즉시 실행 전술

{chr(10).join([f"### {i+1}. {t['tactic']}\n- **행동**: {t['action']}\n- **기간**: {t['timeline']}" 
               for i, t in enumerate(state.get('situational_tactics', []))])}

---
생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        state["execution_content"] = content
        
        msg = AIMessage(content="✅ 실행 계획서 작성 완료")
        state["messages"].append(msg)
        
        return state


class StrategyTeamSupervisor:
    """전략팀 감독자"""
    
    def __init__(self):
        self.llm = get_gemini_model(temperature=0.3)
    
    def run(self, state: StrategyTeamState) -> StrategyTeamState:
        """전략팀 작업 조율"""
        
        has_strategy = "four_p_strategy" in state and state["four_p_strategy"]
        has_tactics = "situational_tactics" in state
        has_content = "execution_content" in state
        
        if not has_strategy:
            state["next"] = "StrategyAgent"
        elif not has_tactics:
            state["next"] = "SituationAgent"
        elif not has_content:
            state["next"] = "ContentAgent"
        else:
            # 최종 문서 생성
            state["strategy_document"] = state["execution_content"]
            state["next"] = "FINISH"
        
        return state


# ============================================================================
# 그래프 구성
# ============================================================================

def build_analysis_team_graph():
    """분석팀 그래프 생성"""
    graph = StateGraph(AnalysisTeamState)
    
    data_cruncher = DataCruncherAgent()
    insight_extractor = InsightExtractorAgent()
    supervisor = AnalysisTeamSupervisor()
    
    graph.add_node("DataCruncher", data_cruncher.run)
    graph.add_node("InsightExtractor", insight_extractor.run)
    graph.add_node("Supervisor", supervisor.run)
    
    graph.add_edge("DataCruncher", "Supervisor")
    graph.add_edge("InsightExtractor", "Supervisor")
    
    graph.add_conditional_edges(
        "Supervisor",
        lambda state: state["next"],
        {
            "DataCruncher": "DataCruncher",
            "InsightExtractor": "InsightExtractor",
            "FINISH": END
        }
    )
    
    graph.set_entry_point("Supervisor")
    
    return graph.compile()


def build_strategy_team_graph():
    """전략팀 그래프 생성"""
    graph = StateGraph(StrategyTeamState)
    
    strategy_agent = StrategyAgent()
    situation_agent = SituationAgent()
    content_agent = ContentAgent()
    supervisor = StrategyTeamSupervisor()
    
    graph.add_node("StrategyAgent", strategy_agent.run)
    graph.add_node("SituationAgent", situation_agent.run)
    graph.add_node("ContentAgent", content_agent.run)
    graph.add_node("Supervisor", supervisor.run)
    
    graph.add_edge("StrategyAgent", "Supervisor")
    graph.add_edge("SituationAgent", "Supervisor")
    graph.add_edge("ContentAgent", "Supervisor")
    
    graph.add_conditional_edges(
        "Supervisor",
        lambda state: state["next"],
        {
            "StrategyAgent": "StrategyAgent",
            "SituationAgent": "SituationAgent",
            "ContentAgent": "ContentAgent",
            "FINISH": END
        }
    )
    
    graph.set_entry_point("Supervisor")
    
    return graph.compile()


# ============================================================================
# 최상위 슈퍼바이저
# ============================================================================

class TopLevelSupervisor:
    """최상위 감독자 - 분석팀과 전략팀 조율"""
    
    def __init__(self):
        self.llm = get_gemini_model(temperature=0.2)
        self.analysis_team = build_analysis_team_graph()
        self.strategy_team = build_strategy_team_graph()
    
    def run(self, user_input: str, business_data: pd.DataFrame) -> str:
        """전체 워크플로우 실행"""
        
        # 1단계: 분석팀 실행
        st.info("🔍 분석팀 작업 시작...")
        
        analysis_state = AnalysisTeamState(
            messages=[HumanMessage(content=user_input)],
            business_data={"df": business_data.to_dict('records')},
            team_members=["DataCruncher", "InsightExtractor"],
            next="",
            cluster_features={},
            pca_components={},
            target_cluster=0,
            our_position={},
            white_space_position={},
            nearby_competitors=[],
            stp_report=""
        )
        
        analysis_result = self.analysis_team.invoke(analysis_state)
        
        st.success("✅ 분석팀 작업 완료")
        st.markdown(analysis_result["stp_report"])
        
        # 2단계: 전략팀 실행
        st.info("💡 전략팀 작업 시작...")
        
        strategy_state = StrategyTeamState(
            messages=[HumanMessage(content="STP 분석 결과를 바탕으로 실행 전략을 수립하세요.")],
            stp_results={
                "segmentation": analysis_result["cluster_features"],
                "targeting": {
                    "target_cluster": analysis_result["target_cluster"],
                    "our_position": analysis_result["our_position"]
                },
                "positioning": {
                    "white_space": analysis_result["white_space_position"],
                    "competitors": analysis_result["nearby_competitors"]
                },
                "pca_interpretation": analysis_result["pca_components"]["interpretation"]
            },
            team_members=["StrategyAgent", "SituationAgent", "ContentAgent"],
            next="",
            positioning_concept="",
            four_p_strategy={},
            situational_tactics=[],
            execution_content="",
            strategy_document=""
        )
        
        strategy_result = self.strategy_team.invoke(strategy_state)
        
        st.success("✅ 전략팀 작업 완료")
        
        return strategy_result["strategy_document"]


# ============================================================================
# Streamlit UI
# ============================================================================

def main():
    st.set_page_config(
        page_title="Marketing MultiAgent System",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 소규모 사업자를 위한 마케팅 전략 자동화")
    st.markdown("**STP 분석 + 4P 전략 + 실행 전술을 자동으로 제안합니다**")
    
    # API 키 입력
    with st.sidebar:
        st.header("⚙️ 설정")
        api_key = st.text_input("Google API Key", type="password", value=GOOGLE_API_KEY)
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
        
        st.markdown("---")
        st.markdown("""
        ### 사용 방법
        1. 가맹점 데이터 CSV 업로드
        2. 분석 목적 입력
        3. '전략 생성' 버튼 클릭
        """)
    
    # 파일 업로드
    uploaded_file = st.file_uploader(
        "📊 가맹점 데이터 CSV 업로드",
        type=['csv'],
        help="가맹점별 매출, 객단가, 재방문율 등의 데이터를 포함한 CSV"
    )
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ 데이터 로드 완료: {len(df)}개 행, {len(df.columns)}개 열")
            
            with st.expander("데이터 미리보기"):
                st.dataframe(df.head())
            
            # 사용자 입력
            user_input = st.text_area(
                "💬 분석 목적 또는 질문을 입력하세요",
                placeholder="예: 우리 가맹점의 시장 포지션을 분석하고 차별화 전략을 제안해주세요.",
                height=100
            )
            
            if st.button("🚀 전략 생성", type="primary"):
                if not api_key:
                    st.error("Google API Key를 입력해주세요.")
                elif not user_input:
                    st.warning("분석 목적을 입력해주세요.")
                else:
                    with st.spinner("분석 중..."):
                        try:
                            supervisor = TopLevelSupervisor()
                            result = supervisor.run(user_input, df)
                            
                            st.markdown("## 📋 최종 실행 계획서")
                            st.markdown(result)
                            
                            # 다운로드 버튼
                            st.download_button(
                                label="📥 계획서 다운로드",
                                data=result,
                                file_name=f"marketing_plan_{datetime.now().strftime('%Y%m%d')}.md",
                                mime="text/markdown"
                            )
                            
                        except Exception as e:
                            st.error(f"오류 발생: {str(e)}")
                            st.exception(e)
        
        except Exception as e:
            st.error(f"CSV 파일 로드 실패: {str(e)}")
    
    else:
        st.info("👆 CSV 파일을 업로드하여 시작하세요.")


if __name__ == "__main__":
    main()