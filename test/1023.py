"""
Marketing MultiAgent System - Improved Version
===============================================
STP 논리성 강화 및 Strategy Agent 역할 구체화

주요 개선사항:
1. 분석팀 ↔ 전략팀 데이터 흐름 명확화 (STP 논리성 강화)
2. Strategy Agent 역할 구체화 (4P 프레임워크 기반)
3. Supervisor 역할 분리 및 명확화
4. White Space Detection 기능 추가
5. RAG 기반 외부 트렌드 데이터 통합
"""

import os
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, TypedDict, Annotated, Sequence, Literal
from pathlib import Path
import operator
import warnings
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Langchain & Langgraph
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field

warnings.filterwarnings('ignore')

# ============================================================================
# Configuration
# ============================================================================

# Gemini 2.5 Pro 모델만 사용
MODEL_NAME = "gemini-2.5-pro"

# 데이터 경로 설정
DATA_DIR = "/mnt/c/Users/rladl/Desktop/bigcontest_2025/2025_shcard_bigcontest/data"

# ============================================================================
# 1. Data Models (Pydantic)
# ============================================================================

class PCAxisInterpretation(BaseModel):
    """PCA 축 해석 정보"""
    axis: str  # PC1 or PC2
    interpretation: str  # 축의 의미
    top_features: List[Dict]  # 상위 가중치 피처들
    
class ClusterProfile(BaseModel):
    """클러스터 프로파일"""
    cluster_id: int
    cluster_name: str  # LLM이 생성
    store_count: int
    pc1_mean: float
    pc2_mean: float
    characteristics: str  # LLM이 생성
    
class StorePosition(BaseModel):
    """가맹점 포지션"""
    store_id: str
    store_name: str
    industry: str
    pc1_score: float
    pc2_score: float
    cluster_id: int
    cluster_name: str
    competitor_count: int

class WhiteSpace(BaseModel):
    """빈 포지션 (White Space)"""
    pc1_coord: float
    pc2_coord: float
    distance_to_nearest_cluster: float
    opportunity_score: float  # 기회 점수 (거리 * 잠재 수요)
    reasoning: str  # 왜 이 위치가 기회인지
    
class STPOutput(BaseModel):
    """STP 분석 결과 (분석팀 → 전략팀 Input)"""
    # Segmentation
    cluster_profiles: List[ClusterProfile]
    pc_axis_interpretation: Dict[str, PCAxisInterpretation]
    
    # Targeting
    target_cluster_id: int
    target_cluster_name: str
    store_current_position: StorePosition
    
    # Positioning
    white_spaces: List[WhiteSpace]
    recommended_white_space: WhiteSpace
    nearby_competitors: List[Dict]
    
class Strategy4P(BaseModel):
    """4P 전략"""
    product: str  # 제품 전략
    price: str    # 가격 전략
    place: str    # 유통 전략
    promotion: str  # 프로모션 전략

# ============================================================================
# 2. Agent State Definitions
# ============================================================================

class MarketAnalysisState(TypedDict):
    """분석팀 State"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # Input
    target_store_id: str
    target_store_name: str
    industry: str
    
    # Output (→ Strategy Team으로 전달)
    stp_output: Optional[STPOutput]
    next: str

class StrategyTeamState(TypedDict):
    """전략팀 State"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # Input (← Analysis Team으로부터 받음)
    stp_output: STPOutput
    
    # RAG Context
    rag_context: str
    
    # Output
    strategy_4p: Optional[Strategy4P]
    positioning_concept: str  # 포지셔닝 컨셉
    execution_plan: str  # 실행 계획
    
    next: str

