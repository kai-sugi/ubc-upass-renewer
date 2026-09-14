from playwright.sync_api import sync_playwright
from datetime import datetime

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

if datetime.now().day < 16:
    print("Pass is not renewable yet. Exiting...")
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

    input("Press ENTER to close...")

    browser.close()