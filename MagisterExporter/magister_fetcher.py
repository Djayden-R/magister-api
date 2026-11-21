import asyncio
from playwright.async_api import Playwright, async_playwright, Page
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

load_dotenv()


async def fill_username(page: Page, username: str):
    await page.locator("#username").fill(username)
    await page.locator("#username_submit").click()
    logger.info("Submitted username")


async def fill_password(page: Page, password: str, retries: int = 3):
    """DOCSTRING HERE"""
    # Definition of all relevant page elements
    password_field = page.locator("[name='passwd']")
    kmsi_checkbox = page.locator("#KmsiCheckboxField")
    password_error = page.locator("#passwordError")
    submit_button = page.locator("#idSIButton9")

    # Wait until password is visible and page is done loading
    # If you don't wait for networkidle, the password is often not (fully) filled in
    await password_field.wait_for(state='visible')
    await page.wait_for_load_state("networkidle")

    # Fill in password and continue
    await password_field.fill(password)
    await submit_button.click()
    logger.debug("Submitted password")

    # Wait until either the error shows or the page redirects to kmsi prompt
    await page.wait_for_load_state("load")

    # Check for both a password error and the kmsi (keep me signed in) prompt
    checks = [
        asyncio.create_task(kmsi_checkbox.wait_for(state='visible', timeout=0)),
        asyncio.create_task(password_error.wait_for(state='visible', timeout=0))
    ]

    finished, pending = await asyncio.wait(checks, timeout=30, return_when=asyncio.FIRST_COMPLETED)

    # Stop checking the last task
    for task in pending:
        task.cancel()

    # Check which element was found on the page
    if finished:
        # The task that finished first is the task that
        finished_task = finished.pop()
        is_on_kmsi_page = finished_task == checks[0]
        password_error_visible = finished_task == checks[1]

        # Password is correct
        if is_on_kmsi_page:
            logger.debug("Password is correct")

        # Password is incorrect
        elif password_error_visible:
            error_text = await password_error.inner_text()
            if error_text == "Please enter your password.":
                pass
            elif ...:
                ...
            raise ValueError("Password is incorrect")
    else:
        raise TimeoutError("Timeout after 30 seconds while checking if password is correct")


async def fetch_magister_token(playwright: Playwright, base_url: str, name: str, username: str, password: str, headless: bool = True):
    logging.info("Starting Playwright...")
    browser = await playwright.chromium.launch(headless=headless)
    page = await browser.new_page()

    logging.info("Going to Magister Login page")
    await page.goto(f"https://{base_url}/oidc/redirect_callback.html")

    await fill_username(page, username)

    await page.wait_for_url("https://login.microsoftonline.com/**")
    logging.debug("Redirected to Microsoft login portal")

    await fill_password(page, password)

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
