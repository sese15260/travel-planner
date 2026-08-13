import argparse
import json
import os

from datetime import datetime

from modules.cache import load_cache, save_cache
from modules.llm import get_travel_recommendation
from modules.places import search_restaurants
from modules.report import generate_report


def validate_date(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return date_string
    except ValueError:
        raise argparse.ArgumentTypeError(
            "날짜 형식은 YYYY-MM-DD 입니다."
        )


parser = argparse.ArgumentParser(
    description="국내 여행 추천 프로그램"
)

parser.add_argument(
    "--date",
    required=True,
    type=validate_date,
    help="여행 날짜 (YYYY-MM-DD)"
)

args = parser.parse_args()


print("=" * 40)
print("국내 여행 추천 프로그램")
print("=" * 40)
print(f"여행 날짜 : {args.date}")


# 오류 목록
errors = []


# ----------------------------------------
# 기존 캐시 확인
# ----------------------------------------

cached_data = load_cache(args.date)


if cached_data:
    print()
    print("기존 결과 데이터를 발견했습니다.")
    print("Gemini 및 Kakao API 호출을 건너뜁니다.")

    recommendation = cached_data.get(
        "recommendation",
        {}
    )

    restaurants_by_city = cached_data.get(
        "restaurants_by_city",
        {}
    )

    errors = cached_data.get(
        "errors",
        []
    )

else:

    # ----------------------------------------
    # [1/3] Gemini 여행 지역 추천
    # ----------------------------------------

    print()
    print("[1/3] 여행 지역 추천 생성 중 (Gemini)...")

    try:
        recommendation = get_travel_recommendation(
            args.date
        )

        print(
            f"  - 추천 지역: "
            f"{recommendation['recommended_cities']}"
        )

        print(
            f"  - 날씨: "
            f"{recommendation['weather']}"
        )

        print(
            f"  - 행사/축제: "
            f"{len(recommendation['events'])}개"
        )

    except Exception as e:

        print(f"  - 오류: {e}")

        errors.append({
            "step": "travel_recommendation",
            "type": "API_ERROR",
            "message": str(e)
        })

        print("프로그램을 종료합니다.")
        exit(1)


    # ----------------------------------------
    # [2/3] Kakao 맛집 검색
    # ----------------------------------------

    print()
    print(
        "[2/3] 지역별 맛집 검색 중 "
        "(Kakao Local)..."
    )

    restaurants_by_city = {}


    for city in recommendation["recommended_cities"]:

        print()
        print(f"  [{city}] 맛집 검색 중...")

        try:
            restaurants = search_restaurants(
                city,
                limit=5
            )

            restaurants_by_city[city] = restaurants

            if restaurants:

                print(
                    f"  - {city}: "
                    f"{len(restaurants)}곳 검색 완료"
                )

                for i, restaurant in enumerate(
                    restaurants,
                    start=1
                ):
                    print(
                        f"    {i}. "
                        f"{restaurant['name']}"
                    )

            else:

                print(
                    f"  - {city}: "
                    f"검색 결과 0건"
                )

                errors.append({
                    "step": "place_search",
                    "type": "EMPTY_RESULT",
                    "city": city,
                    "message": (
                        f"{city} 맛집 검색 결과 0건"
                    )
                })

        except Exception as e:

            print(
                f"  - {city}: "
                f"맛집 검색 오류: {e}"
            )

            print(
                "  - 해당 지역은 "
                "'데이터 없음'으로 처리합니다."
            )

            errors.append({
                "step": "place_search",
                "type": "API_ERROR",
                "city": city,
                "message": str(e)
            })

            restaurants_by_city[city] = []


    # ----------------------------------------
    # 원본 데이터 저장
    # ----------------------------------------

    result_data = {
        "date": args.date,
        "recommendation": recommendation,
        "restaurants_by_city": restaurants_by_city,
        "errors": errors
    }

    save_cache(
        args.date,
        result_data
    )


# ----------------------------------------
# [3/3] 최종 여행 리포트 생성
# ----------------------------------------

print()
print(
    "[3/3] 최종 여행 리포트 생성 중 "
    "(Gemini)..."
)


try:

    report = generate_report(
        recommendation,
        restaurants_by_city,
        errors
    )

    print("  - 리포트 생성 완료")

except Exception as e:

    print(
        f"  - 리포트 생성 오류: {e}"
    )

    errors.append({
        "step": "report_generation",
        "type": "API_ERROR",
        "message": str(e)
    })

    report = None


# ----------------------------------------
# 결과 저장
# ----------------------------------------

os.makedirs(
    "results",
    exist_ok=True
)


json_path = os.path.join(
    "results",
    f"{args.date}_travel_data.json"
)


md_path = os.path.join(
    "results",
    f"{args.date}_travel_plan.md"
)


# 최신 오류 정보까지 반영
result_data = {
    "date": args.date,
    "recommendation": recommendation,
    "restaurants_by_city": restaurants_by_city,
    "errors": errors
}


with open(
    json_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        result_data,
        f,
        ensure_ascii=False,
        indent=2
    )


if report:

    with open(
        md_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)

    print()
    print("=" * 40)
    print("완료!")
    print(f"원본 데이터: {json_path}")
    print(f"여행 리포트: {md_path}")
    print("=" * 40)

else:

    print()
    print(
        "여행 리포트가 생성되지 않았습니다."
    )

    print(
        f"원본 데이터: {json_path}"
    )