class SupervisorState(TypedDict):
    """전체 시스템 State"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # 사용자 입력
    user_query: str
    target_store_id: str
    target_store_name: str
    
    # 분석팀 결과
    stp_output: Optional[STPOutput]
    
    # 전략팀 결과
    strategy_4p: Optional[Strategy4P]
    positioning_concept: str
    execution_plan: str
    
    # 최종 보고서
    final_report: str
    
    next: str

# ============================================================================
# 3. Data Loading & Preprocessing
# ============================================================================

class STPDataLoader:
    """STP 분석을 위한 데이터 로더"""
    
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = Path(data_dir)
        self.pca_loadings = None
        self.cluster_profiles = None
        self.store_positioning = None
        
    def load_all_data(self):
        """모든 STP 관련 데이터 로드"""
        print("📂 STP 데이터 로딩 중...")
        
        # 1. PCA 가중치 데이터
        self.pca_loadings = pd.read_csv(
            self.data_dir / "pca_components_by_industry.csv",
            encoding='utf-8-sig'
        )
        
        # 2. 클러스터 프로파일
        self.cluster_profiles = pd.read_csv(
            self.data_dir / "kmeans_clusters_by_industry.csv",
            encoding='utf-8-sig'
        )
        
        # 3. 가맹점 포지셔닝
        df_base = pd.read_csv(self.data_dir / "df_final.csv", encoding='cp949')
        df_seg = pd.read_csv(
            self.data_dir / "store_segmentation_final.csv",
            encoding='utf-8-sig'
        )
        
        # 병합
        self.store_positioning = df_base.merge(
            df_seg,
            on=['가맹점구분번호', '가맹점명', '업종'],
            how='left'
        )
        
        # 컬럼명 표준화
        column_mapping = {
            'PC1 Score(x좌표)': 'pc1_x',
            'PC2 Score(y좌표)': 'pc2_y',
            'K-Means Cluster (경쟁 그룹)': 'cluster_id',
            '경쟁 그룹 수': 'n_clusters'
        }
        self.store_positioning = self.store_positioning.rename(columns=column_mapping)
        
        print(f"✅ PCA Loadings: {self.pca_loadings.shape}")
        print(f"✅ Cluster Profiles: {self.cluster_profiles.shape}")
        print(f"✅ Store Positioning: {self.store_positioning.shape}")
        
    def get_store_info(self, store_id: str) -> Optional[Dict]:
        """가맹점 기본 정보 조회"""
        df = self.store_positioning[
            self.store_positioning['가맹점구분번호'] == store_id
        ]
        
        if df.empty:
            return None
            
        row = df.iloc[0]
        return {
            'store_id': row['가맹점구분번호'],
            'store_name': row['가맹점명'],
            'industry': row['업종'],
            'commercial_area': row.get('상권', 'N/A'),
            'pc1_x': row['pc1_x'],
            'pc2_y': row['pc2_y'],
            'cluster_id': row['cluster_id']
        }
    
    def get_pc_interpretation(self, industry: str) -> Dict[str, PCAxisInterpretation]:
        """PC축 해석 조회"""
        df = self.pca_loadings[self.pca_loadings['industry'] == industry].copy()
        
        # PC1 상위 가중치 피처
        df['PC1_abs'] = df['PC1 가중치'].abs()
        pc1_top = df.nlargest(3, 'PC1_abs')
        pc1_features = [
            {
                '속성': row['원본 데이터 속성(예)'],
                '가중치': round(row['PC1 가중치'], 2),
                '설명': row['속성 설명']
            }
            for _, row in pc1_top.iterrows()
        ]
        
        # PC2 상위 가중치 피처
        df['PC2_abs'] = df['PC2 가중치'].abs()
        pc2_top = df.nlargest(3, 'PC2_abs')
        pc2_features = [
            {
                '속성': row['원본 데이터 속성(예)'],
                '가중치': round(row['PC2 가중치'], 2),
                '설명': row['속성 설명']
            }
            for _, row in pc2_top.iterrows()
        ]
        
        return {
            'PC1': PCAxisInterpretation(
                axis='PC1',
                interpretation=f"{pc1_features[0]['속성']} vs {pc1_features[1]['속성']}",
                top_features=pc1_features
            ),
            'PC2': PCAxisInterpretation(
                axis='PC2',
                interpretation=f"{pc2_features[0]['속성']} vs {pc2_features[1]['속성']}",
                top_features=pc2_features
            )
        }
    
    def get_cluster_profiles_for_industry(self, industry: str) -> List[Dict]:
        """업종별 클러스터 프로파일"""
        df = self.cluster_profiles[self.cluster_profiles['industry'] == industry]
        return df.to_dict('records')
    
    def find_white_spaces(
        self,
        industry: str,
        grid_resolution: int = 20,
        min_distance: float = 0.5
    ) -> List[Dict]:
        """빈 포지션(White Space) 탐지
        
        Args:
            industry: 업종
            grid_resolution: 그리드 해상도
            min_distance: 최소 거리 (이보다 가까운 경쟁사가 없어야 함)
        
        Returns:
            빈 포지션 리스트
        """
        df = self.store_positioning[self.store_positioning['업종'] == industry]
        
        if df.empty:
            return []
        
        # PC1, PC2 범위 설정
        pc1_min, pc1_max = df['pc1_x'].min(), df['pc1_x'].max()
        pc2_min, pc2_max = df['pc2_y'].min(), df['pc2_y'].max()
        
        # 그리드 생성
        pc1_grid = np.linspace(pc1_min, pc1_max, grid_resolution)
        pc2_grid = np.linspace(pc2_min, pc2_max, grid_resolution)
        
        white_spaces = []
        
        for pc1 in pc1_grid:
            for pc2 in pc2_grid:
                # 가장 가까운 경쟁사까지의 거리 계산
                distances = np.sqrt(
                    (df['pc1_x'] - pc1) ** 2 +
                    (df['pc2_y'] - pc2) ** 2
                )
                min_dist = distances.min()
                
                # 빈 공간 조건: 최소 거리 이상
                if min_dist >= min_distance:
                    # 기회 점수 = 거리 * (1 - 정규화된 위치)
                    # 중앙에 가까울수록 높은 점수
                    center_dist = np.sqrt(
                        ((pc1 - df['pc1_x'].mean()) / df['pc1_x'].std()) ** 2 +
                        ((pc2 - df['pc2_y'].mean()) / df['pc2_y'].std()) ** 2
                    )
                    opportunity_score = min_dist * (1 / (1 + center_dist))
                    
                    white_spaces.append({
                        'pc1_coord': round(pc1, 3),
                        'pc2_coord': round(pc2, 3),
                        'distance_to_nearest': round(min_dist, 3),
                        'opportunity_score': round(opportunity_score, 3)
                    })
        
        # 기회 점수 기준 정렬
        white_spaces = sorted(
            white_spaces,
            key=lambda x: x['opportunity_score'],
            reverse=True
        )
        
        return white_spaces[:10]  # 상위 10개만 반환

# ============================================================================
# 4. RAG System for Trend Data
# ============================================================================

class TrendRAGSystem:
    """외부 트렌드 데이터 RAG 시스템"""
    
    def __init__(self, trend_data_path: Optional[str] = None):
        """
        Args:
            trend_data_path: 트렌드 데이터 파일 경로 (JSON or CSV)
        """
        self.trend_data_path = trend_data_path
        self.vectorstore = None
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        if trend_data_path and Path(trend_data_path).exists():
            self._load_trend_data()
    
    def _load_trend_data(self):
        """트렌드 데이터 로드 및 벡터 스토어 구축"""
        print("📚 트렌드 데이터 로딩 및 벡터화 중...")
        
        # 예시: JSON 파일에서 트렌드 데이터 로드
        with open(self.trend_data_path, 'r', encoding='utf-8') as f:
            trend_data = json.load(f)
        
        # 텍스트 문서로 변환
        documents = []
        for item in trend_data:
            text = f"업종: {item['industry']}\n"
            text += f"트렌드: {item['trend']}\n"
            text += f"설명: {item['description']}\n"
            text += f"추천전략: {item['recommendation']}"
            documents.append(text)
        
        # FAISS 벡터 스토어 구축
        from langchain.schema import Document
        docs = [Document(page_content=text) for text in documents]
        self.vectorstore = FAISS.from_documents(docs, self.embeddings)
        
        print(f"✅ {len(documents)}개 트렌드 문서 벡터화 완료")
    
    def retrieve_relevant_trends(
        self,
        query: str,
        top_k: int = 3
    ) -> str:
        """관련 트렌드 검색
        
        Args:
            query: 검색 쿼리 (예: "일식-우동/소바/라면 업종 트렌드")
            top_k: 반환할 문서 수
        
        Returns:
            관련 트렌드 텍스트
        """
        if not self.vectorstore:
            return "트렌드 데이터가 로드되지 않았습니다."
        
        docs = self.vectorstore.similarity_search(query, k=top_k)
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
    
    def get_mock_trend_data(self, industry: str) -> str:
        """Mock 트렌드 데이터 (실제 RAG 없을 때 사용)"""
        mock_data = {
            "일식-우동/소바/라면": """
            **업종 트렌드:**
            - 건강 지향 메뉴 선호 증가 (저염, 채소 중심)
            - 1인 식사 고객 증가 → 빠른 회전율 중요
            - 배달 수요 증가 (배달 최적화 메뉴 필요)
            
            **추천 전략:**
            - 시그니처 메뉴: 건강 우동 세트
            - 가격대: 10,000~13,000원 (점심 특선 8,000원)
            - 홍보: 인스타그램 비주얼 마케팅
            """,
            "default": """
            **일반 트렌드:**
            - 가성비 중시
            - SNS 마케팅 중요
            - 차별화된 경험 제공
            """
        }
        
        return mock_data.get(industry, mock_data["default"])

# ============================================================================
# 5. Analysis Team Agents
# ============================================================================

def segmentation_agent_node(state: MarketAnalysisState) -> MarketAnalysisState:
    """Segmentation Agent: 시장 군집 정의
    
    역할:
    - K-Means 클러스터링 결과 로드
    - PCA 축 해석
    - 각 클러스터의 특징 정의 (LLM 사용)
    """
    print("\n[Segmentation Agent] 시장 군집 분석 중...")
    
    # 데이터 로더
    loader = STPDataLoader()
    loader.load_all_data()
    
    # 가맹점 정보
    store_info = loader.get_store_info(state['target_store_id'])
    if not store_info:
        state['messages'].append(
            AIMessage(content="❌ 가맹점 정보를 찾을 수 없습니다.")
        )
        state['next'] = END
        return state
    
    industry = store_info['industry']
    
    # PC축 해석
    pc_interp = loader.get_pc_interpretation(industry)
    
    # 클러스터 프로파일
    cluster_data = loader.get_cluster_profiles_for_industry(industry)
    
    # LLM으로 클러스터 특성 생성
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.3)
    
    cluster_profiles = []
    for cluster in cluster_data:
        prompt = f"""
