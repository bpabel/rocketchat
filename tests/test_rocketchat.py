from __future__ import print_function
import os
import time
import json
from pprint import pprint

import pytest
import mock
from mock import patch

from rocketchat import RocketChat
    

_RC = None


def get_login_info():
    with open(os.path.normpath(os.path.join(os.path.abspath(__file__), '../config.json')), 'r') as f:
        d = json.load(f)
    return d['url'], d['username'], d['password']


@pytest.fixture
def api():
    global _RC
    if _RC is None:
        url, username, password = get_login_info()
        _RC = RocketChat(url, username, password)
    return _RC


def test_login():
    url, username, password = get_login_info()
    with patch.object(RocketChat, 'login'):
        api = RocketChat(url, username, password)

    r = api.login()
    assert False
    

def test_users_info(api):
    info = api.users.info(username='babel')
    assert info['username'] == 'babel'


def test_channels_list(api):
    channels = api.channels.list()
    pprint(channels)

    joined = api.channels.list.joined()
    pprint(joined)
    assert False


def test_channels(api):
    name = 'mytestchannel'
    channel = api.channels.create(name=name, members=['babel'], readOnly=False)
    assert channel['name'] == name
    _id = channel['_id']
    
    channel = api.channels.info(roomId=channel['_id'])
    assert channel['_id'] == _id

    channel = api.channels.info(roomName=channel['name'])
    assert channel['_id'] == _id

    channel = api.channels.rename(roomId=channel['_id'], name='mytestchannel2')
    assert channel['_id'] == _id
    assert channel['name'] == 'mytestchannel2'

    desc = api.channels.setDescription(roomId=channel['_id'], description='test description')
    assert desc == 'test description'
    
    purpose = api.channels.setPurpose(roomId=channel['_id'], purpose='test purpose')
    assert purpose == 'test purpose'

    channel = api.channels.setReadOnly(roomId=channel['_id'], readOnly=True)
    assert channel['ro'] == True
    channel = api.channels.setReadOnly(roomId=channel['_id'], readOnly=False)
    assert channel['ro'] == False

    topic = api.channels.setTopic(roomId=channel['_id'], topic='test topic')
    assert topic == 'test topic'

    channel = api.channels.setType(roomId=channel['_id'], type='p')
    assert channel['t'] == 'p'
    time.sleep(5.0)
    channel = api.channels.setType(roomId=channel['_id'], type='c')
    assert channel['t'] == 'c'

    r = api.channels.archive(roomId=channel['_id'])
    assert r == True
    
    r = api.channels.unarchive(roomId=channel['_id'])
    assert r == True


