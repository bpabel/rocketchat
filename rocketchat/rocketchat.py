"""Python wrapper for the RocketChat REST API.

>>> from rocketchat import RocketChat
>>> api = RocketChat('http://server.com', 'username', 'password')
>>> api.users.list()
>>> api.channels.list()

>>> api.settings.get('blah')
>>> api.settings.set('blah', value=True)


"""
from __future__ import print_function
from pprint import pprint
import json

import requests


class RocketChatError(Exception):
    
    def __init__(self, errorType, error):
        self.errorType = errorType
        self.error = error
        message = '{}: {}'.format(errorType, error)
        super(RocketChatError, self).__init__(message)


class APIPath(object):
    """Descriptor object for defining RocketChat API calls.


    """

    def __init__(self, path, method='GET', arg_endpoint=False, result_key=None):
        self._path = path
        self._method = method
        self._arg_endpoint = arg_endpoint
        self._result_key = result_key
        self._api = None

    def _propagate_api(self):
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, APIPath):
                attr._api = self._api
                attr._propagate_api()

    def __get__(self, obj, objtype):
        if self._api is None:
            self._api = obj
            self._propagate_api()
        return self

    def __set__(self, obj, value):
        return None

    def _url(self, path):
        return self._api.url + self._api.api_v1_path + path

    def __call__(self, *args, **kwargs):
        if self._method is None:
            raise Exception('Not a valid endpoint: {}'.format(self._path))

        if self._method == 'GET':
            params = kwargs
            data = None
        else:
            params = None
            data = json.dumps(kwargs)

        url = self._url(self._path)
        if self._arg_endpoint:
            url += '/{}'.format(args[0])
        headers = self._api.auth_header()

        r = requests.request(
            method=self._method,
            url=url,
            params=params,
            data=data, 
            headers=headers,
            )
        r.raise_for_status()
        try:        
            result = r.json()
        except Exception:
            print('RESPONSE')
            print('Status:', r.status_code)
            print('Text:', r.text)
            raise

        if 'error' in result:
            raise RocketChatError(result['errorType'], result['error'])

        if self._result_key is not None:
            result = result[self._result_key]
        return result