당신은 마케팅 분석가입니다. 다음 클러스터의 특성을 간단명료하게 요약하세요.

**업종:** {industry}
**클러스터 ID:** {cluster['cluster_id']}
**PC1 평균:** {cluster['pc1_mean']:.2f}
**PC2 평균:** {cluster['pc2_mean']:.2f}
**가맹점 수:** {cluster['store_count']}

**PC1 해석:** {pc_interp['PC1'].interpretation}
**PC2 해석:** {pc_interp['PC2'].interpretation}

다음 형식으로 응답하세요:
1. 클러스터 이름 (10자 이내)
2. 핵심 특성 (한 문장)
"""
        response = llm.invoke(prompt)
        lines = response.content.strip().split('\n')
        cluster_name = lines[0].replace('1.', '').strip() if len(lines) > 0 else f"그룹 {cluster['cluster_id']}"
        characteristics = lines[1].replace('2.', '').strip() if len(lines) > 1 else "특성 분석 중"
        
        cluster_profiles.append(ClusterProfile(
            cluster_id=cluster['cluster_id'],
            cluster_name=cluster_name,
            store_count=cluster['store_count'],
            pc1_mean=cluster['pc1_mean'],
            pc2_mean=cluster['pc2_mean'],
            characteristics=characteristics
        ))
    
    # State 업데이트 (부분적)
    state['messages'].append(
        AIMessage(content=f"✅ Segmentation 완료: {len(cluster_profiles)}개 군집 정의")
    )
    
    # STP Output 초기화 (나중에 완성)
    state['stp_output'] = STPOutput(
        cluster_profiles=cluster_profiles,
        pc_axis_interpretation=pc_interp,
        target_cluster_id=0,  # 다음 단계에서 결정
        target_cluster_name="",
        store_current_position=None,
        white_spaces=[],
        recommended_white_space=None,
        nearby_competitors=[]
    )
    
    state['next'] = "targeting_agent"
    return state

def targeting_agent_node(state: MarketAnalysisState) -> MarketAnalysisState:
    """Targeting Agent: 타겟 군집 선정
    
    역할:
    - 우리 가맹점의 현재 포지션 파악
    - 타겟 군집 선정
    """
    print("\n[Targeting Agent] 타겟 군집 선정 중...")
    
    loader = STPDataLoader()
    loader.load_all_data()
    
    store_info = loader.get_store_info(state['target_store_id'])
    industry = store_info['industry']
    
    # 현재 포지션
    current_position = StorePosition(
        store_id=store_info['store_id'],
        store_name=store_info['store_name'],
        industry=industry,
        pc1_score=store_info['pc1_x'],
        pc2_score=store_info['pc2_y'],
        cluster_id=int(store_info['cluster_id']),
        cluster_name="",  # 나중에 매칭
        competitor_count=0
    )
    
    # 클러스터 이름 매칭
    for profile in state['stp_output'].cluster_profiles:
        if profile.cluster_id == current_position.cluster_id:
            current_position.cluster_name = profile.cluster_name
            break
    
    # 타겟 군집 = 현재 군집 (일단 현재 위치 기준)
    target_cluster_id = current_position.cluster_id
    target_cluster_name = current_position.cluster_name
    
    # STP Output 업데이트
    state['stp_output'].target_cluster_id = target_cluster_id
    state['stp_output'].target_cluster_name = target_cluster_name
    state['stp_output'].store_current_position = current_position
    
    state['messages'].append(
        AIMessage(content=f"✅ Targeting 완료: {target_cluster_name} 그룹 공략")
    )
    
    state['next'] = "positioning_agent"
    return state

def positioning_agent_node(state: MarketAnalysisState) -> MarketAnalysisState:
    """Positioning Agent: 차별화 포지션 탐색
    
    역할:
    - White Space (빈 포지션) 탐지
    - 최적 포지셔닝 좌표 추천
    - 인근 경쟁사 분석
    """
    print("\n[Positioning Agent] 차별화 포지션 탐색 중...")
    
    loader = STPDataLoader()
    loader.load_all_data()
    
    store_info = loader.get_store_info(state['target_store_id'])
    industry = store_info['industry']
    
    # White Space 탐지
    white_spaces_raw = loader.find_white_spaces(industry, grid_resolution=15, min_distance=0.8)
    
    # LLM으로 각 White Space의 reasoning 생성
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.3)
    
    white_spaces = []
    pc_interp = state['stp_output'].pc_axis_interpretation
    
    for ws in white_spaces_raw[:5]:  # 상위 5개만
        prompt = f"""
