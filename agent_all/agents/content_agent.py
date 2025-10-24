# agents/content_agent.py
"""
Content Agent (콘텐츠 크리에이터)
- 역할: 전략팀의 채널 제안을 받아 실행 가능한 콘텐츠 가이드라인 생성
- 출력: 채널별 포스팅 형식, 카피 예시, 해시태그, 무드보드 등
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# === Gemini 2.5 Flash 모델 사용 ===
MODEL_NAME = "gemini-2.5-flash"


# === 데이터 모델 ===
class ChannelGuideline(BaseModel):
    """채널별 콘텐츠 가이드라인"""
    channel_name: str = Field(description="채널명 (인스타그램, 네이버블로그 등)")
    post_format: str = Field(description="포스팅 형식 (예: 릴스, 피드, 스토리)")
    visual_direction: List[str] = Field(description="시각적 방향성 키워드")
    copy_examples: List[str] = Field(description="카피라이팅 예시 3개")
    hashtags: List[str] = Field(description="필수 해시태그 리스트")
    posting_frequency: str = Field(description="추천 게시 빈도")
    best_time: str = Field(description="최적 게시 시간대")
    content_tips: List[str] = Field(description="채널 특성 맞춤 팁")


class ContentGuide(BaseModel):
    """전체 콘텐츠 가이드"""
    target_store: str = Field(description="가맹점명")
    target_audience: str = Field(description="타겟 고객층")
    brand_tone: str = Field(description="브랜드 톤앤매너")
    mood_board: List[str] = Field(description="무드보드 키워드 (분위기)")
    channels: List[ChannelGuideline] = Field(description="채널별 가이드라인")
    overall_strategy: str = Field(description="전체 콘텐츠 전략 요약")
    do_not_list: List[str] = Field(description="금기 사항 (피해야 할 것)")


# === Main Node ===
def content_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Content Agent 노드
    - 입력: state에서 strategy_4p, targeting_positioning, situation 등 참조
    - 출력: {"content_guide": ContentGuide, "log": [...]}
    """
    logs = state.get("log") or []
    logs.append("[content] 콘텐츠 가이드 생성 시작")

    # ========================================
    # Step 1: 입력 데이터 수집
    # ========================================
    store_name = state.get("target_store_name", "가맹점")
    industry = state.get("industry", "일반 음식점")
    
    # 전략팀 산출물
    strategy_4p = state.get("strategy_4p", {})
    promotion = strategy_4p.get("promotion", "SNS 홍보 권장")
    
    # 분석팀 산출물
    targeting = state.get("targeting_positioning", "")
    market_analysis = state.get("market_customer_analysis", "")
    
    # 상황 정보 (방어 코드)
    situation = state.get("situation", {})
    if situation and isinstance(situation, dict):
        situation_summary = situation.get("summary", "특이 상황 없음")
    else:
        situation_summary = "특이 상황 없음"

    # ========================================
    # Step 2: LLM 프롬프트 구성
    # ========================================
    system_prompt = f"""당신은 소상공인을 위한 콘텐츠 크리에이터입니다.
전략팀이 제안한 마케팅 채널과 아이디어를 받아, 실제 게시할 수 있는 구체적인 콘텐츠 가이드라인을 생성합니다.

**핵심 원칙:**
1. 가게 분위기와 타겟 고객에 맞춰야 함
2. 채널 특성 반영 (인스타그램 vs 블로그 차이)
3. 실행 가능한 구체적인 예시 제공
4. 시각적 방향성 명확히 제시
"""

    user_prompt = f"""
# 가맹점 정보
- 가맹점명: {store_name}
- 업종: {industry}

# 전략팀 제안
## Promotion 전략
{promotion}

## 타겟 고객 & 포지셔닝
{targeting[:500]}

## 시장 분석
{market_analysis[:500]}

# 현재 상황
{situation_summary}

---

위 정보를 바탕으로 **실행 가능한 콘텐츠 가이드**를 생성하세요.

다음 JSON 형식으로 응답:
{{
  "target_store": "{store_name}",
  "target_audience": "주요 타겟 고객층 (예: 2030 직장인 여성)",
  "brand_tone": "브랜드 톤앤매너 (예: 친근하고 활기찬)",
  "mood_board": ["키워드1", "키워드2", "키워드3"],
  "channels": [
    {{
      "channel_name": "인스타그램",
      "post_format": "릴스 + 피드 포스팅",
      "visual_direction": ["밝고 경쾌한", "음식 클로즈업", "고객 리액션"],
      "copy_examples": [
        "런치 타임 공략 카피 예시",
        "이벤트 홍보 카피 예시",
        "일상 소통 카피 예시"
      ],
      "hashtags": ["#성수카페", "#런치맛집", "#직장인점심"],
      "posting_frequency": "주 3-4회",
      "best_time": "평일 12시, 18시 / 주말 14시",
      "content_tips": [
        "릴스는 15초 이내 핵심 전달",
        "스토리로 당일 메뉴 소개",
        "고객 후기 리그램 활용"
      ]
    }}
  ],
  "overall_strategy": "전체 콘텐츠 전략 1-2문장 요약",
  "do_not_list": ["과도한 할인 강조", "경쟁사 언급", "부정적 표현"]
}}

**중요:**
1. 채널은 최소 2개 (인스타그램, 네이버블로그 등)
2. 카피 예시는 구체적으로 (실제 문장 형태)
3. 해시태그는 10개 이상
4. 시각적 방향성은 촬영 가이드로 활용 가능하게
"""

    # ========================================
    # Step 3: LLM 호출
    # ========================================
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.7)
    
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        # JSON 파싱
        import json
        content_text = response.content.strip()
        
        # Markdown 코드 블록 제거
        if content_text.startswith("```json"):
            content_text = content_text.replace("```json", "").replace("```", "").strip()
        elif content_text.startswith("```"):
            content_text = content_text.replace("```", "").strip()
        
        content_data = json.loads(content_text)
        content_guide = ContentGuide(**content_data)
        
        logs.append(f"[content] 가이드 생성 완료: {len(content_guide.channels)}개 채널")
        
        return {
            "content_guide": content_guide.dict(),
            "log": logs
        }
        
    except Exception as e:
        logs.append(f"[content] 생성 실패: {e}")
        
        # Fallback: 기본 가이드
        fallback_guide = ContentGuide(
            target_store=store_name,
            target_audience="일반 고객",
            brand_tone="친근하고 따뜻한",
            mood_board=["깔끔한", "밝은", "맛있는"],
            channels=[
                ChannelGuideline(
                    channel_name="인스타그램",
                    post_format="피드 + 스토리",
                    visual_direction=["음식 사진", "가게 분위기"],
                    copy_examples=[
                        f"{store_name}에서 특별한 하루 시작하세요!",
                        "오늘의 추천 메뉴를 소개합니다",
                        "고객님들의 사랑에 감사드립니다"
                    ],
                    hashtags=["#맛집", "#일상", "#데일리"],
                    posting_frequency="주 2-3회",
                    best_time="점심/저녁 시간대",
                    content_tips=["정기적 업로드", "고객 소통 중요"]
                )
            ],
            overall_strategy=f"{store_name}의 일상적 매력을 SNS로 전달",
            do_not_list=["과장 광고", "부정적 표현"]
        )
        
        return {
            "content_guide": fallback_guide.dict(),
            "log": logs
        }


