import csv
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Navigate to the login page
    page.goto("https://sdms.udiseplus.gov.in/p0/v1/login?state-id=127")
    
    # Fill in the login details
    page.get_by_placeholder("User ID").fill("27250501940")
    page.get_by_placeholder("Enter Password").fill("Walnut@12345")
    
    # Prompt user to handle CAPTCHA and login manually
    page.evaluate("alert('Please complete the CAPTCHA and click the Login button manually. After logging in, click OK to continue.');")
    
    # Wait for user to log in and continue manually
    page.wait_for_selector("text=Go to 2024-", timeout=60000)
    page.get_by_text("Go to 2024-").click()
    page.get_by_role("button", name="Close").click()

    # Navigate to the APAAR Module
    page.locator("#sidebar-wrapper").get_by_text("APAAR Module").click()

    # Prompt user to select division manually
    page.evaluate("alert('Please select the division and section manually, then click OK to continue.');")

    # Wait for user to interact manually and continue
    page.wait_for_selector("button:has-text('Go')")
    #page.get_by_role("button", name="Go").click()

    # Proceed with further interactions
    #page.wait_for_selector("text=ADITYA NISHANT TEMBHURNE")
    page.get_by_role("row", name="ADITYA NISHANT TEMBHURNE").get_by_role("button").click()

    page.get_by_role("textbox").first.click()
    page.locator("span").filter(has_text="SelectFatherMotherLegal").get_by_role("combobox").select_option("1")
    page.locator("span").filter(has_text="SelectFatherMotherLegal").get_by_role("combobox").select_option("2")
    page.locator("span").filter(has_text="SelectFatherMotherLegal").get_by_role("combobox").select_option("3")
    page.locator("span").filter(has_text="SelectAADHAARPANEPIC/Voter").get_by_role("combobox").select_option("1")
    page.locator("span").filter(has_text="SelectAADHAARPANEPIC/Voter").get_by_role("combobox").select_option("2")
    page.locator("span").filter(has_text="SelectAADHAARPANEPIC/Voter").get_by_role("combobox").select_option("3")
    page.locator("span").filter(has_text="SelectAADHAARPANEPIC/Voter").get_by_role("combobox").select_option("4")
    page.locator("span").filter(has_text="SelectAADHAARPANEPIC/Voter").get_by_role("combobox").select_option("5")
    page.get_by_role("textbox").nth(1).click()
    page.get_by_text("and Identity Proof Number").click()
    page.get_by_role("textbox").nth(1).click()
    page.get_by_text("Place of Physical Consent").click()
    page.locator("p").filter(has_text="Place of Physical Consent").get_by_role("textbox").click()
    page.locator("p").filter(has_text="Place of Physical Consent").get_by_role("textbox").click()
    page.get_by_text("Date of Physical Consent").click()
    page.locator("p").filter(has_text="Date of Physical Consent").get_by_role("textbox").click()
    page.pause()
    page.get_by_role("button", name="Submit")
    page.locator("#page-content-wrapper img").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
