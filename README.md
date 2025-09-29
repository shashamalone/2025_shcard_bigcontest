
### 📂 프로젝트 구조 (To-Be)
```
project_root
 ├── app.py                   # ✅ UI (Streamlit)
 ├── agents/
 │    ├── __init__.py
 │    ├── agent_graph.py       # LangGraph 워크플로우 정의
 │    ├── prompts.py           # 시스템 프롬프트 / 메시지 템플릿
 │    └── llm_config.py        # LLM 설정
 ├── tools/                    # ✅ 툴 전용 폴더
 │    ├── __init__.py
 │    ├── mcp_tool.py          # MCP 서버 툴 (가맹점 검색 API)
 │    ├── rag_tool.py          # Pinecone RAG 검색 툴
 │    └── utils.py             # 공통 유틸 (예: 로깅, 포맷팅)
 ├── data/
 │    ├── mct_sample.csv          # 가맹점 샘플데이터
 │    ├── rag_marketing_data.csv  # MCP 서버 툴 (가맹점 검색 API)
 │
 ├── requirements.txt
 └── pyproject.toml
 ```
