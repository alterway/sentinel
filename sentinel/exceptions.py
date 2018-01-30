class NotImplemented(Exception):
    def __init__(self, message):
        self.message = message


class RegisterFailed(Exception):
    def __init__(self, message):
        self.message = message
