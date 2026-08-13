# A1-2_Python 응용: API 활용 국내 여행지 추천 프로그램 개발 작업 기록

상태: 시작 전

![image.png](image.png)

# 국내 여행 추천 프로그램 개발 작업 정리

## 1. 프로젝트 개요

Python CLI 환경에서 사용자가 입력한 여행 날짜를 기준으로 **Gemini API와 Kakao Local API를 연동한 국내 여행 추천 프로그램**을 구현했다.

사용자가 날짜를 입력하면 다음 순서로 프로그램이 실행된다.

```
여행 날짜 입력
    ↓
Gemini 여행 지역 추천
    ↓
추천 지역별 Kakao 맛집 검색
    ↓
Gemini 최종 여행 리포트 생성
    ↓
JSON / Markdown 결과 저장
    ↓
동일 날짜 실행 시 캐시 활용
```

---

# 2. 개발 환경

- 운영체제: Windows
- 개발 도구: VS Code
- 터미널: PowerShell
- Python: 3.13.7
- Git: 2.53.0.windows.2
- 가상환경: `venv`
- GitHub 저장소: `travel-planner`

Python 실행 명령어:

```
py
```

가상환경 활성화:

```
.\venv\Scripts\Activate.ps1
```

---

# 3. 프로젝트 구조

```
travel-planner/
├── modules/
│   ├── __init__.py
│   ├── cache.py
│   ├── llm.py
│   ├── places.py
│   └── report.py
├── results/
├── services/
├── venv/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── test_api.py
├── test_kakao.py
├── travel_planner.py
└── project_structure.txt
```

각 파일의 역할은 다음과 같다.

| 파일 | 역할 |
| --- | --- |
| `travel_planner.py` | 전체 프로그램 실행 및 CLI 처리 |
| `modules/llm.py` | Gemini 여행 추천 |
| `modules/places.py` | Kakao 맛집 검색 |
| `modules/report.py` | 최종 여행 리포트 생성 |
| `modules/cache.py` | 결과 캐싱 |
| `test_api.py` | Gemini API 연결 테스트 |
| `test_kakao.py` | Kakao API 연결 테스트 |
| `requirements.txt` | 필요한 Python 패키지 관리 |
| `.env` | API 키 저장 |
| `.gitignore` | Git에 올리지 않을 파일 관리 |
| `results/` | 실행 결과 저장 |

---

# 4. CLI 기능 구현

`argparse`를 사용하여 `--date` 옵션으로 여행 날짜를 입력받았다.

정상적인 실행 방법:

```powershell
py travel_planner.py --date "2026-10-03"
```

날짜 형식은 `YYYY-MM-DD`로 제한했다.

날짜 검증에는 `datetime.strptime()`을 사용했다.

잘못된 날짜를 입력하면:

```powershell
py travel_planner.py --date "20261003"
```

다음과 같은 오류가 발생한다.

```powershell
usage: travel_planner.py [-h] --date DATE
travel_planner.py: error: argument --date: 날짜 형식은 YYYY-MM-DD 입니다.
```

따라서 잘못된 날짜 형식이 입력되면 프로그램이 실행되지 않고 오류 메시지를 출력한다.

---

# 5. Gemini API 연동

처음에는 OpenAI API를 사용하여 테스트했지만 다음과 같은 문제가 발생했다.

```
429 insufficient_quota
You have no credits remaining.
```

따라서 과제 요구사항에 맞춰 **OpenAI 대신 Gemini API를 사용하도록 변경**했다.

Gemini API 연결 테스트 결과:

```
Gemini API 연결 성공!
응답: ...
```

현재 Gemini API는 `google-genai` 패키지를 사용한다.

API 키는 코드에 직접 작성하지 않고 `.env`에서 가져온다.

```python
api_key = os.getenv("GEMINI_API_KEY")
```

---

# 6. Gemini 여행 추천 기능

Gemini에게 여행 날짜를 전달하고 국내 여행 지역을 추천하도록 구현했다.

Gemini 응답은 자유로운 문장이 아니라 JSON 형태가 되도록 프롬프트에서 요구했다.

JSON의 주요 구조:

```json
{
  "recommended_cities": ["진주","안동","경주"
  ],
  "weather":"...",
  "events": ["...","..."
  ],
  "reason":"..."
}
```

### 주요 데이터

- `recommended_cities` → 추천 지역
- `weather` → 날씨 정보
- `events` → 행사 및 축제
- `reason` → 추천 이유

`recommended_cities`는 **2~3개 지역**을 추천하도록 구현했다.

실제 실행 결과:

```
추천 지역: ['진주', '안동', '경주']
```

이를 통해 **복수 지역 추천 보너스 기능**을 구현했다.

