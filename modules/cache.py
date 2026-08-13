import json
import os


def get_cache_path(date):
    os.makedirs("results", exist_ok=True)

    return os.path.join(
        "results",
        f"{date}_travel_data.json"
    )


def load_cache(date):
    cache_path = get_cache_path(date)

    if not os.path.exists(cache_path):
        return None

    try:
        with open(
            cache_path,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except (json.JSONDecodeError, OSError):
        return None


def save_cache(date, data):
    cache_path = get_cache_path(date)

    with open(
        cache_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    return cache_path