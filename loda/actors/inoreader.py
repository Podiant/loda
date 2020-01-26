from base64 import b64decode
from loda import __version__
from loda.acting import ActorBase
import json
import os
import re
import requests


INOREADER_REFRESH_URL = 'https://www.inoreader.com/oauth2/token'
INOREADER_STREAM_URL = 'https://www.inoreader.com/reader/api/0/stream/contents/'  # NOQA
FOLDER_REGEX = r'user/\d+/label/(.+)'


class Actor(ActorBase):
    receive = [
        r'^get (?:latest )?articles tagged #?(.+)$',
        r'^get (?:latest )?articles in (.+) folder$'
    ]

    greedy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__token = None
        self.__token_refreshed = False
        self.__app_id = self.settings.APP_ID
        self.__app_secret = self.settings.API_KEY

        token = self.settings.TOKEN

        if token:
            token = b64decode(token)
            self.__token = json.loads(token)

    def refresh_token(self):
        if self.__token_refreshed:
            return

        response = requests.post(
            INOREADER_REFRESH_URL,
            data={
                'client_id': self.__app_id,
                'client_secret': self.__app_secret,
                'grant_type': 'refresh_token',
                'refresh_token': self.__token['refresh_token']
            }
        )

        response.raise_for_status()
        self.token = response.json()
        self.__token_refreshed = True

    def perform(self, folder):
        self.refresh_token()
        self.info('Getting articles from %s folder' % folder)
        stream = 'user/-/state/com.google/starred'

        response = requests.get(
            INOREADER_STREAM_URL + stream,
            headers={
                'User-Agent': 'loda/%s' % __version__,
                'Authorization': 'Bearer %(access_token)s' % self.__token
            }
        )

        response.raise_for_status()
        for item in response.json().get('items', []):
            for category in item.get('categories', []):
                match = re.search(FOLDER_REGEX, category)
                if match is None:
                    continue

                article_folder = match.groups()[0]
                if article_folder.lower().strip() != folder.lower().strip():
                    continue

                url = None
                for link in item.get('canonical', []):
                    if link.get('href'):
                        url = link['href']
                        break

                if url and not self.has('read', url):
                    self.push('read', url)

                    yield {
                        'title': item['title'],
                        'url': url
                    }
