# System Architecture Diagrams
## Marketing MultiAgent System - Visual Guide

---

## 1. 전체 시스템 아키텍처

```mermaid
graph TB
    User[👤 사용자] -->|가맹점 선택| UI[🖥️ Streamlit UI]
    UI -->|요청| Supervisor[🎯 Top-Level Supervisor]
    
    Supervisor -->|1. 분석 요청| AnalysisTeam[📊 분석팀<br/>Market Analysis Team]
    AnalysisTeam -->|STPOutput| Supervisor
    
    Supervisor -->|2. 전략 요청| StrategyTeam[🎯 전략팀<br/>Strategy Planning Team]
    StrategyTeam -->|4P 전략| Supervisor
    
    Supervisor -->|3. 보고서 생성| Report[📄 Final Report Generator]
    Report -->|최종 보고서| UI
    UI -->|표시| User
    
    style Supervisor fill:#ff6b6b,color:#fff
    style AnalysisTeam fill:#4ecdc4,color:#fff
    style StrategyTeam fill:#95e1d3,color:#fff
    style Report fill:#f38181,color:#fff
```

---

## 2. 분석팀 (Market Analysis Team) 상세 구조

```mermaid
graph LR
    Start([START]) --> Seg[🔍 Segmentation Agent]
    
    Seg -->|ClusterProfile[]<br/>PCAxisInterpretation| Targ[🎯 Targeting Agent]
    
    Targ -->|target_cluster_id<br/>StorePosition| Pos[📍 Positioning Agent]
    
    Pos -->|WhiteSpace[]<br/>recommended_white_space| End([STPOutput])
    
    subgraph "Segmentation"
        Seg --> KMeans[K-Means 클러스터링]
        Seg --> PCA[PCA 축 해석]
        Seg --> LLM1[Gemini 2.5 Pro<br/>특성 생성]
    end
    
    subgraph "Targeting"
        Targ --> Current[현재 포지션 파악]
        Targ --> Target[타겟 군집 선정]
    end
    
    subgraph "Positioning"
        Pos --> Grid[그리드 생성]
        Pos --> Distance[거리 계산]
        Pos --> Score[기회 점수 계산]
        Pos --> LLM2[Gemini 2.5 Pro<br/>Reasoning 생성]
    end
    
    style Seg fill:#4ecdc4,color:#fff
    style Targ fill:#45b7d1,color:#fff
    style Pos fill:#3d9db5,color:#fff
```

---

## 3. 전략팀 (Strategy Planning Team) 상세 구조

```mermaid
graph LR
    Input([STPOutput]) --> SA[🎯 Strategy Agent]
    
    SA -->|Strategy4P<br/>positioning_concept| CA[📝 Content Agent]
    
    CA -->|execution_plan| Output([최종 전략])
    
    subgraph "Strategy Agent"
        SA --> Validate[STP 검증]
        SA --> RAG[RAG 트렌드 검색]
        SA --> Product[Product 전략]
        SA --> Price[Price 전략]
        SA --> Place[Place 전략]
        SA --> Promotion[Promotion 전략]
    end
    
    subgraph "Content Agent"
        CA --> Week1[1주차 계획]
        CA --> Week2[2주차 계획]
        CA --> Week3[3주차 계획]
        CA --> Week4[4주차 계획]
    end
    
    RAG -.->|트렌드 데이터| TrendDB[(📚 Trend Database<br/>FAISS Vector Store)]
    
    style SA fill:#95e1d3,color:#000
    style CA fill:#81c784,color:#fff
    style TrendDB fill:#ffd54f,color:#000
```

---

## 4. 데이터 흐름 (Data Flow)

```mermaid
sequenceDiagram
    participant U as 👤 사용자
    participant UI as 🖥️ UI
    participant S as 🎯 Supervisor
    participant AT as 📊 분석팀
    participant ST as 🎯 전략팀
    participant R as 📄 Report
    
    U->>UI: 가맹점 선택
    UI->>S: target_store_id
    
    rect rgb(200, 230, 255)
        Note over S,AT: 분석 단계
        S->>AT: 분석 요청
        AT->>AT: Segmentation
        AT->>AT: Targeting
        AT->>AT: Positioning
        AT-->>S: STPOutput
    end
    
    rect rgb(200, 255, 230)
        Note over S,ST: 전략 수립 단계
        S->>ST: STPOutput 전달
        ST->>ST: RAG 트렌드 검색
        ST->>ST: 4P 전략 생성
        ST->>ST: 실행 계획 작성
        ST-->>S: Strategy4P + execution_plan
    end
    
    rect rgb(255, 230, 200)
        Note over S,R: 보고서 생성 단계
        S->>R: 통합 데이터
        R->>R: 보고서 포맷팅
        R-->>S: final_report
    end
    
    S-->>UI: 최종 결과
    UI-->>U: 시각화 + 보고서
```

