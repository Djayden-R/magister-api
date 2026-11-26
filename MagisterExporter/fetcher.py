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


@dataclass
class Student:
    id: int
    first_name: str
    last_name: str
    birth_date: datetime
    official_first_names: str
    initials: str

    @classmethod
    def from_api_input(cls, api_input: dict[str, Any]):
        """ Turn raw API information into a Student class. Returns None if the input is invalid (like missing information or not a Magister student). """
        raw_id: int | None = api_input.get("Id")
        raw_first_name: str | None = api_input.get("Roepnaam")
        raw_last_name: str | None = api_input.get("Achternaam")
        raw_birth_date: str | None = api_input.get("Geboortedatum")
        raw_official_first_names: str | None = api_input.get("OfficieleVoornamen")
        raw_initials: str | None = api_input.get("Voorletters")

        if (
            not isinstance(raw_id, int)
            or not isinstance(raw_first_name, str)
            or not isinstance(raw_last_name, str)
            or not isinstance(raw_birth_date, str)
            or not isinstance(raw_official_first_names, str)
            or not isinstance(raw_initials, str)
        ):
            return None

        return cls(
            raw_id,
            raw_first_name,
            raw_last_name,
            datetime.fromisoformat(raw_birth_date),
            raw_official_first_names,
            raw_initials
        )


@dataclass
class Grade:
    grade_id: int
    description: str
    entered_on: datetime
    subject_code: str
    subject_description: str
    value: str
    weight_factor: float
    is_sufficient: bool
    counts_towards_average: bool
    must_be_made_up: bool
    has_exemption: bool
    achieved_on: datetime | None

    @classmethod
    def from_api_input(cls, api_input: dict[str, Any]):
        """ Turn raw API information into a Grade class. Returns None if the input is invalid (like missing information or not a Magister grade). """
        raw_grade_id: int | None = api_input.get("kolomId")
        raw_description: str | None = api_input.get("omschrijving")
        raw_entered_on: str | None = api_input.get("ingevoerdOp")
        raw_subject_code: str | None = api_input.get("vak", {}).get("code")
        raw_subject_description: str | None = api_input.get("vak", {}).get("omschrijving")
        raw_value: str | None = api_input.get("waarde")
        raw_weight_factor: float | None = api_input.get("weegfactor")
        raw_is_sufficient: bool | None = api_input.get("isVoldoende")
        raw_counts_towards_average: bool | None = api_input.get("teltMee")
        raw_must_be_made_up: bool | None = api_input.get("moetInhalen")
        raw_has_exemption: bool | None = api_input.get("heeftVrijstelling")
        raw_achieved_on: str | None = api_input.get("behaaldOp")

        if (
            not isinstance(raw_grade_id, int)
            or not isinstance(raw_description, str)
            or not isinstance(raw_entered_on, str)
            or not isinstance(raw_subject_code, str)
            or not isinstance(raw_subject_description, str)
            or not isinstance(raw_value, str)
            or not isinstance(raw_weight_factor, float)
            or not isinstance(raw_is_sufficient, bool)
            or not isinstance(raw_counts_towards_average, bool)
            or not isinstance(raw_must_be_made_up, bool)
            or not isinstance(raw_has_exemption, bool)
            or not isinstance(raw_achieved_on, str)
        ):
            return None

        return cls(
            raw_grade_id,
            raw_description,
            datetime.fromisoformat(raw_entered_on),
            raw_subject_code,
            raw_subject_description,
            raw_value,
            raw_weight_factor,
            raw_is_sufficient,
            raw_counts_towards_average,
            raw_must_be_made_up,
            raw_has_exemption,
            datetime.fromisoformat(raw_achieved_on) if raw_achieved_on is not None else None
        )


def fetch_magister_url(base_url: str, endpoint: str, bearer_token: str) -> requests.Response:
    """ Fetch URL from Magister using bearer token and return the response. """
    headers = {
        "Authorization": bearer_token,
        "content-type": "application/json"
    }

    url = f"https://{base_url}/{endpoint}"
    logger.debug(f"Fetching URL: {url}")

    r = requests.get(url, headers=headers)

    return r


def fetch_magister_data(base_url: str, endpoint: str, bearer_token: str) -> dict[str, Any] | None:
    """ Fetch data from Magister using bearer token and return the JSON response as a dictionary. """
    r = fetch_magister_url(base_url, endpoint, bearer_token)

    if r.ok:
        data = json.loads(r.text)
        return data
    else:
        return None


def get_calendar(base_url: str, user_id: str, bearer_token: str, days_to_fetch: int) -> list[Lesson]:
    """ Fetch the calendar for user and return it as a list of Lesson classes. """
    # Generate timestamps for api endpoint
    current_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days_to_fetch)).strftime("%Y-%m-%d")

    # Generate endpoint using timestamps and user_id
    endpoint = f"api/personen/{user_id}/afspraken?status=1&tot={end_date}&van={current_date}"

    calendar_raw = fetch_magister_data(base_url, endpoint, bearer_token)

    # Turn raw calendar data into a list of Lesson classes
    calendar: list[Lesson] = []
    if calendar_raw:
        lessons_raw = calendar_raw.get("Items", None)
        if lessons_raw:
            for lesson_raw in lessons_raw:
                lesson = Lesson.from_api_input(lesson_raw)
                if lesson:
                    calendar.append(lesson)

    return calendar


def get_grades(base_url: str, user_id: str, bearer_token: str) -> list[Grade]:
    """ Fetch all grades for user and return them as a list of Grade classes. """
    # Generate endpoint using user_id
    endpoint = f"api/personen/{user_id}/cijfers/laatste?top=9999&skip=0"

    raw_grades = fetch_magister_data(base_url, endpoint, bearer_token)

    grades: list[Grade] = []
    if raw_grades:
        for grade_raw in raw_grades.get("Items", []):
            grade = Grade.from_api_input(grade_raw)
            if grade:
                grades.append(grade)

    return grades


def get_homework(base_url: str, user_id: str, bearer_token: str, days_to_fetch: int) -> list[Assignment]:
    """Fetch all homework assignments from students calendar and return them as a list of Assignment classes"""
    calendar: list[Lesson] = get_calendar(base_url, user_id, bearer_token, days_to_fetch)
    homework: list[Assignment] = []

    if calendar:
        for lesson in calendar:
            # If lesson.info_type is 1, it is a homework assignment
            if lesson.info_type == 1:
                assignment: Assignment = Assignment(lesson.subjects, lesson.description, lesson.homework_done)
                homework.append(assignment)
    return homework


def get_exams(base_url: str, user_id: str, bearer_token: str, days_to_fetch: int):
    """ Fetch all tests and exams from students calendar and return them as a list of Lesson classes. lesson.info_type is 2 for proefwerk, 3 for tentamen and 4 for S.O. """
    calendar: list[Lesson] = get_calendar(base_url, user_id, bearer_token, days_to_fetch)

    exams: list[Lesson] = []

    if calendar:
        for lesson in calendar:
            if lesson.info_type in [2, 3, 4]:
                exams.append(lesson)

    return exams


def get_student_info(base_url: str, bearer_token: str) -> Student | None:
    endpoint = "/api/account"

    account_info = fetch_magister_data(base_url, endpoint, bearer_token)

    if account_info:
        student_info = account_info.get("Persoon", None)
        return Student.from_api_input(student_info) if student_info else None
    return None


def get_profile_picture(base_url: str, user_id: str, bearer_token: str) -> requests.Response:
    endpoint = f"/api/leerlingen/{user_id}/foto?redirect_type=body"

    r = fetch_magister_url(base_url, endpoint, bearer_token)

    return r
