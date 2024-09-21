import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os

from lib.lib import think, speak, listen, send_esp_instruction

# File path to save the donation logs
file_path = os.getcwd()+'/logs/donation_log.txt'

# Function to save unique entries to a queue and text file (Producer)
def monitor_popup(queue):
    # Setup WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Open the webpage
    driver.get('https://www.paulwatsonfoundation.org/freepaulwatson/')

    # Allow the page to load
    time.sleep(5)

    # Switch to the iframe where the donation popup appears
    iframe = driver.find_element(By.CSS_SELECTOR, 'iframe.fun-social-proof-iframe')
    driver.switch_to.frame(iframe)

    # Function to check for duplicates in the log file
    def is_unique_entry(cleaned_entry):
        # Check if the entry already exists in the file (ignoring timestamps)
        if not os.path.exists(file_path):
            existing_entries = set()
        else:
            with open(file_path, 'r') as f:
                existing_entries = {line.split(' - ')[1].strip() for line in f.readlines()}
        return cleaned_entry not in existing_entries

    # Monitor the popup content within the iframe frequently (without reloading the page)
    try:
        while True:
            try:
                # Wait and look for new donation information (adjust the CSS selector as needed)
                popup_element = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.content-desktop'))  # Adjust the selector inside iframe
                )

                # Extract the popup content (e.g., donation details)
                popup_content = popup_element.text
                print(f"Popup content detected: {popup_content}")
                
                # Clean the entry and ensure it's on one line
                cleaned_entry = popup_content.replace('Donate', '').replace('\n', ' ').strip()

                # Check if the entry is unique
                if is_unique_entry(cleaned_entry):
                    # Add the cleaned entry to the queue for further processing
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    formatted_entry = f"{timestamp} - {cleaned_entry}"
                    queue.put(formatted_entry)  # Put the entry in the queue

                    # Save the entry to the text file
                    with open(file_path, 'a') as f:
                        f.write(f"{formatted_entry}\n")
                    print(f"New entry added to queue and saved to file: {formatted_entry}")
                else:
                    print("Duplicate entry detected, not adding to queue or saving.")

            except Exception as e:
                print("No new popup content or donation detected.")

            # Sleep for a short period before checking again
            time.sleep(5)

    except KeyboardInterrupt:
        print("Monitoring stopped by user.")

    # Close the browser
    driver.quit()

# Function to print entries from the queue (Consumer)
def print_from_queue(queue):
    while True:
        try:
            # Get the next entry from the queue
            entry = queue.get()
            if entry:
                print(f"CONSUMER PROCESS - Entry from queue: {entry}")

                send_esp_instruction('<thinking>')
                response = think(entry)

                print(f"CONSUMER PROCESS - Response: {response}")
                send_esp_instruction('<awake>')
                speak(response)

                # utterance = listen()
                # print(f"CONSUMER PROCESS - Listened: {utterance}")

        except KeyboardInterrupt:
            print("Consumer stopped.")
            break