---

## 5. STP 분석 프로세스

```mermaid
flowchart TD
    Start([시작]) --> LoadData[📂 데이터 로드]
    
    LoadData --> S1[🔍 SEGMENTATION]
    S1 --> S1_1[K-Means 클러스터링<br/>n=3~7개 군집]
    S1_1 --> S1_2[PCA 차원 축소<br/>PC1, PC2 축 정의]
    S1_2 --> S1_3[Gemini로 군집 특성 생성]
    
    S1_3 --> T1[🎯 TARGETING]
    T1 --> T1_1[우리 가맹점 좌표<br/>PC1, PC2 확인]
    T1_1 --> T1_2[소속 군집 확인<br/>cluster_id 매칭]
    T1_2 --> T1_3[타겟 군집 선정<br/>공략 대상 결정]
    
    T1_3 --> P1[📍 POSITIONING]
    P1 --> P1_1[그리드 생성<br/>PC1 × PC2 평면]
    P1_1 --> P1_2{각 그리드<br/>경쟁사 거리 > 0.5?}
    P1_2 -->|Yes| P1_3[White Space로 분류]
    P1_2 -->|No| P1_1
    P1_3 --> P1_4[기회 점수 계산<br/>opportunity_score]
    P1_4 --> P1_5[Gemini로 Reasoning 생성]
    
    P1_5 --> Output([STPOutput 생성])
    
    style S1 fill:#e3f2fd
    style T1 fill:#f3e5f5
    style P1 fill:#e8f5e9
    style Output fill:#fff9c4
```

---

## 6. White Space Detection 알고리즘

```mermaid
flowchart LR
    Input[PC1 × PC2 평면] --> Grid[그리드 생성<br/>20×20]
    
    Grid --> Loop{각 그리드 포인트}
    
    Loop --> CalcDist[가장 가까운<br/>경쟁사 거리 계산]
    
    CalcDist --> Check{거리 ≥ 0.5?}
    
    Check -->|No| Loop
    Check -->|Yes| Score[기회 점수 계산<br/>distance × center_factor]
    
    Score --> Add[White Space 리스트에 추가]
    
    Add --> Loop
    
    Loop --> Sort[기회 점수 기준 정렬]
    
    Sort --> Top10[상위 10개 선택]
    
    Top10 --> LLM[Gemini로<br/>각 포지션의<br/>Reasoning 생성]
    
    LLM --> Output([WhiteSpace[] 반환])
    
    style Check fill:#ffeb3b
    style Score fill:#4caf50,color:#fff
    style LLM fill:#2196f3,color:#fff
```

---

## 7. Strategy Agent 4P 전략 생성 프로세스

```mermaid
flowchart TD
    Input([STPOutput]) --> Validate[입력 검증]
    
    Validate --> RAG[📚 RAG 트렌드 검색]
    RAG --> TrendDB[(FAISS<br/>Trend Database)]
    TrendDB --> Context[트렌드 컨텍스트]
    
    Context --> Combine[STP + 트렌드 결합]
    
    Combine --> Product[🎨 Product 전략<br/>White Space 좌표 기반<br/>시그니처 메뉴 제안]
    
    Combine --> Price[💰 Price 전략<br/>PC1 좌표 기반<br/>가격대 설정]
    
    Combine --> Place[📍 Place 전략<br/>배달/매장 비중<br/>유통 채널 선택]
    
    Combine --> Promotion[📢 Promotion 전략<br/>타겟 고객 맞춤<br/>홍보 방법]
    
    Product --> Concept[포지셔닝 컨셉 정의]
    Price --> Concept
    Place --> Concept
    Promotion --> Concept
    
    Concept --> Output([Strategy4P])
    
    style RAG fill:#ffd54f,color:#000
    style Product fill:#4caf50,color:#fff
    style Price fill:#2196f3,color:#fff
    style Place fill:#ff9800,color:#fff
    style Promotion fill:#e91e63,color:#fff
```

---

## 8. Streamlit UI 구조

