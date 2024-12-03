import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from tkinter import ttk
from playwright.sync_api import sync_playwright
import csv
import shutil
import os
import requests
import sys

def browse_csv():
    """Open a file dialog to browse and select the CSV file."""
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv")], title="Select the Student Data CSV"
    )
    if file_path:  # If a file is selected
        csv_path_var.set(file_path)
        run_button.config(state="normal")  # Enable the "Run" button

def log_output(message):
    """Log messages to the output box."""
    output_box.insert(tk.END, message + "\n")
    output_box.see(tk.END)  # Auto-scroll to the end
    root.update()

def download_sample_csv():
    """Download the sample CSV file from a URL and save it to the selected folder."""
    save_path = filedialog.askdirectory(title="Select Folder to Save Sample CSV")
    
    if not save_path:
        messagebox.showerror("Error", "No folder selected. Please select a folder.")
        return
    
    url = "https://erp.walnutedu.in/files/Apaar.csv"
    filename = os.path.basename(url)
    destination_path = os.path.join(save_path, filename)

    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(destination_path, "wb") as f:
                f.write(response.content)
            messagebox.showinfo("Success", f"Sample CSV downloaded successfully to {destination_path}.")
        else:
            messagebox.showerror("Error", f"Failed to download the file. HTTP Status Code: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not download the file: {str(e)}")

def get_browser_executable_path():
    """Get the path of the Chromium browser executable."""
    if getattr(sys, 'frozen', False):  # Check if running as an executable
        # Adjust the path based on where the executable is bundled
        return os.path.join(sys._MEIPASS, 'playwright', 'driver', 'package', '.local-browsers', 'chromium-1124', 'chrome-win', 'chrome.exe')
    else:
        # Return default location for local development
        return 'C:/Users/User/AppData/Local/ms-playwright/chromium-1124/chrome-win/chrome.exe'

def run_script():
    """Run the Playwright script with the entered UDISE credentials and selected CSV."""
    csv_file = csv_path_var.get()

    # Check if the CSV file path is empty
    if not csv_file:
        messagebox.showerror("Error", "Please select a CSV file first.")
        return  # Exit the function if no file is selected

    # Read the CSV file
    try:
        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)
            student_data = list(reader)
    except Exception as e:
        log_output(f"Error reading CSV: {str(e)}")
        return

    def playwright_script(playwright):
        try:
            browser_path = get_browser_executable_path()
            log_output(f"Using browser path: {browser_path}")
            
            # Set the Playwright browser binary path
            browser = playwright.chromium.launch(executable_path=browser_path, headless=False)
            context = browser.new_context()
            page = context.new_page()

            log_output("Navigating to UDISE login page...")
            page.goto("https://sdms.udiseplus.gov.in/p0/v1/login?state-id=127", timeout=2500000)
            page.wait_for_load_state()

            log_output("Please complete the CAPTCHA manually.")
            page.evaluate("alert('Please complete the CAPTCHA and click OK to continue.');")
            page.wait_for_selector("text=Go to 2024-", timeout=120000)
            log_output("Login successful. Navigating to APAAR Module.")

            page.get_by_text("Go to 2024-").click()
            page.get_by_role("button", name="Close").click()
            page.wait_for_load_state()

            page.locator("#sidebar-wrapper").get_by_text("APAAR Module").click()
            page.wait_for_load_state()
            log_output("APAAR Module loaded. Please select the division manually.")

            page.evaluate("alert('Select division manually, then click OK to continue.');")
            page.wait_for_selector("button:has-text('Go')", timeout=2000)
            page.get_by_placeholder("Search").press("Enter")
            page.wait_for_load_state()

            for student in student_data:
                try:
                    student_name = student["Student Name"]
                    guardian_name = student["Guardian Name"]
                    relation = student["Relation"]
                    document = student["Document"]
                    document_number = student["Document Number"]

                    log_output(f"Processing student: {student_name}")
                    page.wait_for_load_state()

                    try:
                        page.wait_for_load_state()
                        page.get_by_placeholder("Search").click()
                        page.get_by_placeholder("Search").fill(student_name)
                        page.get_by_placeholder("Search").press("Enter")
                        student_row = page.get_by_role("row", name=student_name)
                        button = student_row.get_by_role("button")
                        button.click()
                        page.wait_for_load_state()
                    except Exception as e:
                        log_output(f"No Record found for: {student_name}")
                        continue

                    page.get_by_role("textbox").first.click()
                    page.get_by_role("textbox").first.fill(guardian_name)

                    if relation == "Father":
                        page.locator("span").filter(has_text="SelectFatherMotherLegal").get_by_role("combobox").select_option("1")
                    elif relation == "Mother":
                        page.locator("span").filter(has_text="SelectFatherMotherLegal").get_by_role("combobox").select_option("2")
                    elif relation == "Legal Guardian":
                        page.locator("span").filter(has_text="SelectFatherMotherLegal").get_by_role("combobox").select_option("3")

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

                    page.get_by_text("and Identity Proof Number").click()
                    page.get_by_role("textbox").nth(1).fill(document_number)

                    page.locator("p").filter(has_text="Place of Physical Consent").get_by_role("textbox").fill("Pune")

                    today_date = datetime.now().strftime("%d/%m/%Y")
                    page.get_by_text("Date of Physical Consent").click()
                    page.locator("p").filter(has_text="Date of Physical Consent").get_by_role("textbox").fill(today_date)

                    page.get_by_role("button", name="Submit").click()
                    page.get_by_role("button", name="Confirm").click()

                    try:
                        page.wait_for_selector("button:has-text('OK')", timeout=2000)
                        page.get_by_role("button", name="Okay").click().click(timeout=2000)
                        log_output("Handled OK alert.")
                        page.locator("#page-content-wrapper img").click()
                    except Exception:
                        log_output("Moving to Next Record, proceeding...")

                    page.get_by_role("button", name="Back").click(timeout=0)
                    page.wait_for_selector("input[placeholder='Search']")
                    log_output(f"Successfully processed: {student_name}")
                except Exception as e:
                    log_output(f"Error processing student: {student['Student Name']}. Error: {str(e)}")

        except Exception as e:
            log_output(f"Error: {str(e)}")
        finally:
            try:
                context.close()
                browser.close()
                log_output("Browser closed.")
            except Exception as e:
                log_output(f"Error closing browser: {str(e)}")

    try:
        with sync_playwright() as playwright:
            playwright_script(playwright)
        log_output("Script executed successfully.")
        messagebox.showinfo("Success", "Script executed successfully.")
    except Exception as e:
        log_output(f"Critical Error: {str(e)}")
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Main GUI
root = tk.Tk()
root.title("Apaar Registration")
root.geometry("1100x700")  # Increased window size for better layout
root.configure(bg="#f0f8ff")  # Light blue background

