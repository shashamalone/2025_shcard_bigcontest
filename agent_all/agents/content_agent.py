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
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

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
    mood_board: List[str] = Field(description="무드보드 키워드 - 한글 (사용자 표시용)")
    mood_board_en: List[str] = Field(description="무드보드 키워드 - 영어 (이미지 API 검색용)")
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

    # 🔥 사용자 선택 채널 가져오기
    selected_channels = state.get("content_channels", ["Instagram", "Naver Blog"])
    logs.append(f"[content] 선택된 채널: {selected_channels}")

    # 🔥 사용자 요청 가져오기
    user_query = state.get("user_query", "")
    if user_query and user_query.strip():
        logs.append(f"[content] 사용자 요청: {user_query}")

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
    # Step 2: 채널별 가이드 템플릿 생성
    # ========================================
    def generate_channel_template(channel_name: str) -> str:
        """채널별 템플릿 생성"""
        templates = {
            "Instagram": """
      "channel_name": "인스타그램",
      "post_format": "릴스 + 피드 포스팅 + 스토리",
      "visual_direction": ["밝고 경쾌한 분위기", "음식 클로즈업", "고객 리액션", "가게 분위기"],
      "copy_examples": [
        "감성적인 카피 (예: 오늘 하루도 맛있게 시작하세요)",
        "프로모션 카피 (예: 이번주 특별 이벤트!)",
        "일상 소통 카피 (예: 여러분의 최애 메뉴는?)"
      ],
      "hashtags": ["#인스타맛집", "#데일리", "#오늘의메뉴", "#맛스타그램"],
      "posting_frequency": "주 4-5회 (피드 2-3회, 스토리 매일)",
      "best_time": "평일 12시, 18시 / 주말 14시",
      "content_tips": [
        "릴스는 15초 이내로 핵심만 전달",
        "스토리로 당일 메뉴와 특가 정보 공유",
        "고객 태그/리그램 적극 활용",
        "음악과 트렌디한 효과 사용"
      ]""",
            "Naver Blog": """
      "channel_name": "네이버 블로그",
      "post_format": "리뷰형 포스팅 (1000-1500자)",
      "visual_direction": ["고화질 음식 사진", "가게 전경/내부", "메뉴판", "먹방 컷"],
      "copy_examples": [
        "방문 후기 제목 (예: [성수동 맛집] 회사 근처 숨은 맛집 발견!)",
        "메뉴 리뷰 제목 (예: 이집 시그니처 메뉴 먹어봤어요)",
        "추천 제목 (예: 점심 고민? 여기 가보세요)"
      ],
      "hashtags": ["지역명맛집", "업종명추천", "데일리맛집"],
      "posting_frequency": "주 1-2회",
      "best_time": "평일 오전 10-11시 (점심 전 검색 타임)",
      "content_tips": [
        "도입-본문-결론 구조로 작성",
        "상세한 메뉴 설명과 가격 포함",
        "방문 정보(주차, 영업시간) 필수",
        "SEO 최적화를 위한 키워드 반복"
      ]""",
            "YouTube Shorts": """
      "channel_name": "유튜브 쇼츠",
      "post_format": "60초 이내 세로형 영상",
      "visual_direction": ["먹방 ASMR", "조리 과정", "메뉴 언박싱", "비포/애프터"],
      "copy_examples": [
        "도입 멘트 (예: 이 가게 진짜 미쳤어요)",
        "클라이맥스 (예: 와 이게 진짜...)",
        "마무리 멘트 (예: 꼭 가보세요!)"
      ],
      "hashtags": ["#shorts", "#먹방", "#맛집투어", "#리얼후기"],
      "posting_frequency": "주 3-4회",
      "best_time": "저녁 시간대 (19-21시)",
      "content_tips": [
        "첫 3초가 승부처 (강렬한 비주얼)",
        "자막으로 핵심 정보 전달",
        "트렌드 음악/효과음 활용",
        "CTA 명확히 (구독, 좋아요)"
      ]""",
            "TikTok": """
      "channel_name": "틱톡",
      "post_format": "15-30초 숏폼 영상",
      "visual_direction": ["빠른 전개", "트렌디한 편집", "챌린지 활용", "리액션"],
      "copy_examples": [
        "챌린지 카피 (예: #맛집챌린지 #성수동편)",
        "리액션 카피 (예: POV: 퇴근하고 여기 왔을 때)",
        "팁 공유 (예: 이 메뉴 꿀팁 알려드림)"
      ],
      "hashtags": ["#fyp", "#맛집", "#먹방", "#foodtok", "#k-food"],
      "posting_frequency": "주 5-7회",
      "best_time": "점심시간 (12-13시), 저녁 (18-20시)",
      "content_tips": [
        "트렌드 사운드 적극 활용",
        "빠른 컷 편집 (1-2초마다 전환)",
        "댓글 유도 질문 던지기",
        "듀엣/스티치 기능 활용"
      ]""",
            "카카오톡": """
      "channel_name": "카카오톡 채널",
      "post_format": "채팅형 메시지 + 이미지 카드",
      "visual_direction": ["깔끔한 메뉴 이미지", "쿠폰 디자인", "이벤트 배너"],
      "copy_examples": [
        "푸시 메시지 (예: [오늘만] 친구 할인 10% 🎁)",
        "이벤트 안내 (예: 신메뉴 출시! 첫 100명 사은품 증정)",
        "단골 감사 (예: 항상 감사합니다 ❤️ 특별 쿠폰 드려요)"
      ],
      "hashtags": [],
      "posting_frequency": "주 2-3회 (과도한 알림 주의)",
      "best_time": "오전 11시 (점심 전), 오후 5시 (퇴근 전)",
      "content_tips": [
        "간결하고 명확한 메시지 (1-2줄)",
        "쿠폰/혜택 중심 콘텐츠",
        "이모지 적절히 활용",
        "클릭 유도 CTA 명확히"
      ]"""
        }
        return templates.get(channel_name, templates["Instagram"])

    # ========================================
    # Step 3: LLM 프롬프트 구성
    # ========================================
    system_prompt = f"""당신은 소상공인을 위한 콘텐츠 크리에이터입니다.
전략팀이 제안한 마케팅 채널과 아이디어를 받아, 실제 게시할 수 있는 구체적인 콘텐츠 가이드라인을 생성합니다.

**핵심 원칙:**
1. 가게 분위기와 타겟 고객에 맞춰야 함
2. 채널 특성 반영 (사용자가 선택한 채널만 생성)
3. 실행 가능한 구체적인 예시 제공
4. 시각적 방향성 명확히 제시
"""

    # 🔥 선택된 채널에 대한 템플릿 동적 생성
    channel_templates_str = ",\n    ".join([
        "{" + generate_channel_template(ch) + "}"
        for ch in selected_channels
    ])

    # 🔥 사용자 요청 섹션 추가
    user_query_section = ""
    has_user_query = user_query and user_query.strip() and user_query != f"Analyze {store_name}"

    if has_user_query:
        user_query_section = f"""
# 사용자 요청 사항 (최우선 반영)
**"{user_query}"**

⚠️ **중요**: 위 사용자 요청을 모든 콘텐츠 전략의 **핵심**으로 삼으세요.

**반영 우선순위:**
1. **🎯 사용자 요청**: 위 요청 내용을 최우선으로 반영
2. **📊 전략 데이터**: 전략팀 제안 및 시장 분석 데이터 활용
3. **📋 기본 템플릿**: 채널별 표준 가이드라인 참고

**구체적 반영 방법:**
- 특정 채널 언급 시 (예: "인스타그램", "블로그") → 해당 채널에만 집중, 다른 채널 생략 가능
- 특정 톤/스타일 요청 시 (예: "친근하게", "전문적으로") → brand_tone 및 모든 카피에 반영
- 특정 타겟 언급 시 (예: "20대", "직장인") → target_audience 및 카피/해시태그에 맞춤 반영
- 특정 콘텐츠 형식 요청 시 (예: "릴스", "후기") → post_format 및 visual_direction 우선 반영
- 특정 키워드 요청 시 → 해시태그 및 무드보드에 우선 포함
- 특정 메시지/테마 언급 시 → 모든 카피 예시에 해당 테마 반영

**예시:**
- "인스타그램 릴스에 특화해줘" → Instagram 채널만 생성, post_format은 "릴스 중심"
- "친근하고 MZ 세대에게 어필" → brand_tone = "친근한, 트렌디한, 캐주얼한", target_audience = "MZ세대 (2030)"
- "프리미엄 이미지 강조" → brand_tone = "세련된, 고급스러운", mood_board에 "프리미엄", "엘레강스" 포함

---
"""

    user_prompt = f"""
{user_query_section}

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

{'⚠️ **위 사용자 요청을 최우선으로 반영**하여 콘텐츠 가이드를 생성하세요.' if has_user_query else '위 정보를 바탕으로 콘텐츠 가이드를 생성하세요.'}

**선택된 채널**: {', '.join(selected_channels)}

다음 JSON 형식으로 응답:
{{
  "target_store": "{store_name}",
  "target_audience": "주요 타겟 고객층 (예: 2030 직장인 여성)",
  "brand_tone": "브랜드 톤앤매너 (예: 친근하고, 활기찬, 전문적인, 따뜻한, 세련된)",
  "mood_board": ["한글키워드1", "한글키워드2", "한글키워드3", "한글키워드4", "한글키워드5", "한글키워드6"],
  "mood_board_en": ["english keyword1", "english keyword2", "english keyword3", "english keyword4", "english keyword5", "english keyword6"],
  "channels": [
    {channel_templates_str}
  ],
  "overall_strategy": "전체 콘텐츠 전략 1-2문장 요약",
  "do_not_list": ["과도한 할인 강조", "경쟁사 언급", "부정적 표현"]
}}

**중요:**
{'1. **🎯 사용자 요청을 최우선 반영**: 위 "사용자 요청 사항" 섹션의 내용을 모든 필드에 우선 반영하세요' if has_user_query else '1. 사용자가 선택한 채널에 맞춰 콘텐츠를 생성하세요'}
2. **반드시 선택된 채널만 생성** ({', '.join(selected_channels)})
3. 카피 예시는 구체적으로 (실제 문장 형태로 작성)
4. 해시태그는 채널당 최소 10개 이상
5. 시각적 방향성은 촬영 가이드로 활용 가능하게 구체적으로
6. **무드보드 키워드 생성 규칙**:
   - **mood_board (한글)**: 사용자에게 표시할 키워드 (예: "따뜻한 조명", "신선한 식재료", "아늑한 분위기")
   - **mood_board_en (영어)**: Pexels API 이미지 검색용 키워드 (예: "warm lighting", "fresh ingredients", "cozy atmosphere")
   - 한글과 영어 키워드는 1:1 매칭되어야 함
   - 각각 5-6개 제공
   - 시각적 분위기를 구체적으로 표현
   {'- **사용자 요청 키워드를 우선 반영**: 사용자가 특정 키워드를 요청한 경우 무드보드에 반드시 포함' if has_user_query else ''}
7. **브랜드 톤앤매너는 쉼표로 구분된 키워드 형식** (예: "친근한, 활기찬, 전문적인")
   {'- **사용자 요청 톤 우선 반영**: 사용자가 특정 톤을 요청한 경우 반드시 최우선 반영' if has_user_query else ''}
8. 각 채널의 특성을 명확히 반영 (틱톡은 빠른 편집, 블로그는 SEO 중심 등)
   {'- **사용자 요청 채널/형식 우선**: 사용자가 특정 채널이나 형식을 강조한 경우 해당 채널에 집중' if has_user_query else ''}
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
            brand_tone="친근한, 따뜻한",
            mood_board=["아늑한 분위기", "신선한 음식", "따뜻한 조명", "자연스러운 재료", "일상적인 느낌"],
            mood_board_en=["cozy atmosphere", "fresh food", "warm lighting", "natural ingredients", "daily life"],
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
def generate_channel_display_template(guide: ChannelGuideline) -> str:
    """
    채널별 표시용 템플릿 생성 (모든 채널 지원)

    Args:
        guide: ChannelGuideline 객체

    Returns:
        채널별 포맷팅된 템플릿 문자열
    """
    channel_emoji = {
        "인스타그램": "📸",
        "Instagram": "📸",
        "네이버 블로그": "📝",
        "Naver Blog": "📝",
        "유튜브 쇼츠": "🎥",
        "YouTube Shorts": "🎥",
        "틱톡": "🎵",
        "TikTok": "🎵",
        "카카오톡 채널": "💬",
        "카카오톡": "💬"
    }

    emoji = channel_emoji.get(guide.channel_name, "📱")

    template = f"""
{emoji} {guide.channel_name} 콘텐츠 가이드

