#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('SnapShot')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import time
import threading
import traceback

from   pydispatch       import dispatcher

from DustLinkData       import DustLinkData
from   SmartMeshSDK     import FormatUtils, \
                               ApiConnector, \
                               ApiException

class SnapShot(threading.Thread):
    '''
    \brief Thread which periodically takes a snapshot of the network.
    '''
    
    SNAPSHOT_PERIOD_FIRST    = 5                 ##< in seconds
    
    def __init__(self,connector,connectParams):
        
        assert isinstance(connector,ApiConnector.ApiConnector)
        assert isinstance(connectParams,(str,tuple))
        
        # store params
        self.connector                 = connector
        self.connectParams             = connectParams
        
        # local variables
        self.netname                   = FormatUtils.formatConnectionParams(self.connectParams)
        self.goOn                      = True
        self.delayCounter              = self.SNAPSHOT_PERIOD_FIRST
        self.dataLock                  = threading.Lock()
        self.busySnapshotting          = threading.Lock()
        
        # initialize parent
        threading.Thread.__init__(self)
        self.name                      = '{0}_SnapShot'.format(self.netname)
        
        # connect to EventBus
        dispatcher.connect(
            self._timeToNextSnapShot,
            signal = "timeToNextSnapShot_{0}".format(self.netname),
            weak   = False,
        )
        dispatcher.connect(
            self._snapShotNow,
            signal = "snapShotNow_{0}".format(self.netname),
            weak   = False,
        )
        
        # start itself
        self.start()
    
    #======================== thread ==========================================
    
    def run(self):
        
        # log
        log.info('thread {0} started'.format(self.name))
        
        try:
            while self.goOn:
                
                # delay
                time.sleep(1)
                
                # decide whether to snapshot
                with self.dataLock:
                    self.delayCounter      -=1
                    if self.delayCounter<=0:
                        doSnapshot          = True
                        self.delayCounter   = DustLinkData.DustLinkData().getTestPeriod(self.netname)
                    else:
                        doSnapshot          = False
                
                # snapshot
                if doSnapshot:
                    self._doSnapshot()
            
        except (ApiException.ConnectionError,ApiException.CommandTimeoutError) as err:
            
            # log
            log.warning('connection error={0}'.format(err))
            
            # dispatch
            dispatcher.send(
                signal      =   'deviceCommunicationError',
                data        =   {
                                    'connectionParam': self.connectParams,
                                    'reason':          str(err),
                                },
            )
            
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
        
        # disconnect
        dispatcher.disconnect(
            self._timeToNextSnapShot,
            signal = "timeToNextSnapShot_{0}".format(self.netname),
            weak   = False,
        )
        dispatcher.disconnect(
            self._snapShotNow,
            signal = "snapShotNow_{0}".format(self.netname),
            weak   = False,
        )
        
        # log
        log.info('thread {0} ended'.format(self.name))
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _doSnapshot(self):
        
        with self.busySnapshotting:
        
            motes            = []
            
            # dispatch
            dispatcher.send(
                signal       =   'snapShotStart_{0}'.format(self.netname),
                data         =   None,
            )
            
            try:
                # get MAC addresses of all motes
                currentMac     = (0,0,0,0,0,0,0,0) # start getMoteConfig() iteration with the 0 MAC address
                continueAsking = True
                while continueAsking:
                    try:
                        res = self._execCommandAndDispatch(self.connector.dn_getMoteConfig,(currentMac,True))
                    except ApiException.APIError:
                        continueAsking = False
                    else:
                        motes.append(res.macAddress)
                        currentMac = res.macAddress
                
                # getMoteInfo on all motes
                for mac in motes:
                    self._execCommandAndDispatch(self.connector.dn_getMoteInfo,(mac,))
                
                # get path info on all paths of all motes
                for mac in motes:
                    currentPathId  = 0
                    continueAsking = True
                    while continueAsking:
                        try:
                            res = self._execCommandAndDispatch(self.connector.dn_getNextPathInfo,(mac,0,currentPathId))
                        except ApiException.APIError:
                            continueAsking = False
                        else:
                            currentPathId  = res.pathId
                
            except ApiException.APIError as err:
                log.critical("FAILED: {0}".format(str(err)))
            
            # dispatch
            dispatcher.send(
                signal       =   'snapShotEnd_{0}'.format(self.netname),
                data         =   None,
            )
    
    def _timeToNextSnapShot(self):
        with self.dataLock:
            return self.delayCounter
    
    def _snapShotNow(self):
        with self.dataLock:
            self.delayCounter=0
    
    def tearDown(self):
        self.goOn            = False
    
    #======================== private =========================================
    
    def _execCommandAndDispatch(self,func,params):
        
        try:
            res = func(*params)
        except TypeError as err:
            log.error(str(err))
            raise ApiException.ConnectionError(str(err))
        
        # dispatch
        dispatcher.send(
            signal      =   'managerCmd_{0}'.format(self.netname),
            data        =   res,
        )
        
        return res
