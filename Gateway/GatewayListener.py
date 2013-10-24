#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('GatewayListener')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import time
import threading

from   pydispatch            import dispatcher

import SnapShot

from   EventBus                        import EventBusClient
from   SmartMeshSDK                    import FormatUtils, \
                                              ApiConnector, \
                                              ApiException
from   SmartMeshSDK.IpMgrConnectorMux  import IpMgrSubscribe

class GatewayListener(EventBusClient.EventBusClient):
    
    def __init__(self,connector,connectParams):
        assert isinstance(connector,ApiConnector.ApiConnector)
        assert isinstance(connectParams,(str,tuple))
        
        # record parameters
        self.connector            = connector
        self.connectParams        = connectParams
        
        # log
        log.info("creating instance")
        
        # variables
        self.netname              = FormatUtils.formatConnectionParams(self.connectParams)
        self.statsLock            = threading.Lock()
        self._clearStats()
        
        # start snapshot thread this manager
        self.snapShotThread       = SnapShot.SnapShot(connector,connectParams)
        
        # subscribe to flows
        try:
            self.subscriber       = IpMgrSubscribe.IpMgrSubscribe(self.connector)
            self.subscriber.start()
            
            self.subscriber.subscribe(
                notifTypes =    [
                                    IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                                ],
                fun =           self._subs_notifData,
                isRlbl =        False,
            )
            self.subscriber.subscribe(
                notifTypes =    [
                                    IpMgrSubscribe.IpMgrSubscribe.NOTIFEVENT,
                                ],
                fun =           self._subs_notifEvent,
                isRlbl =        True,
            )
            self.subscriber.subscribe(
                notifTypes =    [
                                    IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                                ],
                fun =           self._subs_notifHealthReport,
                isRlbl =        True,
            )
            self.subscriber.subscribe(
                notifTypes =    [
                                    IpMgrSubscribe.IpMgrSubscribe.ERROR,
                                    IpMgrSubscribe.IpMgrSubscribe.FINISH,
                                ],
                fun =           self._subs_errorORfinish,
                isRlbl =        True,
            )
        except TypeError as err:
            log.error(str(err))
            raise ApiException.ConnectionError(str(err))

        self.subscriber._thread.name   = '{0}_IpMgrSubscribe'.format(self.netname)
        
        # initialize parent class
        EventBusClient.EventBusClient.__init__(self,
            'dataToMesh_{0}'.format(self.netname),
            self._ebHandler_dataToMesh,
        )
        
        # give this thread a name
        self.name                 = '{0}_GatewayListener'.format(self.netname)
    
    #======================== public ==========================================
    
    def tearDown(self):
        
        # tear down internal threads
        self.snapShotThread.tearDown()
        
        # call parent class
        super(GatewayListener,self).tearDown()
    
    #======================== eventBus handlers ===============================
    
    #===== dataToMesh
    
    def _ebHandler_dataToMesh(self,sender,signal,data):
        
        try:
            self.connector.dn_sendData(
                macAddress        = data['mac'],
                priority          = data['priority'],
                srcPort           = data['srcPort'],
                dstPort           = data['dstPort'],
                options           = data['options'],
                data              = data['data'],
            )
        except TypeError as err:
            log.error(str(err))
            raise ApiException.ConnectionError(str(err))
    
    #======================== manager subscriptions ===========================
    
    def _subs_notifData(self, notifName, notifParams):
        '''
        \brief Received data from the manager.
        '''
        
        packet = {
            'timestamp':     float(notifParams.utcSecs)+float(notifParams.utcUsecs/1000000.0),
            'mac':           tuple(notifParams.macAddress),
            'srcPort':       notifParams.srcPort,
            'destPort':      notifParams.dstPort,
            'payload':       [b for b in notifParams.data],
        }
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug('dispatching notifData from {0}:{1} to port {2} ({3} bytes)'.format(
                    packet['mac'],
                    packet['srcPort'],
                    packet['destPort'],
                    len(packet['payload'])
                )
            )
        
        # dispatch
        self._dispatch(
            signal       = 'notifData',
            data         = packet,
        )
        
        # increment stats
        self._updateStats(notifName)
    
    def _subs_notifEvent(self, notifName, notifParams):
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug('dispatching notifEvent')
        
        # dispatch
        self._dispatch(
            signal      =   'notifEvent_{0}'.format(self.netname),
            data        =   notifParams,
        )
        
        # increment stats
        self._updateStats(notifName)
    
    def _subs_notifHealthReport(self, notifName, notifParams):
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug('dispatching notifHealthReport')
        
        # dispatch
        self._dispatch(
            signal      =   'notifHealthReport_{0}'.format(self.netname),
            data        =   notifParams,
        )
        
        # increment stats
        self._updateStats(notifName)
    
    def _subs_errorORfinish(self,notifName=None,notifParams=None):
        
        # log
        log.warning('disconnection indication received')
        
        # dispatch
        self._dispatch(
            signal      =   'deviceCommunicationError',
            data        =   {
                                'connectionParam': self.connectParams,
                                'reason':          'disconnection indication received',
                            },
        )
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    
    def _updateStats(self,notifName):
        with self.statsLock:
            if notifName not in self.stats:
                self.stats[notifName] = 0
            self.stats[notifName] += 1
    
    def _clearStats(self):
        with self.statsLock:
            self.statsStarttime   = time.time()
            self.stats            = {}
