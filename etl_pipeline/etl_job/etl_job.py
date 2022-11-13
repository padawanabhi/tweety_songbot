import logging
import os
import time
import re
from pymongo import MongoClient
from sqlalchemy import create_engine, text
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Init logging handlers with formatting for file and stream handling

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.FileHandler(filename="etl_job.log")
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


def remove_tag(text):
    tag = "@[\w]*"
    new_text = re.sub(tag, '', text)
    return new_text


def remove_new_line(text):
    new_text = re.sub('\n', '', text)
    new_text = new_text.lower()
    return new_text

""" def expand_contraction(text):
    new_text = ''
    new_text = " ".join([contractions.fix(word) for word in text.split()])
    return new_text """

s  = SentimentIntensityAnalyzer()


time.sleep(180)


# Establish a connection to the MongoDB server
mongo_client = MongoClient(host="mongodb", port=27017)

# Connect to the database with tweets
db = mongo_client.twitter

try:
   # The ismaster command is cheap and does not require auth.
   db.command('ismaster')
except:
   logger.error("Server not available")
   raise Exception
finally:
    logger.info("The mongodb server is running and client is connected")


docs = list(db.tweets.find())

postgres_client = create_engine('postgresql://postgres:postgres@postgresdb:5432/tweets_db', echo=True)

postgres_client.execute(text('''
                        DROP TABLE IF EXISTS tweets;
                        '''))

postgres_client.execute(text('''
                        CREATE TABLE IF NOT EXISTS tweets (
                                            text VARCHAR(500),
                                            cleaned_text VARCHAR(500),
                                            sentiment NUMERIC
                                            );
                        '''))


for doc in docs:
    text = doc['tweet']
    new_text = remove_tag(text)
    new_text = remove_new_line(new_text)
#    new_text = expand_contractions(text)
    sentiment = s.polarity_scores(new_text) 
    score = sentiment['compound']
    query = "INSERT INTO tweets VALUES (%s, %s, %s);"
    try:    
        postgres_client.execute(query, (text, new_text, score))
    except Exception as err:
        logger.error(err)

# Connect to the database with ongs
db_songs = mongo_client.spotify

songs = list(db_songs.songs.find())

postgres_client.execute('''
                        DROP TABLE IF EXISTS songs;
                        ''')

postgres_client.execute('''
                        CREATE TABLE IF NOT EXISTS songs (
                                            track_name VARCHAR(100),
                                            track_url TEXT,
                                            track_uri TEXT,
                                            track_image_url TEXT
                                            );
                        ''')





for song in songs:
    query = "INSERT INTO songs VALUES (%s, %s, %s, %s);"
    logger.info(f"The song {song['track_name']} was saved")
    try:    
        postgres_client.execute(query, (song['track_name'], song['track_url'], song['track_uri'], song['track_image_url']))
    except Exception as err:
        logger.error(err)
