#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('NetworkStatePublisher')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading

from   DustLinkData import DustLinkData
from   EventBus     import EventBusClient
from   SmartMeshSDK import FormatUtils

class NetworkStatePublisher(EventBusClient.EventBusClient):
    
    def __init__(self,connectParams):
        
        # log
        log.info("creating instance")
        
        # store params
        self.connectParams        = connectParams
        
        # local variables
        self.netname              = FormatUtils.formatConnectionParams(self.connectParams)
        
        # initialize parent class
        EventBusClient.EventBusClient.__init__(self,
            signal                = 'testResult_{0}'.format(self.netname),
            cb                    = self._ebHandler_testResult,
            teardown_cb           = self._cleanup,
            queuesize             = self.QUEUESIZE,
        )
        self.name                 = '{0}_NetworkStatePublisher'.format(self.netname)
    
    def _cleanup(self):
        pass
    
    #======================== public ==========================================
    
    #======================== eventBus handlers ===============================
    
    #===== testResult
    
    def _ebHandler_testResult(self,sender,signal,data):
        
        dld = DustLinkData.DustLinkData()
        
        dld.addResult(
            netname               = self.netname,
            testName              = data['testName'],
            testDesc              = data['testDesc'],
            outcome               = data['outcome'],
            description           = data['description'],
        )
    
    #======================== private =========================================
    
    #======================== helpers =========================================