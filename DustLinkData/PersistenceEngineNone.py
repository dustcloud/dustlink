#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('PersistenceEngineNone')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import time

import PersistenceEngine
from   PersistenceException import NoSavedData

class PersistenceEngineNone(PersistenceEngine.PersistenceEngine):
    
    def __init__(self,*args,**kwargs):
        PersistenceEngine.PersistenceEngine.__init__(self,*args,**kwargs)
        self.name = 'PersistenceEngineNone'
    
    def retrieveData(self):
        log.debug("no data to retrieve")
        raise NoSavedData()
    
    def saveData(self,dataToSave):
        log.debug("not saving any data")
        return
    
    def quarantineData(self):
        log.debug("not quarantining any data")
        return
    