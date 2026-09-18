from playwright.sync_api import sync_playwright
from datetime import datetime
import keyring

SCHOOL = {
    "BCIT": "British Columbia Institute of Technology",
    "CapU": "Capilano University",
    "DC": "Douglas College",
    "ECU": "Emily Carr University of Art and Design",
    "KPU": "Kwantlen Polytechnic University",
    "Langara": "Langara College",
    "NVIT": "Nicola Valley Institute of Technology",
    "SFU": "Simon Fraser University",
    "UBC": "University of British Columbia",
    "VCC": "Vancouver Community College",
}

SERVICE = "ubc-upass-automator"

if datetime.now().day < 16 :
    print("Pass is not renewable yet. Exiting...")
    exit()

username = keyring.get_password(SERVICE, "username")
password = keyring.get_password(SERVICE, "password")

if not username or not password:
    print("CWL credentials not found.")
    print("Run setup_credentials.py first.")
    exit()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://upassbc.translink.ca/")

    # Select school
    school_dropdown = page.locator("select")
    school_dropdown.select_option(label=SCHOOL["UBC"])

    # Click GO
    page.get_by_role("button", name="GO").click()

    page.wait_for_load_state("networkidle")

    print("UBC login page loaded.")

    page.get_by_label("Login Name").fill(username)
    page.get_by_label("Password").fill(password)

    print("CWL credentials filled.")

    page.get_by_role("button", name="Login").click()

    print("Login submitted.")
    print("Approve the Duo Push on your phone...")

    page.wait_for_url(
    "https://upassbc.translink.ca/**",
    timeout=120000
    )

    # We are requesting the following month
    now = datetime.now()
    next_month = now.month + 1
    next_year = now.year

    if next_month == 13:
        next_month = 1
        next_year += 1

    target_month = datetime(next_year, next_month, 1)
    target_label = target_month.strftime("%B %Y")

    print("Target month:", target_label)

    # Find the table row for the target month
    target_row = page.locator("tr").filter(
        has_text=target_label
    )

    if target_row.count() != 1:
        raise RuntimeError(
            f"Could not uniquely find the row for {target_label}"
        )

    row_text = target_row.inner_text()
    print("Target row:", row_text)

    # Safety check: only proceed if the row says it is eligible
    if "Yes" not in row_text:
        raise RuntimeError(
            f"{target_label} is not marked eligible. Stopping."
        )

    # Make sure it hasn't already been processed
    if "Processed" in row_text:
        print(f"{target_label} is already processed. Nothing to do.")
    else:
        checkbox = target_row.locator('input[type="checkbox"]')

        if checkbox.count() != 1:
            raise RuntimeError(
                f"Could not uniquely find checkbox for {target_label}."
            )

        confirm = input(
            f"Type REQUEST to select your {target_label} U-Pass: "
        )

        if confirm == "REQUEST":
            checkbox.check()

            print("Month selected.")

            # Find the Request button
            request_button = page.locator(
                'input[type="submit"][value="Request"]'
            )

            if request_button.count() != 1:
                raise RuntimeError(
                    "Could not uniquely find the Request button."
                )

            # Submit the U-Pass request
            request_button.click()

            page.wait_for_load_state("networkidle")

            print("Request submitted!")
            print(page.locator("body").inner_text())
        else:
            print("Cancelled. No request was submitted.")

    print("Current Page:", page.url)

    input("Press ENTER to close")

    browser.close()