from simple_youtube_api.Channel import Channel as YTChannel
from simple_youtube_api.LocalVideo import LocalVideo
from pytubefix import YouTube
import scrapetube
import os.path
import subprocess
import requests
from PIL import Image
import pyperclip
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
from dotenv import load_dotenv







# # loggin into the channel
# channel = YTChannel()
# channel.login("client_secret.json", "credentials.storage")

def archive_channel(channel_id):
    initialize_folders()
    videos = scrapetube.get_channel(channel_id)
    for video in videos:
        archive_video(YouTube('https://www.youtube.com/watch?v='+video['videoId'],
        use_oauth=True,
        allow_oauth_cache=True))

def initialize_folders():
    if not os.path.exists('videos'):
        os.makedirs('videos')
    if not os.path.exists('thumbnails'):
        os.makedirs('thumbnails')
    if not os.path.exists('archived'):
        os.makedirs('archived')

def crop_image(image_path):
    """Crops an image to a specific aspect ratio.

    Args:
        image_path: The path to the image file.
        aspect_ratio: The desired aspect ratio of the cropped image.

    Returns:
        A PIL Image object of the cropped image.
    """
    aspect_ratio = 16 / 9

    image = Image.open(image_path)
    width, height = image.size

    # Calculate the new width and height of the cropped image.
    new_width = width
    new_height = int(width / aspect_ratio)

    # Calculate the cropping coordinates to crop equally from the top and bottom.
    top = (height - new_height) // 2
    bottom = top + new_height

    # Crop the image to the new width and height.
    cropped_image = image.crop((0, top, new_width, bottom))

    cropped_image.save(image_path)

def delete_video(video,id):
    output_path = os.path.join('videos', video.author.replace(" ", ""))
    os.remove(os.path.join(output_path, id + ".mp4"))
    os.remove(os.path.join('thumbnails', id + ".jpg"))

def download_video(video, id):
    output_path = os.path.join('videos', video.author.replace(" ", ""))
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    print("Downloading video: " + video.title + " (" + id + ")")
    
    # Download video and audio streams
    video_stream = video.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').desc().first()
    audio_stream = video.streams.filter(progressive=False, type='audio').order_by('abr').desc().first()

    video_filename = id + "_video.mp4"
    audio_filename = id + "_audio." + audio_stream.subtype

    print(video_stream)
    print("Downloading video to: " + os.path.join(output_path, video_filename))
    video_stream.download(output_path=output_path, filename=video_filename)

    print(audio_stream)
    print("Downloading audio to: " + os.path.join(output_path, audio_filename))
    audio_stream.download(output_path=output_path, filename=audio_filename)
    
    # Combine audio and video using ffmpeg
    input_video_path = os.path.join(output_path, video_filename)
    input_audio_path = os.path.join(output_path, audio_filename)
    output_video_path = os.path.join(output_path, id + ".mp4")

    print("Processing video and audio...")
    command = f"ffmpeg -i {input_video_path} -i {input_audio_path} -c:v copy -c:a aac {output_video_path}"
    try:
        subprocess.run(command, check=True, shell=True)
        print("Video and audio processed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error executing ffmpeg command: {e}")
    
    # Clean up downloaded files
    os.remove(os.path.join(output_path, video_filename))
    os.remove(os.path.join(output_path, audio_filename))
    
    print(video.title + " (" + id + ") downloaded and processed successfully! " + output_video_path)

def archive_video(video):
    id = video.vid_info['videoDetails']['videoId']
    video_been_archived = False
    try:
        with open('archived/'+video.author+'.txt', 'r') as file:
            for line in file:
                if line.strip() == id: # Process each line (remove trailing newline)
                    video_been_archived = True
    except FileNotFoundError:
        with open('archived/'+video.author+'.txt', 'w') as file:
            print("Created file for video ids of "+video.author+"!")
    with open('archived/'+video.author+'.txt', 'a') as file:
            if not video_been_archived:
                print("Archiving video: "+video.title+" ("+id+")")
                download_video(video,id)
                # upload_video(video,id)
                browser_upload(video,id)
                delete_video(video,id) ## Enable this line to delete the video after uploading
                file.write(id+"\n")
            else:
                print("Video already archived: "+video.title+" ("+id+")")

