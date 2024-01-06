from flask import Flask, render_template, request
from pytube import YouTube
from moviepy.editor import VideoFileClip
import tweepy
import os

app = Flask(__name__)

# Twitter API credentials
# (Replace with your actual credentials)
bearer_token = 'YOUR_BEARER_TOKEN'
consumer_key = 'YOUR_CONSUMER_KEY'
consumer_secret = 'YOUR_CONSUMER_SECRET'
access_token = 'YOUR_ACCESS_TOKEN'
access_token_secret = 'YOUR_ACCESS_TOKEN_SECRET'

# V1 Twitter API Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# V2 Twitter API Authentication
client = tweepy.Client(
    bearer_token,
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret,
    wait_on_rate_limit=True,
)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form['video_url']
        start_time = int(request.form['start_time'])
        end_time = int(request.form['end_time'])
        text = request.form['text']

        # Download YouTube video
        yt = YouTube(video_url)
        video_stream = yt.streams.filter(file_extension='mp4').first()
        video_path = video_stream.download()

        # Trim video using moviepy
        output_path = "static/trimmed_video.mp4"
        clip = VideoFileClip(video_path).subclip(start_time, end_time)
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

        # Upload trimmed video to Twitter
        media_id = api.media_upload(filename=output_path).media_id_string

        # Send Tweet with Text and media ID
        client.create_tweet(text=text, media_ids=[media_id])

        # Cleanup: Remove downloaded video and trimmed video
        os.remove(video_path)
        os.remove(output_path)

        return render_template('index.html', tweeted=True)

    return render_template('index.html', tweeted=False)


