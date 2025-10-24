# Strategy Agent Improvements

## 개요
4P Strategy Agent의 LLM 응답 파싱 및 전략 카드 생성 로직을 개선하여 실제 데이터 기반의 구체적인 전략 제안이 가능하도록 수정했습니다.

## 주요 개선 사항

### 1. LLM 응답 구조화 파싱 추가

#### 기존 방식
- LLM 응답을 단순 파싱 없이 폴백 전략 사용
- 하드코딩된 템플릿 기반 전략 카드 생성
- 실제 4P 데이터 활용 미흡

#### 개선 사항
```python
# 새로운 파싱 함수 추가
_parse_strategy_cards_from_llm()  # LLM 응답에서 전략 카드 추출
_extract_field()                   # 정규식 기반 필드 추출
_generate_fallback_cards()         # 파싱 실패 시 폴백 전략
```

### 2. 정규식 기반 필드 추출

LLM이 생성한 다음 형식을 파싱:

```
**전략 카드 1: [제목]**
- Product: [제품 전략]
- Price: [가격 전략]
- Place: [유통 전략]
- Promotion: [프로모션 전략]
- 포지셔닝 컨셉: [차별화 메시지]
- 예상 효과: [기대 효과]
- 우선순위: High/Medium/Low
```

### 3. State 스키마 확장

```python
class StrategyPlanningState(TypedDict):
    # ... 기존 필드들
    data_4p_mapped: Optional[Dict]           # 4P 매핑 데이터
    llm_raw_strategy_output: Optional[str]   # LLM 원본 응답 (디버깅)
```

### 4. 향상된 로깅

```python
# 성공 시
print(f"   ✓ {len(strategy_cards)}개 전략 카드 생성 완료")
for i, card in enumerate(strategy_cards, 1):
    print(f"      {i}. {card.title} (우선순위: {card.priority})")

# 실패 시
print("   ⚠️  LLM 응답 파싱 실패 - 폴백 전략 생성")
```

### 5. 폴백 전략 개선

파싱 실패 시에도 실제 4P 데이터의 insights를 활용한 전략 생성:

```python
def _generate_fallback_cards(stp, data_4p_summary, evidence):
    # Product 인사이트 추출
    if 'Product' in data_4p_summary:
        insight = data_4p_summary['Product']['insights'][0]
        # ... 실제 데이터 활용

    # 3가지 대안 전략 생성
    strategies = [
        "데이터 기반 성장 전략",
        "고객 경험 최적화 전략",
        "경쟁 우위 확보 전략"
    ]
```

## 파싱 로직 상세

### 전략 카드 블록 분리
```python
card_blocks = re.split(r'\*\*전략 카드 \d+:', content)
```

### 필드별 정규식 패턴
- **제목**: `r'^([^\n\*]+)'`
- **Product**: `r'[- ]*Product[:\s]*(.+?)(?=\n[- ]*(?:Price|가격)|$)'`
- **Price**: `r'[- ]*Price[:\s]*(.+?)(?=\n[- ]*(?:Place|유통)|$)'`
- **Place**: `r'[- ]*Place[:\s]*(.+?)(?=\n[- ]*(?:Promotion|프로모션)|$)'`
- **Promotion**: `r'[- ]*Promotion[:\s]*(.+?)(?=\n[- ]*(?:포지셔닝|예상|우선순위)|$)'`
- **포지셔닝 컨셉**: `r'[- ]*포지셔닝 컨셉[:\s]*(.+?)(?=\n[- ]*(?:예상|우선순위)|$)'`
- **예상 효과**: `r'[- ]*예상 효과[:\s]*(.+?)(?=\n[- ]*우선순위|$)'`
- **우선순위**: `r'[- ]*우선순위[:\s]*(High|Medium|Low)'`

## 테스트

테스트 스크립트: `test_strategy_parsing.py`

```bash
python test_strategy_parsing.py
```

### 예상 출력
```
파싱 결과: 3개 카드
카드 ID: 1
제목: 배달 특화 성장 전략
포지셔닝: 배달 최적화 맛집
우선순위: High
Product: 배달 전용 메뉴 개발 (배달 매출 비중 65% 활용)...
예상 효과: 배달 매출 20% 증가 예상
```

## 데이터 흐름

```
1. stp_validation_agent
   └─> 4P 데이터 매핑 (data_4p_mapped)

2. strategy_4p_agent
   ├─> 4P 데이터 요약 (data_4p_summary)
   ├─> LLM 프롬프트 생성 (4P 인사이트 포함)
   ├─> LLM 호출 및 응답 저장 (llm_raw_strategy_output)
   ├─> 파싱 시도 (_parse_strategy_cards_from_llm)
   └─> 파싱 실패 시 폴백 (_generate_fallback_cards)

3. execution_plan_agent
   └─> 선택된 전략 기반 4주 실행 계획
```

## 장점

1. **구조화된 출력**: LLM이 일관된 형식으로 전략 제안
2. **데이터 기반**: 실제 4P 인사이트를 전략에 반영
3. **견고성**: 파싱 실패 시에도 폴백 전략으로 안전하게 처리
4. **디버깅 용이**: 원본 LLM 응답 저장으로 문제 추적 가능
5. **확장성**: 정규식 패턴 수정으로 다양한 형식 지원 가능

## 향후 개선 방향

1. **다국어 지원**: 영문 필드명도 파싱 가능하도록 패턴 확장
2. **더 복잡한 구조**: 세부 전술, 타임라인 등 추가 필드 파싱
3. **JSON 출력**: LLM에게 JSON 형식 응답 요청 고려
4. **검증 로직**: 파싱된 전략의 품질 검증 단계 추가
5. **A/B 테스트**: 여러 전략 버전 생성 및 비교 기능

## 참고 파일

- `marketing_multiagent_system.py` (lines 672-979)
  - `_extract_field()` (line 676)
  - `_parse_strategy_cards_from_llm()` (line 700)
  - `_generate_fallback_cards()` (line 765)
  - `strategy_4p_agent()` (line 851)

## 사용 예시

```python
# 실행
result = run_marketing_system(
    store_id="S001234",
    task_type="종합_전략_수립"
)

# 결과 확인
print(result['strategy_cards'])  # List[StrategyCard]
print(result['llm_raw_strategy_output'])  # 디버깅용 원본
```

---
**작성일**: 2025-10-24
**버전**: 2.0
**상태**: 구현 완료
