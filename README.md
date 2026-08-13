# 국내 여행 추천 프로그램

Gemini API와 Kakao Local API를 활용하여 사용자가 입력한 여행 날짜에 맞는 국내 여행지를 추천하고, 해당 지역의 맛집을 검색한 뒤 최종 여행 리포트를 생성하는 CLI 기반 Python 프로그램입니다.

## 1. 프로젝트 개요

사용자가 여행 날짜를 입력하면 다음과 같은 과정으로 여행 정보를 생성합니다.

1. 사용자가 여행 날짜를 입력합니다.
2. Gemini API가 여행하기 좋은 국내 지역을 2~3곳 추천합니다.
3. Gemini API가 해당 시기의 날씨와 행사/축제 정보를 JSON 형태로 제공합니다.
4. Kakao Local API를 이용하여 추천 지역별 맛집을 검색합니다.
5. Gemini API가 여행 지역, 날씨, 행사, 맛집 정보를 종합하여 최종 여행 리포트를 Markdown 형식으로 생성합니다.
6. API 호출 결과와 오류 정보를 JSON 파일로 저장합니다.
7. 최종 여행 리포트를 Markdown 파일로 저장합니다.
8. 같은 날짜로 다시 실행할 경우 저장된 결과를 활용하여 불필요한 API 호출을 줄일 수 있습니다.

---

## 2. 주요 기능

### 2-1. CLI 날짜 입력

`argparse`를 이용하여 터미널에서 여행 날짜를 입력할 수 있습니다.

