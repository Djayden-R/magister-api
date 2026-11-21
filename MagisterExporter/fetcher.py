import requests
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def get_calendar(base_url: str, user_id: str, bearer_token: str, days_to_fetch: int):
    headers = {
        "Authorization": bearer_token,
        "content-type": "application/json"
    }

    current_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days_to_fetch)).strftime("%Y-%m-%d")

    url = f"https://{base_url}/api/personen/{user_id}/afspraken?status=1&tot={end_date}&van={current_date}"

    r = requests.get(url, headers=headers)

    if r.ok:
        calendar = json.loads(r.text)
        return calendar
    else:
        return None


def get_grades():
    ...


def get_home_work():
    ...


def get_exams():
    ...