다음 빈 포지션이 왜 사업 기회인지 간단히 설명하세요.

**PC1 좌표:** {ws['pc1_coord']} (축 의미: {pc_interp['PC1'].interpretation})
**PC2 좌표:** {ws['pc2_coord']} (축 의미: {pc_interp['PC2'].interpretation})
**가장 가까운 경쟁사 거리:** {ws['distance_to_nearest']}

한 문장으로 답변하세요.
"""
        response = llm.invoke(prompt)
        reasoning = response.content.strip()
        
        white_spaces.append(WhiteSpace(
            pc1_coord=ws['pc1_coord'],
            pc2_coord=ws['pc2_coord'],
            distance_to_nearest_cluster=ws['distance_to_nearest'],
            opportunity_score=ws['opportunity_score'],
            reasoning=reasoning
        ))
    
    # 최고 점수 White Space 선택
    recommended_ws = white_spaces[0] if white_spaces else None
    
    # 인근 경쟁사 (현재 포지션 기준)
    df = loader.store_positioning[loader.store_positioning['업종'] == industry]
    df = df[df['가맹점구분번호'] != state['target_store_id']]
    
    current_pos = state['stp_output'].store_current_position
    df['distance'] = np.sqrt(
        (df['pc1_x'] - current_pos.pc1_score) ** 2 +
        (df['pc2_y'] - current_pos.pc2_score) ** 2
    )
    
    nearby = df.nlargest(10, 'distance').to_dict('records')
    
    # STP Output 완성
    state['stp_output'].white_spaces = white_spaces
    state['stp_output'].recommended_white_space = recommended_ws
    state['stp_output'].nearby_competitors = nearby
    
    state['messages'].append(
        AIMessage(content=f"✅ Positioning 완료: {len(white_spaces)}개 기회 포지션 발견")
    )
    
    state['next'] = END
    return state

# ============================================================================
# 6. Strategy Team Agents
# ============================================================================

def strategy_agent_node(state: StrategyTeamState) -> StrategyTeamState:
    """Strategy Agent: 4P 전략 수립
    
    역할:
    - STP 결과 + RAG 트렌드 데이터 결합
    - 4P (Product, Price, Place, Promotion) 전략 구체화
    - 포지셔닝 컨셉 정의
    """
    print("\n[Strategy Agent] 4P 전략 수립 중...")
    
    stp = state['stp_output']
    
    # RAG 시스템 (Mock 데이터 사용)
    rag = TrendRAGSystem()
    trend_context = rag.get_mock_trend_data(stp.store_current_position.industry)
    
    state['rag_context'] = trend_context
    
    # LLM으로 4P 전략 생성
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.7)
    
    prompt = f"""
