# 🚀 Quick Start Guide

## Marketing MultiAgent System 실행 가이드

---

## 📋 사전 준비

### 1. Python 환경
- **Python 3.10 이상** 필수
- 확인: `python --version`

### 2. Google Gemini API Key
1. [Google AI Studio](https://aistudio.google.com/) 접속
2. API Key 발급
3. `.env` 파일에 저장

---

## 🔧 설치 (5분)

### Step 1: 프로젝트 다운로드
```bash
# Git clone (또는 ZIP 다운로드)
git clone https://github.com/your-repo/marketing-multiagent.git
cd marketing-multiagent
```

### Step 2: 가상환경 생성
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### Step 3: 패키지 설치
```bash
pip install -r requirements.txt
```

### Step 4: 환경 변수 설정
```bash
# .env 파일 생성
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
```

---

## 📂 데이터 준비

### 데이터 파일 구조
```
data/
├── pca_components_by_industry.csv       # PCA 가중치 데이터
├── kmeans_clusters_by_industry.csv      # 클러스터 프로파일
├── store_segmentation_final.csv         # 가맹점 포지셔닝 데이터
└── df_final.csv                          # 가맹점 기본 정보
```

### 데이터 로딩 경로 수정
`marketing_multiagent_system_improved.py` 파일에서 데이터 경로 수정:

```python
# Line 27
DATA_DIR = "/your/data/path"  # 실제 데이터 경로로 변경
```

---

## 🎯 실행 방법

### 방법 1: Streamlit UI (권장)

```bash
streamlit run streamlit_app.py
```

브라우저에서 자동으로 열림 (기본 http://localhost:8501)

#### UI 사용법
1. **사이드바**에서 가맹점 선택
   - 업종 필터 사용 가능
   - 가맹점명 검색
   
2. **분석 옵션** 설정
   - 외부 트렌드 데이터 활용 여부
   - 상세도 선택

3. **전략 분석 시작** 버튼 클릭

4. **결과 확인**
   - Tab 1: STP 분석 (포지셔닝 맵)
   - Tab 2: 전략 수립 (4P)
   - Tab 3: 실행 계획 (주차별)
   - Tab 4: 최종 보고서

---

### 방법 2: Python CLI

```python
# Python 스크립트 실행
python marketing_multiagent_system_improved.py
```

또는 Python 인터프리터에서:

```python
from marketing_multiagent_system_improved import run_marketing_strategy_system

# 가맹점 ID와 이름 입력
result = run_marketing_strategy_system(
    target_store_id="0C67B8EDCF",  # 실제 가맹점 ID
    target_store_name="히토****"
)

# 결과 확인
print(result['final_report'])
```

---

## 📊 출력 결과

### 1. STP 분석 결과
```python
result['stp_output']
# - cluster_profiles: 시장 군집 정보
# - pc_axis_interpretation: PC축 해석
# - target_cluster_id: 타겟 군집 ID
# - store_current_position: 현재 포지션
# - white_spaces: 빈 포지션 리스트
# - recommended_white_space: 추천 포지션
```

### 2. 4P 전략
```python
result['strategy_4p']
# - product: 제품 전략
# - price: 가격 전략
# - place: 유통 전략
# - promotion: 프로모션 전략
```

### 3. 실행 계획
```python
result['execution_plan']
# 주차별 액션 플랜
```

### 4. 최종 보고서
```python
result['final_report']
# 통합된 마케팅 전략 보고서 (텍스트)
```

---

## 🐛 문제 해결 (Troubleshooting)

### 1. API Key 오류
```
Error: GOOGLE_API_KEY not found
```

**해결:**
```bash
# .env 파일 확인
cat .env

# 없으면 생성
echo "GOOGLE_API_KEY=your_actual_key" > .env
```

---

### 2. 데이터 파일 없음
```
FileNotFoundError: data/df_final.csv not found
```

**해결:**
- 데이터 파일이 올바른 경로에 있는지 확인
- `DATA_DIR` 변수 수정 (코드 내)

---

### 3. 패키지 버전 충돌
```
ImportError: cannot import name 'XXX'
```

**해결:**
```bash
# 가상환경 재생성
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 4. Streamlit 포트 충돌
```
OSError: [Errno 48] Address already in use
```

**해결:**
```bash
# 다른 포트 사용
streamlit run streamlit_app.py --server.port 8502
```

---

### 5. 메모리 부족
```
MemoryError
```

**해결:**
- `grid_resolution` 파라미터 줄이기 (White Space Detection)
- 대용량 데이터셋 샘플링

---

## 🔍 테스트 실행

### 1. 간단한 기능 테스트
```python
# Python 인터프리터에서
from marketing_multiagent_system_improved import STPDataLoader

loader = STPDataLoader()
loader.load_all_data()

# 데이터 로드 확인
print(f"PCA Loadings: {loader.pca_loadings.shape}")
print(f"Cluster Profiles: {loader.cluster_profiles.shape}")
print(f"Store Positioning: {loader.store_positioning.shape}")
```

### 2. White Space Detection 테스트
```python
from marketing_multiagent_system_improved import STPDataLoader

loader = STPDataLoader()
loader.load_all_data()

# 빈 포지션 탐지
white_spaces = loader.find_white_spaces("일식-우동/소바/라면")
print(f"발견된 White Space: {len(white_spaces)}개")
print(white_spaces[0])  # 최고 점수 포지션
```

---

## 📈 성능 최적화

### 1. LLM 호출 최소화
- Segmentation Agent의 클러스터 특성 생성 시 배치 처리

### 2. 캐싱 활용
```python
# Streamlit 캐싱
@st.cache_data
def load_store_list():
    # 데이터 로딩 로직
    ...
```

### 3. 병렬 처리
- 여러 White Space의 reasoning 생성 시 병렬화 가능

---

## 📚 추가 자료

### 공식 문서
- [Langchain 문서](https://python.langchain.com/docs/)
- [Langgraph 문서](https://langchain-ai.github.io/langgraph/)
- [Streamlit 문서](https://docs.streamlit.io/)

### 커뮤니티
- GitHub Issues: 버그 리포트 및 기능 요청
- Discussions: 사용 방법 문의

---

## 🎓 예제 시나리오

### 시나리오 1: 신규 카페 전략 수립
```python
result = run_marketing_strategy_system(
    target_store_id="CAFE001",
    target_store_name="신촌커피"
)

# STP 분석
print(result['stp_output'].target_cluster_name)
# → "젊은층 집중 군집"

# 추천 포지션
print(result['stp_output'].recommended_white_space.reasoning)
# → "SNS 활성도가 높으면서 경쟁이 적은 블루오션"

# 4P 전략
print(result['strategy_4p'].product)
# → "인스타그래머블 시그니처 음료 개발"
```

### 시나리오 2: 기존 음식점 포지셔닝 변경
```python
result = run_marketing_strategy_system(
    target_store_id="0C67B8EDCF",
    target_store_name="히토****"
)

# 현재 위치 vs 추천 위치
current = result['stp_output'].store_current_position
recommended = result['stp_output'].recommended_white_space

print(f"현재: PC1={current.pc1_score:.2f}, PC2={current.pc2_score:.2f}")
print(f"목표: PC1={recommended.pc1_coord:.2f}, PC2={recommended.pc2_coord:.2f}")

# 이동 전략
print(result['execution_plan'])
# → 4주간의 구체적인 실행 계획
```

---

## 🛠️ 커스터마이징

### 1. White Space 탐지 파라미터 조정
```python
# marketing_multiagent_system_improved.py
white_spaces = loader.find_white_spaces(
    industry,
    grid_resolution=20,    # 그리드 밀도 (높을수록 정밀)
    min_distance=0.8       # 최소 거리 (높을수록 엄격)
)
```

### 2. 4P 전략 템플릿 수정
```python
# strategy_agent_node 함수 내 프롬프트 수정
prompt = f"""
... (기존 내용)

추가 지침:
- 예산: {budget}원 이하
- 기간: {period}개월
- 우선순위: {priority}
"""
```

### 3. RAG 트렌드 데이터 추가
```python
# TrendRAGSystem 클래스
trend_data_path = "data/custom_trends.json"
rag = TrendRAGSystem(trend_data_path)
```

---

## 🎯 다음 단계

1. ✅ **Quick Start 완료**
2. 📖 **README.md** 읽기 (상세 아키텍처)
3. 🧪 **예제 시나리오** 실행
4. 🛠️ **커스터마이징** 적용
5. 🚀 **프로덕션 배포**

---

## 💬 지원

문제가 발생하면:
1. GitHub Issues에 버그 리포트
2. Discussions에서 질문
3. 📧 이메일: support@marketing-ai.com

---

**즐거운 마케팅 전략 수립 되세요! 🎉**
