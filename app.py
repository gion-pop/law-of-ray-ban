import datetime
import random

# "TwitterAPI" library on PyPI
from TwitterAPI import (
    TwitterAPI,
    TwitterRequestError,
    TwitterConnectionError,
)

import os
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN_KEY = os.environ.get('ACCESS_TOKEN_KEY')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

api = TwitterAPI(
    CONSUMER_KEY,
    CONSUMER_SECRET,
    ACCESS_TOKEN_KEY,
    ACCESS_TOKEN_SECRET
)

QUERY = ','.join([
    'goo.gl/pVssDM',
    'bit.ly/1CbwA6e',
    'goo.gl/YbVS1w',
])
WEB_CLIENT_SOURCE = '<a href="http://twitter.com" rel="nofollow">Twitter Web Client</a>'
STATUS_MESSAGE_BASE = list('は逝ってしまったわ、レイバンの理に導かれて……。（試験運用中）')
STATUS_MESSAGE_LEN = len(STATUS_MESSAGE_BASE)
N_RECENT_USER = 32
TWEETS_PER_DAY_THRESHOLD = 1


def create_randomized_message():
    result = list(STATUS_MESSAGE_BASE)
    result.insert(random.randrange(STATUS_MESSAGE_LEN), '\u200c')
    return ''.join(result)


def is_active_user(tweet):
    created_at = datetime.datetime.strptime(
        tweet['user']['created_at'],
        '%a %b %d %H:%M:%S +0000 %Y'
    )
    today = datetime.datetime.today()
    n_tweet = tweet['user']['statuses_count']

    return n_tweet / (today - created_at).days > TWEETS_PER_DAY_THRESHOLD


def get_next_user():
    recent_users = []
    for tweet in get_next_tweet():
        screen_name = tweet['user']['screen_name']

        if is_active_user(tweet) \
           and 'retweet_status' not in tweet \
           and tweet['source'] == WEB_CLIENT_SOURCE \
           and screen_name not in recent_users:
            recent_users.append(screen_name)
            if len(screen_name) > N_RECENT_USER:
                recent_users.pop(0)
            yield (screen_name, tweet['id'])


def get_next_tweet():
    iterator = api.request(
        'statuses/filter',
        {
            'track': QUERY,
            'language': ['ja'],
        }
    ).get_iterator()

    try:
        for tweet in iterator:
            if 'text' in tweet:
                yield tweet

            elif 'disconnect' in tweet:
                print('[Disconnect] {}'.format(tweet['disconnect']['reason']))

    except TwitterRequestError as e:
        if e.status_code < 500:
            # something needs to be fixed before re-connecting
            print('[Disconnect] {}'.format(tweet['disconnect']['reason']))
    except TwitterConnectionError:
        # temporary interruption, re-try request
        pass


if __name__ == '__main__':
    for (screen_name, status_id) in get_next_user():
        result = api.request(
            'statuses/update',
            {
                'status':
                ('.@{} ' + create_randomized_message()).format(screen_name),
                'trim_user': True,
                'in_reply_to_status_id': status_id,
            }
        )
        if result.status_code == 200:
            print('[SUCCESS] @{}'.format(screen_name))
        else:
            print('[FAILURE] @{}: {}'.format(screen_name, result.text))
