#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('DataVault')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import copy
import threading

from   DataVaultException   import Malformed,    \
                                   Unauthorized, \
                                   NotFound
from   PersistenceException import PersistenceException, \
                                   MalformedDataLocation
import PersistenceEngineNone
import PersistenceEngineFile


def synchronized(method):
    """ Work with instance method only !!! """

    def new_method(self, *arg, **kws):
        with self.lock:
            return method(self, *arg, **kws)
    return new_method

class DataVault(object):
    
    ACTION_GET               = 'get'
    ACTION_PUT               = 'put'
    ACTION_DELETE            = 'delete'
    ACTION_ALL               = [ACTION_GET,
                                ACTION_PUT,
                                ACTION_DELETE]
    
    USER_ADMIN               = 'admin'
    USER_SYSTEM              = '_system'
    USER_ANONYMOUS           = 'anonymous'
    RESTRICTED_USERNAMES     = (USER_ADMIN, USER_SYSTEM)
    
    PERSISTENCE_NONE         = 'persistence none'
    PERSISTENCE_FILE         = 'persistence file'
    PERSISTENCE_ALL          = [PERSISTENCE_NONE,
                                PERSISTENCE_FILE]
    
    #======================== singleton pattern ===============================
    
    _instance = None
    _init     = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            log.info("creating instance")
            cls._instance = super(DataVault, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    #======================== init ============================================
    
    def __init__(self,persistenceType=PERSISTENCE_NONE,
                      persistenceLocation='datavault.backup',
                      putDefaultData=True,
                      validateDataIntegrity=True,
                      indicateSystemevents=True,
                      setDemoModeByDefault=True,
                      addDefaultManagerConnections=True):
        
        # don't re-initialize an instance (needed because singleton)
        if self._init:
            return
        self._init = True
        
        # log
        log.debug("initializing instance")
        
        # check params
        assert persistenceType in self.PERSISTENCE_ALL
        
        # store params
        self.persistenceType                = persistenceType
        self.persistenceLocation            = persistenceLocation
        self.putDefaultData                 = putDefaultData
        self.validateDataIntegrity          = validateDataIntegrity
        self.indicateSystemevents           = indicateSystemevents
        self.setDemoModeByDefault           = setDemoModeByDefault
        self.addDefaultManagerConnections   = addDefaultManagerConnections
        
        # localvariables
        self.dataLock                       = threading.RLock()
        self.data                           = {}
        
        # create a persistenceEngine
        if   persistenceType in [self.PERSISTENCE_NONE]:
            self.persistenceEngine          = PersistenceEngineNone.PersistenceEngineNone(self.get)
        elif persistenceType in [self.PERSISTENCE_FILE]:
            self.persistenceEngine          = PersistenceEngineFile.PersistenceEngineFile(self.get)
            self.persistenceEngine.setSavedDataLocation(self.persistenceLocation)
        
        # populate the data
        try:
            self.data = self.persistenceEngine.retrieveData()
        except PersistenceException as err:
            if isinstance(err,MalformedDataLocation):
                self.persistenceEngine.quarantineData()
            if putDefaultData:
                self._putDefaultData()
                if indicateSystemevents:
                    self._indicateLoadedDefaultData()
            if isinstance(err,MalformedDataLocation):
                if indicateSystemevents:
                    self._indicatePersistenceCorrupted() # do last
        else:
            if indicateSystemevents:
                self._indicatePersistenceLoaded()
        
        # check the integrity of the data found
        if validateDataIntegrity:
            self._validateDataIntegrity()
        
        # start the persistence engine
        self.persistenceEngine.start()
    
    @property
    def lock(self):
        return self.dataLock
    
    def close(self):
        
        # log
        log.debug("closing instance")
        
        # stop the peristence engine
        self.persistenceEngine.stop()
        
        # delete the singleton
        self._instance = None
        self._init     = False
    
    #======================== public ==========================================
    
    @synchronized
    def get(self,resource=None,username=USER_SYSTEM, createCopy=True):
        # authorize access
        self.authorize(username,resource,self.ACTION_GET)
        
        # return a copy of resource
        # Note: the line below implicitly checks that the resource exists
        data = self.getDataAtResource(resource)
        if createCopy:
            return copy.deepcopy(data)
        else:
            return data
    
    @synchronized
    def put(self,resource,newValue,username=USER_SYSTEM):
        # authorize access
        self.authorize(username,resource,self.ACTION_PUT)
        
        # convert resource to list
        resource = self._convertResource(resource)
        
        # walk, create resource
        datawalker = self.data
        log.debug("start walking")
        for i in range(len(resource)):
            if resource[i] not in datawalker:
                datawalker[resource[i]] = {}
            if  (
                    (i!=len(resource)-1)
                    and 
                    (not isinstance(datawalker[resource[i]],dict))
                ):
                datawalker[resource[i]] = {}
            datawalker = datawalker[resource[i]]
        
        # walk, add data
        datawalker = self.data
        for i in range(len(resource)):
            if i==len(resource)-1:
                datawalker[resource[i]] = newValue
            else:
                datawalker = datawalker[resource[i]]
    
    @synchronized
    def delete(self,resource,username=USER_ADMIN):
        # authorize access
        self.authorize(username,resource,self.ACTION_DELETE)
        
        # convert resource to list
        resource = self._convertResource(resource)
        
        # make sure resource exists
        self.checkExists(resource)
        
        # walk, delete resource
        datawalker = self.data
        for i in range(len(resource)):
                if i==len(resource)-1:
                    del datawalker[resource[i]]
                else:
                    datawalker = datawalker[resource[i]]

    @synchronized
    def setPersistence(self,persistenceType):
        
        if persistenceType not in self.PERSISTENCE_ALL:
            raise ValueError('invalid persistenceType {0}'.format(persistenceType))
        
        if  persistenceType==self.persistenceType:
            # nothing to do
            return
        
        # store type new persistenceEngine
        self.persistenceType = persistenceType
        
        # stop old persistence
        self.persistenceEngine.stop()
        
        # create new persistenceEngine
        if   persistenceType in (self.PERSISTENCE_NONE):
            self.persistenceEngine     = PersistenceEngineNone.PersistenceEngineNone(self.get)
        elif persistenceType in (self.PERSISTENCE_FILE):
            self.persistenceEngine     = PersistenceEngineFile.PersistenceEngineFile(self.get)
            self.persistenceEngine.setSavedDataLocation(self.persistenceLocation)
        
        # start new persistenceEngine
        self.persistenceEngine.start()
    
    #======================== abstract methods ================================
    
    def _indicateLoadedDefaultData(self):
        raise NotImplementedError()    # to be implemented by child class
    
    def _indicatePersistenceCorrupted(self):
        raise NotImplementedError()    # to be implemented by child class
    
    def _indicatePersistenceLoaded(self):
        raise NotImplementedError()    # to be implemented by child class
    
    def _putDefaultData(self):
        raise NotImplementedError()    # to be implemented by child class
    
    def _validateDataIntegrity(self):
        raise NotImplementedError()    # to be implemented by child class
    
    #======================== private =========================================

    @synchronized    
    def _factoryReset(self):
        # populate the data with default data
        self._putDefaultData()
        
        # check the integrity of the default data
        self._validateDataIntegrity()
    
        # save the changed data
        self.persistenceEngine.indicateChange()
    
    def authorize(self,username,resource,action):
        '''
        \note No checking by default. Overwrite in child class if needed.
        '''
        pass
    
    def checkExists(self,resource):
        '''
        \note Assumes data is already locked.
        '''
        self._dataWalker(resource)
    
    def getDataAtResource(self,resource):
        '''
        \note Assumes data is already locked.
        '''
        return self._dataWalker(resource)
    
    def _dataWalker(self,resource):
        '''
        \note Assumes data is already locked.
        '''
        
        if not resource:
            return self.data
        
        resource = self._convertResource(resource)
        
        try:
            datawalker = self.data
            for key in resource:
                if not isinstance(datawalker,dict):
                    raise NotFound('.'.join(["{0}".format(r) for r in resource]))
                datawalker = datawalker[key]
        except KeyError:
            raise NotFound('.'.join(["{0}".format(r) for r in resource]))
        else:
            return datawalker
    
    #======================== helpers =========================================
    
    def _convertResource(self,resource):
        assert type(resource) in [list,str,tuple]
        if type(resource)==str:
            resource = [resource]
        output = []
        for r in resource:
            if type(r)==list:
                output += r
            else:
                output += [r]
        return output
    
    