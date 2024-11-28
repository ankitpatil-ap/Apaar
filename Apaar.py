import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime   
from tkinter import ttk
from playwright.sync_api import Playwright, sync_playwright
import csv

def browse_csv():
    """Open a file dialog to browse and select the CSV file."""
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv")], title="Select the Student Data CSV"
    )
    csv_path_var.set(file_path)

def run_script():
    """Run the Playwright script with the selected CSV and credentials."""
    location = location_var.get()
    csv_file = csv_path_var.get()
    
    if location == "Select Location" or not csv_file:
        messagebox.showerror("Error", "Please select a location and browse for the CSV file.")
        return
    
    # Map location to credentials
    credentials = {
        "Wakad": {"user_id": "27254100013", "password": "Walwakad@12345"},
        "Shivane": {"user_id": "27250510325", "password": "16PH#rwb"},
        "Fursungi": {"user_id": "27250501940", "password": "Walnut@12345"},
    }
    
    user_id = credentials[location]["user_id"]
    password = credentials[location]["password"]

    # Playwright script
    def playwright_script(playwright: Playwright):
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
        page.get_by_placeholder("User ID").fill(user_id)
        page.get_by_placeholder("Enter Password").fill(password)
        
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

            # Submit the form
            page.get_by_role("button", name="Submit").click()

        # Close the browser
        context.close()
        browser.close()

    # Run the Playwright script
    with sync_playwright() as playwright:
        playwright_script(playwright)
    
    messagebox.showinfo("Success", "Script executed successfully.")

# Create the main window
root = tk.Tk()
root.title("Apaar Registration")
root.geometry("500x300")
root.configure(bg="#f0f8ff")  # Light blue background

# Title Label
title_label = tk.Label(root, text="Apaar Registration", font=("Helvetica", 18, "bold"), bg="#f0f8ff", fg="#2c3e50")
title_label.pack(pady=10)

# Location Selection
tk.Label(root, text="Select Location:", bg="#f0f8ff", fg="#34495e", font=("Arial", 12)).pack(pady=5)
location_var = tk.StringVar(value="Select Location")
location_dropdown = ttk.Combobox(root, textvariable=location_var, state="readonly", font=("Arial", 12))
location_dropdown["values"] = ["Select Location", "Wakad", "Shivane", "Fursungi"]
location_dropdown.pack(pady=5)

# CSV File Browsing
tk.Label(root, text="Select CSV File:", bg="#f0f8ff", fg="#34495e", font=("Arial", 12)).pack(pady=5)
csv_path_var = tk.StringVar()
csv_entry = tk.Entry(root, textvariable=csv_path_var, width=40, state="readonly", font=("Arial", 10))
csv_entry.pack(pady=5)
browse_button = tk.Button(root, text="Browse", command=browse_csv, bg="#1abc9c", fg="white", font=("Arial", 12, "bold"))
browse_button.pack(pady=5)

# Run Button
run_button = tk.Button(root, text="Run Script", command=run_script, bg="#3498db", fg="white", font=("Arial", 14, "bold"))
run_button.pack(pady=20)

# Run the GUI event loop
root.mainloop()
