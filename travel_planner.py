import argparse
import json
import os

from datetime import datetime

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
# [1/3] Gemini 여행 지역 추천
# ----------------------------------------

print()
print("[1/3] 여행 지역 추천 생성 중 (Gemini)...")


try:
    recommendation = get_travel_recommendation(args.date)

    print(
        f"  - 추천 지역: "
        f"{recommendation['recommended_city']}"
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
print("[2/3] 맛집 검색 중 (Kakao Local)...")


try:
    restaurants = search_restaurants(
        recommendation["recommended_city"],
        limit=5
    )

    if restaurants:
        print(
            f"  - 맛집 {len(restaurants)}곳 검색 완료"
        )

        for i, restaurant in enumerate(
            restaurants,
            start=1
        ):
            print(
                f"  {i}. {restaurant['name']} "
                f"- {restaurant['address']}"
            )

    else:
        print("  - 검색 결과 0건")

except Exception as e:
    print(f"  - 맛집 검색 오류: {e}")
    print("  - 맛집 섹션은 '데이터 없음'으로 처리합니다.")

    errors.append({
        "step": "place_search",
        "type": "API_ERROR",
        "message": str(e)
    })

    restaurants = []


# ----------------------------------------
# [3/3] 최종 여행 리포트 생성
# ----------------------------------------

print()
print("[3/3] 최종 여행 리포트 생성 중 (Gemini)...")


try:
    report = generate_report(
        recommendation,
        restaurants,
        errors
    )

    print("  - 리포트 생성 완료")

except Exception as e:
    print(f"  - 리포트 생성 오류: {e}")

    errors.append({
        "step": "report_generation",
        "type": "API_ERROR",
        "message": str(e)
    })

    report = None


# ----------------------------------------
# 결과 저장
# ----------------------------------------

os.makedirs("results", exist_ok=True)


json_path = os.path.join(
    "results",
    f"{args.date}_travel_data.json"
)

md_path = os.path.join(
    "results",
    f"{args.date}_travel_plan.md"
)


result_data = {
    "date": args.date,
    "recommendation": recommendation,
    "restaurants": restaurants,
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
    print("여행 리포트가 생성되지 않았습니다.")
    print(f"원본 데이터: {json_path}")