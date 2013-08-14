class DataVaultException(Exception) :
    def __init__(self, reason=""):
        self.value = reason

    def __str__(self) :
        return "{0}".format(self.value)

class Malformed(DataVaultException):
    pass

class Unauthorized(DataVaultException):
    pass

class NotFound(DataVaultException):
    pass
