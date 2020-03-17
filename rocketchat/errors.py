
class RocketChatError(Exception):
    """
    Error raised if a Rocketchat api call responds with an error.
    """
    def __init__(self, errorType, error):
        super(RocketChatError, self).__init__(error)
        self.errorType = errorType
        self.error = error
