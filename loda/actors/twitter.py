from loda.acting import ActorBase
from loda.exceptions import ConfigError
import json
import os
import time


try:
    from requests_oauthlib import OAuth1Session
except Exception:  # pragma: no cover
    raise ConfigError('loda.twitter requires requests-oauthlib.')


PROFILE_SEARCH_URL = 'https://api.twitter.com/1.1/users/search.json'
PROFILE_SHOW_URL = 'https://api.twitter.com/1.1/users/show.json'
FOLLOW_URL = 'https://api.twitter.com/1.1/friendships/create.json'
TWEET_SEARCH_URL = 'https://api.twitter.com/1.1/search/tweets.json'
RETWEET_URL = 'https://api.twitter.com/1.1/statuses/retweet/%s.json'
TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'


class Actor(ActorBase):
    receive = {
        'follow': [
            r'^follow (.*)'
        ],
        'search': [
            r'find tweets? (.+)',
            r'search for tweets? (.+)'
        ],
        'rt': [
            r'^rt (\d+)'
        ],
        'tweet': [
            r'^tweet "?(.+)"?$'
        ]
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__client = OAuth1Session(
            self.settings.CONSUMER_KEY,
            self.settings.CONSUMER_SECRET,
            resource_owner_key=self.settings.ACCESS_TOKEN,
            resource_owner_secret=self.settings.ACCESS_SECRET
        )

        self.__follow_count = 0
        self.__rt_count = 0
        self.__follow_limited = False
        self.__rate_limited = False

    def _get(self, url, **params):
        response = self.__client.get(url, params=params)
        data = response.json()

        if isinstance(data, dict):
            for error in data.get('errors', []):
                self.fail(
                    error.get('message')
                )

        return data

    def _post(self, url, params={}, **data):
        response = self.__client.post(url, params=params, data=data)
        data = response.json()

        if isinstance(data, dict):
            for error in data.get('errors', []):
                if error.get('code') == 88:
                    self.__rate_limit()
                    return

                if error.get('code') == 161:
                    self.__follow_limit()
                    return

                self.fail(
                    error.get('message')
                )

        return data

    def test_follow(self, criteria):
        if criteria.startswith('@'):
            filename = os.path.join(
                os.path.dirname(
                    os.path.dirname(__file__)
                ),
                'fixtures',
                'twitter',
                'test_follow.json'
            )

            with open(filename, 'rb') as f:
                return json.load(f)
        else:
            filename = os.path.join(
                os.path.dirname(
                    os.path.dirname(__file__)
                ),
                'fixtures',
                'twitter',
                'test_profiles.json'
            )

            with open(filename, 'rb') as f:
                for account in json.load(f):
                    yield account

    def follow(self, criteria):
        if criteria.startswith('@'):
            return self.lookup(criteria[1:], follow=True)

        if self.__follow_limited:
            return

        page = 1
        while True:
            data = self._get(
                PROFILE_SEARCH_URL,
                q=criteria,
                page=page
            )

            if not any(data):
                break

            for account in data:
                yield self._follow(**account)

            if self.__follow_limited:
                return

            page += 1
            self.debug('Moving to page %d' % page)

    def test_search(self, criteria):
        self.context.pop('tweet', None)

        filename = os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)
            ),
            'fixtures',
            'twitter',
            'test_tweets.json'
        )

        with open(filename, 'rb') as f:
            for tweet in json.load(f):
                self.context['tweet'] = tweet
                yield tweet

    def search(self, criteria):
        self.context.pop('tweet', None)

        if self.__rate_limited:
            return

        data = self._get(
            TWEET_SEARCH_URL,
            q=criteria
        )

        for tweet in data['statuses']:
            self.context['tweet'] = tweet
            yield tweet

    def test_rt(self, id_str):
        filename = os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)
            ),
            'fixtures',
            'twitter',
            'test_retweet.json'
        )

        with open(filename, 'rb') as f:
            return json.load(f)

    def rt(self, id_str):
        if self.has('rt', id_str):
            return

        data = self._post(RETWEET_URL % id_str)
        self.__rt_count += 1
        self.push('rt', id_str)
        self.tag('tweeted')
        self.debug('Pausing for 3 seconds')
        time.sleep(3)
        return data

    def lookup(self, screen_name, follow=False):
        data = self._get(
            PROFILE_SHOW_URL,
            screen_name=screen_name
        )

        if follow:
            self._follow(**data)

        return data

    def _follow(self, id_str, screen_name, **kwargs):
        if not self.has('follow', id_str):
            if self.__follow_limited:
                return

            data = self._post(
                FOLLOW_URL,
                params={
                    'user_id': id_str
                }
            )

            self.__follow_count += 1
            self.push('follow', id_str)
            self.debug('Pausing for a second')
            time.sleep(1)
            return data

    def __follow_limit(self):
        self.__follow_limited = True
        self.tag('follow_limited')
        self.debug('Hit Twitter\'s follow limit.')

    def __rate_limit(self):
        self.__rate_limited = True
        self.tag('rate_limited')
        self.debug('Hit Twitter\'s rate limit.')

    def test_tweet(self, text):
        filename = os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)
            ),
            'fixtures',
            'twitter',
            'test_tweet.json'
        )

        with open(filename, 'rb') as f:
            return json.load(f)

    def tweet(self, text):
        data = self._post(TWEET_URL, status=text)
        self.tag('tweeted')
        self.debug('Pausing for 3 seconds')
        time.sleep(3)
        return data
