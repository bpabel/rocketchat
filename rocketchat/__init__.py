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

from .rocketchat import RocketChat

__version__ = "1.0.0"
