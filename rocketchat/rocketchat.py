import logging
from typing import Optional

import requests

from .apipath import APIPath

LOG = logging.getLogger(__name__)


class RocketChat(object):
    """
    Python interface to the RocketChat REST API.
    """

    def __init__(
        self, url: str, username: Optional[str] = None, password: Optional[str] = None
    ):
        self.url = url
        self.user_id = None
        self.auth_token = None
        self.login()

        # fmt:off
        self.me = APIPath(self, "me")
        self.info = APIPath(self, "info", result_key="info", auth=False, api_root="/api/")
        self.directory = APIPath(self, "directory")
        self.spotlight = APIPath(self, "spotlight")
        self.statistics = APIPath(self, "statistics")
        self.statistics.list = APIPath(self, "statistics.list")

        self.assets = APIPath(self, "assets", None)
        self.assets.setAsset = APIPath(self, "assets.setAsset", "POST", result_key="success")
        self.assets.unsetAsset = APIPath(self, "assets.unsetAsset", "POST", result_key="success")

        self.autotranslate = APIPath(self, "autotranslate", None)
        self.autotranslate.getSupportedLanguages = APIPath(self, "autotranslate.getSupportedLanguages", result_key="languages")
        self.autotranslate.saveSettings = APIPath(self, "autotranslate.saveSettings", "POST", result_key="success")
        self.autotranslate.translateMessage = APIPath(self, "autotranslate.translateMessage", "POST", result_key="message")

        self.logout = APIPath(self, "logout", "POST")

        self.users = APIPath(self, "users", None)
        self.users.presence = APIPath(self, "users.presence")
        self.users.create = APIPath(self, "users.create", "POST", result_key="user")
        self.users.createToken = APIPath(self, "users.createToken", "POST", result_key="data")
        self.users.delete = APIPath(self, "users.delete", "POST", result_key="success")
        self.users.deleteOwnAccount = APIPath(self, "users.deleteOwnAccount", "POST")
        self.users.forgotPassword = APIPath(self, "users.forgotPassword", "POST")
        self.users.generatePersonalAccessToken = APIPath(self, "users.generatePersonalAccessToken", "POST")
        self.users.getAvatar = APIPath(self, "users.getAvatar", "GET")
        self.users.getPersonalAccessTokens = APIPath(self, "users.getPersonalAccessTokens", "GET")
        self.users.getPreferences = APIPath(self, "users.getPreferences", "GET")
        self.users.getPresence = APIPath(self, "users.getPresence", "GET", result_key="presence")
        self.users.getUsernameSuggestion = APIPath(self, "users.getUsernameSuggestion", "GET")
        self.users.info = APIPath(self, "users.info", "GET", result_key="user")
        self.users.list = APIPath(self, "users.list", "GET")
        self.users.regeneratePersonalAccessToken = APIPath(self, "users.regeneratePersonalAccessToken", "POST")
        self.users.register = APIPath(self, "users.register", "POST", result_key="user")
        self.users.removePersonalAccessToken = APIPath(self, "users.removePersonalAccessToken", "POST")
        self.users.requestDataDownload = APIPath(self, "users.requestDataDownload")
        self.users.resetAvatar = APIPath(self, "users.resetAvatar", "POST", result_key="success")
        self.users.setAvatar = APIPath(self, "users.setAvatar", "POST", result_key="success")
        self.users.setPreferences = APIPath(self, "users.setPreferences", "POST")
        self.users.setActiveStatus = APIPath(self, "users.setActiveStatus", "POST")
        self.users.update = APIPath(self, "users.update", "POST", result_key="user")
        self.users.updateOwnBasicInfo = APIPath(self, "users.updateOwnBasicInfo", "POST")

        self.channels = APIPath(self, "channels", None)
        self.channels.addAll = APIPath(self, "channels.addAll", "POST", result_key="channel")
        self.channels.addLeader = APIPath(self, "channels.addLeader", "POST")
        self.channels.anonymousread  = APIPath(self, "channels.anonymousread")
        self.channels.archive = APIPath(self, "channels.archive", "POST", result_key="success")
        self.channels.cleanHistory = APIPath(self, "channels.cleanHistory", "POST", result_key="success")
        self.channels.close = APIPath(self, "channels.close", "POST", result_key="success")
        self.channels.counters = APIPath(self, "channels.counters")
        self.channels.create = APIPath(self, "channels.create", "POST", result_key="channel")
        self.channels.delete = APIPath(self, "channels.delete", "POST")
        self.channels.files = APIPath(self, "channels.files")
        self.channels.getAllUserMentionsByChannel = APIPath(self, "channels.getAllUserMentionsByChannel")
        self.channels.getIntegrations = APIPath(self, "channels.getIntegrations", "GET", result_key="integrations")
        self.channels.history = APIPath(self, "channels.history", "GET", result_key="messages")
        self.channels.info = APIPath(self, "channels.info", "GET", result_key="channel")
        self.channels.invite = APIPath(self, "channels.invite", "POST", result_key="channel")
        self.channels.join = APIPath(self, "channels.join", "POST")
        self.channels.kick = APIPath(self, "channels.kick", "POST", result_key="channel")
        self.channels.leave = APIPath(self, "channels.leave", "POST", result_key="channel")
        self.channels.list = APIPath(self, "channels.list", "GET", result_key="channels")
        self.channels.list.joined = APIPath(self, "channels.list.joined", "GET", result_key="channels")
        self.channels.members = APIPath(self, "channels.members")
        self.channels.messages = APIPath(self, "channels.mesages")
        self.channels.moderators = APIPath(self, "channels.moderators")
        self.channels.online = APIPath(self, "channels.online")
        self.channels.open = APIPath(self, "channels.open", "POST", result_key="success")
        self.channels.removeLeader = APIPath(self, "channels.removeLeader", "POST")
        self.channels.rename = APIPath(self, "channels.rename", "POST", result_key="channel")
        self.channels.roles = APIPath(self, "channels.roles")
        self.channels.setCustomFields = APIPath(self, "channels.setCustomFields", "POST")
        self.channels.setAnnouncement = APIPath(self, "channels.setAnnouncement", "POST")
        self.channels.setDefault = APIPath(self, "channels.setDefault", "POST")
        self.channels.setDescription = APIPath(self, "channels.setDescription", "POST", result_key="description")
        self.channels.setJoinCode = APIPath(self, "channels.setJoinCode", "POST", result_key="channel")
        self.channels.setPurpose = APIPath(self, "channels.setPurpose", "POST", result_key="purpose")
        self.channels.setReadOnly = APIPath(self, "channels.setReadOnly", "POST", result_key="channel")
        self.channels.setTopic = APIPath(self, "channels.setTopic", "POST", result_key="topic")
        self.channels.setType = APIPath(self, "channels.setType", "POST", result_key="channel")
        self.channels.unarchive = APIPath(self, "channels.unarchive", "POST", result_key="success")

        self.groups = APIPath(self, "groups", None)
        self.groups.archive = APIPath(self, "groups.archive", "POST")
        self.groups.addLeader = APIPath(self, "groups.addLeader", "POST")
        self.groups.close = APIPath(self, "groups.close", "POST")
        self.groups.create = APIPath(self, "groups.create", "POST")
        self.groups.delete = APIPath(self, "groups.delete", "POST")
        self.groups.files = APIPath(self, "groups.files", "POST")
        self.groups.history = APIPath(self, "groups.history", "GET")
        self.groups.info = APIPath(self, "groups.info", "GET")
        self.groups.invite = APIPath(self, "groups.invite", "POST")
        self.groups.kick = APIPath(self, "groups.kick", "POST")
        self.groups.leave = APIPath(self, "groups.leave", "POST")
        self.groups.list = APIPath(self, "groups.list", "GET")
        self.groups.listAll = APIPath(self, "groups.listAll")
        self.groups.members = APIPath(self, "groups.members")
        self.groups.messages = APIPath(self, "groups.messages")
        self.groups.moderators = APIPath(self, "groups.moderators")
        self.groups.open = APIPath(self, "groups.open", "POST")
        self.groups.removeLeader = APIPath(self, "groups.removeLeader", "POST")
        self.groups.rename = APIPath(self, "groups.rename", "POST")
        self.groups.roles = APIPath(self, "groups.roles")
        self.groups.setAnnouncement = APIPath(self, "groups.setAnnouncement", "POST")
        self.groups.setCustomFields = APIPath(self, "groups.setCustomFields", "POST")
        self.groups.setDescription = APIPath(self, "groups.setDescription", "POST")
        self.groups.setPurpose = APIPath(self, "groups.setPurpose", "POST")
        self.groups.setReadOnly = APIPath(self, "groups.setReadOnly", "POST")
        self.groups.setTopic = APIPath(self, "groups.setTopic", "POST")
        self.groups.setType = APIPath(self, "groups.setType", "POST", result_key="group")
        self.groups.unarchive = APIPath(self, "groups.unarchive", "POST")

        self.chat = APIPath(self, "chat", None)
        self.chat.delete = APIPath(self, "chat.delete", "POST")
        self.chat.followMessage = APIPath(self, "chat.followMessage", "POST")
        self.chat.getDeletedMessages = APIPath(self, "chat.getDeletedMessages")
        self.chat.getDiscussions = APIPath(self, "chat.getDiscussions")
        self.chat.getMentionedMessages = APIPath(self, "chat.getMentionedMessages")
        self.chat.getMessage = APIPath(self, "chat.getMessage", "POST")
        self.chat.getMessageReadReceipts = APIPath(self, "chat.getMessageReadReceipts")
        self.chat.getPinnedMessages = APIPath(self, "chat.getPinnedMessages")
        self.chat.getSnippetedMessages = APIPath(self, "chat.getSnippetedMessages")
        self.chat.getSnippetedMessageById = APIPath(self, "chat.getSnippetedMessageById")
        self.chat.getStarredMessages = APIPath(self, "chat.getStarredMessages")
        self.chat.getThreadsList = APIPath(self, "chat.getThreadsList")
        self.chat.ignoreUser = APIPath(self, "chat.ignoreUser")
        self.chat.pinMessage = APIPath(self, "chat.pinMessage", "POST")
        self.chat.postMessage = APIPath(self, "chat.postMessage", "POST")
        self.chat.react = APIPath(self, "chat.react", "POST")
        self.chat.reportMessage = APIPath(self, "chat.reportMessage", "POST")
        self.chat.search = APIPath(self, "chat.search", "POST")
        self.chat.starMessage = APIPath(self, "chat.starMessage", "POST")
        self.chat.sendMessage = APIPath(self, "chat.sendMessage", "POST")
        self.chat.syncThreadMessages = APIPath(self, "chat.syncThreadMessages", "POST")
        self.chat.syncThreadsList = APIPath(self, "chat.syncThreadsList", "POST")
        self.chat.unfollowMessage = APIPath(self, "chat.unfollowMessage", "POST")
        self.chat.unPinMessage = APIPath(self, "chat.unPinMessage", "POST")
        self.chat.unStarMessage = APIPath(self, "chat.unStarMessage", "POST")
        self.chat.update = APIPath(self, "chat.update", "POST")

        self.custom_sounds = APIPath(self, "custom-sounds", None)
        self.custom_sounds.list = APIPath(self, "custom-sounds.list")

        self.im = APIPath(self, "im")
        self.im.close = APIPath(self, "im.close", "POST")
        self.im.counters = APIPath(self, "im.counters")
        self.im.create = APIPath(self, "im.create", "POST")
        self.im.history = APIPath(self, "im.history", "GET")
        self.im.files = APIPath(self, "im.files")
        self.im.members = APIPath(self, "im.members")
        self.im.messages = APIPath(self, "im.messages")
        self.im.messages.others = APIPath(self, "im.messages.others", "GET")
        self.im.list = APIPath(self, "im.list", "GET")
        self.im.list.everyone = APIPath(self, "im.list.everyone", "GET")
        self.im.open = APIPath(self, "im.open", "POST")
        self.im.setTopic = APIPath(self, "im.setTopic", "POST")
        self.dm = self.im

        self.integrations = APIPath(self, "integrations", None)
        self.integrations.create = APIPath(self, "integrations.create", "POST")
        self.integrations.get = APIPath(self, "integrations.get")
        self.integrations.history = APIPath(self, "integrations.history")
        self.integrations.list = APIPath(self, "integrations.list")
        self.integrations.remove = APIPath(self, "integrations.remove", "POST")
        
        self.findOrCreateInvite = APIPath(self, "findOrCreateInvite", "POST")
        self.listInvites = APIPath(self, "listInvites")
        self.removeInvite = APIPath(self, "removeInvite", "POST")
        self.useInviteToken = APIPath(self, "useInviteToken", "POST")
        self.validateInviteToken = APIPath(self, "validateInviteToken", "POST")

        self.livechat = APIPath(self, "livechat", None)
        self.livechat.inquiries = APIPath(self, "livechat/inquiries", None)
        self.livechat.inquiries.list = APIPath(self, "livechat/inquiries.list")
        self.livechat.inquiries.take = APIPath(self, "livechat/inquiries.take", "POST")
        self.livechat.rooms = APIPath(self, "livechat/rooms")

        self.oauth_apps = APIPath(self, "oauth-apps", None)
        self.oauth_apps.get = APIPath(self, "oauth-apps.get")
        self.oauth_apps.list = APIPath(self, "oauth-apps.list")

        self.permissions = APIPath(self, "permissions", None)
        self.permissions.listAll = APIPath(self, "permissions.listAll")
        self.permissions.update = APIPath(self, "permissions.update", "POST")

        self.roles = APIPath(self, "roles", None)
        self.roles.create = APIPath(self, "roles.create", "POST")
        self.roles.list = APIPath(self, "roles.list")
        self.roles.addUserToRole = APIPath(self, "roles.addUserToRole", "POST")
        self.roles.getUsersInRole = APIPath(self, "roles.getUsersInRole")

        self.push = APIPath(self, "push", None)
        self.push.token = APIPath(self, "push.token", None)
        self.push.token.save = APIPath(self, "push.token", "POST")
        self.push.token.delete = APIPath(self, "push.token", "DELETE")

        self.rooms = APIPath(self, "rooms", None)
        self.rooms.adminRooms = APIPath(self, "rooms.adminRooms")
        self.rooms.cleanHistory = APIPath(self, "rooms.cleanHistory", "POST")
        self.rooms.createDiscussion = APIPath(self, "rooms.createDiscussion", "POST")
        self.rooms.favorite = APIPath(self, "rooms.favorite", "POST")
        self.rooms.get = APIPath(self, "rooms.get")
        self.rooms.getDiscussions = APIPath(self, "rooms.getDiscussions")
        self.rooms.info = APIPath(self, "rooms.info")
        self.rooms.leave = APIPath(self, "rooms.leave", "POST")
        self.rooms.saveNotification = APIPath(self, "rooms.saveNotification", "POST")
        self.rooms.upload = APIPath(self, "rooms.upload", "POST", arg_endpoint=True)

        self.commands = APIPath(self, "commands")
        self.commands.get = APIPath(self, "commands.get", "GET")
        self.commands.list = APIPath(self, "commands.list", "GET")
        self.commands.run = APIPath(self, "commands.run", "POST")

        self.custom_user_status = APIPath(self, "custom-user-status", None)
        self.custom_user_status.list = APIPath(self, "custom-user-status.list")

        self.emoji_custom = APIPath(self, "emoji-custom", None)
        self.emoji_custom.list = APIPath(self, "emoji-custom.list")
        self.emoji_custom.create = APIPath(self, "emoji-custom.create", "POST")
        self.emoji_custom.delete = APIPath(self, "emoji-custom.delete", "POST")
        self.emoji_custom.update = APIPath(self, "emoji-custom.update", "POST")

        self.settings = APIPath(self, "settings", None)
        self.settings.public = APIPath(self, "settings.public")
        self.settings.oauth = APIPath(self, "settings.oauth")
        self.settings.get = APIPath(self, "settings", "GET", arg_endpoint=True)
        self.settings.set = APIPath(self, "settings", "POST", arg_endpoint=True)

        self.service = APIPath(self, "service", None)
        self.service.configurations = APIPath(self, "service.configurations")

        self.subscriptions = APIPath(self, "subscriptions", None)
        self.subscriptions.get = APIPath(self, "subscriptions.get")
        self.subscriptions.getOne = APIPath(self, "subscriptions.getOne")
        self.subscriptions.read = APIPath(self, "subscriptions.read", "POST")
        self.subscriptions.unread = APIPath(self, "subscriptions.unread", "POST")

        self.video_conference = APIPath(self, "video-conference", None)
        self.video_conference.jitsi = APIPath(self, "video-conference/jitsi", None)
        self.video_conference.jitsi.update_timeout = APIPath(self, "video-conference/jitsi.update-timeout", "POST")

        self.webdav = APIPath(self, "webdav", None)
        self.webdav.getMyAccounts = APIPath(self, "webdav.getMyAccounts")
        # fmt:on

    def auth_header(self):
        """
        Return api request header dictionary with Auth data.
        """
        return {
            "X-Auth-Token": self.auth_token,
            "X-User-Id": self.user_id,
            "Content-type": "application/json",
        }

    def login(self, **kwargs):
        """
        Authenticate this Rocketchat API.
        """
        url = self.url + self.api_v1_path + "login"
        r = requests.post(url, data=kwargs)
        j = r.json()
        if j["status"] != "success":
            raise Exception(j["message"])
        self.user_id = j["data"]["userId"]
        self.auth_token = j["data"]["authToken"]
