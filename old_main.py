import requests
import json
import logging
from fetch_magister import fetch_magister_calendar, fetch_magister_token
from pathlib import Path
from playwright.async_api import async_playwright
import asyncio
from ics_manager import calendar_to_ics, save_ics_file, read_ics_file
import http.server
from http.server import SimpleHTTPRequestHandler
import socket
import threading


def get_user_info(username: str):
    ...

    return token, user_id, session_id


async def main():
    token, user_id = get_user_info(username)

    calendar = None

    if token and user_id:
        print("Token found in tokens.json, testing it...")
        calendar = fetch_magister_calendar(base_url, user_id, token, days_to_fetch)

    if not calendar:
        print("No valid token found, fetching new one...")


    if not (token and user_id):
        print(f"Failed to fetch token and user id for {username}")
        continue

    if not calendar:
        print("Unable to fetch magister calendar")
        continue

    ics_calendar = calendar_to_ics(calendar, ignore_lessons)
