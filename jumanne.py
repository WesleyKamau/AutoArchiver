from simple_youtube_api.Channel import Channel as YTChannel
from simple_youtube_api.LocalVideo import LocalVideo
from pytube import YouTube
import scrapetube
import os.path
import subprocess
import requests
from PIL import Image


# loggin into the channel
channel = YTChannel()
channel.login("client_secret.json", "credentials.storage")

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
                upload_video(video,id)
                delete_video(video,id) ## Enable this line to delete the video after uploading
                file.write(id+"\n")
            else:
                print("Video already archived: "+video.title+" ("+id+")")
    


def archive_channel(channel_id):
    initialize_folders()
    videos = scrapetube.get_channel(channel_id)
    for video in videos:
        archive_video(YouTube('https://www.youtube.com/watch?v='+video['videoId']))

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

    # liking video
    localvideo.like()

archive_channel('UCb69WJJK-8FFvaNYw2q3OZA')