당신은 마케팅 전략가입니다. 다음 STP 분석 결과를 바탕으로 실행 가능한 4P 전략을 수립하세요.

# STP 분석 결과

## Segmentation
- 업종: {stp.store_current_position.industry}
- PC1 축: {stp.pc_axis_interpretation['PC1'].interpretation}
- PC2 축: {stp.pc_axis_interpretation['PC2'].interpretation}
- 전체 군집: {len(stp.cluster_profiles)}개

## Targeting
- 타겟 군집: {stp.target_cluster_name}
- 현재 포지션: PC1={stp.store_current_position.pc1_score:.2f}, PC2={stp.store_current_position.pc2_score:.2f}

## Positioning
- 추천 포지션: PC1={stp.recommended_white_space.pc1_coord:.2f}, PC2={stp.recommended_white_space.pc2_coord:.2f}
- 이유: {stp.recommended_white_space.reasoning}

# 외부 트렌드 데이터
{trend_context}

---

다음 형식으로 4P 전략을 작성하세요 (각 항목 2-3문장):

**Product (제품 전략):**
[추천 포지션에 맞는 시그니처 메뉴/서비스]

**Price (가격 전략):**
[PC1 좌표에 맞는 가격대 설정]

**Place (유통 전략):**
[배달/포장/매장 중 어디에 집중할지]

