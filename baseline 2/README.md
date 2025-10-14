# 🎯 마케팅 Multi-Agent 시스템

점포/상권 데이터를 기반으로 근거 중심의 마케팅 전략을 생성하는 Multi-Agent 시스템입니다.

## 📋 주요 기능

- **컨텍스트 생성**: 점포/상권 데이터 수집 및 파생 지표 계산
- **상황 인식**: 날씨/행사 등 외부 상황 탐지
- **리소스 매칭**: 예산/채널에 맞는 실행 계획 생성
- **전략 생성**: 데이터 기반 마케팅 전략 카드 생성
- **전략 평가**: 생성된 전략의 품질 검증 및 수정 권고

## 🏗️ 시스템 구조

```
User Input → AgentState → [Context, Situation, Resource] → Strategy → Evaluation → Output
```

### Agent 구성

1. **Strategy Supervisor**: 최상위 의사결정 및 오케스트레이션
2. **Context Agent**: 점포/상권 컨텍스트 생성
3. **Situation Agent**: 외부 상황 인식
4. **Resource Agent**: 예산/채널/툴 매칭
5. **Evaluation Agent**: 전략 평가 및 수정 권고

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# Python 3.12 이상 필요
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 API 키 입력
```

필수 환경 변수:
- `GOOGLE_API_KEY`: Gemini API 키
- `PINECONE_API_KEY`: Pinecone API 키 (선택)
- `TAVILY_API_KEY`: Tavily API 키 (선택)

### 3. 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 📁 프로젝트 구조

```
marketing_agent/
├── app.py                       # Streamlit 메인 앱
├── requirements.txt
├── .env.example
│
├── agents/                      # Agent 노드
│   ├── graph.py                # LangGraph 조립
│   ├── strategy_supervisor.py  # 전략 슈퍼바이저
│   ├── context_agent.py        # 컨텍스트 에이전트
│   ├── situation_agent.py      # 상황 에이전트
│   ├── resource_agent.py       # 리소스 에이전트
│   └── evaluation_agent.py     # 평가 에이전트
│
├── contracts/                   # JSON 스키마
│   ├── intents.py              # 의도 정의
│   ├── context_schema.py       # 컨텍스트 스키마
│   └── card_schema.py          # 전략/평가 스키마
│
├── tools/                       # 외부 도구
│   ├── rag_tool.py             # Pinecone RAG
│   └── web_tool.py             # Tavily 웹 검색
│
└── prompts/                     # 프롬프트
    ├── strategy.md
    └── evaluation.md
```

## 🔧 기술 스택

- **Language**: Python 3.12
- **Framework**: LangChain, LangGraph, Streamlit
- **AI 모델**: Gemini 2.5 Flash
- **Vector DB**: Pinecone
- **Embeddings**: jhgan/ko-sroberta-multitask
- **Web Search**: Tavily
- **Libs**: pydantic, loguru, pandas, plotly

## 📊 데이터 스키마

### Context JSON
점포 기본 정보, 핵심 지표, 파생 지표, 상권 정보, 위험 평가 등을 포함합니다.

주요 파생 지표:
- 업종평균대비 매출비
- 매출 변동성 (4주)
- 런치/주말/오후 비중
- 경쟁 강도
- 상권 churn율
- 유동인구 지수

### Strategy Card
생성된 전략 카드는 다음을 포함합니다:
- 전략 가설 및 근거
- 타겟 세그먼트
- 채널 및 제안 내용
- 실행 기간 및 예산
- KPI 목표
- 위험 요소 및 가정

### Evaluation Report
전략 카드 평가 결과:
- 제약 조건 부합 여부
- 근거 품질 검증
- 실행 가능성 평가
- 수정 권고

## 🎯 사용 예시

### 1. 기본 전략 생성

```
질문: "평일 점심 매출을 늘리고 싶어. 예산 5만원, 인스타로."

제약:
- 예산: 50,000원
- 채널: Instagram

출력: 평일 런치 타겟 번들 프로모션 전략 카드
```

### 2. 상황 대응 전략

```
질문: "이번 주 비 온다는데 매출 영향 있을까?"

분석: 날씨 신호 탐지 → 우천 대응 전략 생성
```

## 🔐 보안 고려사항

- API 키는 절대 코드에 하드코딩하지 마세요
- `.env` 파일은 `.gitignore`에 추가하세요
- 프로덕션 환경에서는 적절한 인증/권한 시스템을 구축하세요

## 📝 개발 가이드

### Agent 추가하기

1. `agents/` 디렉토리에 새 Agent 파일 생성
2. `graph.py`에 노드 등록
3. 필요한 경우 스키마 추가 (`contracts/`)

### 프롬프트 수정하기

`prompts/` 디렉토리의 Markdown 파일을 수정하세요.

### 새 도구 추가하기

`tools/` 디렉토리에 새 도구 클래스 생성 후 Agent에서 호출하세요.

## 🐛 문제 해결

### Pinecone 연결 실패
- API 키와 Environment 확인
- 무료 플랜은 1개 인덱스만 지원

### LangGraph 실행 오류
- pydantic 버전 확인 (v2 필요)
- 모든 Agent 노드가 상태를 반환하는지 확인

### Streamlit 렌더링 문제
- 브라우저 캐시 삭제
- `streamlit cache clear` 실행

## 📚 참고 문서

- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [Pinecone 문서](https://docs.pinecone.io/)
- [Gemini API 문서](https://ai.google.dev/docs)
- [Streamlit 문서](https://docs.streamlit.io/)

## 📄 라이선스

MIT License

## 👥 기여

이슈 및 PR을 환영합니다!

## 📧 문의

문제가 있거나 제안이 있으시면 Issue를 생성해주세요.