```bash
py travel_planner.py --date "2026-10-03"

날짜는 반드시 YYYY-MM-DD 형식으로 입력해야 합니다.

잘못된 형식으로 입력하면 프로그램이 실행되지 않고 사용 방법과 오류 메시지를 출력합니다.

예:

usage: travel_planner.py [-h] --date DATE
travel_planner.py: error: argument --date: 날짜 형식은 YYYY-MM-DD 입니다.
2-2. 복수 지역 추천

Gemini API를 이용하여 하나의 지역이 아닌 여러 여행 지역을 추천받습니다.

예:

{
  "recommended_cities": [
    "진주",
    "안동",
    "경주"
  ]
}

추천된 각 지역에 대해 Kakao Local API를 이용하여 맛집을 검색합니다.

2-3. 날씨 및 행사/축제 정보

입력한 여행 날짜를 기준으로 Gemini API에 여행 지역 추천을 요청합니다.

결과에는 다음 정보가 포함됩니다.

추천 지역
해당 시기의 날씨 요약
행사/축제 후보
추천 이유

LLM의 응답은 다음과 같이 JSON 형태로 구조화하여 사용합니다.

{
  "recommended_cities": [
    "진주",
    "안동",
    "경주"
  ],
  "weather": "선선하고 맑은 가을 날씨",
  "events": [
    "진주 남강유등축제",
    "안동 국제탈춤페스티벌",
    "경주 신라문화제"
  ],
  "reason": "가을 축제와 야외 활동을 즐기기 좋은 시기이기 때문입니다."
}
2-4. 지역별 맛집 검색

Kakao Local API를 이용하여 Gemini가 추천한 각 지역의 맛집을 검색합니다.

지역별로 최대 5곳을 검색합니다.

예:

[진주] 맛집 검색 중...
- 진주: 5곳 검색 완료

1. 유정장어 본점
2. 진주냉면 산홍 진주시청점
3. 하연옥 본점
4. 천황식당
5. 소우주

검색 결과에는 다음 정보가 포함됩니다.

맛집 이름
주소
카테고리
장소 URL
위치 좌표
2-5. 최종 여행 리포트 생성

Gemini API를 이용하여 여행 추천 정보와 맛집 정보를 종합합니다.

최종 결과는 Markdown 파일로 저장됩니다.

리포트에는 다음 내용이 포함됩니다.

추천 지역
추천 이유
날씨 요약
행사/축제
지역별 맛집
1일 여행 일정
오류 요약
2-6. 결과 캐싱

같은 날짜로 프로그램을 다시 실행할 경우 이전 실행 결과가 존재하면 저장된 데이터를 활용합니다.

예:

기존 결과 데이터를 발견했습니다.
Gemini 및 Kakao API 호출을 건너뜁니다.

이를 통해 같은 날짜를 반복해서 실행할 때 API 호출을 줄이고 실행 시간을 단축할 수 있습니다.

2-7. 오류 처리

외부 API를 사용하는 과정에서 발생할 수 있는 오류를 try-except로 처리합니다.

예를 들어 Kakao Local API에서 오류가 발생하더라도 프로그램 전체를 종료하지 않고 해당 지역의 맛집을 다음과 같이 처리합니다.

데이터 없음

또한 발생한 오류는 결과 JSON 파일의 errors 항목에 저장합니다.

3. 프로젝트 구조
travel-planner/
│
├── travel_planner.py       # 프로그램 실행 및 전체 흐름 제어
├── test_api.py             # Gemini API 연결 테스트
├── test_kakao.py           # Kakao API 연결 테스트
├── requirements.txt        # Python 패키지 목록
├── .gitignore              # Git에 저장하지 않을 파일 설정
├── README.md               # 프로젝트 설명 및 실행 방법
│
├── modules/
│   ├── __init__.py
│   ├── llm.py              # Gemini API 관련 기능
│   ├── places.py           # Kakao Local API 관련 기능
│   ├── report.py           # 최종 여행 리포트 생성
│   └── cache.py            # 결과 캐싱 기능
│
└── results/
    ├── 2026-10-03_travel_data.json
    └── 2026-10-03_travel_plan.md
4. 개발 환경
OS: Windows
개발 도구: Visual Studio Code
Python: 3.13.7
Git: 2.53.0
Python 가상환경: venv
5. 사용 API
Gemini API

여행 날짜를 기반으로 여행 지역, 날씨, 행사/축제 및 최종 여행 리포트를 생성하는 데 사용합니다.

Kakao Local API

Gemini가 추천한 국내 여행 지역을 기준으로 맛집 정보를 검색하는 데 사용합니다.

6. 설치 방법
6-1. 저장소 가져오기

GitHub 저장소를 clone합니다.

git clone https://github.com/sese15260/travel-planner.git

프로젝트 폴더로 이동합니다.

cd travel-planner
6-2. 가상환경 생성
py -m venv venv
6-3. 가상환경 활성화

Windows PowerShell에서 다음 명령어를 실행합니다.

.\venv\Scripts\Activate.ps1

활성화되면 터미널 앞에 다음과 같이 표시됩니다.

(venv) PS C:\Users\...\travel-planner>

만약 PowerShell의 실행 정책으로 인해 활성화되지 않는 경우 다음 명령어를 실행합니다.

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

그 후 다시 가상환경을 활성화합니다.

.\venv\Scripts\Activate.ps1
6-4. 필요한 패키지 설치
pip install -r requirements.txt
7. API 키 설정

이 프로그램은 Gemini API와 Kakao Local API를 사용합니다.

API 키는 Python 코드에 직접 작성하지 않고 환경변수로 관리합니다.

Windows PowerShell

현재 터미널 세션에서 다음과 같이 설정할 수 있습니다.

$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
$env:KAKAO_REST_API_KEY="YOUR_KAKAO_REST_API_KEY"

YOUR_GEMINI_API_KEY와 YOUR_KAKAO_REST_API_KEY 부분에는 실제 발급받은 키를 입력합니다.

실제 API 키는 GitHub에 업로드하면 안 됩니다.

8. API 연결 확인

프로그램을 실행하기 전에 Gemini API 연결을 확인할 수 있습니다.

py test_api.py

정상적으로 연결되면 다음과 같은 결과가 출력됩니다.

Gemini API 연결 성공!

Kakao Local API는 다음 명령어로 테스트할 수 있습니다.

py test_kakao.py

정상적으로 연결되면 검색 결과와 맛집 정보가 출력됩니다.

Kakao API 연결 성공!
검색 결과: 5곳
9. 프로그램 실행

여행 날짜를 YYYY-MM-DD 형식으로 입력합니다.

py travel_planner.py --date "2026-10-03"

정상적으로 실행되면 다음과 같은 과정이 진행됩니다.

========================================
국내 여행 추천 프로그램
========================================
여행 날짜 : 2026-10-03

[1/3] 여행 지역 추천 생성 중 (Gemini)...

[2/3] 지역별 맛집 검색 중 (Kakao Local)...

[3/3] 최종 여행 리포트 생성 중 (Gemini)...

========================================
완료!
========================================
10. 결과물 확인

프로그램 실행이 완료되면 results/ 폴더에 결과가 저장됩니다.

원본 데이터 JSON
results/2026-10-03_travel_data.json

JSON 파일에는 다음 정보가 포함됩니다.

여행 날짜
Gemini 여행 추천 결과
추천 지역별 맛집 검색 결과
오류 목록

구조 예시:

{
  "date": "2026-10-03",
  "recommendation": {
    "recommended_cities": [
      "진주",
      "안동",
      "경주"
    ],
    "weather": "...",
    "events": [],
    "reason": "..."
  },
  "restaurants_by_city": {
    "진주": [],
    "안동": [],
    "경주": []
  },
  "errors": []
}
최종 여행 리포트
results/2026-10-03_travel_plan.md

Markdown 파일을 VS Code에서 열어 최종 여행 추천 결과를 확인할 수 있습니다.

11. 캐싱 기능

같은 날짜의 결과가 이미 저장되어 있는 경우 캐싱 기능을 이용할 수 있습니다.

예:

기존 결과 데이터를 발견했습니다.
Gemini 및 Kakao API 호출을 건너뜁니다.

이 경우 이전 API 결과를 활용하여 불필요한 API 호출을 방지합니다.

캐싱은 외부 API 사용량과 실행 시간을 줄이는 데 목적이 있습니다.

12. 보안 주의사항

API 키는 외부에 공개되면 안 됩니다.

따라서 다음과 같은 방법으로 API 키를 관리합니다.

API 키를 Python 코드에 직접 작성하지 않습니다.
환경변수를 사용합니다.
.env를 사용하는 경우 .gitignore에 등록합니다.
API 키가 포함된 파일을 GitHub에 업로드하지 않습니다.
README에 실제 API 키를 작성하지 않습니다.
터미널 실행 결과를 캡처하거나 공유할 때 API 키가 표시되지 않았는지 확인합니다.

API 키가 GitHub에 공개되면 다른 사람이 해당 키를 사용할 수 있고, API 사용량이나 비용 문제가 발생할 수 있습니다.

13. GitHub

프로젝트 저장소:

https://github.com/sese15260/travel-planner

프로젝트의 소스 코드는 GitHub 저장소에서 확인할 수 있습니다.
