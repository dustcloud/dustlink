#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('NetworkState')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading

from   pydispatch   import dispatcher

import Gateway

from   DustLinkData import DustLinkData
from   EventBus     import EventBusClient
from   SmartMeshSDK import FormatUtils, \
                           HrParser
from   SmartMeshSDK.IpMgrConnectorSerial.IpMgrConnectorSerial import IpMgrConnectorSerial
from   SmartMeshSDK.IpMgrConnectorMux.IpMgrConnectorMux       import IpMgrConnectorMux

class NetworkState(EventBusClient.EventBusClient):
    
    QUEUESIZE = 100
    
    def __init__(self,connectParams):
        
        # log
        log.info("creating instance")
        
        # store params
        self.connectParams         = connectParams
        
        # local variables
        self.netname               = FormatUtils.formatConnectionParams(self.connectParams)
        self.hrParser              = HrParser.HrParser()
        self.dataLock              = threading.Lock()
        self.snapPaths             = []
        self.snapshotOngoing       = False
        
        # initialize parent class
        EventBusClient.EventBusClient.__init__(self,
            signal      = 'notifEvent_{0}'.format(self.netname),
            cb          = self._ebHandler_notifEvent,
            teardown_cb = self._cleanup,
            queuesize   = self.QUEUESIZE,
        )
        self.name                  = '{0}_NetworkState'.format(self.netname)
        
        # connect extra applications
        dispatcher.connect(
            self._ebHandler_snapShotStart,
            signal = 'snapShotStart_{0}'.format(self.netname),
            weak   = False,
        )
        dispatcher.connect(
            self._ebHandler_managerCmd,
            signal = 'managerCmd_{0}'.format(self.netname),
            weak   = False,
        )
        dispatcher.connect(
            self._ebHandler_snapShotEnd,
            signal = 'snapShotEnd_{0}'.format(self.netname),
            weak   = False,
        )
        dispatcher.connect(
            self._ebHandler_notifHealthReport,
            signal = 'notifHealthReport_{0}'.format(self.netname),
            weak   = False,
        )
    
    def _cleanup(self):
        
        # disconnect extra applications
        dispatcher.disconnect(
            self._ebHandler_snapShotStart,
            signal = 'snapShotStart_{0}'.format(self.netname),
            weak   = False,
        )
        dispatcher.disconnect(
            self._ebHandler_managerCmd,
            signal = 'managerCmd_{0}'.format(self.netname),
            weak   = False,
        )
        dispatcher.disconnect(
            self._ebHandler_snapShotEnd,
            signal = 'snapShotEnd_{0}'.format(self.netname),
            weak   = False,
        )
        dispatcher.disconnect(
            self._ebHandler_notifHealthReport,
            signal = 'notifHealthReport_{0}'.format(self.netname),
            weak   = False,
        )
    
    #======================== public ==========================================
    
    #======================== eventBus handlers ===============================
    
    #===== snapShotStart
    
    def _ebHandler_snapShotStart(self,sender,signal,data):
        with self.dataLock:
            self.snapshotOngoing  = True
            self.snapPaths        = []
    
    #===== managerCmd
    
    def _ebHandler_managerCmd(self,sender,signal,data):
        if   (isinstance(data,IpMgrConnectorSerial.Tuple_dn_getMoteConfig)     or isinstance(data,IpMgrConnectorMux.Tuple_dn_getMoteConfig)):
            self._handle_getMoteConfig(data)
        elif (isinstance(data,IpMgrConnectorSerial.Tuple_dn_getMoteInfo)       or isinstance(data,IpMgrConnectorMux.Tuple_dn_getMoteInfo)):
            self._handle_getMoteInfo(data)
        elif (isinstance(data,IpMgrConnectorSerial.Tuple_dn_getNextPathInfo)   or isinstance(data,IpMgrConnectorMux.Tuple_dn_getNextPathInfo)):
            self._handle_getNextPathInfo(data)
        else:
            log.warning('unhandled managerCmd {0}'.format(data))
    
    def _handle_getMoteConfig(self,res):
        
        dld      = DustLinkData.DustLinkData()
        mac      = tuple(res.macAddress)
        
        with dld.dataLock:
            self._addNewMoteIfNeeded(mac)
            for k,v in {'moteId':          res.moteId,
                        'isAP':            res.isAP,
                        'state':           res.state,
                        'isRouting':       res.isRouting,}.items():
                dld.setMoteInfo(mac,k,v)
    
    def _handle_getMoteInfo(self,res):
        
        dld      = DustLinkData.DustLinkData()
        mac      = tuple(res.macAddress)
        
        with dld.dataLock:
            self._addNewMoteIfNeeded(mac)
            for k,v in {'state':           res.state,
                        'numNbrs':         res.numNbrs,
                        'numGoodNbrs':     res.numGoodNbrs,
                        'requestedBw':     res.requestedBw,
                        'totalNeededBw':   res.totalNeededBw,
                        'assignedBw':      res.assignedBw,
                        'packetsReceived': res.packetsReceived,
                        'packetsLost':     res.packetsLost,
                        'avgLatency':      res.avgLatency,}.items():
                dld.setMoteInfo(mac,k,v)
    
    def _handle_getNextPathInfo(self,res):
        with self.dataLock:
            self.snapPaths.append(res)
    
    #===== snapShotEnd
    
    def _ebHandler_snapShotEnd(self,sender,signal,data):
        
        dld  = DustLinkData.DustLinkData()
        
        with self.dataLock:
            if self.snapshotOngoing:
                with dld.dataLock:
                    currentPaths  = dld.getNetworkPaths(self.netname)
                    receivedPaths = [(tuple(p.source),tuple(p.dest)) for p in self.snapPaths]
                    
                    # delete paths that have disappeared
                    for path in currentPaths:
                        if path not in receivedPaths:
                            dld.deletePath(self.netname,path[0],path[1])
                    
                    # add paths that have appeared
                    for path in receivedPaths:
                        if path not in currentPaths:
                            dld.addPath(self.netname,path[0],path[1])
                    
                    # update paths
                    for path in self.snapPaths:
                        mac       = tuple(path.source)
                        neighbor  = tuple(path.dest)
                        
                        self._addNewMoteIfNeeded(mac)
                        self._addNewMoteIfNeeded(neighbor)
                        
                        for k,v in {'pathId':          path.pathId,
                                    'direction':       path.direction,
                                    'numLinks':        path.numLinks,
                                    'quality':         path.quality,
                                    'rssiSrcDest':     path.rssiSrcDest,
                                    'rssiDestSrc':     path.rssiDestSrc,}.items():
                            dld.setPathInfo(
                                self.netname,
                                mac,neighbor,
                                k,
                                v
                            )
            
            self.snapshotOngoing  = False
    
    #===== notifHealthReport
    
    def _ebHandler_notifHealthReport(self,sender,signal,data):
        
        dld = DustLinkData.DustLinkData()
        mac = tuple(data.macAddress)
        
        hr  = self.hrParser.parseHr(data.payload)
        
        with dld.dataLock:
            self._addNewMoteIfNeeded(mac)
            
            if 'Device' in hr:
                self._handle_HealthReport_Device(mac,hr['Device'])
            if 'Neighbors' in hr:
                self._handle_HealthReport_Neighbors(mac,hr['Neighbors'])
            if 'Discovered' in hr:
                self._handle_HealthReport_Discovered(mac,hr['Discovered'])
        
    def _handle_HealthReport_Device(self,mac,hr):
        
        dld = DustLinkData.DustLinkData()
        
        with dld.dataLock:
            for k,v in hr.items():
                dld.setMoteInfo(mac,k,v)
    
    def _handle_HealthReport_Neighbors(self,mac,hr):
        
        dld = DustLinkData.DustLinkData()
        
        with dld.dataLock:
            myMac                 = mac
            for neighbor in hr['neighbors']:
                neighborId        = neighbor['neighborId']
                neighborMac       = self._id2mac(neighborId)
                for (k,v) in neighbor.items():
                    dld.setPathInfo(
                        netname   = self.netname,
                        fromMAC   = myMac,
                        toMAC     = neighborMac,
                        infoKey   = k,
                        infoVal   = v,
                    )
    
    def _handle_HealthReport_Discovered(self,mac,hr):
        pass # nothing to do
    
    #===== notifEvent
    
    def _ebHandler_notifEvent(self,sender,signal,data):
        
        if   (isinstance(data,IpMgrConnectorSerial.Tuple_eventMoteCreate)      or isinstance(data,IpMgrConnectorMux.Tuple_eventMoteCreate)):
            self._handle_eventMoteCreate(data)
        elif (isinstance(data,IpMgrConnectorSerial.Tuple_eventMoteJoin)        or isinstance(data,IpMgrConnectorMux.Tuple_eventMoteJoin)):
            self._handle_eventMoteJoin(data)
        elif (isinstance(data,IpMgrConnectorSerial.Tuple_eventMoteOperational) or isinstance(data,IpMgrConnectorMux.Tuple_eventMoteOperational)):
            self._handle_eventMoteOperational(data)
        elif (isinstance(data,IpMgrConnectorSerial.Tuple_eventPathCreate)      or isinstance(data,IpMgrConnectorMux.Tuple_eventPathCreate)):
            self._handle_eventPathCreate(data)
        elif (isinstance(data,IpMgrConnectorSerial.Tuple_eventPathDelete)      or isinstance(data,IpMgrConnectorMux.Tuple_eventPathDelete)):
            self._handle_eventPathDelete(data)
        elif (isinstance(data,IpMgrConnectorSerial.Tuple_eventMoteLost)        or isinstance(data,IpMgrConnectorMux.Tuple_eventMoteLost)):
            self._handle_eventMoteLost(data)
        elif (isinstance(data,IpMgrConnectorSerial.Tuple_eventPacketSent)      or isinstance(data,IpMgrConnectorMux.Tuple_eventPacketSent)):
            pass # nothing to do
        else:
            log.warning('unhandled notifEvent {0}'.format(data))
    
    def _handle_eventMoteCreate(self,event):
        
        dld      = DustLinkData.DustLinkData()
        mac      = tuple(event.macAddress)
        
        with dld.dataLock:
            # add mote if needed
            self._addNewMoteIfNeeded(mac)
            
            # configure the mote's id
            dld.setMoteInfo(mac,'moteId',event.moteId)
    
    def _handle_eventMoteJoin(self,event):
        
        dld      = DustLinkData.DustLinkData()
        mac      = tuple(event.macAddress)
        
        with dld.dataLock:
            # add mote if needed
            self._addNewMoteIfNeeded(mac)
            
            # configure the mote's state
            dld.setMoteInfo(mac,'moteState',1) # state 1=negotiating
    
    def _handle_eventMoteOperational(self,event):
        
        dld      = DustLinkData.DustLinkData()
        mac      = tuple(event.macAddress)
        
        with dld.dataLock:
            # add mote if needed
            self._addNewMoteIfNeeded(mac)
            
            # increment number of joins
            
            # increment the number of joins
            moteInfo = dld.getMoteInfo(mac)
            if 'numOperationalEvents' in moteInfo:
                dld.setMoteInfo(mac,'numOperationalEvents',moteInfo['numOperationalEvents']+1)
            else:
                if (('state' in moteInfo) and (moteInfo['state']==4)):
                    # this mote is already operational, this is at least the second operational event
                    dld.setMoteInfo(mac,'numOperationalEvents',2)
                else:
                    dld.setMoteInfo(mac,'numOperationalEvents',1)
            
            # configure the mote's state
            dld.setMoteInfo(mac,'moteState',4) # state 1=operational
    
    def _handle_eventPathCreate(self,event):
        
        dld  = DustLinkData.DustLinkData()
        
        with self.dataLock:
            if not self.snapshotOngoing:
                with dld.dataLock:
                    source        = tuple(event.source)
                    destination   = tuple(event.dest)
                    
                    # add motes if needed
                    self._addNewMoteIfNeeded(source)
                    self._addNewMoteIfNeeded(destination)
                    
                    thisPath      = (source,destination)
                    currentPaths  = dld.getNetworkPaths(self.netname)
                    
                    # add path
                    if thisPath not in currentPaths:
                        dld.addPath(self.netname,thisPath[0],thisPath[1])
                    
                    # update path info
                    dld.setPathInfo(
                        self.netname,
                        thisPath[0],thisPath[1],
                        'direction',
                        event.direction
                    )
    
    def _handle_eventPathDelete(self,event):
        
        dld  = DustLinkData.DustLinkData()
        
        with self.dataLock:
            if not self.snapshotOngoing:
                with dld.dataLock:
                    source        = tuple(event.source)
                    destination   = tuple(event.dest)
                    
                    # add motes if needed
                    self._addNewMoteIfNeeded(source)
                    self._addNewMoteIfNeeded(destination)
                    
                    thisPath      = (source,destination)
                    reversePath   = (destination, source)
                    currentPaths  = dld.getNetworkPaths(self.netname)
                    
                    # delete path
                    if thisPath in currentPaths:
                        dld.deletePath(self.netname,thisPath[0],thisPath[1])
                    if reversePath in currentPaths:
                        dld.deletePath(self.netname,reversePath[0],reversePath[1])
    
    def _handle_eventMoteLost(self,event):
        
        dld  = DustLinkData.DustLinkData()
        
        with self.dataLock:
            if not self.snapshotOngoing:
                with dld.dataLock:
                    source        = tuple(event.macAddress)
                    
                    # add motes if needed
                    self._addNewMoteIfNeeded(source)
                    
                    currentPaths  = dld.getNetworkPaths(self.netname)
                    
                    # delete path
                    for path in currentPaths:
                        if source == path[0]:
                            dld.deletePath(self.netname,*path)
    
    #======================== helpers =========================================
    
    def _addNewMoteIfNeeded(self,mac):
        
        dld = DustLinkData.DustLinkData()
        
        with dld.dataLock:
            # add mote
            try:
                dld.addMote(mac)
            except ValueError:
                pass # happens when mote already exists
            
            # in demo mode, add demo mode apps to mote
            if dld.getDemoMode():
                moteInfo = dld.getMoteInfo(mac)
                if moteInfo and ('isAP' in moteInfo) and moteInfo['isAP']==0:
                    for appname in dld.DEMO_MODE_APPS.keys():
                        try:
                            dld.attachAppToMote(mac,appname)
                        except ValueError:
                            pass # happens when app does not exist, or already attached
            
            # add mote to network
            try:
                dld.addNetworkMote(
                    self.netname,
                    mac
                )
            except ValueError:
                pass # happens when mote already in network
    
    def _id2mac(self,id):
        
        dld   = DustLinkData.DustLinkData()
        macs  = dld.getNetworkMotes(self.netname)
        
        for mac in macs:
            moteId = dld.getMoteInfo(mac)['moteId']
            if moteId==id:
                return mac
        raise ValueError("Can not find MAC of motedId={0} in network {1}".format(id,self.netname))