import asyncio
from playwright.async_api import async_playwright, Page
import logging
from num2words import num2words

logger = logging.getLogger(__name__)

NO_PASSWORD_ERRORS = ["Please enter your password", "Voer uw wachtwoord in"]
WRONG_PASSWORD_ERRORS = ["Uw account of wachtwoord is onjuist", "Your account or password is incorrect"]


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

    for i in range(1, retries + 1):
        # Start with cleared password field
        await password_field.clear()

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

        # Stop checking for the last element
        for task in pending:
            task.cancel()

        # Check which element was found on the page
        if finished:
            # The task that finished first is the element that was found
            finished_task = finished.pop()
            is_on_kmsi_page = finished_task == checks[0]
            password_error_visible = finished_task == checks[1]

            # Password is correct
            if is_on_kmsi_page:
                logger.debug("Password is correct")
                return True

            # Password is incorrect
            elif password_error_visible:
                # Get error text from page
                error_text = await password_error.inner_text()
                try_str = num2words(i, to="ordinal").capitalize()

                # Log type of error
                if any(keyword in error_text for keyword in NO_PASSWORD_ERRORS):
                    logger.debug(f"{try_str} try has failed; no password was entered")
                elif any(keyword in error_text for keyword in WRONG_PASSWORD_ERRORS):
                    logger.debug(f"{try_str} try has failed; password is wrong or wasn't entered correctly")
                else:
                    logger.warning(f"Unknown error occured when filling in password: {error_text}")
        else:
            logger.warning("Timeout after 30 seconds while checking if password is correct")
    return False


async def fetch_magister_token(base_url: str, username: str, password: str, headless: bool = True):
    """..."""
    async with async_playwright() as playwright:
        # Start browser
        logging.info("Starting Playwright...")
        browser = await playwright.chromium.launch(headless=headless)
        page = await browser.new_page()

        # Go to Magister login page
        logging.info("Going to Magister Login page")
        await page.goto(f"https://{base_url}/oidc/redirect_callback.html")

        # Fill in credentials
        await fill_username(page, username)

        await page.wait_for_url("https://login.microsoftonline.com/**")
        logging.debug("Redirected to Microsoft login portal")

        if not await fill_password(page, password):
            raise ValueError("Unable to fill password")

        # Click "Yes" on keep-me-signed-in prompt
        await page.locator("#idSIButton9").click()

        # Wait until student request is found
        async with page.expect_response("**.magister.net/api/account*", timeout=30000) as response_info:
            response = await response_info.value
            body = await response.json()
            headers = await response.request.all_headers()

        logger.debug("Student request found")
        user_token = headers.get("authorization", None)
        student_info = body.get("Persoon", None)
        if student_info:
            user_id = student_info.get("Id", None)
        else:
            user_id = None

        return user_token, user_id
