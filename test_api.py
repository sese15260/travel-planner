import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Gemini API 키가 설정되지 않았습니다.")
    exit()

try:
    client = genai.Client(api_key=api_key)

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input="안녕하세요. 국내 여행 추천 프로그램 API 연결 테스트입니다. 한 문장으로 답해주세요."
    )

    print("Gemini API 연결 성공!")
    print("응답:", interaction.output_text)

except Exception as e:
    print("Gemini API 호출 실패")
    print("오류:", e)