from loda.actors.inoreader import Actor
from loda.storage.engines.locmem import LocalMemoryEngine
from mock import patch
from ..helpers import mock_response


def getenv(key, default=None):
    if key == 'INOREADER_APP_ID':
        return 'foo'

    if key == 'INOREADER_API_KEY':
        return 'foo'

    if key == 'INOREADER_TOKEN':
        return (
            'eyJhY2Nlc3NfdG9rZW4iOiAiMDFhMmIzNDVjNjc4OWRlMDEyM2Y0ZmdoNWlqNjc4'
            'OTAxMmszNGw1NiIsICJleHBpcmVzX2luIjogODY0MDAsICJ0b2tlbl90eXBlIjog'
            'IkJlYXJlciIsICJzY29wZSI6ICJyZWFkIiwgInJlZnJlc2hfdG9rZW4iOiAiMTJh'
            'YmMzNDU2N2RlOGZnOWgwaTFqMjNrNGxtNTZuN29wOHFyOTAxMiJ9'
        )

    return default


@patch('os.getenv', getenv)
def test_refresh_token():
    actor = Actor(LocalMemoryEngine(), [], {})

    with patch('requests.post', mock_response('inoreader.refresh_token')):
        actor.refresh_token()

    actor.refresh_token()


@patch('os.getenv', getenv)
@patch('requests.post', mock_response('inoreader.refresh_token'))
@patch('requests.get', mock_response('inoreader.stream'))
def test_tagged_articles():
    actor = Actor(LocalMemoryEngine(), [], {})
    args, func = actor.match('get latest articles tagged #loda')
    articles = []

    for article in func(*args):
        articles.append(article)

    assert articles == [
        {
            'title': 'Podcast listening without the app',
            'url': 'https://podnews.net/update/podinstall-launches'
        }
    ]


@patch('os.getenv', getenv)
@patch('requests.post', mock_response('inoreader.refresh_token'))
@patch('requests.get', mock_response('inoreader.stream'))
def test_articles_in_folder():
    actor = Actor(LocalMemoryEngine(), [], {})
    args, func = actor.match('get latest articles in Podcasting folder')
    articles = []

    for article in func(*args):
        articles.append(article)

    assert len(articles) == 2
    assert {
        'title': 'Deezer adds podcasting to its app in Colombia',
        'url': 'https://podnews.net/update/deezer-colombia'
    } in articles
