#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('AppIdentifier')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import time
import struct

from   DustLinkData                    import DustLinkData
from   EventBus                        import EventBusClient
from   SmartMeshSDK.protocols.oap      import OAPDispatcher, \
                                              OAPNotif
from   SmartMeshSDK.IpMgrConnectorMux  import IpMgrConnectorMux, \
                                              IpMgrSubscribe

class AppIdentifier(EventBusClient.EventBusClient):
    
    QUEUESIZE = 100
    
    def __init__(self):
        # log
        log.info('creating instance')
        
        # initialize parent class
        EventBusClient.EventBusClient.__init__(self,
            'notifData',
            self._identifyApp,
            queuesize=self.QUEUESIZE,
        )
        self.name  = 'DataConnector_AppIdentifier'
        
        # add stats
        
        # local variables
        self.oap_dispatch   = OAPDispatcher.OAPDispatcher()
        self.oap_dispatch.register_notif_handler(self._handle_oap_notif)
        self.appTransports  = {}
        
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _identifyApp(self,sender,signal,data):
        
        alreadyDispatchedOap = False
        
        dld = DustLinkData.DustLinkData()
        
        with dld.dataLock:
            # log
            if log.isEnabledFor(logging.DEBUG):
                log.debug('identifying app for data={0}'.format(data))
            
            # get the transports of the apps
            if dld.getFastMode():
                # using caching
                if not self.appTransports:
                    for appName in dld.getAppNames():
                        self.appTransports[appName] = dld.getAppTransport(appName)
            
            else:
                # not using caching
                for appName in dld.getAppNames():
                    self.appTransports[appName] = dld.getAppTransport(appName)
        
        # TODO: add support for OAP, CoAP, MoteRunner
        
        # match incoming data to app
        for appname,(transport,resource) in self.appTransports.items():
            
            if transport == DustLinkData.DustLinkData.APP_TRANSPORT_UDP:
                
                if resource == data['destPort']:
                    
                    packetOut     = {
                        #'timestamp' : data['timestamp'],
                        'timestamp' : time.time(),
                        'mac'       : data['mac'],
                        'payload'   : data['payload'],
                    }
                    
                    # log
                    if log.isEnabledFor(logging.DEBUG):
                        log.debug('coming from app {0}'.format(appname))
                
                    # dispatch
                    self._dispatch (
                        signal        = 'rawAppData_'+ str(appname),
                        data          = packetOut,
                    )
            
            elif transport == DustLinkData.DustLinkData.APP_TRANSPORT_OAP:
                
                if not alreadyDispatchedOap:
                    
                    notifParams = IpMgrConnectorMux.IpMgrConnectorMux.Tuple_notifData(
                        utcSecs        = int(data['timestamp']),
                        utcUsecs       = int((data['timestamp']*1000)%1000),
                        macAddress     = data['mac'],
                        srcPort        = data['srcPort'],
                        dstPort        = data['destPort'],
                        data           = data['payload'],
                    )
                    
                    self.oap_dispatch.dispatch_pkt(IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA, notifParams)
                    
                    alreadyDispatchedOap = True
            
            elif transport == DustLinkData.DustLinkData.APP_TRANSPORT_COAP:
                
                raise NotImplementedError()
                
            elif transport == DustLinkData.DustLinkData.APP_TRANSPORT_MOTERUNNER:
                
                raise NotImplementedError()
                
            else:
                # not transport specified yet. Can happen if  addApp() is
                # called, but not setAppTransport() yet.
                pass
    
    def _handle_oap_notif(self,mac,notif):
        
        # convert MAC to tuple
        mac = tuple(mac)
        
        if isinstance(notif,OAPNotif.OAPTempSample):
            
            appname = 'OAPTemperature'
            
            # attach this app to this mote
            dld = DustLinkData.DustLinkData()
            with dld.dataLock:
                if not dld.getFastMode():
                    try:
                        dld.attachAppToMote(mac,appname)
                    except ValueError:
                        pass # happens when mote not known, app not known, or app already attached to mote
            
            # TODO: use timestamp from packet. Need to sync manager to UTC for that
            
            packetOut     = {
                #'timestamp' : time.mktime(notif.received_timestamp.timetuple()),
                'timestamp' : time.time(),
                'mac'       : mac,
                'payload'   : [ord(b) for b in struct.pack('>h',notif.samples[0])],
            }
            
            # log
            if log.isEnabledFor(logging.DEBUG):
                log.debug('coming from app {0}'.format(appname))
        
            # dispatch
            self._dispatch (
                signal        = 'rawAppData_{0}'.format(appname),
                data          = packetOut,
            )
            