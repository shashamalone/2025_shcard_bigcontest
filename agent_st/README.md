# Marketing MultiAgent System - 개선 버전
## STP 논리성 강화 및 Strategy Agent 역할 구체화

---

## 📋 목차
1. [시스템 개요](#1-시스템-개요)
2. [핵심 개선사항](#2-핵심-개선사항)
3. [아키텍처 설계](#3-아키텍처-설계)
4. [데이터 흐름](#4-데이터-흐름)
5. [에이전트 상세 설명](#5-에이전트-상세-설명)
6. [실행 방법](#6-실행-방법)

---

## 1. 시스템 개요

### 1.1 목적
소상공인을 위한 **자동화된 마케팅 전략 수립 시스템**으로, STP 분석과 MultiAgent 협업을 통해 실행 가능한 전략을 제공합니다.

### 1.2 핵심 기술 스택
- **Framework**: Langchain, Langgraph
- **LLM**: Gemini 2.5 Pro (모든 LLM 호출에 사용)
- **Data Analysis**: pandas, numpy, scikit-learn
- **Visualization**: plotly, matplotlib, seaborn
- **UI**: Streamlit

---

## 2. 핵심 개선사항

### 2.1 분석팀 ↔ 전략팀 데이터 흐름 명확화

#### 기존 문제점
- STP 분석 결과가 전략팀에 명확히 전달되지 않음
- Positioning 단계에서 "빈 포지션(White Space)" 탐지 부재
- 데이터 흐름의 논리적 연결성 부족

#### 개선 방안

```
┌─────────────────────────────────────────────────────────────┐
│                      분석팀 (Analysis Team)                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │ Segmentation     │───▶│ Targeting        │              │
│  │ Agent            │    │ Agent            │              │
│  │                  │    │                  │              │
│  │ • K-Means 클러스터│    │ • 타겟 군집 선정  │              │
│  │ • PCA 축 해석    │    │ • 현재 포지션 파악│              │
│  └──────────────────┘    └──────────────────┘              │
│           │                        │                         │
│           │                        ▼                         │
│           │            ┌──────────────────┐                 │
│           └───────────▶│ Positioning      │                 │
│                        │ Agent            │                 │
│                        │                  │                 │
│                        │ • White Space    │◀─── 🆕 핵심 추가 │
│                        │   Detection      │                 │
│                        │ • 최적 좌표 추천  │                 │
│                        └──────────────────┘                 │
│                                │                             │
└────────────────────────────────┼─────────────────────────────┘
                                 │
                        STPOutput (구조화된 데이터)
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────┐
│                      전략팀 (Strategy Team)                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │ Strategy Agent   │───▶│ Content Agent    │              │
│  │                  │    │                  │              │
│  │ • STP 입력 검증  │    │ • 실행 계획서    │              │
│  │ • RAG 트렌드 통합│    │   작성          │              │
│  │ • 4P 전략 수립   │    │ • 타임라인 생성  │              │
│  └──────────────────┘    └──────────────────┘              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

#### STP 단계별 Output

| STP 단계 | 분석팀 Output | 논리적 기능 |
|---------|--------------|------------|
| **Segmentation** | - K-Means 클러스터 프로파일<br>- PCA 축 해석<br>- 각 군집의 특성 정의 | "시장에 존재하는 경쟁 그룹은 무엇인가?" |
| **Targeting** | - 타겟 군집 선정<br>- 우리 가맹점의 현재 포지션 (PC1, PC2 좌표) | "누구를 공략할 것인가?" |
| **Positioning** | - **White Space 좌표** (🆕 핵심)<br>- 인근 경쟁사 정보<br>- 기회 점수 | "어떻게 차별화할 것인가?" |

---

### 2.2 Strategy Agent 역할 구체화

#### 기존 문제점
- 전략 수립이 추상적이고 실행 가능성이 낮음
- STP 결과와 전략의 연결고리가 약함
- 외부 트렌드 데이터 미활용

#### 개선 방안: 4P 프레임워크 기반 구조화

```python
class Strategy4P(BaseModel):
    product: str   # 제품 전략
    price: str     # 가격 전략
    place: str     # 유통 전략
    promotion: str # 프로모션 전략
```

#### Strategy Agent의 논리적 작동 방식

| 기능 | 활용 데이터 | 논리적 작동 |
|-----|-----------|-----------|
| **Targeting 검증** | Segment 특징 정의 | 선정된 타겟 군집의 핵심 니즈와 고객 구조를 RAG로 외부 트렌드와 결합 검증 |
| **Positioning 정의** | White Space 좌표, PCA 축 해석 | 빈 포지션의 PC1, PC2 속성 분석하여 경쟁 우위 컨셉 정의 |
| **4P 전략 구체화** | RAG (업종 트렌드) + STP 결과 | 1. Product: 정의된 포지션에 맞는 시그니처 메뉴<br>2. Price: PC1 수준에 맞는 가격 책정<br>3. Place: 유통 전략<br>4. Promotion: 타겟 고객 맞춤 판촉 |

#### RAG (Retrieval-Augmented Generation) 통합

```python
class TrendRAGSystem:
    """외부 트렌드 데이터베이스"""
    
    def retrieve_relevant_trends(query: str) -> str:
        """
        업종별 최신 트렌드 검색
        - 건강 지향 메뉴 선호도
        - 1인 식사 고객 증가
        - 배달 수요 패턴
        """
```

---

### 2.3 Supervisor 역할 분리 및 명확화

#### 기존 문제점
- Supervisor 역할 중복
- 에이전트 간 조율 로직 부재

#### 개선 방안: 2-Tier Supervisor 구조

| Supervisor | 역할 범위 | 논리적 기능 |
|-----------|---------|-----------|
| **Top-Level Supervisor** | 전체 시스템 | - 사용자 요청 받기<br>- 분석팀 → 전략팀 흐름 제어<br>- 최종 보고서 포맷팅 |
| **Strategy Team Supervisor** | 전략팀 내부 | - Strategy Agent ↔ Content Agent 조율<br>- 장기 전략 vs 단기 전술 일관성 검증 |

---

## 3. 아키텍처 설계

### 3.1 전체 시스템 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                     Top-Level Supervisor                         │
│                     (전체 시스템 조율)                            │
└────────────────┬────────────────────────┬────────────────────────┘
                 │                        │
                 ▼                        ▼
┌────────────────────────────┐  ┌────────────────────────────┐
│   Market Analysis Team     │  │   Strategy Planning Team   │
│   (분석팀)                  │  │   (전략팀)                  │
├────────────────────────────┤  ├────────────────────────────┤
│                            │  │                            │
│  ┌──────────────────────┐ │  │  ┌──────────────────────┐ │
│  │ Segmentation Agent   │ │  │  │ Strategy Agent       │ │
│  │ • 시장 군집 정의      │ │  │  │ • 4P 전략 수립       │ │
│  │ • PCA 축 해석        │ │  │  │ • RAG 트렌드 통합    │ │
│  └──────────────────────┘ │  │  └──────────────────────┘ │
│            │               │  │            │               │
│            ▼               │  │            ▼               │
│  ┌──────────────────────┐ │  │  ┌──────────────────────┐ │
│  │ Targeting Agent      │ │  │  │ Content Agent        │ │
│  │ • 타겟 군집 선정      │ │  │  │ • 실행 계획서 작성   │ │
│  └──────────────────────┘ │  │  └──────────────────────┘ │
│            │               │  │                            │
│            ▼               │  └────────────────────────────┘
│  ┌──────────────────────┐ │
│  │ Positioning Agent    │ │
│  │ • White Space 탐지   │ │
│  │ • 최적 좌표 추천     │ │
│  └──────────────────────┘ │
│                            │
└────────────────────────────┘
         │
         │ STPOutput
         ▼
┌────────────────────────────┐
│   Final Report Generator   │
│   (최종 보고서 생성)        │
└────────────────────────────┘
```

### 3.2 State 구조

#### MarketAnalysisState (분석팀)
```python
class MarketAnalysisState(TypedDict):
    messages: List[BaseMessage]
    
    # Input
    target_store_id: str
    target_store_name: str
    industry: str
    
    # Output (→ Strategy Team)
    stp_output: STPOutput
    next: str
```

#### StrategyTeamState (전략팀)
```python
class StrategyTeamState(TypedDict):
    messages: List[BaseMessage]
    
    # Input (← Analysis Team)
    stp_output: STPOutput
    
    # RAG Context
    rag_context: str
    
    # Output
    strategy_4p: Strategy4P
    positioning_concept: str
    execution_plan: str
    next: str
```

---

## 4. 데이터 흐름

### 4.1 단계별 데이터 전달

```
[사용자 입력]
  ↓
  가맹점 ID, 가맹점명
  ↓
[분석팀 START]
  ↓
┌─────────────────────────────────────────────┐
│ Segmentation Agent                           │
│                                              │
│ Input:  가맹점 정보                          │
│ Output: - ClusterProfile[] (군집 프로파일)  │
│         - PCAxisInterpretation (축 해석)    │
└─────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────┐
│ Targeting Agent                              │
│                                              │
│ Input:  ClusterProfile[]                     │
│ Output: - target_cluster_id                  │
│         - StorePosition (현재 위치)          │
└─────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────┐
│ Positioning Agent                            │
│                                              │
│ Input:  StorePosition, ClusterProfile[]      │
│ Output: - WhiteSpace[] (빈 포지션 리스트)   │
│         - recommended_white_space (추천)    │
│         - nearby_competitors (경쟁사)       │
└─────────────────────────────────────────────┘
  ↓
  STPOutput (구조화된 전체 결과)
  ↓
[전략팀 START]
  ↓
┌─────────────────────────────────────────────┐
│ Strategy Agent                               │
│                                              │
│ Input:  STPOutput + RAG Trends               │
│ Output: - Strategy4P (Product/Price/...)    │
│         - positioning_concept               │
└─────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────┐
│ Content Agent                                │
│                                              │
│ Input:  Strategy4P                           │
│ Output: - execution_plan (주차별 액션)      │
└─────────────────────────────────────────────┘
  ↓
[최종 보고서 생성]
  ↓
  PDF / DOCX / Web Display
```

### 4.2 White Space Detection 알고리즘

```python
def find_white_spaces(
    industry: str,
    grid_resolution: int = 20,
    min_distance: float = 0.5
) -> List[WhiteSpace]:
    """
    1. PC1 x PC2 평면에 그리드 생성
    2. 각 그리드 포인트에서 가장 가까운 경쟁사까지의 거리 계산
    3. min_distance 이상인 포인트 = White Space
    4. 기회 점수 계산:
       opportunity_score = distance * (1 / (1 + center_distance))
       → 경쟁이 적고, 시장 중심에 가까울수록 높은 점수
    5. 상위 10개 반환
    """
```

---

## 5. 에이전트 상세 설명

### 5.1 Segmentation Agent

#### 역할
시장을 의미 있는 군집으로 세분화

#### 주요 작업
1. K-Means 클러스터링 결과 로드
2. PCA 주성분 분석 결과 로드
3. 각 축의 의미 해석 (LLM 사용)
4. 각 클러스터의 특성 정의 (LLM 사용)

#### LLM 프롬프트 예시
```
당신은 마케팅 분석가입니다. 다음 클러스터의 특성을 간단명료하게 요약하세요.

**업종:** 일식-우동/소바/라면
**클러스터 ID:** 2
**PC1 평균:** 1.23 (매출 성장률 vs 고객 적합도)
**PC2 평균:** -0.45 (경쟁 강도 vs 리스크)
**가맹점 수:** 45

다음 형식으로 응답하세요:
1. 클러스터 이름 (10자 이내)
2. 핵심 특성 (한 문장)
```

#### Output
```python
ClusterProfile(
    cluster_id=2,
    cluster_name="성장형 안정군",
    store_count=45,
    pc1_mean=1.23,
    pc2_mean=-0.45,
    characteristics="매출이 꾸준히 성장하고 있으며, 경쟁이 낮고 안정적인 그룹"
)
```

---

### 5.2 Targeting Agent

#### 역할
공략할 타겟 군집 선정 및 현재 포지션 파악

#### 주요 작업
1. 우리 가맹점의 PC1, PC2 좌표 조회
2. 소속 클러스터 확인
3. 타겟 군집 선정 (현재는 현재 클러스터 기준, 향후 확장 가능)

#### Output
```python
StorePosition(
    store_id="0C67B8EDCF",
    store_name="히토****",
    industry="일식-우동/소바/라면",
    pc1_score=1.08,
    pc2_score=-0.42,
    cluster_id=2,
    cluster_name="성장형 안정군",
    competitor_count=44
)
```

---

### 5.3 Positioning Agent (🆕 핵심 개선)

#### 역할
차별화 가능한 빈 포지션 탐지 및 추천

#### 주요 작업
1. **White Space Detection**
   - PC1 x PC2 평면을 그리드로 분할
   - 각 그리드 포인트에서 경쟁사까지의 거리 계산
   - min_distance 이상인 지점 = 빈 포지션
   
2. **기회 점수 계산**
   ```
   opportunity_score = distance_to_nearest * (1 / (1 + normalized_center_distance))
   ```
   - 경쟁사가 멀수록 유리
   - 시장 중심에 가까울수록 유리

3. **LLM을 통한 Reasoning 생성**
   - 각 White Space가 왜 기회인지 설명

#### LLM 프롬프트 예시
```
다음 빈 포지션이 왜 사업 기회인지 간단히 설명하세요.

**PC1 좌표:** 1.5 (축 의미: 고객 적합도 vs 매출 성장률)
**PC2 좌표:** 0.3 (축 의미: 경쟁 강도 vs 리스크)
**가장 가까운 경쟁사 거리:** 1.2

한 문장으로 답변하세요.
```

#### Output
```python
WhiteSpace(
    pc1_coord=1.5,
    pc2_coord=0.3,
    distance_to_nearest_cluster=1.2,
    opportunity_score=0.85,
    reasoning="고객 만족도가 높으면서도 경쟁이 적은 블루오션 지역"
)
```

---

### 5.4 Strategy Agent (🆕 역할 구체화)

#### 역할
STP 결과와 외부 트렌드를 결합하여 실행 가능한 4P 전략 수립

#### 주요 작업
1. **STP 결과 입력 검증**
   - Segmentation: 군집 특성 확인
   - Targeting: 타겟 고객층 니즈 분석
   - Positioning: 차별화 포인트 도출

2. **RAG를 통한 외부 트렌드 통합**
   ```python
   trend_context = rag.retrieve_relevant_trends(
       query=f"{industry} 업종 최신 트렌드"
   )
   ```

3. **4P 전략 구체화**
   
   | 4P | 활용 데이터 | 전략 내용 |
   |---|-----------|---------|
   | **Product** | - White Space 좌표<br>- RAG 트렌드 | 추천 포지션에 맞는 시그니처 메뉴/서비스 제안 |
   | **Price** | - PC1 좌표 (매출/객단가)<br>- 클러스터 평균 | PC1 수준에 맞는 가격대 설정 |
   | **Place** | - 업종 특성<br>- 배달 수요 트렌드 | 매장/배달/포장 중 집중 채널 |
   | **Promotion** | - 타겟 군집 특성<br>- RAG SNS 트렌드 | 타겟 고객 도달 홍보 방법 |

#### LLM 프롬프트 구조
```
당신은 마케팅 전략가입니다. 다음 STP 분석 결과를 바탕으로 실행 가능한 4P 전략을 수립하세요.

# STP 분석 결과
[Segmentation, Targeting, Positioning 데이터]

# 외부 트렌드 데이터
[RAG에서 검색된 업종별 트렌드]

---

다음 형식으로 4P 전략을 작성하세요 (각 항목 2-3문장):

**Product (제품 전략):**
**Price (가격 전략):**
**Place (유통 전략):**
**Promotion (프로모션 전략):**
**포지셔닝 컨셉 (한 문장):**
```

#### Output
```python
Strategy4P(
    product="건강 지향 우동 세트 (채소 중심, 저염)",
    price="점심 특선 8,000원, 정규 메뉴 10,000~13,000원",
    place="배달 40%, 매장 60% 집중, 포장 특화 메뉴 개발",
    promotion="인스타그램 비주얼 마케팅, 첫 방문 쿠폰 10%"
)

positioning_concept = "한양대 근처 건강한 한 끼, 빠르고 맛있는 우동 전문점"
```

---

### 5.5 Content Agent

#### 역할
전략을 실행 가능한 액션 플랜으로 변환

#### 주요 작업
1. 4P 전략을 주차별 실행 항목으로 분해
2. 타임라인 생성
3. 측정 가능한 목표 설정

#### LLM 프롬프트
```
다음 4P 전략을 실행 가능한 액션 플랜으로 변환하세요.

# 4P 전략
[Strategy Agent의 Output]

---

다음 형식으로 실행 계획을 작성하세요:

## 1주차: [액션 1]
## 2주차: [액션 2]
## 3주차: [액션 3]
## 4주차: [액션 4]

각 주차별 구체적인 실행 항목을 2-3개씩 나열하세요.
```

#### Output
```
## 1주차: Product 전략 실행
- 건강 우동 세트 레시피 개발
- 시식 이벤트 진행
- 고객 피드백 수집

## 2주차: Price 전략 실행
- 점심 특선 8,000원 프로모션 시작
- 객단가 모니터링

## 3주차: Place 전략 실행
- 배달앱 노출 최적화
- 포장 전용 메뉴 추가

## 4주차: Promotion 전략 실행
- 인스타그램 광고 집행
- 첫 방문 쿠폰 배포
```

---

## 6. 실행 방법

### 6.1 환경 설정

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install langchain langchain-google-genai langgraph
pip install pandas numpy scikit-learn
pip install streamlit plotly matplotlib seaborn
pip install faiss-cpu python-dotenv

# 환경 변수 설정
echo "GOOGLE_API_KEY=your_gemini_api_key" > .env
```

### 6.2 데이터 준비

```
data/
├── pca_components_by_industry.csv       # PCA 가중치
├── kmeans_clusters_by_industry.csv      # 클러스터 프로파일
├── store_segmentation_final.csv         # 가맹점 포지셔닝
└── df_final.csv                          # 가맹점 기본 정보
```

### 6.3 실행

#### CLI 실행
```bash
python marketing_multiagent_system_improved.py
```

#### Streamlit UI 실행
```bash
streamlit run streamlit_app.py
```

---

## 7. 시스템 테스트

### 7.1 단위 테스트

```python
# Segmentation Agent 테스트
def test_segmentation_agent():
    state = {
        'target_store_id': '0C67B8EDCF',
        'messages': []
    }
    result = segmentation_agent_node(state)
    assert 'stp_output' in result
    assert len(result['stp_output'].cluster_profiles) > 0

# White Space Detection 테스트
def test_white_space_detection():
    loader = STPDataLoader()
    loader.load_all_data()
    ws_list = loader.find_white_spaces("일식-우동/소바/라면")
    assert len(ws_list) > 0
    assert ws_list[0]['opportunity_score'] > 0
```

### 7.2 통합 테스트

```python
# 전체 시스템 실행
result = run_marketing_strategy_system(
    target_store_id="0C67B8EDCF",
    target_store_name="히토****"
)

# 검증
assert result['stp_output'] is not None
assert result['strategy_4p'] is not None
assert len(result['final_report']) > 0
```

---

## 8. 향후 확장 계획

### 8.1 단기 (1개월)
- [ ] 실제 RAG 시스템 구축 (Mock → Real)
- [ ] Situation Agent 추가 (단기 전술 담당)
- [ ] 보고서 PDF/DOCX 자동 생성

### 8.2 중기 (3개월)
- [ ] A/B 테스트 기능 추가
- [ ] 실시간 매출 데이터 연동
- [ ] 경쟁사 모니터링 Agent

### 8.3 장기 (6개월)
- [ ] Multi-modal 분석 (이미지, 리뷰 텍스트)
- [ ] 자동 실행 및 피드백 루프
- [ ] 다국어 지원

---

## 9. 참고 문서

- Langchain 공식 문서: https://python.langchain.com/docs/
- Langgraph 공식 문서: https://langchain-ai.github.io/langgraph/
- Gemini API 문서: https://ai.google.dev/docs

---

## 라이선스
MIT License

## 기여자
Marketing AI Team (2025)
