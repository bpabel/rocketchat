"""Python interface for the RocketChat REST API.

This api attempts to mirror the official REST API as close as possible.  The api names
and paths should generally match the same names in the REST API.  Each python endpoint
accepts the same keyword arguments as the REST API.  No attempt has been made to codify
the argument order for each method, so only keyword arguments should be used.

There are a few exceptions to these guidelines:

When the REST api uses the same endpoint with different HTTP methods, like
settings.GET and settings.POST, this api will use appropriate names to
differentiate between the different uses of the same api endpoint.

In cases where the API has a variable endpoint (i.e. where a portion of the endpoint is based
on a variable), the api method will accept a single positional argument (in addition to the
keyword arguments) that will be appended to the api path to create the full endpoint.



>>> from rocketchat import RocketChat
>>> api = RocketChat('http://server.com', 'username', 'password')
>>> api.users.list()
>>> api.channels.list()

>>> api.settings.get('blah')
>>> api.settings.set('blah', value=True)


"""
from __future__ import absolute_import, division, print_function, unicode_literals
from pprint import pprint
import inspect
import json

import requests


class RocketChatError(Exception):
    
    def __init__(self, errorType, error):
        self.errorType = errorType
        self.error = error
        super(RocketChatError, self).__init__(error)


class APIPath(object):
    """Descriptor object for defining RocketChat API calls.

    """

    def __init__(self, path, method='GET', arg_endpoint=False, result_key=None):
        """

        :param path: API endpoint (e.g. users.create)
        :param method: HTTP method (e.g. GET, POST, DELETE).  If None is given, this will not
            be a valid endpoint and will raise an error if called as one.
        :param arg_endpoint: If True, this APIPath will accept a single positional argument that
            will be added to the api path with a preceding slash to create the final
            endpoint. (e.g. api.settings.get('ARG') -> /settings/ARG
        :param result_key: A specific key in the returned json object that should be returned
            instead of the entire json response object.
        """
        self._path = path
        self._method = method
        self._arg_endpoint = arg_endpoint
        self._result_key = result_key
        self._api = None

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self._path))

    def __repr__(self):
        args = inspect.getargspec(self.__init__).args[1:]
        attrs = ['{}={}'.format(arg, repr(getattr(self, '_' + arg))) for arg in args]
        return '{}({})'.format(self.__class__.__name__, ', '.join(attrs))

    def _propagate_api(self):
        """Propogate the RocketChat api class down to all sublevel api calls.

        Since only the top level APIPath definitions are class attributes (the sublevel
        APIPath definitions are instance attributes on the top level APIPath definitions),
        only the top level APIPath's will receive a __get__ call from the API instance.
        This will pass the api instance down to all child APIPaths.

        """
        for name, attr in self.__dict__.items():
            if isinstance(attr, APIPath):
                attr._api = self._api
                attr._propagate_api()

    def __get__(self, obj, objtype):
        if self._api is None:
            self._api = obj
            self._propagate_api()
        return self

    def __set__(self, obj, value):
        raise AttributeError('APIPaths are read-only')

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
    """Python interface to the RocketChat REST API.

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
    groups.setType = APIPath('groups.setType', 'POST', result_key='group')
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

    def login(self, username=None, password=None):
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        data = {'username': self.username, 'password': self.password}
        r = requests.post(self._url('login'), data=data)
        j = r.json()
        if j['status'] != 'success':
            raise Exception(j['message'])
        self.user_id = j['data']['userId']
        self.auth_token = j['data']['authToken']




