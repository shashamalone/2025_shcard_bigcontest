from langchain.tools import tool


@tool
def suggest_design_concept(brand_style: str, campaign_type: str) -> str:
    """브랜드 스타일과 캠페인 유형에 맞는 디자인 컨셉을 제안합니다."""
    design = f"""
    === 디자인 컨셉 제안 ===
    
    브랜드 스타일: {brand_style}
    캠페인 유형: {campaign_type}
    
    컬러 팔레트:
    - 주 색상: #2C3E50 (진한 네이비)
    - 보조 색상: #E74C3C (따뜻한 레드)
    - 강조 색상: #F39C12 (오렌지 골드)
    
    타이포그래피:
    - 헤드라인: 고딕체 (굵게)
    - 본문: 명조체 또는 산세리프
    
    레이아웃 가이드:
    - 깔끔하고 현대적인 그리드 시스템
    - 충분한 여백 활용
    - 시각적 계층 구조 명확히
    
    비주얼 요소:
    - 고품질 이미지 사용
    - 아이콘으로 정보 시각화
    - 일관된 브랜드 아이덴티티 유지
    
    플랫폼별 최적화:
    - 모바일: 1080x1080 (정사각형)
    - 데스크톱: 1200x628 (와이드)
    - 스토리: 1080x1920 (세로)
    """
    return design


@tool
def create_visual_hierarchy(content_elements: str) -> str:
    """콘텐츠 요소들의 시각적 계층을 구성합니다."""
    hierarchy = f"""
    === 시각적 계층 구조 ===
    
    콘텐츠 요소: {content_elements}
    
    계층 구조 (중요도 순):
    
    1단계 (최우선): 
       - 헤드라인/메인 메시지
       - 크기: 크게 (32-48pt)
       - 위치: 상단 중앙
    
    2단계:
       - 핵심 이미지/비주얼
       - 크기: 화면의 40-50%
       - 위치: 메인 컨텐츠 영역
    
    3단계:
       - 부제목/설명 텍스트
       - 크기: 중간 (18-24pt)
       - 위치: 이미지 하단
    
    4단계:
       - CTA 버튼
       - 크기: 명확하게 보이는 크기
       - 위치: 하단 또는 우측
    
    5단계:
       - 부가 정보/세부사항
       - 크기: 작게 (12-16pt)
       - 위치: 가장 하단
    """
    return hierarchy


@tool
def optimize_for_platform(design_type: str, platform: str) -> str:
    """특정 플랫폼에 최적화된 디자인 가이드를 제공합니다."""
    platform_specs = {
        "instagram": "1080x1080 (피드), 1080x1920 (스토리), 밝고 생동감 있는 색상",
        "facebook": "1200x628 (링크), 1080x1080 (포스트), 텍스트 20% 이하",
        "youtube": "1280x720 (썸네일), 임팩트 있는 텍스트와 얼굴",
        "blog": "1200x630 (대표 이미지), 읽기 쉬운 레이아웃",
        "email": "600px 너비, 모바일 최적화 필수"
    }
    
    spec = platform_specs.get(platform.lower(), "일반 웹 표준 (1200x630)")
    
    guide = f"""
    === {platform} 최적화 가이드 ===
    
    디자인 유형: {design_type}
    
    기술 스펙:
    {spec}
    
    플랫폼별 팁:
    - 모바일 우선 고려
    - 로딩 속도 최적화
    - 접근성 (가독성, 대비) 확보
    - 브랜드 일관성 유지
    
    체크리스트:
    ✓ 파일 크기 최적화 (< 1MB)
    ✓ 해상도 적절한지 확인
    ✓ 텍스트 가독성 테스트
    ✓ 여러 기기에서 테스트
    """
    return guide


# 모든 도구를 리스트로 제공
designer_tools = [
    suggest_design_concept,
    create_visual_hierarchy,
    optimize_for_platform,
]
