from langchain.tools import tool


@tool
def create_marketing_copy(product_info: str, target_audience: str) -> str:
    """제품 정보와 타겟 고객을 기반으로 마케팅 카피를 작성합니다."""
    copy = f"""
    === 마케팅 카피 초안 ===
    
    제품/서비스: {product_info}
    타겟: {target_audience}
    
    헤드라인:
    "당신의 일상을 특별하게 만드는 {product_info}"
    
    본문:
    {target_audience}을 위한 최적의 솔루션을 제공합니다.
    우리는 고객의 니즈를 정확히 이해하고, 
    가장 효과적인 방법으로 문제를 해결합니다.
    
    CTA (Call-to-Action):
    "지금 바로 시작하세요!"
    
    추가 메시지:
    - 고객 만족도 98%
    - 빠르고 신뢰할 수 있는 서비스
    - 합리적인 가격
    """
    return copy


@tool
def create_social_media_content(platform: str, message: str) -> str:
    """특정 소셜 미디어 플랫폼에 맞는 콘텐츠를 작성합니다."""
    platform_guide = {
        "instagram": "시각적 요소 강조, 해시태그 활용, 스토리 형식",
        "facebook": "커뮤니티 참여 유도, 긴 형식 가능, 링크 공유",
        "twitter": "짧고 임팩트 있는 메시지, 트렌드 활용",
        "linkedin": "전문성 강조, B2B 포커스",
        "kakao": "친근한 톤, 이모티콘 활용"
    }
    
    guide = platform_guide.get(platform.lower(), "일반적인 소셜 미디어 가이드")
    
    content = f"""
    === {platform} 콘텐츠 ===
    
    플랫폼 특성: {guide}
    
    콘텐츠 초안:
    {message}
    
    추천 해시태그:
    #소상공인 #마케팅 #성공사례 #비즈니스팁
    
    게시 최적 시간: 오전 11시, 오후 7시
    """
    return content


@tool
def create_email_campaign(subject: str, target_segment: str) -> str:
    """이메일 캠페인 초안을 작성합니다."""
    email = f"""
    === 이메일 캠페인 ===
    
    제목: {subject}
    타겟 세그먼트: {target_segment}
    
    이메일 본문:
    
    안녕하세요, [고객명]님!
    
    {subject}에 대한 특별한 소식을 전해드립니다.
    
    {target_segment}을 위한 맞춤 혜택:
    - 특별 할인 제공
    - 무료 상담 기회
    - 추가 서비스 제공
    
    지금 바로 확인하시고,
    이 기회를 놓치지 마세요!
    
    [CTA 버튼: 자세히 보기]
    
    감사합니다.
    """
    return email


# 모든 도구를 리스트로 제공
content_writer_tools = [
    create_marketing_copy,
    create_social_media_content,
    create_email_campaign,
]
