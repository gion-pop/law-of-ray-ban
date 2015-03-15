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
])
STATUS_MESSAGE = '.@{} は逝ってしまったわ、レイバンの理に導かれて……。'
N_RECENT_USER = 32


def get_next_user():
    recent_users = []
    for tweet in get_next_tweet():
        screen_name = tweet['user']['screen_name']

        if screen_name not in recent_users:
            recent_users.append(screen_name)
            if len(screen_name) > N_RECENT_USER:
                recent_users.pop(0)
            yield screen_name


def get_next_tweet():
    iterator = api.request(
        'statuses/filter',
        {'track': QUERY}
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
    for screen_name in get_next_user():
        result = api.request(
            'statuses/update',
            {
                'status': STATUS_MESSAGE.format(screen_name),
                'trim_user': True,
            }
        )
        if result.status_code == 200:
            print('[SUCCESS] @{}'.format(screen_name))
        else:
            print('[FAILURE] @{}: {}'.format(screen_name, result.text))