---

# 7. JSON 파싱 및 검증

Gemini가 반환한 문자열을 Python에서 JSON으로 변환한다.

```python
data = json.loads(text)
```

이후 필수 키가 존재하는지 확인한다.

```
recommended_cities
weather
events
reason
```

또한 각 데이터의 타입도 검사한다.

```
recommended_cities → list
weather → str
events → list
reason → str
```

추천 지역의 개수 역시 2~3개인지 검증한다.

따라서 Gemini가 예상과 다른 데이터를 반환하더라도 프로그램에서 사용할 수 있는 데이터인지 확인할 수 있도록 했다.

---

# 8. Gemini JSON 오류 처리

LLM이 항상 완벽한 JSON을 반환한다고 보장할 수 없기 때문에 JSON 파싱 오류를 처리했다.

또한 Gemini가 실수로 Markdown 코드 블록 형태의 JSON을 반환할 경우 이를 제거한 후 파싱하도록 처리했다.

JSON 파싱에 실패할 경우 **최대 1회 재시도**하도록 구현했다.

최종적으로도 정상적인 JSON을 얻지 못하면 오류로 처리한다.

---

# 9. Kakao Local API 연동

추천된 지역을 이용하여 Kakao Local API에서 맛집을 검색하도록 구현했다.

Kakao API 연결 테스트 결과:

```
Kakao API 연결 성공!
검색 결과: 5곳
```

검색 요청에는 다음과 같은 정보를 사용한다.

```python
params= {
    "query":f"{city} 맛집",
    "size":limit
}
```

지역별 최대 5개의 맛집을 검색한다.

저장하는 정보:

- 맛집 이름
- 주소
- 카테고리
- URL
- X 좌표
- Y 좌표

실제 실행 결과:

```
[진주]
5곳 검색

[안동]
5곳 검색

[경주]
5곳 검색
```

---

# 10. Kakao API 오류 처리

Kakao API에서 특정 지역 검색이 실패하더라도 프로그램 전체가 종료되지 않도록 구현했다.

오류가 발생한 지역은:

```
데이터 없음
```

으로 처리하고 `errors` 배열에 오류 내용을 저장한다.

또한 검색 결과가 0건인 경우에도 프로그램을 종료하지 않고:

```
EMPTY_RESULT
```

형태로 오류를 기록한다.

이를 통해 일부 지역에서 API 오류가 발생해도 다른 지역의 여행 정보와 최종 리포트를 계속 생성할 수 있다.

---

# 11. API 제공자를 모듈로 분리

Kakao API 기능은 `modules/places.py`의:

```python
search_restaurants()
```

함수로 분리했다.

메인 프로그램에서는:

```python
restaurants = search_restaurants(
    city,
    limit=5
)
```

형태로 사용한다.

따라서 추후 Kakao 대신 Naver 등의 다른 장소 API를 사용하게 되더라도 메인 프로그램 전체를 수정하는 것이 아니라 **장소 검색 모듈 중심으로 수정할 수 있도록 구성**했다.

---

# 12. 최종 여행 리포트 생성

Gemini를 다시 사용하여 최종 Markdown 여행 리포트를 생성했다.

`modules/report.py`에서:

```python
generate_report()
```

함수가 담당한다.

Gemini에게 전달하는 정보:

- 추천 지역
- 날씨
- 행사
- 추천 이유
- 지역별 맛집
- 오류 정보

최종 리포트에는 다음 내용을 포함하도록 구성했다.

```
# 국내 여행 추천 리포트

## 추천 지역

## 추천 이유

## 날씨 요약

## 행사/축제

## 맛집 추천

## 1일 일정 제안

## 오류 요약
```

또한 실제 데이터에 없는 맛집을 Gemini가 임의로 만들어내지 않도록 프롬프트에서 제한했다.

---

# 13. 오류 목록 관리

프로그램에서는:

```python
errors = []
```

로 오류 목록을 만든다.

오류가 발생하면 다음과 같은 형태로 저장한다.

```python
errors.append({
    "step":"place_search",
    "type":"API_ERROR",
    "city":city,
    "message":str(e)
})
```

이렇게 모은 `errors`를 최종 리포트 생성 함수에 전달한다.

따라서 오류가 발생했더라도 최종 리포트의 **오류 요약**에서 확인할 수 있다.

---

# 14. 결과 저장

실행 결과는 `results/` 폴더에 저장한다.

예:

```
results/
├── 2026-10-03_travel_data.json
└── 2026-10-03_travel_plan.md
```

### JSON

원본 여행 데이터를 저장한다.

