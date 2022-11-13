import spotipy
import logging
import time
from dotenv import load_dotenv
from pymongo import MongoClient
from os import path, environ
from spotipy.oauth2 import SpotifyClientCredentials

# Init logging handlers with formatting for file and stream handling

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.FileHandler(filename="spotify_client.log")
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

SPOTIFY_CLIENT_ID = environ.get("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = environ.get("CLIENT_SECRET")


credentials = SpotifyClientCredentials(
                                    client_id=SPOTIFY_CLIENT_ID,
                                    client_secret=SPOTIFY_CLIENT_SECRET)

spotify_client = spotipy.Spotify(auth_manager=credentials)

results = spotify_client.search(q='playlist:Chill Hits', limit=40)


time.sleep(90)

mongo_client = MongoClient(host="mongodb", port=27017)

mongo_client.drop_database('spotify')

db = mongo_client.spotify

try:
   # The ismaster command is cheap and does not require auth.
   db.command('ismaster')
except:
   logger.error("Server not available")
   raise ConnectionError(f'Connection to MongoDB not available yet')
finally:
    logger.info("The mongodb server is running and client is connected")

songs = db.songs

logger.info("The tracks will now be uploaded to MongoDB....")

for idx, track in enumerate(results['tracks']['items']):
    dict = { 'id': idx,
            'track_name': track['name'],
            'track_url': track['preview_url'],
            'track_uri': track['uri'],
            'track_image_url': track['album']['images'][0]['url']
            }
    songs.insert_one(dict)

logger.info("The tracks were saved....")

mongo_client.close()

logger.info("Client connectiíon to Database closed after data upload...")