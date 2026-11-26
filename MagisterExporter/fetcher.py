import requests
import json
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Assignment:
    subjects: list[str]
    content: str
    done: bool


@dataclass
class Lesson:
    id: int  # A unique identifier for the lesson
    start: datetime
    end: datetime
    start_period: int  # Starting period of lesson, so 1 (first period), 2 (second period) etc.
    end_period: int  # Same thing, but end period
    description: str  # The description of the lesson provided by the teachers (may be homework, exams or other information)
    info_type: int  # Type of information provided by the teachers (1 = homework, 2 = proefwerk, 3 = tentamen, 4 = S.O.)
    homework_done: bool  # Whether homework has been marked as done in Magister
    whole_day: bool  # Whether it is a whole day event
    name: str  # String containing subject, teacher, and class info, eg: na - nagl - a6.na1 (subject - teacher - class)
    subjects: list[str]  # List of subjects for the lesson
    classrooms: list[str]  # List of classrooms for the lesson
    teachers: list[str]  # List of teachers for the lesson

    @classmethod
    def from_api_input(cls, api_input: dict[str, Any]):
        """ Turn raw API information into a Lesson class. Returns None if the input is invalid (like missing information or not a Magister lesson). """
        raw_id: int | None = api_input.get("Id")
        raw_start: str | None = api_input.get("Start")
        raw_end: str | None = api_input.get("Einde")
        raw_start_period: int | None = api_input.get("LesuurVan")
        raw_end_period: int | None = api_input.get("LesuurTotMet")
        raw_description: str | None = api_input.get("Inhoud")
        raw_info_type: int | None = api_input.get("InfoType")
        raw_homework_done: bool | None = api_input.get("Afgerond")
        raw_whole_day: bool | None = api_input.get("DuurtHeleDag")
        raw_name: str | None = api_input.get("Omschrijving")
        raw_subjects: list[dict[str, str | int]] | None = api_input.get("Vakken")
        raw_classrooms: list[dict[str, str | int]] | None = api_input.get("Lokalen")
        raw_teachers: list[dict[str, str | int]] | None = api_input.get("Docenten")

        if (
            not isinstance(raw_id, int)
            or not isinstance(raw_start, str)
            or not isinstance(raw_end, str)
            or not isinstance(raw_start_period, int)
            or not isinstance(raw_end_period, int)
            or not isinstance(raw_description, str)
            or not isinstance(raw_info_type, int)
            or not isinstance(raw_homework_done, bool)
            or not isinstance(raw_whole_day, bool)
            or not isinstance(raw_name, str)
            or not isinstance(raw_subjects, list)
            or not isinstance(raw_classrooms, list)
            or not isinstance(raw_teachers, list)
        ):
            return None

        return cls(
            raw_id,
            datetime.fromisoformat(raw_start),
            datetime.fromisoformat(raw_end),
            raw_start_period,
            raw_end_period,
            raw_description,
            raw_info_type,
            raw_homework_done,
            raw_whole_day,
            raw_name,
            [subject.get("Name", None) for subject in raw_subjects],  # pyright: ignore[reportArgumentType]
            [classroom.get("Name", None) for classroom in raw_classrooms],  # pyright: ignore[reportArgumentType]
            [teacher.get("Name", None) for teacher in raw_teachers]  # pyright: ignore[reportArgumentType]
        )

def fetch_magister_url(base_url: str, endpoint: str, bearer_token: str) -> requests.Response:
    headers = {
        "Authorization": bearer_token,
        "content-type": "application/json"
    }

    url = f"https://{base_url}/{endpoint}"

    r = requests.get(url, headers=headers)

    return r

    if r.ok:
        data = json.loads(r.text)
        return data
    else:
        return None


def get_calendar(base_url: str, user_id: str, bearer_token: str, days_to_fetch: int) -> list[Lesson]:
    current_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days_to_fetch)).strftime("%Y-%m-%d")

    endpoint = f"api/personen/{user_id}/afspraken?status=1&tot={end_date}&van={current_date}"

    calendar_raw = fetch_magister_data(base_url, endpoint, bearer_token)

    calendar: list[Lesson] = []
    if calendar_raw:
        lessons_raw = calendar_raw.get("Items", None)
        if lessons_raw:
            for lesson_raw in lessons_raw:
                lesson = Lesson.from_api_input(lesson_raw)
                if lesson:
                    calendar.append(lesson)

    return calendar


def get_grades(base_url: str, user_id: str, bearer_token: str):
    endpoint = f"api/personen/{user_id}/cijfers/laatste?top=9999&skip=0"

    grades = fetch_magister_url(base_url, endpoint, bearer_token)

    return grades


def get_homework(base_url: str, user_id: str, bearer_token: str, days_to_fetch: int) -> list[Assignment]:
    "Fetch all homework assignments from students calendar and return them as a list of Assignment classes"
    calendar: list[Lesson] = get_calendar(base_url, user_id, bearer_token, days_to_fetch)
    homework: list[Assignment] = []

    if calendar:
        for lesson in calendar:
            if lesson.info_type == 1:
                assignment: Assignment = Assignment(lesson.subjects, lesson.description, lesson.homework_done)
                homework.append(assignment)
    return homework


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


def get_student_info(base_url: str, bearer_token: str):
    endpoint = "/api/account"

    account_info = fetch_magister_url(base_url, endpoint, bearer_token)

    if account_info:
        student_info = account_info.get("Persoon", None)
        return student_info
    return None
