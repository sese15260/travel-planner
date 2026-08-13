import json
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY가 설정되지 않았습니다. "
            ".env 파일을 확인해주세요."
        )

    return genai.Client(api_key=api_key)


def get_travel_recommendation(date):
    client = get_gemini_client()

    prompt = f"""
당신은 국내 여행 전문 추천가입니다.

사용자가 여행하려는 날짜는 {date}입니다.

해당 날짜에 여행하기 좋은 국내 도시 2~3곳을 추천해주세요.

다음 조건을 반드시 지켜주세요.

1. 반드시 JSON 객체 하나만 출력하세요.
2. JSON 앞이나 뒤에 설명을 붙이지 마세요.
3. Markdown 코드 블록(```)을 사용하지 마세요.
4. recommended_cities에는 서로 다른 국내 도시 2~3곳을 넣으세요.
5. events는 1~3개의 행사 또는 축제 후보를 문자열 배열로 작성하세요.
6. 실제 행사 일정이 확실하지 않은 경우 "일정 변동 가능"이라는 표현을 포함하세요.
7. weather는 해당 시기의 일반적인 날씨를 요약하세요.
8. reason은 추천 근거를 2~4문장으로 작성하세요.

반드시 다음 JSON 구조를 지켜주세요.

{{
    "recommended_cities": [
        "도시 이름 1",
        "도시 이름 2",
        "도시 이름 3"
    ],
    "weather": "해당 시기의 일반적인 날씨 요약",
    "events": [
        "행사 또는 축제 후보 1",
        "행사 또는 축제 후보 2"
    ],
    "reason": "추천 근거"
}}
"""

    max_attempts = 2

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            text = response.text.strip()

            # Gemini가 ```json ... ``` 형태로 응답하는 경우 제거
            if text.startswith("```"):
                text = text.replace("```json", "", 1)
                text = text.replace("```", "")
                text = text.strip()

            data = json.loads(text)

            required_keys = [
                "recommended_cities",
                "weather",
                "events",
                "reason"
            ]

            for key in required_keys:
                if key not in data:
                    raise ValueError(
                        f"필수 키가 없습니다: {key}"
                    )

            if not isinstance(data["recommended_cities"], list):
                raise ValueError(
                    "recommended_cities는 배열이어야 합니다."
                )

            if not 2 <= len(data["recommended_cities"]) <= 3:
                raise ValueError(
                    "recommended_cities는 2~3개여야 합니다."
                )

            if not all(
                isinstance(city, str)
                for city in data["recommended_cities"]
            ):
                raise ValueError(
                    "recommended_cities의 각 지역은 문자열이어야 합니다."
                )

            if not isinstance(data["weather"], str):
                raise ValueError(
                    "weather는 문자열이어야 합니다."
                )

            if not isinstance(data["events"], list):
                raise ValueError(
                    "events는 배열이어야 합니다."
                )

            if not all(
                isinstance(event, str)
                for event in data["events"]
            ):
                raise ValueError(
                    "events의 각 항목은 문자열이어야 합니다."
                )

            if not isinstance(data["reason"], str):
                raise ValueError(
                    "reason은 문자열이어야 합니다."
                )

            return data

        except json.JSONDecodeError as e:
            if attempt == 0:
                print(
                    "Gemini 응답을 JSON으로 변환하지 못했습니다."
                )
                print("JSON 파싱을 1회 재시도합니다.")
                continue

            raise ValueError(
                f"Gemini 응답을 JSON으로 변환하지 못했습니다: {e}"
            )

        except Exception as e:
            raise RuntimeError(
                f"Gemini 여행 추천 생성 실패: {e}"
            )