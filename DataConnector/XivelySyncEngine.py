#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('XivelySyncEngine')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import time
import copy
import threading

from   pydispatch import dispatcher

from   EventBus                                  import EventBusClient
from   DustLinkData                              import DustLinkData
from   SmartMeshSDK                              import FormatUtils
from   SmartMeshSDK.protocols.xivelyConnector    import xivelyConnector
                                                        
class XivelySyncEngine(EventBusClient.EventBusClient):
    
    CHECKDELAY     = 5 # in s, delay between verifying that there is so API key
    
    def __init__(self):
        
        # log
        log.info('creating instance')
        
        # store params
        
        # local variables
        self.connector                           = None
        self.lastCheck                           = None
        self.xivelyApiKey                        = None
        self.subscribedMotes                     = []
        self.statusLock                          = threading.Lock()
        self.status                              = {}
        self.status['apiKeySet']                 = 'WAIT...'
        self.status['status']                    = 'DISCONNECTED'
        self.status['numConnectionsOK']          = 0
        self.status['numConnectionsFailed']      = 0
        self.status['numSubscriptionsFailed']    = 0
        self.status['lastConnected']             = None
        self.status['lastDisconnected']          = None
        self.status['numPublishedOK']            = 0
        self.status['numPublishedFail']          = 0
        
        # initialize parent class
        EventBusClient.EventBusClient.__init__(self,
            signal      = 'newDataMirrored',
            cb          = self._publish,
            teardown_cb = self._cleanup,
        )
        self.name                                = 'DataConnector_xivelyConnector'
        
        # connect extra events
        dispatcher.connect(
            self.getStatus,
            signal      = 'xivelystatus',
            weak        = False,
        )
        
        # add stats
    
    #======================== public ==========================================
    
    def getStatus(self):
        with self.statusLock:
           return copy.deepcopy(self.status)
    
    #======================== private =========================================
    
    def _cleanup(self):
        
        # disconnect extra events
        dispatcher.disconnect(
            self.getStatus,
            signal      = 'xivelystatus',
            weak        = False,
        )
    
    def _publish(self,sender,signal,data):
        
        now = time.time()
        dld = DustLinkData.DustLinkData()
        mac = data['mac']
        
        #========== connect/disconnect
        
        if (self.lastCheck==None) or (now-self.lastCheck>self.CHECKDELAY):
            
            # remember I just checked
            self.lastCheck = now
            
            # we need to use "raw" access because dld.getPublisherSettings()
            # does not return all settings
            settings = dld.get(['system','publishers','xively'])
            
            # record the xivelyApiKey
            xivelyApiKey = None
            if ('xivelyApiKey' in settings) and settings['xivelyApiKey']:
                xivelyApiKey = settings['xivelyApiKey']
            
            # update status
            if xivelyApiKey==None:
                with self.statusLock:
                    self.status['apiKeySet']     = 'NO'
            else:
                with self.statusLock:
                    self.status['apiKeySet']     = 'YES'
            
            # decide whether to connect/disconnect
            if   (not self.connector) and xivelyApiKey:
                # connect
                
                # log
                log.info("Connecting to Xively")
                
                # remember API key
                self.xivelyApiKey                = xivelyApiKey
                
                # connect
                try:
                    self.connector = xivelyConnector.xivelyConnector(
                        apiKey                   = self.xivelyApiKey,
                        productName              = 'SmartMesh IP Starter Kit',
                        productDesc              = 'Connecting using DustLink',
                    )
                except Exception as err:
                    
                    # log
                    log.error("Error while connecting to Xively: {0}".format(err))
                    
                    # update status
                    with self.statusLock:
                        self.status['status']    = 'CONNECTION FAILED'
                        self.status['numConnectionsFailed']+= 1
                    
                    # disconnect
                    self._disconnect()
                    
                else:
                    # update status
                    with self.statusLock:
                        self.status['status']              = 'CONNECTED'
                        self.status['numConnectionsOK']   += 1
                        self.status['lastConnected']       = dld.timestampToStringShort(now)
                
            elif ((self.connector) and (not xivelyApiKey)) or (self.xivelyApiKey!=xivelyApiKey):
                
                # disconnect
                self._disconnect()
        
        #========== publish data
        
        if self.connector:
            
            try:
                
                self.connector.publish(
                    mac                          = data['mac'],
                    datastream                   = data['type'],
                    value                        = data['lastvalue'],
                )
                
            except Exception as err:
                
                # log
                log.error(
                    "Error while publishing to {0}/{1}: {2}".format(
                        FormatUtils.formatMacString(mac),
                        data['type'],
                        err,
                    )
                )
                
                # update status
                with self.statusLock:
                    self.status['numPublishedFail']  += 1
                
                # disconnect
                self._disconnect()
                
            else:
                
                # update status
                with self.statusLock:
                    self.status['numPublishedOK']    += 1
        
        #========== subscribe
        
        if self.connector:
            
            if mac not in self.subscribedMotes:
                
                try:
                    
                    if   ('subscribeToLed' in data) and (data['subscribeToLed']):
                        
                        # create datastream
                        self.connector.publish(
                           mac                   = mac,
                           datastream            = 'led',
                           value                 = 0,
                        )
                        
                        # subscribe                    
                        self.connector.subscribe(
                            mac                  = mac,
                            datastream           = 'led',
                            callback             = self._led_cb,
                        )
                    
                except Exception as err:
                    
                    # log
                    log.error(
                        "Error while subscribing to {0}/{1}: {2}".format(
                            FormatUtils.formatMacString(mac),
                            'led',
                            err,
                        )
                    )
                    
                    # update status
                    with self.statusLock:
                        self.status['status']    = 'SUBSCRIPTION FAILED'
                        self.status['numSubscriptionsFailed']  += 1
                    
                    # disconnect
                    self._disconnect()
                    
                else:
                    self.subscribedMotes        += [mac]
    
    def _disconnect(self):
        
        now = time.time()
        dld = DustLinkData.DustLinkData()
        
        # log
        log.info("Disconnecting from Xively")
        
        # close connector
        try:
            self.connector.close()
        except Exception:
            pass # happens when no active subscription
        
        # reset variables
        self.connector                           = None
        self.xivelyApiKey                        = None
        self.subscribedMotes                     = []
        
        # update status
        with self.statusLock:
            self.status['status']                = 'DISCONNECTED'
            self.status['lastDisconnected']      = dld.timestampToStringShort(now)
    
    def _led_cb(self,mac,datastream,value):
        
        # all non-0 values turn LED on
        if value==0:
            value = 0
        else:
            value = 1
        
        dispatcher.send(
            signal        = 'fieldsToMesh_OAPLED',
            data          = {
                'mac':    mac,
                'fields': {
                    'status': value,
                },
            }
        )