def upload_video(video:YouTube,id):
    # setting up the video that is going to be uploaded
    output_path = os.path.join('videos', video.author.replace(" ", ""))
    print(output_path)
    localvideo = LocalVideo(file_path=output_path+"\\"+id+".mp4")

    # setting snippet
    localvideo.set_title("["+video.author+"] "+video.title)
    localvideo.set_description("This video was originally posted on the "+video.author+" channel on "+video.publish_date.strftime("%A, %B %e, %Y")+".\nOriginal link: https://www.youtube.com/watch?v="+id+"\n"+video.description)
    localvideo.set_tags(["Jumanne", "Archive", video.author, video.title])
    localvideo.set_category("entertainment")
    localvideo.set_default_language("en-US")
    localvideo.set_made_for_kids(False)

    # setting status
    localvideo.set_embeddable(True)
    localvideo.set_license("creativeCommon")
    localvideo.set_privacy_status("private")
    localvideo.set_public_stats_viewable(True)

    # setting thumbnail
    img_data = requests.get(video.vid_info['videoDetails']['thumbnail']['thumbnails'][-1]['url']).content
    thumbnail_path = 'thumbnails\\'+id+'.jpg'
    with open(thumbnail_path, 'wb') as handler:
        handler.write(img_data)
    crop_image(thumbnail_path)
    localvideo.set_thumbnail_path(thumbnail_path)
    print(video.vid_info['videoDetails']['thumbnail']['thumbnails'][-1]['url'])
    #video.set_playlist("PLDjcYN-DQyqTeSzCg-54m4stTVyQaJrGi")

    # uploading video and printing the results
    localvideo = channel.upload_video(localvideo)
    print(localvideo, " Video uploaded successfully!")

def browser_upload(video:YouTube,id):
    output_path = os.path.join('videos', video.author.replace(" ", ""))
    img_data = requests.get(video.vid_info['videoDetails']['thumbnail']['thumbnails'][-1]['url']).content
    thumbnail_path = 'thumbnails\\'+id+'.jpg'
    with open(thumbnail_path, 'wb') as handler:
        handler.write(img_data)
    crop_image(thumbnail_path)
    
    # Define local variables
    TITLE = "["+video.author+"] "+video.title
    DESCRIPTION = "This video was originally posted on the "+video.author+" channel on "+video.publish_date.strftime("%A, %B %e, %Y")+".\nOriginal link: https://www.youtube.com/watch?v="+id
    if(video.description != None):
        DESCRIPTION += "\n"+video.description
    TAGS = f'Jumanne, Archive, {video.author}, {video.title}'
    VIDEO_PATH = output_path+"\\"+id+".mp4"
    THUMBNAIL_PATH = thumbnail_path

    # Retrieve username and password from environment variables
    username = os.getenv('YOUTUBE_USERNAME')
    print(username)
    password = os.getenv('YOUTUBE_PASSWORD')

    # Initialize the WebDriver (make sure to download the appropriate WebDriver and provide the correct path)
    driver = webdriver.Chrome()

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
        time.sleep(1)
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
        pyperclip.copy(TITLE)
        title_box.send_keys(Keys.CONTROL,"v")

        description_box = driver.find_element(By.XPATH, '//div[@id="textbox" and @aria-label="Tell viewers about your video (type @ to mention a channel)"]')
        pyperclip.copy(DESCRIPTION)
        description_box.send_keys(Keys.CONTROL,"v")

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
        time.sleep(9)
        not_made_for_kids_radio.click()

        show_more = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@aria-label="Show more"]'))
        )
        show_more.click()

        # Add tags
        tags_box = driver.find_element(By.XPATH, '//input[@aria-label="Tags"]')
        pyperclip.copy(TAGS)
        time.sleep(3)
        tags_box.send_keys(Keys.CONTROL,"v")

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
        time.sleep(6.5)
        save_button.click()

        # Wait for the "Video processing" dialog to appear
        WebDriverWait(driver, 2800).until(
            EC.visibility_of_element_located((By.XPATH, '//h1[@id="dialog-title" and contains(text(), "Video processing")]'))
        )
        print("Video processing dialog detected.")
    finally:
        driver.quit()

load_dotenv()

# Load the accounts.json file
with open('accounts.json', 'r') as file:
    accounts = json.load(file)
# Iterate over the accounts and pass the "id" to the archive_channel function

for account in accounts:
    print(f'Archiving the channel: {account.get("name")}\n')
    archive_channel(account.get("id"))