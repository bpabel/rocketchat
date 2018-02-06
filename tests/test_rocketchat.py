
import pytest
import mock
from mock import patch

from rocketchat import RocketChat


url = ''
username = ''
password = ''


@pytest.fixture
def api()
    return RocketChat(url, username, password)


def test_login():
    with patch.object(RocketChat, 'login'):
        api = RocketChat(url, username, password)

    r = api.login()
    assert False
    