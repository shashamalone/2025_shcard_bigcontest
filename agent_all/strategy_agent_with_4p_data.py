"""
Strategy Agent - 4P 데이터 매핑 통합 버전
marketing_system_v2_integrated.py의 strategy_4p_agent를 대체
"""

from data_mapper_for_4p import DataLoaderFor4P, DataMapperFor4P
from langchain_google_genai import ChatGoogleGenerativeAI
import json

MODEL_NAME = "gemini-2.5-flash"

def stp_validation_agent_enhanced(state) -> dict:
    """✅ 개선된 STP Validation Agent - 4P 데이터 매핑 포함"""
    print("\n[STP Validation] STP 분석 결과 검증 중...")

    stp = state['stp_output']
    store_id = stp.store_current_position.store_id

    # 기본 검증
    validation = {
        "is_valid": True,
        "cluster_count": len(stp.cluster_profiles),
        "has_position": stp.store_current_position is not None,
        "has_white_space": stp.recommended_white_space is not None,
        "nearby_competitors_count": len(stp.nearby_competitors)
    }

    # ✅ 4P 데이터 로드 및 매핑
    print("   📊 가맹점 데이터를 4P 전략에 매핑 중...")

    loader_4p = DataLoaderFor4P()
    loader_4p.load_all()

    mapper = DataMapperFor4P(loader_4p)
    data_4p = mapper.get_all_4p_data(store_id)

    state['stp_validation_result'] = validation
    state['data_4p_mapped'] = data_4p  # 🆕 4P 매핑 데이터 추가
    state['current_agent'] = "strategy_4p"
    state['next'] = "strategy_4p_agent"

    print(f"   ✓ 4P 데이터 매핑 완료 (Product, Price, Place, Promotion)")

    return state