```json
{
  "date":"2026-10-03",
  "recommendation": {
    "recommended_cities": ["진주","안동","경주"
    ],
    "weather":"...",
    "events": [],
    "reason":"..."
  },
  "restaurants_by_city": {
    "진주": [],
    "안동": [],
    "경주": []
  },
  "errors": []
}
```

### Markdown

Gemini가 생성한 최종 여행 리포트를 저장한다.

실제 실행에서도 두 파일 모두 정상적으로 생성되는 것을 확인했다.

---

# 15. 캐싱 기능

**캐싱**은 API에서 한 번 받아온 결과를 저장해두었다가 같은 요청이 다시 들어오면 저장된 데이터를 재사용하는 기능이다.

날짜별 JSON을 캐시 파일로 사용했다.

예:

```
results/2026-10-03_travel_data.json
```

프로그램 실행 시 먼저 캐시가 있는지 확인한다.

```python
cached_data = load_cache(args.date)
```

캐시가 있으면:

- Gemini 여행 추천 API 호출 생략
- Kakao 맛집 검색 API 호출 생략
- 기존 JSON 데이터 재사용

을 수행한다.

실제 동일 날짜 재실행 테스트:

```
기존 결과 데이터를 발견했습니다.
Gemini 및 Kakao API 호출을 건너뜁니다.
```

따라서 **결과 캐싱 보너스 기능도 실제로 테스트 완료**했다.

---

# 16. 캐시 파일 오류 처리

캐시 파일이 존재하지만 JSON 형식이 잘못되어 있거나 파일을 읽을 수 없는 경우도 고려했다.

`load_cache()`에서:

```python
except (json.JSONDecodeError, OSError):
    return None
```

으로 처리한다.

따라서 캐시 파일에 문제가 있더라도 프로그램 전체가 비정상 종료되지 않고 캐시가 없는 것처럼 처리하여 새로운 API 호출을 진행할 수 있다.

---

# 17. API 키 보안

API 키는 `.env`에서 관리했다.

사용하는 환경변수:

```
GEMINI_API_KEY
KAKAO_API_KEY
```

`.gitignore`에는:

```
venv/
.env
__pycache__/
*.pyc
```

를 설정했다.

특히:

```
.env
```

를 등록하여 API 키가 GitHub에 올라가지 않도록 했다.

실제 `git status`에서도 `.env`가 나타나지 않는 것을 확인했다.

---

# 18. API 오류 해결 경험

Kakao Local API를 처음 테스트했을 때 다음과 같은 403 오류가 발생했다.

```
App(여행 추천 프로그램) disabled OPEN_MAP_AND_LOCAL service.
```

원인을 확인한 결과 Kakao 개발자 페이지에서 해당 서비스가 활성화되지 않은 상태였다.

Kakao 개발자 페이지에서 **Open Map & Local 서비스 활성화** 후 다시 테스트했고:

```
Kakao API 연결 성공!
검색 결과: 5곳
```

으로 정상 작동하는 것을 확인했다.

이 과정을 통해 API 오류가 발생했을 때 단순히 코드만 확인하는 것이 아니라:

```
API 키
→ 인증 방식
→ 서비스 활성화
→ 권한
→ 요청 URL
→ 요청 파라미터
→ 실제 응답 내용
```

순서로 원인을 확인해야 한다는 것을 학습했다.

---

# 19. 테스트 결과

## Gemini API

```
Gemini API 연결 성공!
```

실제 API 연결을 확인했다.

## Kakao API

```
Kakao API 연결 성공!
검색 결과: 5곳
```

실제 API 연결을 확인했다.

## 정상 프로그램 실행

```
추천 지역: ['진주', '안동', '경주']

[진주]
5곳 검색

[안동]
5곳 검색

[경주]
5곳 검색

리포트 생성 완료
```

## 날짜 검증

잘못된 날짜:

```
20261003
```

입력 시 오류 메시지가 출력되는 것을 확인했다.

## 캐싱

동일 날짜 재실행 시:

```
기존 결과 데이터를 발견했습니다.
Gemini 및 Kakao API 호출을 건너뜁니다.
```

가 출력되는 것을 확인했다.

---

# 20. GitHub 관리

GitHub 저장소와 로컬 프로젝트를 연결하여 작업 과정에서 변경사항을 커밋하고 push했다.

주요 커밋:

```
49eabf4 프로젝트 초기 설정
6db2994 CLI 날짜 입력 및 검증 기능 구현
8713508 복수 지역 추천 및 결과 캐싱 기능 구현
8352063 README 작성 및 프로젝트 사용법 정리
e2bcbcd Gemini 여행 추천 기능 보완
```

최종 수정사항도 GitHub에 push했다.

최종 Git 상태:

```
On branch main
Your branch is up to date with 'origin/main'.
```

