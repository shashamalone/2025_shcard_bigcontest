# 🎯 소상공인 마케팅 MultiAgent 시스템

LangChain과 LangGraph를 활용한 AI 기반 마케팅 전략 자동 생성 시스템

## 📋 프로젝트 개요

소규모 비즈니스 소유자를 위해 자동으로 맞춤형 마케팅 전략을 제안하는 MultiAgent 시스템입니다.

### 주요 기능

- **데이터 분석가 Agent**: RAG(Pinecone) + 웹 검색(Tavily)으로 성공 사례 및 트렌드 분석
- **콘텐츠 작가 Agent**: 타겟 고객에 맞는 마케팅 카피 및 소셜 미디어 콘텐츠 생성
- **그래픽 디자이너 Agent**: 브랜드 스타일 및 플랫폼별 디자인 컨셉 제안
- **브랜드 매니저 Agent**: 최종 검토 및 전략 승인

## 🏗️ 시스템 구조

```
marketing_agent/
├── app.py                          # Streamlit UI
├── requirements.txt                # 패키지 목록
├── .env.example                    # 환경 변수 템플릿
├── README.md
│
├── agents/
│   ├── __init__.py
│   └── agent_graph_simple.py      # LangGraph 워크플로우
│
└── tools/
    ├── __init__.py
    ├── analyst_tool.py            # 데이터 분석 도구
    ├── designer_tool.py           # 디자인 도구
    └── content_writer_tool.py     # 콘텐츠 작성 도구
```

## 🔄 Agent 워크플로우

```
Start 
  ↓
Content Writer (콘텐츠 초안 작성)
  ↓
Graphic Designer (디자인 컨셉)
  ↓
Data Analyst (시장 분석 + RAG + 웹 검색)
  ↓
Brand Manager (검토 및 승인)
  ↓
[수정 필요?] → Yes → Content Writer로 복귀 (최대 2회)
  ↓
[승인] → End
```

## 🛠️ 기술 스택

- **Language**: Python 3.10+
- **Framework**: 
  - LangChain (MultiAgent 시스템)
  - LangGraph (워크플로우 관리)
  - Streamlit (UI)
- **AI Models**: 
  - OpenAI GPT-4o-mini
  - HuggingFace Embeddings (ko-sroberta-multitask)
- **Tools**:
  - Pinecone (Vector DB for RAG)
  - Tavily (웹 검색)
- **Libraries**: pandas, matplotlib, seaborn, plotly, scikit-learn

## 📦 설치 방법

### 1. 저장소 클론

```bash
git clone <repository-url>
cd marketing_agent
```

### 2. 가상환경 생성 및 활성화

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

`.env.example` 파일을 `.env`로 복사하고 API 키를 입력합니다:

```bash
cp .env.example .env
```

`.env` 파일 편집:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=my-index
```

### 5. __init__.py 파일 생성

```bash
# agents 디렉토리
touch agents/__init__.py

# tools 디렉토리
touch tools/__init__.py
```

## 🚀 실행 방법

```bash
streamlit run app.py
```

브라우저에서 자동으로 `http://localhost:8501` 열림

## 📖 사용 방법

1. **비즈니스 정보 입력**
   - 비즈니스 이름, 업종, 타겟 고객 입력
   - 마케팅 목표 및 예산 설정

2. **마케팅 채널 선택**
   - Instagram, Facebook, 블로그 등 선호 채널 선택
   - 캠페인 유형 및 기간 설정

3. **AI 전략 생성**
   - "AI 마케팅 전략 생성" 버튼 클릭
   - 각 Agent가 순차적으로 작업 수행

4. **결과 확인**
   - 종합 전략, 데이터 분석, 콘텐츠, 디자인 탭에서 결과 확인
   - TXT 파일로 다운로드 가능

## 🔑 API 키 발급

### OpenAI (필수)
- https://platform.openai.com/api-keys
- GPT-4o-mini 모델 사용

### Tavily (선택 - 웹 검색)
- https://tavily.com
- 무료 플랜: 월 1,000회 검색

### Pinecone (선택 - RAG)
- https://www.pinecone.io
- 무료 플랜: 1 index, 100K 벡터

## 📊 Agent 상세 설명

### 1. Content Writer Agent
- 마케팅 카피 작성
- 소셜 미디어 콘텐츠 생성
- 이메일 캠페인 초안 작성

### 2. Graphic Designer Agent
- 브랜드 컬러 팔레트 제안
- 플랫폼별 디자인 가이드
- 시각적 계층 구조 설계

### 3. Data Analyst Agent
- **RAG**: Pinecone에서 성공 사례 검색
- **웹 검색**: Tavily로 최신 트렌드 조사
- 시장 데이터 분석 및 인사이트 제공

### 4. Brand Manager Agent
- 전체 전략 검토
- 품질 확인 (콘텐츠, 디자인, 분석)
- 수정 필요 시 재작업 요청 (최대 2회)

## ⚙️ 커스터마이징

### Agent 수정

`agents/agent_graph_simple.py`에서 각 Agent의 system_prompt 수정:

```python
system_prompt = """당신은 전문 마케팅 콘텐츠 작가입니다.
[원하는 역할과 지시사항 추가]
"""
```

### Tool 추가

`tools/` 디렉토리에 새로운 도구 파일 생성:

```python
from langchain.tools import tool

@tool
def your_new_tool(input: str) -> str:
    """도구 설명"""
    # 로직 구현
    return result
```

### 워크플로우 변경

`agents/agent_graph_simple.py`의 `create_marketing_workflow()` 함수에서 노드 및 엣지 수정

## 🐛 문제 해결

### API 키 오류
```
Error: OpenAI API key not found
```
→ `.env` 파일에 `OPENAI_API_KEY` 확인

### Pinecone 연결 오류
```
Pinecone 초기화 실패
```
→ Pinecone index가 생성되어 있는지 확인
→ 없으면 RAG 기능이 비활성화되지만 다른 기능은 정상 작동

### 패키지 설치 오류
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

## 📝 라이선스

MIT License

## 🤝 기여

Pull Request 환영합니다!

## 📧 문의

문제가 있거나 제안사항이 있으시면 Issue를 등록해주세요.

---

**Made with ❤️ using LangChain & LangGraph**