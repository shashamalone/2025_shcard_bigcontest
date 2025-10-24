# Marketing MultiAgent System - Changelog

## [2.1.0] - 2025-10-24

### 🔥 주요 개선사항

#### 4P Strategy Agent 파싱 로직 개선
- **추가된 함수**:
  - `_extract_field()`: 정규식 기반 필드 추출 헬퍼
  - `_parse_strategy_cards_from_llm()`: LLM 응답 구조화 파싱
  - `_generate_fallback_cards()`: 파싱 실패 시 폴백 전략 생성

- **State 스키마 확장**:
  ```python
  class StrategyPlanningState(TypedDict):
      # ... 기존 필드
      data_4p_mapped: Optional[Dict]           # 4P 매핑 데이터
      llm_raw_strategy_output: Optional[str]   # LLM 원본 응답
  ```

- **향상된 로깅**:
  - 전략 카드 생성 성공/실패 상세 로그
  - 각 카드의 제목과 우선순위 출력

### 개선된 코드 위치

#### `marketing_multiagent_system.py`

**Helper Functions** (lines 672-849)
```python
def _extract_field(text, pattern, default)  # line 676
def _extract_evidence(text)                 # line 682
def _parse_strategy_cards_from_llm(...)     # line 700
def _generate_fallback_cards(...)           # line 765
```

**Strategy Agent** (lines 851-979)
```python
def strategy_4p_agent(state)                # line 851
    # 4P 데이터 요약
    # LLM 프롬프트 생성
    # 응답 파싱
    # 폴백 처리
    # 로깅
```

### 파싱 지원 형식

```
**전략 카드 N: [제목]**
- Product: [내용]
- Price: [내용]
- Place: [내용]
- Promotion: [내용]
- 포지셔닝 컨셉: [내용]
- 예상 효과: [내용]
- 우선순위: High|Medium|Low
```

### 데이터 흐름

```
User Input
    ↓
Top Supervisor
    ↓
Market Analysis Team
    ├─> STP 분석
    └─> PC축 해석
    ↓
Strategy Planning Team
    ├─> stp_validation_agent (4P 데이터 매핑)
    ├─> strategy_4p_agent (전략 카드 생성) ← 🔥 개선됨
    └─> execution_plan_agent
    ↓
Report Generation
    ├─> 종합 보고서
    ├─> 전술 카드 (상황 정보 반영)
    └─> 콘텐츠 가이드
```

### 테스트 파일

- `test_strategy_parsing.py`: 파싱 로직 단위 테스트
- `STRATEGY_AGENT_IMPROVEMENTS.md`: 상세 개선 문서

### Breaking Changes
없음 (하위 호환성 유지)

### Bug Fixes
- 중복 typing import 제거

### Performance
- 파싱 성공 시 폴백 로직 스킵으로 효율성 향상

---

## [2.0.0] - 2025-10-23

### 초기 통합 버전
- 실제 CSV 데이터 기반 STP 분석
- 3가지 작업 유형 지원
- 상황 정보 수집 (날씨 + 이벤트)
- GPS 좌표 매핑
- Streamlit UI

---

## 사용법

### 기본 실행
```python
from marketing_multiagent_system import run_marketing_system

result = run_marketing_system(
    store_id="S001234",
    task_type="종합_전략_수립"
)
```

### 디버깅
```python
# LLM 원본 응답 확인
print(result.get('llm_raw_strategy_output'))

# 생성된 전략 카드
for card in result['strategy_cards']:
    print(card.title)
    print(card.strategy_4p)
```

### 테스트 실행
```bash
cd agent_all
python test_strategy_parsing.py
```

---

**Maintained by**: BigContest 2025 Team
**Last Updated**: 2025-10-24