class RocketChat(object):
    """


    """
    
    api_v1_path = '/api/v1/'

    me = APIPath('me', 'GET')
    info = APIPath('info', 'GET', result_key='info')

    users = APIPath('users', None)
    users.create = APIPath('users.create', 'POST', result_key='user')
    users.createToken = APIPath('users.createToken', 'POST', result_key='data')
    users.delete = APIPath('users.delete', 'POST', result_key='success')
    users.getAvatar = APIPath('users.getAvatar', 'GET')
    users.getPresence = APIPath('users.getPresence', 'GET', result_key='presence')
    users.info = APIPath('users.info', 'GET', result_key='user')
    users.list = APIPath('users.list', 'GET')
    users.register = APIPath('users.register', 'POST', result_key='user')
    users.resetAvatar = APIPath('users.resetAvatar', 'POST', result_key='success')
    users.setAvatar = APIPath('users.setAvatar', 'POST', result_key='success')
    users.update = APIPath('users.update', 'POST', result_key='user')

    channels = APIPath('channels', None)
    channels.addAll = APIPath('channels.addAll', 'POST', result_key='channel')
    channels.archive = APIPath('channels.archive', 'POST', result_key='success')
    channels.cleanHistory = APIPath('channels.cleanHistory', 'POST', result_key='success')
    channels.close = APIPath('channels.close', 'POST', result_key='success')
    channels.create = APIPath('channels.create', 'POST', result_key='channel')
    channels.getIntegrations = APIPath('channels.getIntegrations', 'GET', result_key='integrations')
    channels.history = APIPath('channels.history', 'GET', result_key='messages')
    channels.info = APIPath('channels.info', 'GET', result_key='channel')
    channels.invite = APIPath('channels.invite', 'POST', result_key='channel')
    channels.kick = APIPath('channels.kick', 'POST', result_key='channel')
    channels.leave = APIPath('channels.leave', 'POST', result_key='channel')
    channels.list = APIPath('channels.list', 'GET', result_key='channels')
    channels.list.joined = APIPath('channels.list.joined', 'GET', result_key='channels')
    channels.open = APIPath('channels.open', 'POST', result_key='success')
    channels.rename = APIPath('channels.rename', 'POST', result_key='channel')
    channels.setDescription = APIPath('channels.setDescription', 'POST', result_key='description')
    channels.setJoinCode = APIPath('channels.setJoinCode', 'POST', result_key='channel')
    channels.setPurpose = APIPath('channels.setPurpose', 'POST', result_key='purpose')
    channels.setReadOnly = APIPath('channels.setReadOnly', 'POST', result_key='channel')
    channels.setTopic = APIPath('channels.setTopic', 'POST', result_key='topic')
    channels.setType = APIPath('channels.setType', 'POST', result_key='channel')
    channels.unarchive = APIPath('channels.unarchive', 'POST', result_key='success')
    
    groups = APIPath('groups', None)
    groups.archive = APIPath('groups.archive', 'POST')
    groups.close = APIPath('groups.close', 'POST')
    groups.create = APIPath('groups.create', 'POST')
    groups.history = APIPath('groups.history', 'GET')
    groups.info = APIPath('groups.info', 'GET')
    groups.invite = APIPath('groups.invite', 'POST')
    groups.kick = APIPath('groups.kick', 'POST')
    groups.leave = APIPath('groups.leave', 'POST')
    groups.list = APIPath('groups.list', 'GET')
    groups.open = APIPath('groups.open', 'POST')
    groups.rename = APIPath('groups.rename', 'POST')
    groups.setDescription = APIPath('groups.setDescription', 'POST')
    groups.setPurpose = APIPath('groups.setPurpose', 'POST')
    groups.setReadOnly = APIPath('groups.setReadOnly', 'POST')
    groups.setTopic = APIPath('groups.setTopic', 'POST')
    groups.setType = APIPath('groups.setType', 'POST')
    groups.unarchive = APIPath('groups.unarchive', 'POST')

    chat = APIPath('chat', None)
    chat.delete = APIPath('chat.delete', 'POST')
    chat.getMessage = APIPath('chat.getMessage', 'POST')
    chat.pinMessage = APIPath('chat.pinMessage', 'POST')
    chat.postMessage = APIPath('chat.postMessage', 'POST')
    chat.react = APIPath('chat.react', 'POST')
    chat.starMessage = APIPath('chat.starMessage', 'POST')
    chat.unPinMessage = APIPath('chat.unPinMessage', 'POST')
    chat.unStarMessage = APIPath('chat.unStarMessage', 'POST')
    chat.update = APIPath('chat.update', 'POST')

    im = APIPath('im')
    im.close = APIPath('im.close', 'POST')
    im.history = APIPath('im.history', 'GET')
    im.messages = APIPath('im.messages', None)
    im.messages.others = APIPath('im.messages.others', 'GET')
    im.list = APIPath('im.list', 'GET')
    im.list.everyone = APIPath('im.list.everyone', 'GET')
    im.open = APIPath('im.open', 'POST')
    im.setTopic = APIPath('im.setTopic', 'POST')
    dm = im

    commands = APIPath('commands')
    commands.get = APIPath('commands.get', 'GET')
    commands.list = APIPath('commands.list', 'GET')
    commands.run = APIPath('commands.run', 'POST')

    settings = APIPath('settings', None)
    settings.get = APIPath('settings', 'GET', arg_endpoint=True)
    settings.set = APIPath('settings', 'POST', arg_endpoint=True)

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.user_id = None
        self.auth_token = None
        self.login()

    def auth_header(self):
        return {
            'X-Auth-Token': self.auth_token,
            'X-User-Id': self.user_id,
            'Content-type': 'application/json'
        } 

    def _url(self, path):
        return self.url + self.api_v1_path + path

    def login(self):
        data = {'username': self.username, 'password': self.password}
        r = requests.post(self._url('login'), data=data)
        j = r.json()
        if j['status'] != 'success':
            raise Exception(j['message'])
        self.user_id = j['data']['userId']
        self.auth_token = j['data']['authToken']




