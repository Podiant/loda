from loda.actors.twitter import Actor
from loda.exceptions import PerformanceError
from loda.storage.engines.locmem import LocalMemoryEngine
from mock import patch
from ..helpers import mock_response
import pytest


def getenv(key, default=None):
    if key == 'TWITTER_CONSUMER_KEY':
        return 'foo'

    if key == 'TWITTER_CONSUMER_SECRET':
        return 'foo'

    if key == 'TWITTER_ACCESS_TOKEN':
        return 'foo'

    if key == 'TWICCER_ACCESS_SECRET':
        return 'foo'

    return default


@patch('os.getenv', getenv)
@patch('requests_oauthlib.OAuth1Session.get', mock_response('twitter.profile'))
@patch('requests_oauthlib.OAuth1Session.post', mock_response('twitter.follow'))
@patch('time.sleep', lambda i: None)
def test_follow_username():
    actor = Actor(LocalMemoryEngine(), [], {})
    args, func = actor.match('follow @jack')
    for account in func(*args):
        assert account['screen_name'] == 'jack'


@patch('os.getenv', getenv)
@patch('requests_oauthlib.OAuth1Session.get', mock_response('twitter.profile'))
@patch('requests_oauthlib.OAuth1Session.post', mock_response('twitter.follow_limited'))  # NOQA
@patch('time.sleep', lambda i: None)
def test_follow_limited():
    actor = Actor(LocalMemoryEngine(), [], {})
    args, func = actor.match('follow @jack')
    assert not any(list(func(*args)))


@patch('os.getenv', getenv)
@patch('requests_oauthlib.OAuth1Session.get', mock_response('twitter.profile'))
@patch('requests_oauthlib.OAuth1Session.post', mock_response('twitter.internal_error'))  # NOQA
@patch('time.sleep', lambda i: None)
def test_follow_error():
    actor = Actor(LocalMemoryEngine(), [], {})
    args, func = actor.match('follow @jack')

    with pytest.raises(PerformanceError) as ctx:
        list(func(*args))

    assert ctx.value.args[0] == 'Internal error'


@patch('os.getenv', getenv)
@patch('requests_oauthlib.OAuth1Session.get', mock_response('twitter.profiles', paged='page'))  # NOQA
@patch('requests_oauthlib.OAuth1Session.post', mock_response('twitter.follow'))
@patch('time.sleep', lambda i: None)
def test_follow_topic():
    actor = Actor(LocalMemoryEngine(), [], {})
    args, func = actor.match('follow podcasting')
    accounts = []

    for data in func(*args):
        accounts.append(data)

    assert len(accounts) == 2


@patch('os.getenv', getenv)
@patch('requests_oauthlib.OAuth1Session.get', mock_response('twitter.tweets'))
def test_search():
    actor = Actor(LocalMemoryEngine(), [], {})
    args, func = actor.match('find tweets frmo:jack')
    tweets = []

    for data in func(*args):
        tweets.append(data)

    assert len(tweets) == 1


@patch('os.getenv', getenv)
@patch('requests_oauthlib.OAuth1Session.get', mock_response('twitter.rate_limited'))  # NOQA
def test_search_rate_limited():
    actor = Actor(LocalMemoryEngine(), [], {})
    args, func = actor.match('find tweets frmo:jack')

    with pytest.raises(PerformanceError) as ctx:
        list(func(*args))

    assert ctx.value.args[0] == 'Rate limit exceeded'


@patch('os.getenv', getenv)
@patch('requests_oauthlib.OAuth1Session.get', mock_response('twitter.internal_error'))  # NOQA
def test_search_error():
    actor = Actor(LocalMemoryEngine(), [], {})
    args, func = actor.match('find tweets frmo:jack')

    with pytest.raises(PerformanceError) as ctx:
        list(func(*args))

    assert ctx.value.args[0] == 'Internal error'


@patch('os.getenv', getenv)
@patch('requests_oauthlib.OAuth1Session.post', mock_response('twitter.retweet'))  # NOQA
@patch('time.sleep', lambda i: None)
def test_rt():
    actor = Actor(LocalMemoryEngine(), [], {})
    args, func = actor.match('rt 1221106159907680256')
    data = func(*args)
    assert data['id_str'] == '1221131656481923073'


@patch('os.getenv', getenv)
@patch('requests_oauthlib.OAuth1Session.post', mock_response('twitter.tweet'))
@patch('time.sleep', lambda i: None)
def test_tweet():
    actor = Actor(LocalMemoryEngine(), [], {})
    args, func = actor.match('tweet the cat sat on the mat')
    data = func(*args)
    assert data['id_str'] == '1221133422271389697'


@patch('os.getenv', getenv)
@patch('requests_oauthlib.OAuth1Session.post', mock_response('twitter.rate_limited'))  # NOQA
@patch('time.sleep', lambda i: None)
def test_rate_limited():
    actor = Actor(LocalMemoryEngine(), [], {})
    args, func = actor.match('tweet the cat sat on the mat')
    data = func(*args)
    assert data is None
