import logging
import time
import re
import random
from os import path, environ
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import requests

# Init logging handlers with formatting for file and stream handling

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.FileHandler(filename="slack_bot.log")
handler.setLevel(level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(level=logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(funcName)s | %(message)s')

# add formatter to stream and file handler
handler.setFormatter(formatter)
console.setFormatter(formatter)

# Add the handlers to logger
logger.addHandler(handler)
logger.addHandler(console)

# Get env variables with Api credentials
BASE_DIR = path.abspath(path.dirname(__file__))
load_dotenv(path.join(BASE_DIR, ".env"))

SPOTIFY_URL = 'https://open.spotify.com/track/'
WEBHOOK_URL = environ.get("WEBHOOK_URL")
PG_USER = environ.get("PG_USER")
PG_PASSWORD = environ.get("PG_PASSWORD")
PG_DATABASE = environ.get("PG_DATABASE")
PG_PORT = environ.get("PG_PORT")
PG_HOST = environ.get("PG_HOST")


time.sleep(240)

postgres_client = create_engine(f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}', echo=True)

tweets = postgres_client.execute(text("""
                            SELECT * FROM tweets
                            ORDER BY sentiment DESC
                            LIMIT 20;
                            """))

songs = postgres_client.execute(text("""
                            SELECT * FROM songs
                            ORDER BY track_name DESC;
                            """))



song_list = []
for song in songs:
    song_url = SPOTIFY_URL + song['track_uri'].split(':')[2]
    song_list.append([song['track_name'], song_url, song['track_image_url']])


for tweet in tweets:
    song = random.choice(song_list)
    data = {
                "blocks": [
                    {
                        "type": "divider"
                    },
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "A new tweet"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": tweet['text']
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": f"{str(tweet['sentiment'])} : The sentiment of this tweet seems positive"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Perhaps a suitable song to set you in the same mood : "
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": f"Spotify: {song[0]}"
                            },
                            "value": "click_me_123",
                            "url": song[1],
                            "action_id": "button-action"
                        }
                    },
                    {
                        "type": "image",
                        "image_url": song[2],
                        "alt_text": "inspiration"
                    },
                    {
                        "type": "divider"
                    }
                ]
            }
    requests.post(url=WEBHOOK_URL, json = data)
    time.sleep(10)


