#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('DustLink')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import time
import traceback

from pydispatch import dispatcher

from Gateway       import Gateway
from DataConnector import DataConnector
from DustLinkData  import DustLinkData

class DustLink(threading.Thread):
    
    REFRESH_PERIOD = 10.0 # in seconds
    
    def __init__(self,refresh_period=REFRESH_PERIOD):
        
        # log
        log.info('creating instance')
        
        # store params
        self.refresh_period       = refresh_period
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name                 = 'DustLink'
        
        # local variables
        self.goOn                 = True
        self.dataLock             = threading.Lock()
        self.gateway              = None
        self.lbr                  = None
        self.dataConnector        = None
        
        # connect to dispatcher
        dispatcher.connect(
            self.tearDown,
            signal = 'tearDown',
            weak   = False,
        )
        
        # start itself
        self.start()
    
    def run(self):
        
        dld = DustLinkData.DustLinkData()
        
        try:
            
            # log
            log.info("thread started")
            
            while self.goOn:
                
                # log
                if log.isEnabledFor(logging.DEBUG):
                    log.debug("updating DustLink modules")
                    authCache = dld.authCache
                    log.debug("Authentication cache hits={0}, misses={1}, size={2}".format(authCache.getHit(), authCache.getMiss(), authCache.getSize()))
                
                # update modules
                self._updateGateway()
                self._updateLbr()
                self._updateDataConnector()
                self._updatePersistence()
                
                # sleep a bit
                time.sleep(self.refresh_period)
            
            # disconnect from dispatcher
            dispatcher.disconnect(
                self.tearDown,
                signal = 'tearDown',
                weak   = False,
            )
            
            # log
            log.info('thread ended')
            
        except Exception as err:
            output  = []
            output += ['===== crash in thread {0} ====='.format(self.name)]
            output += ['\nerror:\n']
            output += [str(err)]
            output += ['\ncall stack:\n']
            output += [traceback.format_exc()]
            output  = '\n'.join(output)
            print output # critical error
            log.critical(output)
            raise
    
    #======================== public ==========================================
    
    def tearDown(self):
        
        # log
        log.info('tearDown() called')
        
        # kill the child threads
        if self.gateway:
            self.gateway.tearDown()
        if self.lbr:
            self.lbr.tearDown()
        if self.dataConnector:
            self.dataConnector.tearDown()
        
        # cause the main loop to stop
        self.goOn = False
    
    #======================== private =========================================
    
    def _updateGateway(self):
        dld = DustLinkData.DustLinkData()
        with dld.dataLock:
            if  (DustLinkData.DustLinkData.MODULE_GATEWAY in dld.getEnabledModules()):
                if not self.gateway:
                    log.info('starting gateway')
                    self.gateway = Gateway.Gateway()
            else:
                if self.gateway:
                    log.info('stopping gateway')
                    self.gateway.tearDown()
                    self.gateway = None
    
    def _updateLbr(self):
        pass
    
    def _updateDataConnector(self):
        dld = DustLinkData.DustLinkData()
        with dld.dataLock:
            if  (DustLinkData.DustLinkData.MODULE_DATACONNECTOR in dld.getEnabledModules()):
                if not self.dataConnector:
                    log.info('starting dataConnector')
                    self.dataConnector = DataConnector.DataConnector()
            else:
                if self.dataConnector:
                    log.info('stopping dataConnector')
                    self.dataConnector.tearDown()
                    self.dataConnector = None
    
    def _updatePersistence(self):
        dld = DustLinkData.DustLinkData()
        with dld.dataLock:
            activePersistence = dld.getEnabledPersistence()
            
            if not activePersistence:
                activePersistence = DustLinkData.DustLinkData.PERSISTENCE_NONE
            else:
                assert len(activePersistence)==1
                activePersistence = activePersistence[0]
            
            dld.setPersistence(activePersistence)
