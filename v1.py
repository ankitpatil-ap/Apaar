import csv
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    # Load the CSV data
    csv_file = 'stud.csv'
    with open(csv_file, newline='') as file:
        reader = csv.DictReader(file)
        student_data = list(reader)
    
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Navigate to the login page
    page.goto("https://sdms.udiseplus.gov.in/p0/v1/login?state-id=127")
    page.wait_for_load_state()
    
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

    # Process each student record from the CSV
    for student in student_data:
        guardian_name = student["Guardian Name"]
        student_name = student["Student Name"]
        relation = student["Relation"]
        document = student["Document"]
        document_number = student["Document Number"]
        
        # Find and select the student row dynamically
        page.get_by_role("row", name=student_name).get_by_role("button").click()

        page.get_by_role("textbox").first.click()
        page.get_by_role("textbox").first.fill(guardian_name)

        # Select relation dynamically
        if relation == "Father":
            page.locator("span").filter(has_text="SelectFatherMotherLegal").get_by_role("combobox").select_option("1")
        elif relation == "Mother":
            page.locator("span").filter(has_text="SelectFatherMotherLegal").get_by_role("combobox").select_option("2")
        elif relation == "Legal Guardian":
            page.locator("span").filter(has_text="SelectFatherMotherLegal").get_by_role("combobox").select_option("3")
        
        # Select document type dynamically
        page.locator("span").filter(has_text="SelectFatherMotherLegal").get_by_role("combobox").press("Tab")
        page.locator("span").filter(has_text="SelectAADHAARPANEPIC/Voter").get_by_role("combobox").press("Enter")
        if document == "Aadhaar":
            page.locator("span").filter(has_text="SelectAADHAARPANEPIC/Voter").get_by_role("combobox").select_option("1")
        elif document == "Pan":
            page.locator("span").filter(has_text="SelectAADHAARPANEPIC/Voter").get_by_role("combobox").select_option("2")
        elif document == "EPIC/VOTER ID":
            page.locator("span").filter(has_text="SelectAADHAARPANEPIC/Voter").get_by_role("combobox").select_option("3")
        elif document == "Driving License":
            page.locator("span").filter(has_text="SelectAADHAARPANEPIC/Voter").get_by_role("combobox").select_option("4")
        elif document == "Passport":
            page.locator("span").filter(has_text="SelectAADHAARPANEPIC/Voter").get_by_role("combobox").select_option("5")
        
        # Fill in the document number
        page.get_by_text("and Identity Proof Number").click()
        page.get_by_role("textbox").nth(1).fill(document_number)

        # Fill in the place of physical consent
        page.locator("p").filter(has_text="Place of Physical Consent").get_by_role("textbox").fill("Pune")

        # Fill in the date of physical consent with today's date
        today_date = datetime.now().strftime("%d/%m/%Y")
        page.get_by_text("Date of Physical Consent").click()
        page.locator("p").filter(has_text="Date of Physical Consent").get_by_role("textbox").fill(today_date)
        page.pause()
        # Submit the form
        page.get_by_role("button", name="Submit").click()

    # Close the browser
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
