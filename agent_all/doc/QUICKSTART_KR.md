# 🚀 빠른 시작 가이드

## 30초 만에 시작하기

### 1단계: 파일 다운로드 ✅

다음 파일들을 같은 폴더에 저장:
```
📁 your_project/
  ├── models.py
  ├── data_enricher.py
  ├── strategy_card_generator.py
  ├── marketing_system_integrated.py
  └── streamlit_app_final.py
```

### 2단계: 실행! 🎯

```bash
streamlit run streamlit_app_final.py
```

끝! 브라우저가 자동으로 열립니다 🎉

---

## 사용법

### ① 사이드바 설정

1. **데이터 경로** 입력
   ```
   /your/data/directory
   ```

2. **가맹점 선택**
   - 드롭다운에서 선택 또는
   - ID 직접 입력 (예: `0C67B8EDCF`)

3. **작업 유형 선택**
   - 📊 종합 전략 수립 (기본)
   - ⚡ 상황 전술 제안 (날씨/이벤트)
   - 📱 콘텐츠 생성 가이드 (준비중)

4. **분석 시작** 버튼 클릭

### ② 결과 확인

3개 탭으로 결과 제공:
- **Tab 1**: 가맹점 정보
- **Tab 2**: 📋 전략 카드 3개 (가로 배치)
- **Tab 3**: 상세 보고서

---

## 전략 카드 예시

### 카드 1: 재방문 유도 스탬프 프로그램
```
💡 가설: 낮은 재방문율로 고객 이탈 심각
🎁 혜택: 스탬프 5회 적립 시 무료 쿠폰 증정
📢 채널: 카카오톡
📈 목표: 재방문율 +15% (4주)
```

### 카드 2: 중가 가격대 경쟁력 강화
```
💡 가설: 중가 포지션, 가격 경쟁력 강화 필요
🎁 혜택: Happy Hour 할인 (14:00-17:00, 15% 할인)
📢 채널: 인스타그램, 네이버 플레이스
📈 목표: 매출 +12% (3주)
```

### 카드 3: 신규 고객 유입 캠페인
```
💡 가설: 신규 고객 유입 부족, 인지도 제고 필요
🎁 혜택: 첫 방문 고객 20% 할인 + SNS 리뷰 이벤트
📢 채널: 인스타그램, 카카오톡
📈 목표: 신규 고객수 +20% (2주)
```

---

## 상황 전술 예시 (비 오는 날)

### 카드 1: ☔ 우천 대비 배달 특가
```
💡 가설: 비 예보로 외출 감소, 배달 수요 증가
🎁 혜택: 배달 주문 시 즉시 2,000원 할인 + 무료 배달
📢 채널: 배달앱, 카카오톡
📈 목표: 매출 +15% (당일)
⏰ 긴급: 지금 ~ 오늘 오후 6시까지
```

---

## 문제 해결

### ❌ "모듈을 찾을 수 없습니다"
```python
# streamlit_app_final.py 상단에 추가
import sys
sys.path.append('/파일이/있는/경로')
```

### ❌ "데이터 로드 실패"
1. 사이드바에서 데이터 경로 확인
2. CSV 파일이 있는지 확인:
   - `big_data_set2_f_re.csv`
   - `big_data_set3_f_re.csv`
   - `df_final.csv`
   - `store_segmentation_final_re.csv`

### ❌ 전략 카드가 제대로 안 나옴
- 터미널 로그 확인
- 가맹점 ID가 올바른지 확인

---

## 핵심 기능

### ✨ 종합 전략 수립
- Product, Price, Promotion 3가지 전략
- 데이터 기반 근거 제시
- 실행 가능한 구체적 액션

### ⚡ 상황 전술 제안
- 날씨 대응 (비, 폭염, 한파)
- 이벤트 연계
- 긴급 할인

### 📊 데이터 검증
- Segmentation 적합도
- Targeting 종합 점수
- Positioning 실현 가능성

---

## 커스터마이징

### 예산 변경
```python
# 사이드바에서 설정
budget_cap = 50000  # 원하는 금액
```

### 전략 로직 수정
```python
# strategy_card_generator.py
class StrategyCardGenerator:
    def _generate_product_card(self, store_data, budget_cap):
        # 여기서 수정
        offer = "원하는 혜택 내용"
        ...
```

---

## 다음 단계

1. ✅ 기본 실행 확인
2. 🎨 UI 커스터마이징
3. 🧠 전략 로직 개선
4. 📱 콘텐츠 템플릿 추가
5. 🔗 실시간 데이터 연동

---

## 💬 도움이 필요하신가요?

- 📖 [README_FINAL.md](README_FINAL.md) - 상세 가이드
- 📊 [stp_data_mapping.md](stp_data_mapping.md) - 데이터 구조
- 📋 [final_implementation_plan.md](final_implementation_plan.md) - 구현 계획

---

**팁**: 처음 실행 시 데이터 로딩에 5-10초 정도 걸릴 수 있습니다. 
잠시만 기다려주세요! ⏳

**버전**: 1.0.0  
**최종 업데이트**: 2025-10-24
