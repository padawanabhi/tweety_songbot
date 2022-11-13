import tweepy
from os import environ, path
from dotenv import load_dotenv
import logging
import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


# Init logging handlers with formatting for file and stream handling

logger = logging.getLogger(__name__)
#logger = logging.getLogger("tweepy")
logger.setLevel(level=logging.DEBUG)
handler = logging.FileHandler(filename="twitter_client.log")
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


TWITTER_API_KEY = environ.get("API_KEY")
TWITTER_API_KEY_SECRET = environ.get("API_KEY_SECRET")
TWITTER_BEARER_TOKEN = environ.get("BEARER_TOKEN")
TWITTER_ACCESS_TOKEN = environ.get("ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = environ.get("ACCESS_TOKEN_SECRET")

# Authentication instantiation

auth = tweepy.OAuth1UserHandler(
                            consumer_key=TWITTER_API_KEY, consumer_secret=TWITTER_API_KEY_SECRET, 
                            access_token=TWITTER_ACCESS_TOKEN, access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
                                )

api = tweepy.API(auth)

logger.info('Twitter Api Connection established')

# Twitter client initialization

twitter_client = tweepy.Client(
    bearer_token=TWITTER_BEARER_TOKEN,
    wait_on_rate_limit=True,
)

logger.info("Client connection established")


# Get a user's timeline 

""" cursor = tweepy.Paginator(
    method=client.get_users_tweets,
    id=user.id,
    exclude=['replies', 'retweets'],
    tweet_fields=['author_id', 'created_at', 'public_metrics']
).flatten(limit=5)

for tweet in cursor:
    print(tweet.text)
 """


# Search for Tweets #

# - means NOT
search_queries = ["Barack Obama -is:retweet -is:reply -is:quote lang:en -has:links",

                "Donald Trump -is:retweet -is:reply -is:quote lang:en -has:links",

                "Kim Kardashian -is:retweet -is:reply -is:quote lang:en -has:links",

                "Elon Musk -is:retweet -is:reply -is:quote lang:en -has:links"
                ]


# Establish connection to MongoDB

mongo_client = MongoClient(host="mongodb", port=27017)

mongo_client.drop_database('twitter')

db = mongo_client.twitter

try:
   # The ismaster command is cheap and does not require auth.
   db.command('ismaster')
except:
   logger.error("Server not available")
   raise ConnectionError(f'Connection to MongoDB not available yet')
finally:
    logger.info("The mongodb server is running and client is connected")

tweets = db.tweets

def save_tweets(client, queries):
    for query in queries:
        logger.info(f"The search query {query} will be executed on twitter")

        cursor = tweepy.Paginator(
                                method=twitter_client.search_recent_tweets,
                                query=query,
                                tweet_fields=['author_id', 'created_at', 'public_metrics'],
                                expansions=['author_id'],
                                user_fields=['created_at', 'description', 'location','username', 'id']
                                ).flatten(limit=400)

        logger.info("The query results have been saved to memory")
        logger.info("The tweets will now be saved in MongoDB. This could take a few minutes.")

        try:
            for tweet in cursor:
                if len(tweet.text) >= 100:
                    dict = {'author_id': tweet.author_id ,
                            'created_at': tweet.created_at, 
                            'public_metrics': tweet.public_metrics,
                            'tweet': tweet.text
                            }
                    tweets.insert_one(dict)
        except Exception as err:
            logger.exception(err)

        logger.info(f"The tweets for {query} were saved")
        time.sleep(10)


save_tweets(twitter_client, search_queries)



mongo_client.close()

logger.info("Client connectiíon to Database closed after data upload.")

