from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # Add this line
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os

# Define local variables
TITLE = "Selenium Video Title Test"
DESCRIPTION = "Selenium Video Description Test"
TAGS = "tag1, tag2, tag3"
CATEGORY = "22"  # Category ID for 'People & Blogs'
PRIVACY = "private"  # Options: 'private', 'unlisted', 'public'
VIDEO_PATH = "videos\\Jumanne6\\eZJax_ms1BQ.mp4"
THUMBNAIL_PATH = "thumbnails\\2dZdOX8bHUo.jpg"

# Initialize the WebDriver (make sure to download the appropriate WebDriver and provide the correct path)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    # Open YouTube Studio
    driver.get('https://youtube.com/')

    with open('cookies.json', 'r') as cookies_file:
        cookies = json.load(cookies_file)
        for cookie in cookies:
            driver.add_cookie(cookie)
    # Refresh the page to apply cookies
    driver.get('https://studio.youtube.com/')
    

    # Click the upload button

    upload_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="upload-icon"]'))
    )
    upload_button.click()

    # Upload the video file
    video_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
    )
    video_input.send_keys(os.path.abspath(VIDEO_PATH))

    # Wait for video details page to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//div[@id="textbox" and @aria-label="Add a title that describes your video (type @ to mention a channel)"]'))
    )

    # Fill in the video details
    title_box = driver.find_element(By.XPATH, '//div[@id="textbox" and @aria-label="Add a title that describes your video (type @ to mention a channel)"]')
    title_box.clear()
    title_box.send_keys(TITLE)

    description_box = driver.find_element(By.XPATH, '//div[@id="textbox" and @aria-label="Tell viewers about your video (type @ to mention a channel)"]')
    description_box.send_keys(DESCRIPTION)

    # Scroll down to the 'Made for kids' section and select 'No, it's not made for kids'
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    not_made_for_kids_radio = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.NAME, 'VIDEO_MADE_FOR_KIDS_NOT_MFK'))
    )
    not_made_for_kids_radio.click()

    # //*[@id="toggle-button"]/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]
    show_more = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="toggle-button"]/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]'))
    )
    show_more.click()

    # Add tags
    tags_box = driver.find_element(By.XPATH, '//input[@aria-label="Tags"]')
    tags_box.send_keys(TAGS)

    # //*[@id="next-button"]
    next_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="next-button"]'))
    )
    next_button.click()

    

    # Set the language to English
    language_dropdown = driver.find_element(By.XPATH, '//ytcp-dropdown-trigger[@label="Video language"]')
    language_dropdown.click()
    english_option = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//yt-formatted-string[text()="English"]'))
    )
    english_option.click()

    # Set the privacy
    privacy_dropdown = driver.find_element(By.XPATH, '//ytcp-dropdown-trigger[@label="Visibility"]')
    privacy_dropdown.click()
    privacy_option = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f'//tp-yt-paper-item[@test-id="{PRIVACY.upper()}"]'))
    )
    privacy_option.click()

    # Upload thumbnail
    thumbnail_input = driver.find_element(By.XPATH, '//input[@id="file-loader"]')
    thumbnail_input.send_keys(THUMBNAIL_PATH)

    # Save and publish
    save_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//ytcp-button[@id="done-button"]'))
    )
    save_button.click()

    # Confirm if prompted
    confirm_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//ytcp-button[@id="done-button"]'))
    )
    confirm_button.click()

    print("Video upload process completed.")

finally:
    # Close the WebDriver after some delay to ensure everything is processed
    ## time.sleep(10)
    driver.quit()