```mermaid
graph TB
    Main[📱 Main Page] --> Sidebar[📋 Sidebar]
    Main --> Content[📊 Main Content]
    
    Sidebar --> Filter[업종 필터]
    Sidebar --> Select[가맹점 선택]
    Sidebar --> Options[분석 옵션]
    Sidebar --> Button[🚀 분석 시작 버튼]
    
    Button -->|클릭| Execute[시스템 실행]
    
    Execute --> Tab1[Tab 1: STP 분석]
    Execute --> Tab2[Tab 2: 전략 수립]
    Execute --> Tab3[Tab 3: 실행 계획]
    Execute --> Tab4[Tab 4: 최종 보고서]
    
    Tab1 --> Map[포지셔닝 맵<br/>Plotly 시각화]
    Tab1 --> Table[군집별 특성 테이블]
    
    Tab2 --> Cards[4P 전략 카드]
    Tab2 --> Concept[포지셔닝 컨셉]
    
    Tab3 --> Timeline[실행 타임라인<br/>Gantt 차트]
    Tab3 --> Plan[주차별 계획]
    
    Tab4 --> Report[최종 보고서 텍스트]
    Tab4 --> Download[📥 다운로드 버튼]
    
    style Main fill:#1976d2,color:#fff
    style Execute fill:#f44336,color:#fff
    style Map fill:#4caf50,color:#fff
    style Cards fill:#ff9800,color:#fff
    style Timeline fill:#9c27b0,color:#fff
    style Report fill:#607d8b,color:#fff
```

---

## 9. 에이전트 간 State 전달

```mermaid
stateDiagram-v2
    [*] --> SupervisorState
    
    SupervisorState --> MarketAnalysisState: route to analysis
    
    state MarketAnalysisState {
        [*] --> SegmentationAgent
        SegmentationAgent --> TargetingAgent: cluster_profiles
        TargetingAgent --> PositioningAgent: store_position
        PositioningAgent --> [*]: STPOutput
    }
    
    MarketAnalysisState --> SupervisorState: STPOutput
    
    SupervisorState --> StrategyTeamState: route to strategy
    
    state StrategyTeamState {
        [*] --> StrategyAgent
        StrategyAgent --> ContentAgent: Strategy4P
        ContentAgent --> [*]: execution_plan
    }
    
    StrategyTeamState --> SupervisorState: final_data
    
    SupervisorState --> ReportGenerator: generate report
    
    ReportGenerator --> [*]: final_report
    
    note right of MarketAnalysisState
        STPOutput 생성:
        - cluster_profiles
        - pc_interpretation
        - white_spaces
    end note
    
    note right of StrategyTeamState
        전략 생성:
        - Strategy4P
        - positioning_concept
        - execution_plan
    end note
```

---

## 10. 데이터 모델 관계도

```mermaid
erDiagram
    STPOutput ||--o{ ClusterProfile : contains
    STPOutput ||--o{ PCAxisInterpretation : contains
    STPOutput ||--|| StorePosition : has
    STPOutput ||--o{ WhiteSpace : contains
    STPOutput ||--|| WhiteSpace : recommends
    
    ClusterProfile {
        int cluster_id
        string cluster_name
        int store_count
        float pc1_mean
        float pc2_mean
        string characteristics
    }
    
    PCAxisInterpretation {
        string axis
        string interpretation
        list top_features
    }
    
    StorePosition {
        string store_id
        string store_name
        string industry
        float pc1_score
        float pc2_score
        int cluster_id
        string cluster_name
    }
    
    WhiteSpace {
        float pc1_coord
        float pc2_coord
        float distance_to_nearest
        float opportunity_score
        string reasoning
    }
    
    Strategy4P {
        string product
        string price
        string place
        string promotion
    }
    
    STPOutput ||--|| Strategy4P : generates
```

---

## 사용 방법

### Mermaid 다이어그램 렌더링

1. **GitHub/GitLab**: 마크다운 파일에서 자동 렌더링
2. **VSCode**: Mermaid 확장 프로그램 설치
3. **온라인 에디터**: https://mermaid.live/

### 다이어그램 수정

```mermaid
graph LR
    A[시작] --> B{조건}
    B -->|Yes| C[작업 1]
    B -->|No| D[작업 2]
    C --> E[종료]
    D --> E
```

---

## 참고

- [Mermaid 공식 문서](https://mermaid.js.org/)
- [Mermaid Live Editor](https://mermaid.live/)
