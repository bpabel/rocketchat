from pprint import pprint
import inspect
import json
from typing import Optional, Union

import requests


class RocketChatError(Exception):
    def __init__(self, errorType, error):
        super(RocketChatError, self).__init__(error)
        self.errorType = errorType
        self.error = error
        


class APIPath(object):
    """
    Descriptor object for defining RocketChat API calls.
    """

    def __init__(
        self,
        path: str,
        method: Union[str, None] = "GET",
        arg_endpoint: bool = False,
        result_key: Optional[str] = None,
        auth: bool = True,
        api_root: str = "/api/v1/"
    ):
        """
        Args:
            path: API endpoint (e.g. users.create)
            method: HTTP method (e.g. GET, POST, DELETE). Defaults to "GET", if
                set to None, it will not be a valid endpoint and will raise an 
                exception if called as one.
            arg_endpoint: If True, this APIPath will accept a single positional 
                argument that will be added to the api path with a preceding 
                slash to create the final endpoint. (e.g. api.settings.get('ARG') -> /settings/ARG
            result_key: A specific key in the returned json object that should 
                be returned instead of the entire json response object.
        """
        self._path = path
        self._method = method
        self._arg_endpoint = arg_endpoint
        self._result_key = result_key
        self._api = None

    def __get__(self, obj, objtype):
        if self._api is None:
            self._api = obj
            self._propagate_api()
        return self

    def __set__(self, obj, value):
        raise AttributeError("APIPaths are read-only")

    def __delete__(self, obj):
        raise AttributeError("APIPaths are read-only")

    def __set_name__(self, owner, name):
        pass

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, repr(self._path))

    def __repr__(self):
        args = inspect.getargspec(self.__init__).args[1:]
        attrs = ["{}={}".format(arg, repr(getattr(self, "_" + arg))) for arg in args]
        return "{}({})".format(self.__class__.__name__, ", ".join(attrs))

    def _propagate_api(self):
        """
        Propogate the RocketChat api class down to all sublevel api calls.

        Since only the top level APIPath definitions are class attributes (the sublevel
        APIPath definitions are instance attributes on the top level APIPath definitions),
        only the top level APIPath's will receive a __get__ call from the API instance.
        This will pass the api instance down to all child APIPaths.

        """
        for name, attr in self.__dict__.items():
            if isinstance(attr, APIPath):
                attr._api = self._api
                attr._propagate_api()

    def _url(self, path):
        return self._api.url + self._api.api_v1_path + path

    def __call__(self, *args, **kwargs):
        if self._method is None:
            raise Exception("Not a valid endpoint: {}".format(self._path))

        if self._method == "GET":
            params = kwargs
            data = None
        else:
            params = None
            data = json.dumps(kwargs)

        url = self._url(self._path)
        if self._arg_endpoint:
            url += "/{}".format(args[0])
        headers = self._api.auth_header()

        r = requests.request(
            method=self._method, url=url, params=params, data=data, headers=headers,
        )
        try:
            result = r.json()
        except Exception:
            print("RESPONSE")
            print("Status:", r.status_code)
            print("Text:", r.text)
            raise

        if "error" in result:
            raise RocketChatError(result["errorType"], result["error"])

        if self._result_key is not None:
            result = result[self._result_key]
        return result


