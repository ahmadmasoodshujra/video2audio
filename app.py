from flask import Flask, render_template, request, send_file, after_this_request
from moviepy.editor import *
import os

app = Flask(__name__)

def cleanup_temp_folder():
    # Check if the "temp" folder exists
    if os.path.exists("temp"):
        # Get a list of all files in the "temp" folder
        files = os.listdir("temp")
        for file in files:
            try:
                # Delete each file in the "temp" folder
                os.remove(os.path.join("temp", file))
            except Exception as e:
                print(f"Error deleting file {file}: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert_video_to_audio():
    if "video" not in request.files:
        return "No video found", 400

    video = request.files["video"]
    if video.filename == "":
        return "No video selected", 400

    # Clean up the "temp" folder before converting the video
    cleanup_temp_folder()

    # Save the video to a temporary location
    video_path = f"temp/{video.filename}"
    video.save(video_path)

    # Convert video to audio
    audio_path = f"temp/{video.filename.split('.')[0]}.mp3"
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path)

    # Close the video and audio clips
    video_clip.close()
    audio_clip.close()

    # Clean up temporary files after the response is sent
    @after_this_request
    def remove_files(response):
        try:
            os.remove(video_path)
            os.remove(audio_path)
        except Exception as e:
            print(f"Error deleting files: {e}")
        return response

    return send_file(audio_path, as_attachment=True)

if __name__ == "__main__":
    app.run()
