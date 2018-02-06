"""

>>> api = RocketChat('http://server.com', 'username', 'password')
>>> api.users.create()
>>> api.channels.addAll()



"""

from pprint import pprint

import requests


class APINamespace(object):

    def __init__(self, name):
        self._name = name
        self._api = None

    def __get__(self, obj, objtype):
        if self._api is None:
            self._api = obj
        return self



class RocketChat(object):
    
    users = APINamespace('users')
    channels = APINamespace('channels')
    groups = APINamespace('groups')
    chat = APINamespace('chat')
    im = APINamespace('im')
    commands = APINamespace('commands')

    users.create = None

    api_path = '/api/v1/'

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.login()

    def _url(path):
        return self.url + self.api_path + path

    def _post(path, data)
        requests.post(self._url(path), data=data)

    def login(self):
        data = {'username': self.username, 'password': self.password}
        r = requests.post(self._url('login'), data=data)
        pprint(r.json())

    def me(self):
        pass



