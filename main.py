import asyncio
from playwright.async_api import Playwright, async_playwright, Page
from dotenv import load_dotenv
import os

load_dotenv()


async def fill_username(page: Page, username: str):
    await page.locator("#username").fill(username)
    await page.locator("#username_submit").click()
    print("Submitted username")


async def fetch_magister_token(playwright: Playwright, base_url: str, name: str, username: str, password: str, headless: bool = True):
    print("Starting Playwright")
    browser = await playwright.chromium.launch(headless=headless)
    page = await browser.new_page()

    print(f"Finding {name}'s token")
    await page.goto(f"https://{base_url}/oidc/redirect_callback.html")

    await fill_username(page, username)

    await page.wait_for_url("https://login.microsoftonline.com/**")

    password_field = page.locator("[name='passwd']")
    await password_field.wait_for(state='visible')
    await page.wait_for_load_state("networkidle")
    await password_field.fill(password)
    await page.locator("#idSIButton9").click()
    print("Submitted password")

    await page.wait_for_load_state("load")

    # Check if passwordError or KmsiCheckboxField is visible
    kmsi_checkbox = page.locator("#KmsiCheckboxField")
    password_error = page.locator("#passwordError")

    checks = [
        asyncio.create_task(kmsi_checkbox.wait_for(state='visible', timeout=30000)),
        asyncio.create_task(password_error.wait_for(state='visible', timeout=30000))
    ]

    finished, pending = await asyncio.wait(checks, timeout=30, return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()

    if finished:
        first_task = finished.pop()
        # If the kmsi checkbox is visible, the password is correct
        if first_task == checks[0]:
            print("Password is correct")

        # If passwordError is visible, the password is incorrect
        elif first_task == checks[1]:
            print(first_task)
            if await password_error.is_visible():
                error_text = await password_error.inner_text()
                if error_text == "Please enter your password.":
                    pass
                raise ValueError("Password is incorrect")
    else:
        raise TimeoutError("Timeout after 30 seconds while checking if password is correct")

    await page.locator("#idSIButton9").click()
    print("Continued past Microsoft prompt")

    # Use a glob url pattern
    async with page.expect_response("**/api/leerlingen/**", timeout=30000) as response_info:
        print("Found network leerling request")
        response = await response_info.value
        body = response
        headers = await response.request.all_headers()

    url = response.url
    token = headers.get("authorization", None)
    user_id = body

    print(f"URL: {url}\nToken: {token},\nUser: {user_id}")


async def main():
    BASE_URL = os.environ["BASE_URL"]
    NAME = os.environ["NAME"]
    USERNAME = os.environ["USERNAME"]
    PASSWORD = os.environ["PASSWORD"]
    async with async_playwright() as playwright:
        result = await fetch_magister_token(playwright, BASE_URL, NAME, USERNAME, PASSWORD, headless=False)
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
