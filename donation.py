from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open the webpage
driver.get('https://www.paulwatsonfoundation.org/freepaulwatson/')

# File path to save the donation logs
file_path = 'donation_log.txt'

# Function to save data to a file if it's a unique entry
def save_unique_entry(entry_text):
    # Clean up the entry by removing "Donate" and ensuring it is on one line
    cleaned_entry = entry_text.replace('Donate', '').replace('\n', ' ').strip()
    
    # Check if the cleaned entry already exists in the file (ignore timestamps)
    if not os.path.exists(file_path):
        existing_entries = set()
    else:
        with open(file_path, 'r') as f:
            existing_entries = {line.split(' - ')[1].strip() for line in f.readlines()}
    
    # Create the entry with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_entry = f"{timestamp} - {cleaned_entry}\n"
    
    # Only save the entry if the cleaned message is not a duplicate (ignoring timestamp)
    if cleaned_entry not in existing_entries:
        with open(file_path, 'a') as f:
            f.write(formatted_entry)
        print(f"New entry saved: {formatted_entry.strip()}")
    else:
        print("Duplicate entry detected, not saving.")

# Allow the page to load
time.sleep(5)

# Switch to the iframe where the donation popup appears
iframe = driver.find_element(By.CSS_SELECTOR, 'iframe.fun-social-proof-iframe')
driver.switch_to.frame(iframe)

# Monitor the popup content within the iframe frequently (without reloading the page)
try:
    while True:
        try:
            # Wait and look for new donation information (adjust the CSS selector as needed)
            popup_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.content-desktop'))  # Adjust the selector inside iframe
            )

            # Extract and print the popup content (e.g., donation details)
            popup_content = popup_element.text
            print(f"Popup content detected: {popup_content}")

            # Save the popup content without duplicates
            save_unique_entry(popup_content)
        
        except Exception as e:
            print("Exception:", e)

        # Sleep for a short period before checking again (for frequent checks)
        time.sleep(5)

except KeyboardInterrupt:
    print("Monitoring stopped by user.")

# Close the browser
driver.quit()
