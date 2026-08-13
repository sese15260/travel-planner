import argparse
from datetime import datetime

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