현재 `project_structure.txt`만 아직 Git에 추가하지 않은 상태이며, 필수 파일이 아니므로 커밋하지 않고 유지했다.

---

# 21. 최종 구현 기능

### 필수 기능

- [x]  `argparse` CLI
- [x]  `-date` 옵션
- [x]  날짜 형식 검증
- [x]  Gemini API 연동
- [x]  JSON 응답 생성
- [x]  JSON 필수 키 검증
- [x]  JSON 타입 검증
- [x]  JSON 파싱 오류 처리
- [x]  JSON 파싱 실패 1회 재시도
- [x]  복수 지역 추천
- [x]  Kakao Local API 연동
- [x]  지역별 최대 5개 맛집
- [x]  맛집 API 오류 처리
- [x]  0건 검색 처리
- [x]  오류 `errors` 배열 저장
- [x]  Gemini 최종 리포트 생성
- [x]  1일 일정 제안
- [x]  JSON 결과 저장
- [x]  Markdown 결과 저장
- [x]  `.env` API 키 관리
- [x]  `.gitignore` API 키 보호

### 보너스 기능

- [x]  복수 지역 추천
- [x]  결과 캐싱

---

# 22. 스크린샷 자료

제출 자료에는 다음 스크린샷을 추천한다.

### 스크린샷 1 — 정상 실행

```powershell
py travel_planner.py --date "2026-08-14"
```

![image.png](image%201.png)

```
추천 지역: ['진주', '안동', '경주']

[진주]
5곳 검색

[안동]
5곳 검색

[경주]
5곳 검색

리포트 생성 완료

원본 데이터: ...
여행 리포트: ...
```

**증명:** CLI + Gemini + Kakao + 최종 리포트 전체 흐름

---

### 스크린샷 2 — 날짜 오류

```python
py travel_planner.py --date "20261003"
```

다음 오류가 보이도록 한다.

```
usage: travel_planner.py [-h] --date DATE
travel_planner.py: error: argument --date: 날짜 형식은 YYYY-MM-DD 입니다.
```

**증명:** 날짜 형식 검증

![스크린샷 2026-08-13 211857.png](%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7_2026-08-13_211857.png)

---

### 스크린샷 3 — JSON 결과

`results/2026-10-03_travel_data.json`을 VS Code에서 연다.

다음 내용이 보이도록 한다.

```
date
recommended_cities
weather
events
reason
restaurants_by_city
errors
```

**증명:** JSON 결과, 복수 지역, 맛집 검색 결과, 오류 목록

![image.png](image%202.png)

---

### 스크린샷 4 — Markdown 리포트

`results/2026-10-03_travel_plan.md`를 연다.

다음 항목이 보이도록 한다.

```
추천 지역
추천 이유
날씨 요약
행사/축제
맛집 추천
1일 일정 제안
오류 요약
```

**증명:** 최종 여행 리포트

![image.png](image%203.png)

---

### 스크린샷 5 — 캐싱

같은 날짜를 다시 실행한다.

```python
py travel_planner.py --date "2026-10-03"
```

다음 문구가 보이도록 한다.

```
기존 결과 데이터를 발견했습니다.
Gemini 및 Kakao API 호출을 건너뜁니다.
```

**증명:** 캐싱 보너스 기능

![스크린샷 2026-08-13 211459.png](%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7_2026-08-13_211459.png)

---

### 스크린샷 6 — API 키 보안

`.gitignore`를 열어 다음 내용이 보이도록 한다.

```
venv/
.env
__pycache__/
*.pyc
```

**주의:** `.env` 파일 자체는 캡처하지 않는다.

**증명:** API 키 보안 관리

![image.png](image%204.png)

---

# 23. 최종 결과

이번 프로젝트를 통해 Python CLI 프로그램에서 여러 외부 API를 연결하고, API 응답을 JSON으로 구조화하여 다른 API의 입력으로 사용하는 전체 흐름을 구현했다.

특히 다음과 같은 기능을 실제 실행으로 검증했다.

```
사용자 날짜 입력
       ↓
Gemini 복수 지역 추천
       ↓
JSON 파싱 및 검증
       ↓
Kakao 지역별 맛집 검색
       ↓
오류 발생 시 errors에 기록
       ↓
Gemini 최종 리포트 생성
       ↓
JSON + Markdown 저장
       ↓
동일 날짜 재실행 시 캐시 사용
```

또한 API 키를 `.env`와 `.gitignore`를 통해 관리하고, Git을 이용해 프로젝트 변경사항을 GitHub에 지속적으로 커밋하고 push하여 버전 관리했다.

**필수 기능과 두 가지 보너스 기능을 모두 구현하고 실제 실행 테스트까지 완료했다.**