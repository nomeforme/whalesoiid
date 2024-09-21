from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time
import os

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Path for the output text file
file_path = 'petition_signatures.txt'

# Function to save data to file
def save_to_file(signer, message, actual_time):
    with open(file_path, 'a') as f:
        f.write(f"Signer: {signer}, Message: {message}, Datetime: {actual_time}\n")

# Function to load all existing entries (ignoring timestamps) from the file
def load_existing_entries():
    if not os.path.exists(file_path):
        return set()
    
    existing_entries = set()
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            # Only consider signer and message for duplicate checking
            if "Signer: " in line and "Message: " in line:
                signer_message = line.split(", Datetime:")[0]
                existing_entries.add(signer_message.strip())
    return existing_entries

# Function to convert "time ago" strings to actual datetime
def convert_time_ago_to_datetime(time_ago_str):
    current_time = datetime.now()
    if "minute" in time_ago_str:
        minutes = int(time_ago_str.split(' ')[0])
        return current_time - timedelta(minutes=minutes)
    elif "hour" in time_ago_str:
        hours = int(time_ago_str.split(' ')[0])
        return current_time - timedelta(hours=hours)
    elif "day" in time_ago_str:
        days = int(time_ago_str.split(' ')[0])
        return current_time - timedelta(days=days)
    else:
        # If it's a new type of time format, return current time for simplicity
        return current_time

# Load existing entries into memory (ignoring timestamps)
existing_entries = load_existing_entries()

print("Existing entries loaded:", existing_entries)

# Infinite loop for refreshing the page and scraping
iteration_counter = 0

while True:
    # Increment the iteration counter
    iteration_counter += 1
    print(f"--- Iteration {iteration_counter} ---")
    
    # Open the webpage
    driver.get('https://www.paulwatsonfoundation.org/freepaulwatson/')
    
    # Allow some time for the page to load
    time.sleep(5)
    
    # Locate the parent div that contains all entries
    entries = driver.find_elements(By.CSS_SELECTOR, 'div.gwpm-last-entries li')
    
    # Flag to check if new messages are found
    new_messages_found = False
    
    for entry in entries:
        try:
            # Extract the name and signing details
            name = entry.find_element(By.CSS_SELECTOR, 'span.entrie-data').text
            message = entry.find_element(By.TAG_NAME, 'br').text if entry.find_element(By.TAG_NAME, 'br') else None
            time_ago_str = entry.find_element(By.TAG_NAME, 'small').text
            
            # Convert the "time ago" string to an actual datetime
            actual_time = convert_time_ago_to_datetime(time_ago_str)
            
            # Create a unique identifier for duplicate checking (excluding timestamp)
            signer_message = f"Signer: {name}, Message: {message}"
            
            # Check if the entry (signer and message) is new
            if signer_message not in existing_entries:
                # Print the new entry to the console
                print(f"Signer: {name}, Message: {message}, Datetime: {actual_time}")
                
                # Save the full entry (with timestamp) to the file
                save_to_file(name, message, actual_time.strftime("%Y-%m-%d %H:%M:%S"))
                
                # Add the signer-message combination to the existing entries set
                existing_entries.add(signer_message)
                
                # Mark that new messages were found
                new_messages_found = True
                
        except Exception as e:
            print(f"Error extracting entry: {e}")
    
    # If no new messages were found in this iteration, print it to the console
    if not new_messages_found:
        print("No new messages found in this iteration.")
    
    # Sleep for 30 seconds before refreshing the page again
    time.sleep(10)

# Close the browser when the loop ends (it won't, but in case it ever does)
driver.quit()
