class DustLinkDataException(Exception) :
    def __init__(self, reason=""):
        self.value = reason

    def __str__(self) :
        return "{0}".format(self.value)

class Malformed(DustLinkDataException):
    pass
