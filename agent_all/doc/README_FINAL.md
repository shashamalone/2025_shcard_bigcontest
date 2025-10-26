# Marketing MultiAgent System - Phase 1-3 구현 완료 🎉

## 📦 구현 완료 내용

### ✅ Phase 1: 데이터 매핑 (2시간)
- **StoreRawData 모델** - 가맹점 실제 데이터 통합
- **StoreDataEnricher 클래스** - CSV 데이터 추출 및 변환
- **STP 검증 함수** - Segmentation/Targeting/Positioning 검증

### ✅ Phase 2: 전략 카드 생성 (2시간)
- **StrategyCard 모델** - 전략 카드 데이터 구조
- **StrategyCardGenerator 클래스** - 3가지 전략 카드 생성 로직
  - 종합 전략 (Product/Price/Promotion)
  - 상황 전술 (날씨/이벤트 기반) ⚡
  - 콘텐츠 생성 (하드코딩, 템플릿 확장 가능)

### ✅ Phase 3: UI 재구성 (1.5시간)
- **Streamlit UI** - 전략 카드 3개 가로 배치
- **3개 탭 구조**:
  - Tab 1: 가맹점 정보
  - Tab 2: 전략 카드 (핵심!)
  - Tab 3: 상세 보고서

---

## 📂 파일 구조

```
/home/claude/
├── models.py                          # 데이터 모델 (StoreRawData, StrategyCard 등)
├── data_enricher.py                   # 데이터 추출 클래스
├── strategy_card_generator.py         # 전략 카드 생성 로직
├── marketing_system_integrated.py     # 통합 시스템 (Strategy Node)
├── streamlit_app_final.py             # Streamlit UI (최종)
└── README_FINAL.md                    # 이 문서
```

---

## 🚀 실행 방법

### 1. 필수 라이브러리 설치

```bash
pip install streamlit pandas numpy pydantic langchain langchain-google-genai
```

### 2. 데이터 경로 설정

**방법 1: 코드에서 직접 수정**
```python
# streamlit_app_final.py 또는 marketing_system_integrated.py
DATA_DIR = "/your/data/path"
```

**방법 2: Streamlit UI에서 설정**
- 사이드바 "데이터 디렉토리" 입력창에서 경로 입력

### 3. Streamlit 앱 실행

```bash
streamlit run streamlit_app_final.py
```

---

## 🎯 주요 기능

### 1. 작업 유형 선택 (3가지)

#### 📊 종합 전략 수립
- **Product 전략** (재방문율 향상)
- **Price 전략** (가격 경쟁력)
- **Promotion 전략** (신규 고객 유입)

#### ⚡ 상황 전술 제안
- **날씨 기반 전술** (비, 폭염, 한파 등)
- **이벤트 기반 전술** (근처 행사 연계)
- **긴급 할인 전술** (Flash Sale)

#### 📱 콘텐츠 생성 가이드
- 채널별 템플릿 (Instagram, Naver Blog 등)
- 향후 확장 가능 (현재 하드코딩)

### 2. 전략 카드 구성

각 전략 카드는 다음 정보를 포함:

| 항목 | 설명 |
|------|------|
| **제목** | 전략 핵심 이름 |
| **가설** | 문제 진단 요약 |
| **채널** | 실행 채널 (카카오톡, 인스타그램 등) |
| **혜택** | 구체적 프로모션 내용 |
| **기간** | 실행 기간 |
| **예산** | 예산 상한 및 등급 |
| **KPI** | 목표 지표 및 변화율 |
| **근거** | 데이터 기반 증거 |
| **전제조건** | 가정 사항 |
| **리스크** | 주의 사항 |
| **준비물** | 필요 자산 |

### 3. 데이터 검증

#### Segmentation 검증
- 고객 연령/성별 분포
- 고객 유형 (거주민/직장인/유동인구)
- 재방문율 및 충성도

#### Targeting 검증
- **수익성 점수** (0~100)
- **성장성 점수** (0~100)
- **안정성 점수** (0~100)
- **종합 점수** (가중 평균)

#### Positioning 검증
- **Product** - 배달 비중, 재방문율
- **Price** - 가격 수준, PC1 좌표
- **Place** - 채널 믹스 추천
- **Promotion** - 타겟 연령대, 프로모션 초점

---

## 💡 사용 예시

### 종합 전략 수립

```python
# 1. 가맹점 선택: 히토**** (일식)
# 2. 작업 유형: 종합 전략 수립
# 3. 예산: 50,000원

# 결과:
# - 카드 1: 재방문 유도 스탬프 프로그램
# - 카드 2: 중가 가격대 경쟁력 강화 전략
# - 카드 3: 직장인 타겟 신규 고객 유입 캠페인
```

### 상황 전술 제안

```python
# 1. 가맹점 선택: 성우** (축산물)
# 2. 작업 유형: 상황 전술 제안
# 3. 상황 정보:
#    - 날씨: 비
#    - 강수 확률: 70%
#    - 이벤트: 마장동 축제

# 결과:
# - 카드 1: ☔ 우천 대비 배달 특가 프로모션
# - 카드 2: 🎉 마장동 축제 연계 프로모션
# - 카드 3: ⚡ 긴급 Flash Sale (오늘만)
```

---

## 🔧 커스터마이징 가이드

### 1. 전략 카드 로직 수정

**파일**: `strategy_card_generator.py`

```python
class StrategyCardGenerator:
    def _generate_product_card(self, store_data, budget_cap):
        # 여기에서 Product 전략 로직 수정
        ...
    
    def _generate_weather_tactical_card(self, store_data, situation, budget_cap):
        # 여기에서 날씨 전술 로직 수정
        ...
```

### 2. 콘텐츠 템플릿 추가

**파일**: `strategy_card_generator.py`

```python
def generate_content_cards(self, store_data, channels, budget_cap):
    # TODO: 채널별 템플릿 확장
    
    # 예시: Instagram 템플릿
    if 'instagram' in channels:
        card = self._generate_instagram_content_card(store_data)
    
    # 예시: Naver Blog 템플릿
    if 'naver_blog' in channels:
        card = self._generate_naver_blog_card(store_data)
```

### 3. UI 스타일 변경

**파일**: `streamlit_app_final.py`

CSS 스타일 수정:
```python
st.markdown("""
<style>
    .strategy-card {
        background-color: #ffffff;  /* 카드 배경색 */
        border: 2px solid #e0e0e0;   /* 테두리 */
        ...
    }
</style>
""", unsafe_allow_html=True)
```

---

## 📊 데이터 요구사항

시스템이 정상 작동하려면 다음 CSV 파일이 필요합니다:

| 파일명 | 용도 | 필수 컬럼 |
|--------|------|-----------|
| `big_data_set2_f_re.csv` | 매출/운영 데이터 | 가맹점구분번호, 기준년월, 매출금액 구간, 배달매출금액 비율 등 |
| `big_data_set3_f_re.csv` | 고객 인구통계 | 가맹점구분번호, 기준년월, 연령/성별 비중, 재방문 고객 비중 등 |
| `df_final.csv` | 가맹점 기본 정보 | 가맹점구분번호, 가맹점명, 업종, 상권, risk_score_xgb 등 |
| `store_segmentation_final_re.csv` | PCA/Cluster 결과 | 가맹점구분번호, pc1_x, pc2_y, cluster_id 등 |