**Promotion (프로모션 전략):**
[타겟 고객에게 도달하는 홍보 방법]

**포지셔닝 컨셉 (한 문장):**
[우리 가맹점의 차별화 메시지]
"""
    
    response = llm.invoke(prompt)
    content = response.content.strip()
    
    # 파싱 (간단한 방식)
    sections = content.split('**')
    strategy_4p = Strategy4P(
        product="분석 중",
        price="분석 중",
        place="분석 중",
        promotion="분석 중"
    )
    positioning_concept = "차별화 전략 수립 중"
    
    for i, section in enumerate(sections):
        if 'Product' in section and i+1 < len(sections):
            strategy_4p.product = sections[i+1].replace(':', '').strip()
        elif 'Price' in section and i+1 < len(sections):
            strategy_4p.price = sections[i+1].replace(':', '').strip()
        elif 'Place' in section and i+1 < len(sections):
            strategy_4p.place = sections[i+1].replace(':', '').strip()
        elif 'Promotion' in section and i+1 < len(sections):
            strategy_4p.promotion = sections[i+1].replace(':', '').strip()
        elif '포지셔닝 컨셉' in section and i+1 < len(sections):
            positioning_concept = sections[i+1].replace(':', '').strip()
    
    state['strategy_4p'] = strategy_4p
    state['positioning_concept'] = positioning_concept
    
    state['messages'].append(
        AIMessage(content="✅ Strategy Agent: 4P 전략 수립 완료")
    )
    
    state['next'] = "content_agent"
    return state

def content_agent_node(state: StrategyTeamState) -> StrategyTeamState:
    """Content Agent: 실행 계획서 작성
    
    역할:
    - Strategy Agent의 4P 전략을 실행 가능한 액션 플랜으로 변환
    - 타임라인 포함
    """
    print("\n[Content Agent] 실행 계획서 작성 중...")
    
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.5)
    
    prompt = f"""