class RocketChat(object):
    """Python interface to the RocketChat REST API.

    """

    me = APIPath("me")
    info = APIPath("info", result_key="info", auth=False, api_root="/api/")
    directory = APIPath("directory")
    spotlight = APIPath("spotlight")
    statistics = APIPath("statistics")
    statistics.list = APIPath("statistics.list")

    assets = APIPath("assets", None)
    assets.setAsset = APIPath("assets.setAsset", "POST", result_key="success")
    assets.unsetAsset = APIPath("assets.unsetAsset", "POST", result_key="success")

    autotranslate = APIPath("autotranslate", None)
    autotranslate.getSupportedLanguages = APIPath("autotranslate.getSupportedLanguages", result_key="languages")
    autotranslate.saveSettings =  APIPath("autotranslate.saveSettings", "POST", result_key="success")
    autotranslate.translateMessage = APIPath("autotranslate.translateMessage", "POST", result_key="message")

    logout = APIPath("logout", "POST")

    users = APIPath("users", None)
    users.presence = APIPath("users.presence")
    users.create = APIPath("users.create", "POST", result_key="user")
    users.createToken = APIPath("users.createToken", "POST", result_key="data")
    users.delete = APIPath("users.delete", "POST", result_key="success")
    users.deleteOwnAccount = APIPath("users.deleteOwnAccount", "POST")
    users.forgotPassword = APIPath("users.forgotPassword", "POST")
    users.generatePersonalAccessToken = APIPath("users.generatePersonalAccessToken", "POST")
    users.getAvatar = APIPath("users.getAvatar", "GET")
    users.getPersonalAccessTokens = APIPath("users.getPersonalAccessTokens", "GET")
    users.getPreferences = APIPath("users.getPreferences", "GET")
    users.getPresence = APIPath("users.getPresence", "GET", result_key="presence")
    users.getUsernameSuggestion = APIPath("users.getUsernameSuggestion", "GET")
    users.info = APIPath("users.info", "GET", result_key="user")
    users.list = APIPath("users.list", "GET")
    users.regeneratePersonalAccessToken = APIPath("users.regeneratePersonalAccessToken", "POST")
    users.register = APIPath("users.register", "POST", result_key="user")
    users.removePersonalAccessToken = APIPath("users.removePersonalAccessToken", "POST")
    users.requestDataDownload = APIPath("users.requestDataDownload")
    users.resetAvatar = APIPath("users.resetAvatar", "POST", result_key="success")
    users.setAvatar = APIPath("users.setAvatar", "POST", result_key="success")
    users.setPreferences = APIPath("users.setPreferences", "POST")
    users.setActiveStatus = APIPath("users.setActiveStatus", "POST")
    users.update = APIPath("users.update", "POST", result_key="user")
    users.updateOwnBasicInfo = APIPath("users.updateOwnBasicInfo", "POST")

    channels = APIPath("channels", None)
    channels.addAll = APIPath("channels.addAll", "POST", result_key="channel")
    channels.addLeader = APIPath("channels.addLeader", "POST")
    channels.anonymousread  = APIPath("channels.anonymousread")
    channels.archive = APIPath("channels.archive", "POST", result_key="success")
    channels.cleanHistory = APIPath(
        "channels.cleanHistory", "POST", result_key="success"
    )
    channels.close = APIPath("channels.close", "POST", result_key="success")
    channels.counters = APIPath("channels.counters")
    channels.create = APIPath("channels.create", "POST", result_key="channel")
    channels.delete = APIPath("channels.delete", "POST")
    channels.files = APIPath("channels.files")
    channels.getAllUserMentionsByChannel = APIPath("channels.getAllUserMentionsByChannel")
    channels.getIntegrations = APIPath(
        "channels.getIntegrations", "GET", result_key="integrations"
    )
    channels.history = APIPath("channels.history", "GET", result_key="messages")
    channels.info = APIPath("channels.info", "GET", result_key="channel")
    channels.invite = APIPath("channels.invite", "POST", result_key="channel")
    channels.join = APIPath("channels.join", "POST")
    channels.kick = APIPath("channels.kick", "POST", result_key="channel")
    channels.leave = APIPath("channels.leave", "POST", result_key="channel")
    channels.list = APIPath("channels.list", "GET", result_key="channels")
    channels.list.joined = APIPath("channels.list.joined", "GET", result_key="channels")
    channels.members = APIPath("channels.members")
    channels.messages = APIPath("channels.mesages")
    channels.moderators = APIPath("channels.moderators")
    channels.online = APIPath("channels.online")
    channels.open = APIPath("channels.open", "POST", result_key="success")
    channels.removeLeader = APIPath("channels.removeLeader", "POST")
    channels.rename = APIPath("channels.rename", "POST", result_key="channel")
    channels.roles = APIPath("channels.roles")
    channels.setCustomFields = APIPath("channels.setCustomFields", "POST")
    channels.setAnnouncement = APIPath("channels.setAnnouncement", "POST")
    channels.setDefault = APIPath("channels.setDefault", "POST")
    channels.setDescription = APIPath(
        "channels.setDescription", "POST", result_key="description"
    )
    channels.setJoinCode = APIPath("channels.setJoinCode", "POST", result_key="channel")
    channels.setPurpose = APIPath("channels.setPurpose", "POST", result_key="purpose")
    channels.setReadOnly = APIPath("channels.setReadOnly", "POST", result_key="channel")
    channels.setTopic = APIPath("channels.setTopic", "POST", result_key="topic")
    channels.setType = APIPath("channels.setType", "POST", result_key="channel")
    channels.unarchive = APIPath("channels.unarchive", "POST", result_key="success")

    groups = APIPath("groups", None)
    groups.archive = APIPath("groups.archive", "POST")
    groups.addLeader = APIPath("groups.addLeader", "POST")
    groups.close = APIPath("groups.close", "POST")
    groups.create = APIPath("groups.create", "POST")
    groups.delete = APIPath("groups.delete", "POST")
    groups.files = APIPath("groups.files", "POST")
    groups.history = APIPath("groups.history", "GET")
    groups.info = APIPath("groups.info", "GET")
    groups.invite = APIPath("groups.invite", "POST")
    groups.kick = APIPath("groups.kick", "POST")
    groups.leave = APIPath("groups.leave", "POST")
    groups.list = APIPath("groups.list", "GET")
    groups.listAll = APIPath("groups.listAll")
    groups.members = APIPath("groups.members")
    groups.messages = APIPath("groups.messages")
    groups.moderators = APIPath("groups.moderators")
    groups.open = APIPath("groups.open", "POST")
    groups.removeLeader = APIPath("groups.removeLeader", "POST")
    groups.rename = APIPath("groups.rename", "POST")
    groups.roles = APIPath("groups.roles")
    groups.setAnnouncement = APIPath("groups.setAnnouncement", "POST")
    groups.setCustomFields = APIPath("groups.setCustomFields", "POST")
    groups.setDescription = APIPath("groups.setDescription", "POST")
    groups.setPurpose = APIPath("groups.setPurpose", "POST")
    groups.setReadOnly = APIPath("groups.setReadOnly", "POST")
    groups.setTopic = APIPath("groups.setTopic", "POST")
    groups.setType = APIPath("groups.setType", "POST", result_key="group")
    groups.unarchive = APIPath("groups.unarchive", "POST")

    chat = APIPath("chat", None)
    chat.delete = APIPath("chat.delete", "POST")
    chat.followMessage = APIPath("chat.followMessage", "POST")
    chat.getDeletedMessages = APIPath("chat.getDeletedMessages")
    chat.getDiscussions = APIPath("chat.getDiscussions")
    chat.getMentionedMessages = APIPath("chat.getMentionedMessages")
    chat.getMessage = APIPath("chat.getMessage", "POST")
    chat.getMessageReadReceipts = APIPath("chat.getMessageReadReceipts")
    chat.getPinnedMessages = APIPath("chat.getPinnedMessages")
    chat.getSnippetedMessages = APIPath("chat.getSnippetedMessages")
    chat.getSnippetedMessageById = APIPath("chat.getSnippetedMessageById")
    chat.getStarredMessages = APIPath("chat.getStarredMessages")
    chat.getThreadsList = APIPath("chat.getThreadsList")
    chat.ignoreUser = APIPath("chat.ignoreUser")
    chat.pinMessage = APIPath("chat.pinMessage", "POST")
    chat.postMessage = APIPath("chat.postMessage", "POST")
    chat.react = APIPath("chat.react", "POST")
    chat.reportMessage = APIPath("chat.reportMessage", "POST")
    chat.search = APIPath("chat.search", "POST")
    chat.starMessage = APIPath("chat.starMessage", "POST")
    chat.sendMessage = APIPath("chat.sendMessage", "POST")
    chat.syncThreadMessages = APIPath("chat.syncThreadMessages", "POST")
    chat.syncThreadsList = APIPath("chat.syncThreadsList", "POST")
    chat.unfollowMessage = APIPath("chat.unfollowMessage", "POST")
    chat.unPinMessage = APIPath("chat.unPinMessage", "POST")
    chat.unStarMessage = APIPath("chat.unStarMessage", "POST")
    chat.update = APIPath("chat.update", "POST")

    custom_sounds = APIPath("custom-sounds", None)
    custom_sounds.list = APIPath("custom-sounds.list")

    im = APIPath("im")
    im.close = APIPath("im.close", "POST")
    im.counters = APIPath("im.counters")
    im.create = APIPath("im.create", "POST")
    im.history = APIPath("im.history", "GET")
    im.files = APIPath("im.files")
    im.members = APIPath("im.members")
    im.messages = APIPath("im.messages")
    im.messages.others = APIPath("im.messages.others", "GET")
    im.list = APIPath("im.list", "GET")
    im.list.everyone = APIPath("im.list.everyone", "GET")
    im.open = APIPath("im.open", "POST")
    im.setTopic = APIPath("im.setTopic", "POST")
    dm = im

    integrations = APIPath("integrations", None)
    integrations.create = APIPath("integrations.create", "POST")
    integrations.get = APIPath("integrations.get")
    integrations.history = APIPath("integrations.history")
    integrations.list = APIPath("integrations.list")
    integrations.remove = APIPath("integrations.remove", "POST")
    
    findOrCreateInvite = APIPath("findOrCreateInvite", "POST")
    listInvites = APIPath("listInvites")
    removeInvite = APIPath("removeInvite", "POST")
    useInviteToken = APIPath("useInviteToken", "POST")
    validateInviteToken = APIPath("validateInviteToken", "POST")

    livechat = APIPath("livechat", None)
    livechat.inquiries = APIPath("livechat/inquiries", None)
    livechat.inquiries.list = APIPath("livechat/inquiries.list")
    livechat.inquiries.take = APIPath("livechat/inquiries.take", "POST")
    livechat.rooms = APIPath("livechat/rooms")

    oauth_apps = APIPath("oauth-apps", None)
    oauth_apps.get = APIPath("oauth-apps.get")
    oauth_apps.list = APIPath("oauth-apps.list")

    permissions = APIPath("permissions", None)
    permissions.listAll = APIPath("permissions.listAll")
    permissions.update = APIPath("permissions.update", "POST")

    roles = APIPath("roles", None)
    roles.create = APIPath("roles.create", "POST")
    roles.list = APIPath("roles.list")
    roles.addUserToRole = APIPath("roles.addUserToRole", "POST")
    roles.getUsersInRole = APIPath("roles.getUsersInRole")

    push = APIPath("push", None)
    push.token = APIPath("push.token", None)
    push.token.save = APIPath("push.token", "POST")
    push.token.delete = APIPath("push.token", "DELETE")

    rooms = APIPath("rooms", None)
    rooms.adminRooms = APIPath("rooms.adminRooms")
    rooms.cleanHistory = APIPath("rooms.cleanHistory", "POST")
    rooms.createDiscussion = APIPath("rooms.createDiscussion", "POST")
    rooms.favorite = APIPath("rooms.favorite", "POST")
    rooms.get = APIPath("rooms.get")
    rooms.getDiscussions = APIPath("rooms.getDiscussions")
    rooms.info = APIPath("rooms.info")
    rooms.leave = APIPath("rooms.leave", "POST")
    rooms.saveNotification = APIPath("rooms.saveNotification", "POST")
    rooms.upload = APIPath("rooms.upload", "POST", arg_endpoint=True)

    commands = APIPath("commands")
    commands.get = APIPath("commands.get", "GET")
    commands.list = APIPath("commands.list", "GET")
    commands.run = APIPath("commands.run", "POST")

    custom_user_status = APIPath("custom-user-status", None)
    custom_user_status.list = APIPath("custom-user-status.list")

    emoji_custom = APIPath("emoji-custom", None)
    emoji_custom.list = APIPath("emoji-custom.list")
    emoji_custom.create = APIPath("emoji-custom.create", "POST")
    emoji_custom.delete = APIPath("emoji-custom.delete", "POST")
    emoji_custom.update = APIPath("emoji-custom.update", "POST")

    settings = APIPath("settings", None)
    settings.public = APIPath("settings.public")
    settings.oauth = APIPath("settings.oauth")
    settings.get = APIPath("settings", "GET", arg_endpoint=True)
    settings.set = APIPath("settings", "POST", arg_endpoint=True)

    service = APIPath("service", None)
    service.configurations = APIPath("service.configurations")

    subscriptions = APIPath("subscriptions", None)
    subscriptions.get = APIPath("subscriptions.get")
    subscriptions.getOne = APIPath("subscriptions.getOne")
    subscriptions.read = APIPath("subscriptions.read", "POST")
    subscriptions.unread = APIPath("subscriptions.unread", "POST")

    video_conference = APIPath("video-conference", None)
    video_conference.jitsi = APIPath("video-conference/jitsi", None)
    video_conference.jitsi.update_timeout = APIPath("video-conference/jitsi.update-timeout", "POST")

    webdav = APIPath("webdav", None)
    webdav.getMyAccounts = APIPath("webdav.getMyAccounts")

    def __init__(self, url, username, password):
        self.url = url
        self.user_id = None
        self.auth_token = None
        self.login()

    def auth_header(self):
        return {
            "X-Auth-Token": self.auth_token,
            "X-User-Id": self.user_id,
            "Content-type": "application/json",
        }

    def _url(self, path):
        return self.url + self.api_v1_path + path

    def login(self, **kwargs):
        r = requests.post(self._url("login"), data=kwargs)
        j = r.json()
        if j["status"] != "success":
            raise Exception(j["message"])
        self.user_id = j["data"]["userId"]
        self.auth_token = j["data"]["authToken"]

