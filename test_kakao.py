import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("KAKAO_API_KEY")

if not api_key:
    print("Kakao API 키가 설정되지 않았습니다.")
    exit()

url = "https://dapi.kakao.com/v2/local/search/keyword.json"

headers = {
    "Authorization": f"KakaoAK {api_key}"
}

params = {
    "query": "제주 맛집",
    "size": 5
}

try:
    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()
    places = data.get("documents", [])

    print("Kakao API 연결 성공!")
    print(f"검색 결과: {len(places)}곳")

    for i, place in enumerate(places, start=1):
        print(f"\n{i}. {place.get('place_name')}")
        print(f"   주소: {place.get('address_name')}")
        print(f"   카테고리: {place.get('category_name')}")
        print(f"   URL: {place.get('place_url')}")
        print(f"   위치: ({place.get('x')}, {place.get('y')})")

except requests.exceptions.HTTPError as e:
    print("Kakao API HTTP 오류")
    print("상태 코드:", response.status_code)
    print("응답 내용:", response.text)
    print("오류:", e)

except requests.exceptions.RequestException as e:
    print("Kakao API 네트워크 오류")
    print("오류:", e)

except ValueError as e:
    print("Kakao API 응답 JSON 파싱 오류")
    print("오류:", e)

except Exception as e:
    print("Kakao API 호출 실패")
    print("오류:", e)