다음 4P 전략을 실행 가능한 액션 플랜으로 변환하세요.

# 4P 전략
- **Product:** {state['strategy_4p'].product}
- **Price:** {state['strategy_4p'].price}
- **Place:** {state['strategy_4p'].place}
- **Promotion:** {state['strategy_4p'].promotion}

# 포지셔닝 컨셉
{state['positioning_concept']}

---

다음 형식으로 실행 계획을 작성하세요:

## 1주차: [액션 1]
## 2주차: [액션 2]
## 3주차: [액션 3]
## 4주차: [액션 4]

각 주차별 구체적인 실행 항목을 2-3개씩 나열하세요.
"""
    
    response = llm.invoke(prompt)
    execution_plan = response.content.strip()
    
    state['execution_plan'] = execution_plan
    
    state['messages'].append(
        AIMessage(content="✅ Content Agent: 실행 계획서 작성 완료")
    )
    
    state['next'] = END
    return state

# ============================================================================
# 7. Supervisor Nodes
# ============================================================================

def top_level_supervisor_node(state: SupervisorState) -> SupervisorState:
    """Top-Level Supervisor: 전체 시스템 조율
    
    역할:
    - 사용자 요청 받기
    - 분석팀 → 전략팀 흐름 제어
    - 최종 보고서 포맷팅
    """
    print("\n[Top-Level Supervisor] 시스템 시작...")
    
    if not state.get('stp_output'):
        # 분석팀으로 라우팅
        state['next'] = "market_analysis_team"
        return state
    elif not state.get('strategy_4p'):
        # 전략팀으로 라우팅
        state['next'] = "strategy_team"
        return state
    else:
        # 최종 보고서 생성
        state['next'] = "generate_final_report"
        return state

def generate_final_report_node(state: SupervisorState) -> SupervisorState:
    """최종 보고서 생성"""
    print("\n[Report Generator] 최종 보고서 생성 중...")
    
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.3)
    
    stp = state['stp_output']
    strategy = state['strategy_4p']
    
    prompt = f"""
다음 분석 결과를 마케팅 전략 보고서로 작성하세요.

# 가맹점 정보
- 이름: {state['target_store_name']}
- 업종: {stp.store_current_position.industry}

# STP 분석
- 타겟 시장: {stp.target_cluster_name}
- 현재 포지션: PC1={stp.store_current_position.pc1_score:.2f}, PC2={stp.store_current_position.pc2_score:.2f}
- 추천 포지션: PC1={stp.recommended_white_space.pc1_coord:.2f}, PC2={stp.recommended_white_space.pc2_coord:.2f}

# 4P 전략
- Product: {strategy.product}
- Price: {strategy.price}
- Place: {strategy.place}
- Promotion: {strategy.promotion}

# 실행 계획
{state['execution_plan']}

---

