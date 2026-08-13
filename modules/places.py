import os

import requests
from dotenv import load_dotenv


load_dotenv()


def search_restaurants(city, limit=5):
    api_key = os.getenv("KAKAO_API_KEY")

    if not api_key:
        raise RuntimeError(
            "KAKAO_API_KEY가 설정되지 않았습니다. "
            ".env 파일을 확인해주세요."
        )

    url = "https://dapi.kakao.com/v2/local/search/keyword.json"

    headers = {
        "Authorization": f"KakaoAK {api_key}"
    }

    params = {
        "query": f"{city} 맛집",
        "size": limit
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    restaurants = []

    for place in data.get("documents", []):
        restaurants.append({
            "name": place.get("place_name", ""),
            "address": place.get("address_name", ""),
            "category": place.get("category_name", ""),
            "url": place.get("place_url", ""),
            "x": float(place["x"]) if place.get("x") else None,
            "y": float(place["y"]) if place.get("y") else None
        })

    return restaurants