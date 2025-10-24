"""
Moodboard Helper - Pexels API를 활용한 무드보드 이미지 생성
Streamlit에서 content_guide의 mood_board 키워드를 받아 이미지 검색
"""
import os
import requests
import random
from typing import List, Dict, Optional

# Pexels API 키워드 필터
SCENE_KEYWORDS = [
    "interior", "table", "counter", "bar", "kitchen", "menu", "flatlay",
    "plating", "latte", "espresso", "dessert", "dish", "cup", "storefront"
]

def search_pexels_images(
    keywords: List[str],
    api_key: str,
    per_keyword: int = 1,
    orientation: str = "portrait"
) -> List[Dict]:
    """
    Pexels API로 키워드 기반 이미지 검색

    Args:
        keywords: 무드보드 키워드 리스트 (예: ['밝고 경쾌한', '세련된', '도시적인'])
        api_key: Pexels API 키
        per_keyword: 키워드당 가져올 이미지 수
        orientation: 이미지 방향 (portrait/landscape/square)

    Returns:
        이미지 정보 리스트 [{'url': ..., 'photographer': ..., 'alt': ...}, ...]
    """
    if not api_key:
        raise ValueError("PEXELS_API_KEY가 필요합니다")

    results = []
    seen_urls = set()

    # 한글 키워드를 영문 쿼리로 변환 (간단 매핑)
    keyword_map = {
        "밝고 경쾌한": "bright coffee shop interior",
        "세련된": "elegant cafe interior",
        "도시적인": "modern urban cafe",
        "친근한": "cozy cafe atmosphere",
        "전문적인": "professional restaurant interior",
        "깔끔한": "clean minimal cafe",
        "밝은": "bright interior",
        "맛있는": "delicious food plating"
    }

    for idx, keyword in enumerate(keywords):
        # 한글이면 매핑, 영문이면 그대로
        query = keyword_map.get(keyword, keyword)

        # Pexels API 호출
        url = f"https://api.pexels.com/v1/search"
        params = {
            "query": query,
            "per_page": 30,
            "orientation": orientation,
            "page": 1  # 각 키워드마다 다른 페이지 시작
        }
        headers = {"Authorization": api_key}

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            photos = response.json().get("photos", [])

            # 랜덤 셔플로 매번 다른 이미지 선택
            random.shuffle(photos)

            # 현재 키워드에서 per_keyword개만 선택
            added_count = 0
            for photo in photos:
                if added_count >= per_keyword:
                    break

                src = photo.get("src", {})
                img_url = src.get("portrait") or src.get("large") or src.get("original")

                if img_url and img_url not in seen_urls:
                    # 사람 사진 필터링 (간단 버전)
                    alt = (photo.get("alt") or "").lower()
                    if any(word in alt for word in ["person", "people", "woman", "man", "portrait"]):
                        continue

                    seen_urls.add(img_url)
                    results.append({
                        "url": img_url,
                        "photographer": photo.get("photographer", "Unknown"),
                        "photographer_url": photo.get("photographer_url", "#"),
                        "alt": photo.get("alt", keyword),
                        "avg_color": photo.get("avg_color", "#999999"),
                        "keyword": keyword  # 어떤 키워드에서 왔는지 추적
                    })
                    added_count += 1

        except Exception as e:
            print(f"⚠️ Pexels API 오류 ({keyword}): {e}")
            continue

    # 최소 6개 보장 (부족하면 복사)
    while len(results) < 6 and results:
        results.append(results[-1].copy())

    return results[:6]


def generate_moodboard_queries(mood_board: List[str], industry: str) -> List[str]:
    """
    무드보드 키워드와 업종을 조합하여 검색 쿼리 생성

    Args:
        mood_board: ['밝고 경쾌한', '세련된', ...]
        industry: '축산물', '카페', ...

    Returns:
        영문 검색 쿼리 리스트
    """
    # 업종별 기본 쿼리
    industry_base = {
        "축산물": "butcher shop interior",
        "카페": "coffee shop interior",
        "한식": "korean restaurant interior",
        "치킨": "chicken restaurant",
        "베이커리": "bakery interior"
    }

    base_query = industry_base.get(industry, "restaurant interior")

    # 무드보드 키워드별 쿼리 생성
    queries = [base_query]

    mood_keywords = {
        "밝고 경쾌한": "bright",
        "세련된": "elegant",
        "도시적인": "modern urban",
        "친근한": "cozy warm",
        "전문적인": "professional",
        "깔끔한": "clean minimal",
        "밝은": "bright",
        "맛있는": "delicious food"
    }

    for mood in mood_board[:5]:
        english_mood = mood_keywords.get(mood, mood)
        queries.append(f"{english_mood} {base_query}")

    return queries[:6]


# ========== 폴백: API 없이 샘플 이미지 ==========
def get_fallback_images() -> List[Dict]:
    """API 키 없을 때 샘플 이미지"""
    return [
        {
            "url": "https://images.pexels.com/photos/302899/pexels-photo-302899.jpeg?auto=compress&cs=tinysrgb&w=400",
            "photographer": "Pexels",
            "photographer_url": "https://www.pexels.com",
            "alt": "Coffee shop interior",
            "avg_color": "#8B7355"
        },
        {
            "url": "https://images.pexels.com/photos/1907642/pexels-photo-1907642.jpeg?auto=compress&cs=tinysrgb&w=400",
            "photographer": "Pexels",
            "photographer_url": "https://www.pexels.com",
            "alt": "Latte art",
            "avg_color": "#C4A57B"
        },
        {
            "url": "https://images.pexels.com/photos/1833336/pexels-photo-1833336.jpeg?auto=compress&cs=tinysrgb&w=400",
            "photographer": "Pexels",
            "photographer_url": "https://www.pexels.com",
            "alt": "Dessert flatlay",
            "avg_color": "#D4AF87"
        }
    ] * 2  # 6개로 확장
