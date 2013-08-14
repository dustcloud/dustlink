#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('PersistenceEngineFile')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import os
import pickle
import shutil
import time

import PersistenceEngine
from   PersistenceException import NoSavedDataLocation,    \
                                   InvalidDataLocation,    \
                                   MalformedDataLocation,  \
                                   CouldNotSaveData

class PersistenceEngineFile(PersistenceEngine.PersistenceEngine):
    
    def __init__(self,*args,**kwargs):
        PersistenceEngine.PersistenceEngine.__init__(self,*args,**kwargs)
        self.name = 'PersistenceEngineFile'
    
    def retrieveData(self):
        
        # make sure a savedDataLocation was specified
        if not self.savedDataLocation:
            log.warning('No saved data location')
            raise NoSavedDataLocation()
        
        # open backup file
        try:
            dbfile = open(self.savedDataLocation,'r')
        except IOError:
            log.warning('Invalid data location: {0}'.format(self.savedDataLocation))
            raise InvalidDataLocation()
        
        # read data from backup file
        try:
            dataRead = pickle.load(dbfile)
        except:
            log.warning('Malformed data in {0}'.format(self.savedDataLocation))
            raise MalformedDataLocation()
        
        # log
        log.info("retrieved data from {0}".format(self.savedDataLocation))
        
        # return the data read
        return dataRead
    
    def saveData(self,dataToSave):
        
        # make sure a savedDataLocation was specified
        if not self.savedDataLocation:
            log.warning('No saved data location')
            raise NoSavedDataLocation()
        
        # open new back file
        try:
            dbfile = open(self.savedDataLocation+'.new','w')
        except IOError:
            log.warning('Invalid data location: {0}'.format(self.savedDataLocation))
            raise InvalidDataLocation()
        
        # store data in backup file
        try:
            pickle.dump(dataToSave,dbfile)
        except Exception as err:
            log.warning('Could not save data')
            raise CouldNotSaveData(str(err))
        finally:
            dbfile.close()
        
        # swap new and old
        try:
            os.rename(self.savedDataLocation, self.savedDataLocation+'.old')
        except:
            pass # happens when file does not exist yet
        os.rename(self.savedDataLocation+'.new', self.savedDataLocation)
        try:
            os.remove(self.savedDataLocation+'.old')
        except:
            pass # happens when file does not exist yet
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug('data backed up in {0}'.format(self.savedDataLocation))
    
    def quarantineData(self):
        
        # make sure a savedDataLocation was specified
        if not self.savedDataLocation:
            log.warning('No saved data location')
            raise NoSavedDataLocation()
        
        # rename backup file
        shutil.copyfile(self.savedDataLocation,
                        self.savedDataLocation+'.corrupted-{0}'.format(int(time.time())))
        