## 포스팅 형식
{guide.post_format}

## 시각적 방향
{', '.join(guide.visual_direction)}

## 카피/제목 예시
{chr(10).join(f"{i+1}. {ex}" for i, ex in enumerate(guide.copy_examples))}

## 해시태그/키워드
{' '.join(f'#{tag}' if not tag.startswith('#') else tag for tag in guide.hashtags[:15])}

## 게시 빈도
{guide.posting_frequency}

## 최적 게시 시간
{guide.best_time}

## 콘텐츠 팁
{chr(10).join(f"• {tip}" for tip in guide.content_tips)}
"""
    return template


# 레거시 호환성 유지
def generate_instagram_template(guide: ChannelGuideline) -> str:
    """인스타그램 포스팅 템플릿 생성 (레거시)"""
    return generate_channel_display_template(guide)


def generate_blog_template(guide: ChannelGuideline) -> str:
    """블로그 포스팅 템플릿 생성 (레거시)"""
    return generate_channel_display_template(guide)


# === 테스트용 ===
if __name__ == "__main__":
    test_state = {
        "target_store_name": "성수 브런치 카페",
        "industry": "카페",
        "content_channels": ["Instagram"],  # 🔥 인스타그램만 선택
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
    print(f"\n무드보드 (한글): {', '.join(guide['mood_board'])}")
    print(f"무드보드 (영어): {', '.join(guide['mood_board_en'])}")
    print(f"\n채널 수: {len(guide['channels'])}")

    for ch in guide["channels"]:
        print(f"\n[{ch['channel_name']}]")
        print(f"  형식: {ch['post_format']}")
        print(f"  시각 방향: {', '.join(ch['visual_direction'][:3])}...")
        print(f"  해시태그: {', '.join(ch['hashtags'][:5])}...")
        print(f"  게시 빈도: {ch['posting_frequency']}")
        print(f"  최적 시간: {ch['best_time']}")
