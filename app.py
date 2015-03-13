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


RAYBAN_URLS = ['http://goo.gl/pVssDM']
STATUS_MESSAGE = '.@{} は逝ってしまったわ、レイバンの理に導かれて……。'
N_RECENT_USER = 32


def get_next_user():
    iterator = api.request(
        'statuses/filter',
        {'track': 'goo gl pVssDM'}
    ).get_iterator()

    try:
        for tweet in iterator:
            if 'text' in tweet:
                for url in tweet['entities']['urls']:
                    if url.get('expanded_url', None) in RAYBAN_URLS:
                        yield tweet['user']['screen_name']

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
    recent_users = []
    for screen_name in get_next_user():
        if screen_name not in recent_users:
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
            recent_users.append(screen_name)
            if len(screen_name) > N_RECENT_USER:
                recent_users.pop(0)
