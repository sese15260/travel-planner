import json
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY가 설정되지 않았습니다."
        )

    return genai.Client(api_key=api_key)


def generate_report(
    recommendation,
    restaurants_by_city,
    errors
):
    client = get_gemini_client()

    prompt = f"""
당신은 국내 여행 일정 전문 작가입니다.

다음 여행 정보를 바탕으로 여행 리포트를 Markdown 형식으로 작성하세요.

[여행 추천 정보]
{json.dumps(recommendation, ensure_ascii=False, indent=2)}

[지역별 맛집 정보]
{json.dumps(restaurants_by_city, ensure_ascii=False, indent=2)}

[오류 정보]
{json.dumps(errors, ensure_ascii=False, indent=2)}

반드시 다음 항목을 포함하세요.

# 국내 여행 추천 리포트

## 추천 지역
추천 지역을 작성하세요.

## 추천 이유
추천 이유를 자연스럽게 요약하세요.

## 날씨 요약
여행 날짜의 날씨 정보를 작성하세요.

## 행사/축제
행사 또는 축제 목록을 작성하세요.

## 맛집 추천
맛집은 지역별로 구분해서 작성하세요.

각 추천 지역마다 해당 지역의 맛집을 별도로 표시하세요.

예:

## 맛집 추천

### 안동
1. 맛집 A
2. 맛집 B

### 진주
1. 맛집 C
2. 맛집 D

### 정선
1. 맛집 E
2. 맛집 F

특정 지역의 맛집 데이터가 없다면 해당 지역에 "데이터 없음"이라고 표시하세요.

제공된 맛집 데이터에 없는 식당을 새로 만들어내지 마세요.

## 1일 일정 제안
오전 / 오후 / 저녁으로 나누어 여행 일정을 제안하세요.

## 오류 요약
오류가 없다면 "없음"이라고 작성하세요.

중요:
- Markdown 형식으로만 작성하세요.
- Markdown 코드 블록으로 감싸지 마세요.
- 제공된 맛집 데이터에 없는 식당을 새로 만들어내지 마세요.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text.strip()