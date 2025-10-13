# 🎯 소상공인 마케팅 MultiAgent 시스템 v2.0

LangChain과 LangGraph를 활용한 지능형 마케팅 전략 자동 생성 시스템

## 📋 주요 특징

### MultiAgent 아키텍처
- **Strategy Supervisor**: 의도 분석 및 전략 통합
- **Context Agent**: 점포/상권 컨텍스트 생성
- **Situation Agent**: 날씨/이벤트 기반 상황 인식
- **Resource Agent**: 예산/채널/도구 매칭
- **Evaluation Agent**: 전략 검증 및 품질 보증

### 사전 질문 검증
1. 카페 - 고객 특성별 채널 추천 및 홍보안
2. 재방문율 30% 이하 - 개선 마케팅 아이디어
3. 요식업 - 문제점 진단 및 보완 방안
4. 상권 특화 - 이벤트/날씨 결합 전략

## 🏗️ 시스템 구조

```
marketing_agent/
├── app.py                          # Streamlit UI
├── requirements.txt
├── .env.example
├── README.md
│
├── agents/
│   ├── __init__.py
│   ├── graph.py                    # LangGraph 메인
│   ├── strategy_supervisor.py      # 최상위 의사결정
│   ├── context_agent.py            # 점포/상권 분석
│   ├── situation_agent.py          # 날씨/행사 인식
│   ├── resource_agent.py           # 예산/채널 매칭
│   └── evaluation_agent.py         # 전략 평가
│
├── tools/
│   ├── __init__.py
│   ├── analyst_tool.py             # 데이터 분석
│   ├── content_writer_tool.py      # 콘텐츠 생성
│   ├── designer_tool.py            # 디자인 제안
│   ├── rag_tool.py                 # Pinecone RAG
│   └── web_tool.py                 # Tavily/날씨/행사
│
├── contracts/                      # 스키마 정의 (추가 예정)
├── data/sql/                       # SQL 템플릿 (추가 예정)
└── prompts/                        # 프롬프트 (추가 예정)
```

## 🔄 Agent 워크플로우

```
User Input
    ↓
strategy_supervisor (의도 분석)
    ↓
    ├─→ context_agent (점포/상권)
    ├─→ situation_agent (날씨/이벤트)
    └─→ resource_agent (예산/채널)
    ↓
merge_supervisor (전략 카드 생성)
    ↓
evaluation_agent (품질 검증)
    ↓
END (최종 전략)
```

## 🛠️ 기술 스택

- **Language**: Python 3.12
- **Framework**: LangChain, LangGraph, Streamlit
- **AI 모델**: 
  - Gemini 2.0 Flash (생성)
  - HuggingFace `jhgan/ko-sroberta-multitask` (임베딩)
- **Tools**: 
  - Pinecone (Vector DB)
  - Tavily (웹 검색)
- **Libraries**: pandas, plotly, matplotlib, scikit-learn, pydantic v2

## 📦 설치 방법

### 1. 저장소 클론

```bash
git clone <repository-url>
cd marketing_agent
```

### 2. 가상환경 생성

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일 편집:

```env
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_key  # 선택
PINECONE_API_KEY=your_pinecone_key  # 선택
PINECONE_INDEX_NAME=marketing-kb
```

### 5. 디렉토리 초기화

```bash
# __init__.py 생성
touch agents/__init__.py
touch tools/__init__.py
```

## 🚀 실행 방법

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 자동 실행

## 📖 사용 방법

### 1. 비즈니스 정보 입력
- 가맹점명 (비공개 가능)
- 업종 선택
- 구체적인 마케팅 질문

### 2. 제약 조건 설정
- 월 마케팅 예산
- 선호 채널
- 실행 기간

### 3. AI 전략 생성
- "AI 전략 생성 시작" 버튼 클릭
- MultiAgent 시스템이 순차 실행

### 4. 결과 확인
- **전략 카드**: 구체적인 실행 방안
- **컨텍스트**: 점포/상권 분석
- **상황**: 날씨/이벤트 정보
- **리소스**: 예산/채널/도구
- **평가**: 전략 품질 검증
- **로그**: Agent 실행 과정

## 🔑 API 키 발급

### Google Gemini (필수)
```
https://makersuite.google.com/app/apikey
```

### Tavily (선택)
```
https://tavily.com
무료: 월 1,000회 검색
```

### Pinecone (선택)
```
https://www.pinecone.io
무료: 1 index, 100K 벡터
```

## 📊 State 스키마

```python
class AgentState(BaseModel):
    user_query: str
    intent: Literal["strategy", "overview"]
    constraints: dict
    context_json: dict | None
    situation_json: dict | None
    resource_json: dict | None
    strategy_cards: list[dict]
    eval_report: dict | None
    logs: list[str]
```

## 🎯 전략 카드 스키마

```python
{
    "card_type": "strategy",
    "title": "전략명",
    "why": ["근거1", "근거2"],
    "what": ["실행내용1", "실행내용2"],
    "how": [
        {"step": "단계", "owner": "담당자", "eta_min": 시간}
    ],
    "expected_effect": {
        "kpi": "지표명",
        "lift_hypothesis": "예상효과"
    },
    "references": [{"type": "출처유형", "source": "출처"}]
}
```

## ⚙️ 커스터마이징

### Agent 수정
각 `agents/*.py` 파일에서 LLM 프롬프트 수정

### Tool 추가
`tools/` 디렉토리에 새 도구 추가:

```python
from langchain.tools import tool

@tool
def your_tool(input: str) -> str:
    """도구 설명"""
    return result
```

### 워크플로우 변경
`agents/graph.py`의 `build_graph()` 수정