간단명료한 보고서 형식으로 작성하세요 (한글, A4 1페이지 분량).
"""
    
    response = llm.invoke(prompt)
    final_report = response.content.strip()
    
    state['final_report'] = final_report
    state['next'] = END
    
    return state

# ============================================================================
# 8. Graph Construction
# ============================================================================

def create_market_analysis_team() -> StateGraph:
    """분석팀 그래프 생성"""
    workflow = StateGraph(MarketAnalysisState)
    
    # 노드 추가
    workflow.add_node("segmentation_agent", segmentation_agent_node)
    workflow.add_node("targeting_agent", targeting_agent_node)
    workflow.add_node("positioning_agent", positioning_agent_node)
    
    # 엣지
    workflow.add_edge(START, "segmentation_agent")
    workflow.add_edge("segmentation_agent", "targeting_agent")
    workflow.add_edge("targeting_agent", "positioning_agent")
    workflow.add_edge("positioning_agent", END)
    
    return workflow.compile()

def create_strategy_team() -> StateGraph:
    """전략팀 그래프 생성"""
    workflow = StateGraph(StrategyTeamState)
    
    # 노드 추가
    workflow.add_node("strategy_agent", strategy_agent_node)
    workflow.add_node("content_agent", content_agent_node)
    
    # 엣지
    workflow.add_edge(START, "strategy_agent")
    workflow.add_edge("strategy_agent", "content_agent")
    workflow.add_edge("content_agent", END)
    
    return workflow.compile()

def create_super_graph() -> StateGraph:
    """전체 시스템 그래프"""
    workflow = StateGraph(SupervisorState)
    
    # 서브그래프
    market_team = create_market_analysis_team()
    strategy_team = create_strategy_team()
    
    # 노드 추가
    workflow.add_node("supervisor", top_level_supervisor_node)
    workflow.add_node("market_analysis_team", lambda s: {"stp_output": market_team.invoke(s)['stp_output']})
    workflow.add_node("strategy_team", lambda s: {"strategy_4p": strategy_team.invoke(s)['strategy_4p'], "execution_plan": strategy_team.invoke(s)['execution_plan']})
    workflow.add_node("generate_final_report", generate_final_report_node)
    
    # 엣지
    workflow.add_edge(START, "supervisor")
    
    # 조건부 라우팅
    def route_next(state: SupervisorState) -> str:
        return state['next']
    
    workflow.add_conditional_edges(
        "supervisor",
        route_next,
        {
            "market_analysis_team": "market_analysis_team",
            "strategy_team": "strategy_team",
            "generate_final_report": "generate_final_report",
            END: END
        }
    )
    
    workflow.add_edge("market_analysis_team", "supervisor")
    workflow.add_edge("strategy_team", "supervisor")
    workflow.add_edge("generate_final_report", END)
    
    return workflow.compile(checkpointer=MemorySaver())

# ============================================================================
# 9. Main Execution
# ============================================================================

def run_marketing_strategy_system(
    target_store_id: str,
    target_store_name: str
) -> Dict:
    """마케팅 전략 수립 시스템 실행
    
    Args:
        target_store_id: 가맹점 고유 번호
        target_store_name: 가맹점 이름
    
    Returns:
        최종 보고서 및 중간 결과
    """
    print("=" * 80)
    print("🚀 Marketing MultiAgent System - 실행 시작")
    print("=" * 80)
    
    # 초기 State
    initial_state = {
        "messages": [HumanMessage(content=f"{target_store_name} 가맹점 마케팅 전략 수립 요청")],
        "user_query": f"Analyze marketing strategy for {target_store_name}",
        "target_store_id": target_store_id,
        "target_store_name": target_store_name,
        "stp_output": None,
        "strategy_4p": None,
        "positioning_concept": "",
        "execution_plan": "",
        "final_report": "",
        "next": ""
    }
    
    # 그래프 실행
    app = create_super_graph()
    
    config = {"configurable": {"thread_id": "marketing_strategy_001"}}
    
    final_state = app.invoke(initial_state, config=config)
    
    print("\n" + "=" * 80)
    print("✅ 마케팅 전략 수립 완료")
    print("=" * 80)
    
    return {
        "final_report": final_state['final_report'],
        "stp_output": final_state['stp_output'],
        "strategy_4p": final_state['strategy_4p'],
        "execution_plan": final_state['execution_plan']
    }

# ============================================================================
# 10. CLI Interface
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   Marketing MultiAgent System - Improved Version              ║
    ║   STP 논리성 강화 + Strategy Agent 역할 구체화                ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # 예시 실행
    store_id = "0C67B8EDCF"  # 실제 가맹점 ID로 변경
    store_name = "히토****"
    
    result = run_marketing_strategy_system(
        target_store_id=store_id,
        target_store_name=store_name
    )
    
    print("\n" + "=" * 80)
    print("📄 최종 마케팅 전략 보고서")
    print("=" * 80)
    print(result['final_report'])