class PersistenceException(Exception) :
    def __init__(self, reason=""):
        self.value = reason

    def __str__(self) :
        return "{0}".format(self.value)

class NoSavedDataLocation(PersistenceException):
    '''
    \brief Not saved data location has been specified.
    '''
    pass

class InvalidDataLocation(PersistenceException):
    '''
    \brief Saved data location specified is not a valid location.
    '''
    pass

class NoSavedData(PersistenceException):
    '''
    \brief No saved data.
    '''
    pass

class MalformedDataLocation(PersistenceException):
    '''
    \brief Saved data location specified is malformed.
    '''
    pass

class CouldNotSaveData(PersistenceException):
    '''
    \brief Data to be saved could not be saved.
    '''
    pass
