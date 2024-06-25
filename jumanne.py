from simple_youtube_api.Channel import Channel as YTChannel
from simple_youtube_api.LocalVideo import LocalVideo
from pytube import YouTube,Channel
import scrapetube
import os.path
import ffmpeg
import subprocess


# loggin into the channel
channel = YTChannel()
channel.login("client_secret.json", "credentials.storage")

def download_video(video, id):
    output_path = os.path.join('videos', video.author.replace(" ", ""))
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    print("Downloading video: " + video.title + " (" + id + ")")
    
    # Download video and audio streams
    video_stream = video.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').desc().first()
    audio_stream = video.streams.filter(progressive=False, type='audio').order_by('abr').desc().first()
    print(video_stream)
    print(audio_stream)
    
    video_filename = id + "_video.mp4"
    audio_filename = id + "_audio." + audio_stream.subtype
    
    video_stream.download(output_path=output_path, filename=video_filename)
    audio_stream.download(output_path=output_path, filename=audio_filename)
    
    # Combine audio and video using ffmpeg
    input_video_path = os.path.join("C:\\GitHub\\Jumanne", output_path, video_filename)
    input_audio_path = os.path.join("C:\\GitHub\\Jumanne", output_path, audio_filename)
    output_video_path = os.path.join("C:\\GitHub\\Jumanne", output_path, id + ".mp4")

    print(input_video_path)
    print(input_audio_path)
    print(output_video_path)
    command = f"{r"C:\Users\weska\ffmpeg\ffmpeg.exe"} -i {input_video_path} -i {input_audio_path} -c:v copy -c:a aac {output_video_path}"
    try:
        subprocess.run(command, check=True, shell=True)
        print("ffmpeg command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing ffmpeg command: {e}")
    
    # Clean up downloaded files
    os.remove(os.path.join(output_path, video_filename))
    os.remove(os.path.join(output_path, audio_filename))
    
    print(video.title + " downloaded!")

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
            print("created file!")
    with open('archived/'+video.author+'.txt', 'a') as file:
            if not video_been_archived:
                print("archiving video: "+video.title+" ("+id+")")
                download_video(video,id)
                ## upload video
                file.write(id+"\n")
            else:
                print("Video already archived: "+video.title+" ("+id+")")
    


def archive_channel(channel_id):
    videos = scrapetube.get_channel(channel_id)
    for video in videos:
        archive_video(YouTube('https://www.youtube.com/watch?v='+video['videoId']))

def upload_video(filename):
    # setting up the video that is going to be uploaded
    video = LocalVideo(file_path="test_vid.mp4")

    # setting snippet
    video.set_title("My Title")
    video.set_description("This is a description")
    video.set_tags(["this", "tag"])
    video.set_category("gaming")
    video.set_default_language("en-US")

    # setting status
    video.set_embeddable(True)
    video.set_license("creativeCommon")
    video.set_privacy_status("private")
    video.set_public_stats_viewable(True)

    # setting thumbnail
    #video.set_thumbnail_path("test_thumb.png")
    #video.set_playlist("PLDjcYN-DQyqTeSzCg-54m4stTVyQaJrGi")

    # uploading video and printing the results
    video = channel.upload_video(video)
    print(video.id)
    print(video)

    # liking video
    video.like()

archive_channel('UCb69WJJK-8FFvaNYw2q3OZA')