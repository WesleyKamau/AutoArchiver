from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from pytube import YouTube
import time
import os

def browser_upload(video:YouTube,id):
    output_path = os.path.join('videos', video.author.replace(" ", ""))
    img_data = requests.get(video.vid_info['videoDetails']['thumbnail']['thumbnails'][-1]['url']).content
    thumbnail_path = 'thumbnails\\'+id+'.jpg'
    with open(thumbnail_path, 'wb') as handler:
        handler.write(img_data)
    crop_image(thumbnail_path)

    # Define local variables
    TITLE = "["+video.author+"] "+video.title
    DESCRIPTION = "This video was originally posted on the "+video.author+" channel on "+video.publish_date.strftime("%A, %B %e, %Y")+".\nOriginal link: https://www.youtube.com/watch?v="+id+"\n"+video.description
    TAGS = f'Jumanne, Archive, {video.author}, {video.title}'
    VIDEO_PATH = output_path+"\\"+id+".mp4"
    THUMBNAIL_PATH = thumbnail_path

    # Retrieve username and password from environment variables
    username = os.getenv('YOUTUBE_USERNAME')
    password = os.getenv('YOUTUBE_PASSWORD')

    # Initialize the WebDriver (make sure to download the appropriate WebDriver and provide the correct path)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        print("Starting the upload process...")
        # Open YouTube Studio
        driver.get('https://studio.youtube.com/')

        # Enter username
        username_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="identifierId"]'))
        )
        username_input.send_keys(username)
        username_input.send_keys(Keys.RETURN)

        # Enter password
        password_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input'))
        )
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        
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

        # Upload the thumbnail file
        thumbnail_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
        )
        thumbnail_input.send_keys(os.path.abspath(THUMBNAIL_PATH))

        # Scroll down to the 'Made for kids' section and select 'No, it's not made for kids'
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        not_made_for_kids_radio = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.NAME, 'VIDEO_MADE_FOR_KIDS_NOT_MFK'))
        )
        not_made_for_kids_radio.click()

        show_more = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@aria-label="Show more"]'))
        )
        show_more.click()

        # Add tags
        tags_box = driver.find_element(By.XPATH, '//input[@aria-label="Tags"]')
        tags_box.send_keys(TAGS)

        next_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="next-button"]'))
        )
        next_button.click()
        # time.sleep(1)
        next_button.click()
        # time.sleep(1)
        next_button.click()

        # Set the privacy
        privacy_option = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="private-radio-button"]'))
        )
        privacy_option.click()

        # Save and publish
        save_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="done-button"]'))
        )
        time.sleep(1)
        save_button.click()

        # Wait for the "Video processing" dialog to appear
        WebDriverWait(driver, 600).until(
            EC.visibility_of_element_located((By.XPATH, '//h1[@id="dialog-title" and contains(text(), "Video processing")]'))
        )
        print("Video processing dialog detected.")
    finally:
        driver.quit()


test = YouTube('https://www.youtube.com/watch?v='+'12312')