import requests
import logging
from .fetcher import Assignment


logger = logging.getLogger(__name__)


def send_magister_data(base_url: str, endpoint: str, bearer_token: str, json):
    """ Fetch URL from Magister using bearer token and return the response. """
    headers = {
        "Authorization": bearer_token,
        "content-type": "application/json"
    }

    url = f"https://{base_url}/{endpoint}"
    logger.debug(f"Fetching URL: {url}")

    requests.put(url, headers=headers, json=json)


def change_status_homework(base_url: str, user_id: int, homework: Assignment, user_token: str, done=True):
    end_point = f"api/personen/{user_id}/afspraken/{homework.id}"
    homework.lesson.raw["Afgerond"] = done
    payload = homework.lesson.raw
    print(payload)
    send_magister_data(base_url, end_point, user_token, json=payload)
