import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import spacy
import time

# Set up Selenium WebDriver
chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # Path to your Chrome
options = Options()
options.binary_location = chrome_path
options.add_argument("--headless")  # Run headless Chrome
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
capabilities = options.to_capabilities()
capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Load SpaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Create output directory
output_dir = "extracted_text"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Starting URL
base_url = "https://lhohq.info/"
driver.set_page_load_timeout(30)

# Function to get all text from the current page, including hidden elements
def get_all_text(driver):
    elements = driver.find_elements(By.XPATH, "//*")
    text_content = ""
    for elem in elements:
        text_content += elem.text + " " + elem.get_attribute("innerText") + " "
    return text_content

# Spider function to collect all text and save it to files
def spider(driver, url):
    visited = set()
    to_visit = {url}
    page_count = 0

    while to_visit:
        current_url = to_visit.pop()
        if current_url not in visited:
            for attempt in range(3):  # Retry up to 3 times
                try:
                    driver.get(current_url)
                    time.sleep(5)  # Wait for the page to load
                    visited.add(current_url)
                    page_text = get_all_text(driver)
                    # Save text to file
                    page_count += 1
                    file_name = os.path.join(output_dir, f"page_{page_count}.txt")
                    with open(file_name, "w") as file:
                        file.write(page_text)
                    print(f"Saved text from {current_url} to {file_name}")
                    # Get new links
                    elements = driver.find_elements(By.TAG_NAME, 'a')
                    for elem in elements:
                        href = elem.get_attribute('href')
                        if href and href.startswith(base_url) and href not in visited:
                            to_visit.add(href)
                    break  # Exit the retry loop if successful
                except Exception as e:
                    print(f"Error accessing {current_url}: {e}")
                    time.sleep(5)  # Wait before retrying
            else:
                print(f"Failed to access {current_url} after 3 attempts")

# Run the spider and get all text
spider(driver, base_url)

# Close the WebDriver
driver.quit()