# Title Label
title_label = tk.Label(
    root,
    text="Apaar Registration",
    font=("Helvetica", 30, "bold"),
    bg="#f0f8ff",
    fg="#2c3e50"
)
title_label.pack(pady=20)

# Main Input Frame (Inner Box)
input_frame = tk.Frame(root, bg="#e8f4fc", relief=tk.RAISED, borderwidth=2)
input_frame.place(relx=0.2, rely=0.4, anchor=tk.CENTER)  # Centered on the left side
input_frame.configure(width=400, height=300)  # Adjust height for the new button
input_frame.pack_propagate(False)

# CSV File Browsing
tk.Label(input_frame, text="Select CSV File:", bg="#e8f4fc", fg="#34495e", font=("Arial", 14)).pack(pady=10, anchor=tk.W, padx=20)
csv_path_var = tk.StringVar()
csv_entry = tk.Entry(input_frame, textvariable=csv_path_var, width=35, state="readonly", font=("Arial", 12))
csv_entry.pack(pady=5)
browse_button = tk.Button(input_frame, text="Browse", command=browse_csv, bg="#1abc9c", fg="white", font=("Arial", 12, "bold"))
browse_button.pack(pady=10)

# New Button to Download Sample CSV
download_button = tk.Button(input_frame, text="Download Sample CSV", command=download_sample_csv, bg="#e67e22", fg="white", font=("Arial", 14, "bold"))
download_button.pack(pady=10)

# Run Button (Initially Disabled)
run_button = tk.Button(input_frame, text="Login and Run Script", command=run_script, bg="#3498db", fg="white", font=("Arial", 14, "bold"), state="disabled")
run_button.pack(pady=10)

# Instructions Below Inner Box
instructions = tk.Label(
    root,
    text="Instructions:\n1. All Fields are mandatory.\n2. Student Name must match with Aadhar Name.\n3. Document Details should not contain any blank space.",
    bg="#f0f8ff",
    fg="#34495e",
    font=("Arial", 10),  # Smaller font size
    anchor="w",
    justify="left"
)
instructions.place(relx=0.2, rely=0.75, anchor=tk.CENTER)  # Placing it below the input_frame

# Output Box Frame (Output Box)
output_frame = tk.Frame(root, bg="#f0f8ff", relief=tk.RIDGE, borderwidth=2)
output_frame.place(relx=0.7, rely=0.5, anchor=tk.CENTER)  # Centered on the right side
output_frame.configure(width=600, height=450)  # Increased height for better visibility
output_frame.pack_propagate(False)

# Output Box
output_label = tk.Label(output_frame, text="Output Log:", bg="#f0f8ff", fg="#2c3e50", font=("Arial", 14, "bold"))
output_label.pack(anchor=tk.W, padx=10, pady=5)
output_box = tk.Text(output_frame, wrap=tk.WORD, font=("Arial", 12))
output_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Run the GUI event loop
root.mainloop()