# === 채널별 템플릿 생성 헬퍼 ===
def generate_instagram_template(guide: ChannelGuideline) -> str:
    """인스타그램 포스팅 템플릿 생성"""
    template = f"""
📸 Instagram 포스팅 가이드

## 포스팅 형식
{guide.post_format}

## 시각적 방향
{', '.join(guide.visual_direction)}

## 카피 예시
{chr(10).join(f"{i+1}. {ex}" for i, ex in enumerate(guide.copy_examples))}

## 필수 해시태그
{' '.join(guide.hashtags[:15])}

## 게시 빈도
{guide.posting_frequency}

## 최적 시간
{guide.best_time}

## 팁
{chr(10).join(f"• {tip}" for tip in guide.content_tips)}
"""
    return template


def generate_blog_template(guide: ChannelGuideline) -> str:
    """블로그 포스팅 템플릿 생성"""
    template = f"""
📝 블로그 포스팅 가이드

## 포스팅 형식
{guide.post_format}

## 콘텐츠 구성
1. 도입부: 방문 계기 또는 메뉴 소개
2. 본문: 상세 리뷰 및 사진
3. 마무리: 추천 메시지

## 키워드
{', '.join(guide.visual_direction)}

## 제목 예시
{chr(10).join(guide.copy_examples)}

## SEO 키워드
{' '.join(guide.hashtags[:10])}

## 게시 빈도
{guide.posting_frequency}

## 팁
{chr(10).join(f"• {tip}" for tip in guide.content_tips)}
"""
    return template


# === 테스트용 ===
if __name__ == "__main__":
    test_state = {
        "target_store_name": "성수 브런치 카페",
        "industry": "카페",
        "strategy_4p": {
            "promotion": "인스타그램 릴스 + 네이버 블로그로 2030 직장인 타겟 홍보"
        },
        "targeting_positioning": "직장인 밀집 지역, 런치/브런치 수요 높음",
        "market_customer_analysis": "평일 점심 시간대 매출 집중",
        "situation": {
            "summary": "주변 팝업스토어 이벤트 예정"
        },
        "log": []
    }
    
    result = content_agent_node(test_state)
    print("=== Content Guide ===")
    guide = result["content_guide"]
    print(f"타겟: {guide['target_audience']}")
    print(f"톤앤매너: {guide['brand_tone']}")
    print(f"채널 수: {len(guide['channels'])}")
    
    for ch in guide["channels"]:
        print(f"\n[{ch['channel_name']}]")
        print(f"  형식: {ch['post_format']}")
        print(f"  해시태그: {', '.join(ch['hashtags'][:5])}...")
