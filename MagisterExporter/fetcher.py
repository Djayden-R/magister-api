import requests
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def fetch_magister_url(base_url: str, endpoint: str, bearer_token: str):
    headers = {
        "Authorization": bearer_token,
        "content-type": "application/json"
    }

    url = f"https://{base_url}/{endpoint}"

    r = requests.get(url, headers=headers)

    if r.ok:
        data = json.loads(r.text)
        return data
    else:
        return None


def get_calendar(base_url: str, user_id: str, bearer_token: str, days_to_fetch: int):
    current_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days_to_fetch)).strftime("%Y-%m-%d")

    endpoint = f"api/personen/{user_id}/afspraken?status=1&tot={end_date}&van={current_date}"

    calendar = fetch_magister_url(base_url, endpoint, bearer_token)

    return calendar


def get_grades(base_url: str, user_id: str, bearer_token: str):
    endpoint = f"api/personen/{user_id}/cijfers/laatste?top=9999&skip=0"

    grades = fetch_magister_url(base_url, endpoint, bearer_token)

    return grades


def get_home_work(base_url: str, user_id: str, bearer_token: str, days_to_fetch: int):
    calendar = get_calendar(base_url, user_id, bearer_token, days_to_fetch)
    all_homework = []

    if calendar:
        lessons = calendar.get("Items", None)
        for lesson in lessons:
            lesson_type = lesson.get("InfoType", None)
            if lesson_type == 1:
                homework = lesson.get("Inhoud", None)
                homework_done = lesson.get("Afgerond", None)
                subjects = lesson.get("Vakken", None)

                all_homework.append((homework, homework_done, subjects))
    return all_homework


def get_exams(base_url: str, user_id: str, bearer_token: str, days_to_fetch: int):
    calendar = get_calendar(base_url, user_id, bearer_token, days_to_fetch)

    tentamens = []
    proefwerken = []
    schriftelijke_overhoringen = []

    if calendar:
        lessons = calendar.get("Items", None)
        for lesson in lessons:
            lesson_type = lesson.get("InfoType", None)
            if lesson_type == 4:
                schriftelijke_overhoringen.append(lesson)
            elif lesson_type == 3:
                tentamens.append(lesson)
            elif lesson_type == 2:
                proefwerken.append(lesson)
    return tentamens, proefwerken, schriftelijke_overhoringen
