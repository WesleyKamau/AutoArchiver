import subprocess

# Example of running ffmpeg command directly
ffmpeg_executable = r"C:\Users\weska\ffmpeg\ffmpeg.exe"
input_video_path = r"C:\GitHub\Jumanne\videos\Jumanne6\eZJax_ms1BQ_video.mp4"
input_audio_path = r"C:\GitHub\Jumanne\videos\Jumanne6\eZJax_ms1BQ_audio.webm"
output_video_path = r"C:\GitHub\Jumanne\videos\Jumanne6\eZJax_ms1BQ.mp4"

command = f"{ffmpeg_executable} -i {input_video_path} -i {input_audio_path} -c:v copy -c:a aac {output_video_path}"
try:
    result = subprocess.run(command, check=True, shell=True, capture_output=True, text=True)
    print("ffmpeg output:", result.stdout)
except subprocess.CalledProcessError as e:
    print(f"Error executing ffmpeg command: {e}")
    print("ffmpeg error output:", e.stderr)