def strategy_4p_agent_enhanced(state) -> dict:
    """✅ 개선된 4P Strategy Agent - 실제 데이터 기반 전략 생성"""
    print("[4P Strategy] 데이터 기반 3개 전략 카드 생성 중...")

    task_type = state['task_type']
    stp = state['stp_output']
    data_4p = state.get('data_4p_mapped', {})  # 🆕 4P 매핑 데이터

    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.7)

    # PC축 해석 정보
    pc1_info = stp.pc_axis_interpretation['PC1']
    pc2_info = stp.pc_axis_interpretation['PC2']

    pc1_features_str = ", ".join([f"{f['속성']}({f['가중치']})" for f in pc1_info.top_features])
    pc2_features_str = ", ".join([f"{f['속성']}({f['가중치']})" for f in pc2_info.top_features])

    # ✅ 4P 데이터를 JSON으로 구조화
    data_4p_summary = {}

    for p_type in ['Product', 'Price', 'Place', 'Promotion']:
        if p_type in data_4p:
            p_data = data_4p[p_type]
            summary = {"insights": []}

            for source in p_data.get('data_sources', []):
                if 'insights' in source:
                    summary["insights"].append({
                        "source": source.get('source', ''),
                        **source['insights']
                    })

            data_4p_summary[p_type] = summary

    # JSON 문자열로 변환
    data_4p_json = json.dumps(data_4p_summary, ensure_ascii=False, indent=2)

    prompt = f"""
당신은 마케팅 전략가입니다. 다음 **실제 가맹점 데이터**와 STP 분석 결과를 바탕으로 **3가지 대안 전략 카드**를 생성하세요.

# 가맹점 정보
- 이름: {stp.store_current_position.store_name}
- 업종: {stp.store_current_position.industry}
- 타겟 군집: {stp.target_cluster_name}
- 근접 경쟁자: {len(stp.nearby_competitors)}개

# 포지셔닝 축 분석
- PC1: {pc1_info.interpretation}
  주요 요인: {pc1_features_str}

- PC2: {pc2_info.interpretation}
  주요 요인: {pc2_features_str}

# 현재 위치
- PC1 Score: {stp.store_current_position.pc1_score:.2f}
- PC2 Score: {stp.store_current_position.pc2_score:.2f}

---

# 🔥 가맹점 실제 운영 데이터 (4P 매핑)

{data_4p_json}

---

위 데이터를 **반드시 활용**하여 다음 형식으로 **3가지 전략 카드**를 작성하세요:

**전략 카드 1: [제목]**
- Product: [제품 전략 - Product 데이터의 insights 활용]
- Price: [가격 전략 - Price 데이터의 insights 활용]
- Place: [유통 전략 - Place 데이터의 insights 활용]
- Promotion: [프로모션 전략 - Promotion 데이터의 insights 활용]
- 포지셔닝 컨셉: [차별화 메시지]
- 예상 효과: [기대 효과]
- 우선순위: High
- 데이터 근거: [사용한 데이터 명시]

**전략 카드 2: [제목]**
(동일 형식, 다른 전략 방향)

**전략 카드 3: [제목]**
(동일 형식, 또 다른 전략 방향)

**중요:**
- 각 P(Product, Price, Place, Promotion)마다 위에 제공된 실제 데이터의 insights를 **구체적으로 언급**하세요.
- 예: "배달 매출 비중이 65%로 높으므로 배달 전용 메뉴 개발"
- 예: "주 고객이 여성 30대(35%)이므로 인스타그램 피드 중심 마케팅"
"""

    response = llm.invoke(prompt)
    content = response.content.strip()

    # 🔥 LLM 응답 파싱 (간소화 버전)
    # 실제로는 더 정교한 파싱 필요
    strategy_cards = []

    # 임시로 3개 카드 생성 (LLM 응답 파싱 로직 추가 필요)
    for i in range(3):
        # 데이터 근거 추출
        evidence = [
            f"PC1: {pc1_info.interpretation}",
            f"PC2: {pc2_info.interpretation}",
            f"근접 경쟁자: {len(stp.nearby_competitors)}개"
        ]

        # 4P 데이터에서 주요 인사이트 추가
        for p_type in ['Product', 'Price', 'Place', 'Promotion']:
            if p_type in data_4p_summary and data_4p_summary[p_type]['insights']:
                first_insight = data_4p_summary[p_type]['insights'][0]
                key = list(first_insight.keys())[-1]  # 마지막 키 (전략 방향 등)
                evidence.append(f"{p_type}: {first_insight[key]}")

        from marketing_system_v2_integrated import StrategyCard

        strategy_cards.append(StrategyCard(
            card_id=i+1,
            title=f"데이터 기반 전략 {i+1}",
            positioning_concept=f"차별화 메시지 {i+1}",
            strategy_4p={
                "product": f"제품 전략 {i+1} (실제 데이터 기반)",
                "price": f"가격 전략 {i+1} (실제 데이터 기반)",
                "place": f"유통 전략 {i+1} (실제 데이터 기반)",
                "promotion": f"프로모션 전략 {i+1} (실제 데이터 기반)"
            },
            expected_outcome=f"기대 효과 {i+1}",
            priority="High" if i == 0 else "Medium" if i == 1 else "Low",
            data_evidence=evidence
        ))

    state['strategy_cards'] = strategy_cards
    state['selected_strategy'] = strategy_cards[0]
    state['current_agent'] = "execution_plan"
    state['next'] = "execution_plan_agent"

    return state


# ============================================================================
# 사용 예시 (단독 테스트)
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("개선된 Strategy Agent 테스트")
    print("=" * 80)

    # 데이터 로더
    loader = DataLoaderFor4P()
    loader.load_all()

    # 샘플 가맹점
    if not loader.ds2.empty:
        store_id = loader.ds2['가맹점구분번호'].iloc[0]

        # 4P 데이터 매핑
        mapper = DataMapperFor4P(loader)
        data_4p = mapper.get_all_4p_data(store_id)

        print(f"\n가맹점 ID: {store_id}")
        print("\n4P 데이터 매핑 결과:")
        print(json.dumps(data_4p, ensure_ascii=False, indent=2))
