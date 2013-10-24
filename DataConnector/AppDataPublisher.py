#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('AppDataPublisher')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import copy
import threading

from DustLinkData import DustLinkData

from EventBus import EventBusClient

class AppDataPublisher(EventBusClient.EventBusClient):
    '''
    \brief Publishes the data into the DustLinkData database.
    
    One instance of this class is created for each application.
    '''
    
    def __init__(self,appName):
        
        # store params
        self._appName = appName
        
        # log
        log.info('creating instance')
        
        # initialize parent class
        EventBusClient.EventBusClient.__init__(self,
            'parsedAppData_{0}'.format(self._appName),
            self._publish,
        )
        self.name  = 'DataConnector_AppDataPublisher_{0}'.format(self._appName)
        
        # add stats
        
        # local variables
        
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _publish(self,sender,signal,data):
        dld = DustLinkData.DustLinkData()
        if not dld.getFastMode():
            
            # add mote if needed
            try:
                dld.addMote(data['mac'])
            except ValueError:
                pass # happens when mote already exists
            
            # in demo mode, add demo mode apps to mote
            if dld.getDemoMode():
                for appname in dld.DEMO_MODE_APPS.keys():
                    try:
                        dld.attachAppToMote(data['mac'],appname)
                    except ValueError:
                        pass # happens when app does not exist, or already attached
            
            # attach app to mote if needed
            try:
                dld.attachAppToMote(data['mac'],self._appName)
            except ValueError:
                pass # happens when app not known, or app already attached to mote
            
            # publish in DustLinkData
            dld.indicateData(data['mac'],
                             self._appName,
                             data['fields'],
                             timestamp=data['timestamp'],
                             )
            
            # log
            if log.isEnabledFor(logging.DEBUG):
                log.debug('published {0}'.format(data))
            