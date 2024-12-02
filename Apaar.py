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

    def playwright_script(playwright: Playwright):
        # Open log file to write processed and failed records
        with open('process_log.txt', 'w') as log_file:
            try:
                with open(csv_file, newline='') as file:
                    reader = csv.DictReader(file)
                    student_data = list(reader)

                browser = playwright.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()

                # Navigate to the login page
                page.goto("https://sdms.udiseplus.gov.in/p0/v1/login?state-id=127", timeout=0)  # Set timeout to 60 seconds
                #page.wait_for_load_state()

                # Fill in the login details
                page.get_by_placeholder("User ID").fill(user_id)
                page.get_by_placeholder("Enter Password").fill(password)
                page.wait_for_load_state()
                
                # Prompt user to handle CAPTCHA and login manually
                page.evaluate("alert('Please complete the CAPTCHA and click the Login button manually. After logging in, click OK to continue.');")
                page.wait_for_load_state()
                
                # Wait for user to log in and continue manually
                page.wait_for_selector("text=Go to 2024-")
                page.wait_for_load_state()
                page.get_by_text("Go to 2024-").click()
                page.get_by_role("button", name="Close").click()
                page.wait_for_load_state()

                # Navigate to the APAAR Module
                page.locator("#sidebar-wrapper").get_by_text("APAAR Module").click()
                page.wait_for_load_state()

                # Prompt user to select division manually
                page.evaluate("alert('Please select the division and section manually, then click OK to continue.');")

                # Wait for user to interact manually and continue
                page.wait_for_selector("button:has-text('Go')")
                page.wait_for_load_state()

                # Process each student record from the CSV
                for student in student_data:
                    reference_number = student["Reference Number"]
                    guardian_name = student["Guardian Name"]
                    student_name = student["Student Name"]
                    relation = student["Relation"]
                    document = student["Document"]
                    document_number = student["Document Number"]

                    try:
                        # Attempt to find the row with the student's name and click the button
                        student_row = page.get_by_role("row", name=student_name)  # Locate the row by student name
                        
                        # Try to find and click the button within that row
                        button = student_row.get_by_role("button")
                        button.click()
                        page.wait_for_load_state()

                    except Exception as e:
                        # If an error occurs (button not found or clickable), log the error and move to the next record
                        print(f"Error or no button found for {student_name}, moving to the next record.")
                        
                        # Log the failed record to the 'not processed' file
                        reference_number = student.get("Reference Number", "N/A")  # Assuming you have the reference number in the CSV
                        log_file.write(f"Not Processed: {student_name} - {guardian_name} - Ref: {reference_number}\n")
                        
                        # Optionally, wait before continuing to the next record
                        page.wait_for_timeout(1000)  # Wait for 1 second before continuing to the next record

                        # Skip to the next student record
                        continue  # Move to the next student record

                    # Fill in the student details as before
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
                    elif document == "PAN":
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

                                    # After clicking the Confirm button
                    page.get_by_role("button", name="Submit").click()
                    page.get_by_role("button", name="Confirm").click()

                    # Wait for the potential appearance of the "OK" button (error handling)
                    try:
                        # Check if the "OK" button appears, if so, click it
                        page.wait_for_selector("button:has-text('OK')", timeout=2000)  # Timeout after 5 seconds
                        page.get_by_role("button", name="Okay").click().click(timeout=2000)
                        print("OK button clicked due to error.")

                        # After clicking OK, click on the image to continue (as per your instructions)
                        page.locator("#page-content-wrapper img").click()
                        print("Clicked on the page image to continue.")
                    except Exception as e:
                        # If "OK" button does not appear or there's an error, continue with the normal flow
                        print("No OK button found, continuing...")

                    # Go back after submission and proceed to the next student
                    page.get_by_role("button", name="Back").click(timeout=0)  # Disable timeout for click

                    # Wait until the search box is available and fill the next student's name
                    page.wait_for_selector("input[placeholder='Search']")
                    next_student = student_data[student_data.index(student) + 1]
                    page.get_by_placeholder("Search").fill(next_student["Student Name"])

                    print(f"{next_student['Reference Number']},{next_student['Student Name']} Inserted")



            finally:
                # Ensure the browser and context are always closed
                #page.pause()
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
