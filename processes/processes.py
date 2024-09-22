import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os

from lib.lib import think, speak, listen, send_esp_instruction, log_response, get_random_stimulus, play_speech_indicator, play_speech_acknowledgement

# Function to save unique entries to a queue and text file (Producer)
def monitor_popup(donation_queue, donation_timeout_event, donation_timeout_seconds: int = 60):

    # File path to save the donation logs
    file_path = os.getcwd()+'/logs/donation_log.txt'

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
    
    # Initialize last_donation_time to the current time
    last_donation_time = datetime.now()

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

                    if donation_timeout_event.is_set():
                        donation_timeout_event.clear()
                        print("Donation detected - timeout event cleared")

                    # Add the cleaned entry to the queue for further processing
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    formatted_entry = f"{timestamp} - {cleaned_entry}"
                    donation_queue.put(formatted_entry)  # Put the entry in the queue

                    # Save the entry to the text file
                    with open(file_path, 'a') as f:
                        f.write(f"{formatted_entry}\n")
                    print(f"New entry added to queue and saved to file: {formatted_entry}")

                    # Update last_donation_time since a new donation was detected
                    last_donation_time = datetime.now()

                else:
                    print("Duplicate entry detected, not adding to queue or saving.")

            except Exception as e:
                print("No new popup content or donation detected.")

            # Check if no donations have been detected
            time_since_last_donation = datetime.now() - last_donation_time

            if time_since_last_donation.total_seconds() >= donation_timeout_seconds:  # time in seconds

                if not donation_timeout_event.is_set():

                    donation_timeout_event.set()
                    print(f"No donations detected for {donation_timeout_seconds} seconds - donation timeout event set")

            # Sleep for a short period before checking again
            time.sleep(5)

    except KeyboardInterrupt:
        print("Monitoring stopped by user.")

    # Close the browser
    driver.quit()

# Function to print entries from the queue (Consumer)
def speak_donations(donation_queue, donation_timeout_event):

    file_path = os.getcwd()+'/logs/cta.txt'

    while True:

        if donation_timeout_event.is_set():
            time.sleep(0.1)
            continue

        try:
            # Get the next entry from the queue
            donation_entry = donation_queue.get()

            if donation_entry:

                print(f"DONATION PROCESS - Entry from queue: {donation_entry}")

                send_esp_instruction('<thinking>')
                response = think(donation_entry, use_system_message='donation')

                print(f"DONATION PROCESS - Response: {response}")
                send_esp_instruction('<awake>')

                log_response(response, file_path)
                speak(response)

                send_esp_instruction('<thinking>')

                # utterance = listen()
                # print(f"CONSUMER PROCESS - Listened: {utterance}")

        except KeyboardInterrupt:
            print("Consumer stopped.")
            break

def conversation(donation_timeout_event, max_rounds: int = 5):

    file_path = os.getcwd()+'/logs/conversation.txt'

    while True:

        if not donation_timeout_event.is_set():
            time.sleep(0.1)
            continue

        try:
            # # Get the next entry from the queue
            # donation_entry = donation_queue.get()

            n_rounds = 0
            message_history = []

            while n_rounds < max_rounds:

                print("CONVERSATION PROCESS - Round: ", n_rounds)

                if n_rounds == 0:

                    send_esp_instruction('<awake>')
                    stimulus = get_random_stimulus()
                    print(f"CONVERSATION PROCESS - Stimulus: {stimulus}")

                    speak(stimulus)

                send_esp_instruction('<listening>')
                play_speech_indicator()
                utterance = listen()

                play_speech_acknowledgement()

                print(f"CONVERSATION PROCESS - Listened: {utterance}")

                message_history.append(f"human: {utterance}")
                log_response(f"human: {utterance}", file_path)

                send_esp_instruction('<thinking>')
                response = think(utterance, use_system_message='conversation', message_history=message_history, word_count=50)

                message_history.append(f"whalesoid: {response}")
                log_response(f"whalesoid: {response}", file_path)

                print(f"CONVERSATION PROCESS - Response: {response}")
                send_esp_instruction('<awake>')

                speak(response)

                send_esp_instruction('<thinking>')

                n_rounds += 1

        except KeyboardInterrupt:
            print("Consumer stopped.")
            break