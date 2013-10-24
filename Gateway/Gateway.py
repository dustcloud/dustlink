#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('Gateway')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import time
import threading
import traceback

from   pydispatch                           import dispatcher

import GatewayListener
import NetworkState
import NetworkStateAnalyzer
import NetworkStatePublisher

from   DustLinkData                         import DustLinkData
from   SmartMeshSDK                         import ApiException, \
                                                   FormatUtils
from   SmartMeshSDK.IpMgrConnectorSerial    import IpMgrConnectorSerial
from   SmartMeshSDK.IpMgrConnectorMux       import IpMgrConnectorMux

class Gateway(threading.Thread):
    
    REFRESH_PERIOD = 10.0 # in seconds
    
    def __init__(self,refresh_period=REFRESH_PERIOD):
        
        # log
        log.info('creating instance')
    
        # store params
        self.refresh_period       = refresh_period
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name                 = 'Gateway'
        
        # local variables
        self.goOn                 = True
        self.dataLock             = threading.Lock()
        self.apiconnectors        = {}
        self.listeners            = {}
        self.netstate             = {}
        self.analyzers            = {}
        self.publishers           = {}
        
        # connect to dispatcher
        dispatcher.connect(
            self.tearDown,
            signal = 'tearDown',
            weak   = False,
        )
        dispatcher.connect(
            self._ebHandler_deviceCommunicationError,
            signal = 'deviceCommunicationError',
            weak   = False,
        )
        
        # start itself
        self.start()
    
    #======================== thread ==========================================
    
    def run(self):
        
        try:
            
            # log
            log.info('thread started')
            
            # run
            while self.goOn:
                
                # update modules
                with self.dataLock:
                    self._updateManagerConnections()
                
                # sleep a bit
                time.sleep(self.refresh_period)
            
            # cleanup
            self._cleanup()
            
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
            print output
            log.critical(output)
            raise
    
    def _cleanup(self):
        
        # kill associated threads
        with self.dataLock:
            for connectParam in self.apiconnectors.keys():
                self._deleteManagerConnection(connectParam)
        
        # disconnect from dispatcher
        dispatcher.disconnect(
            self.tearDown,
            signal = 'tearDown',
            weak   = False,
        )
        dispatcher.disconnect(
            self._ebHandler_deviceCommunicationError,
            signal = 'deviceCommunicationError',
            weak   = False,
        )
    
    #======================== public ==========================================
    
    def tearDown(self):
        
        # log
        log.info('tearDown() called')
        
        # kill main thread (will kill associated threads)
        self.goOn = False
    
    #======================== eventBus handlers ===============================
    
    def _ebHandler_deviceCommunicationError(self,sender,signal,data):
        assert isinstance(data,dict)
        assert sorted(data.keys())==sorted(['connectionParam','reason'])
        
        log.warning('received device communication error for connection {0}'.format(
                data['connectionParam']
            )
        )
        
        dld = DustLinkData.DustLinkData()
        
        with self.dataLock:
            with dld.dataLock:
                # update state
                try:
                    dld.updateManagerConnectionState(
                        data['connectionParam'],
                        DustLinkData.DustLinkData.MANAGERCONNECTION_STATE_FAIL,
                        reason = data['reason'],
                    )
                except ValueError:
                    pass # happens when connection has already been deleted
                
                self._deleteManagerConnection(data['connectionParam'])
    
    #======================== private =========================================
    
    def _updateManagerConnections(self):
        dld = DustLinkData.DustLinkData()
        
        with dld.dataLock:
            # get the connections
            activeConnections     = self.apiconnectors.keys()   # active now
            storedConnections     = dld.getManagerConnections() # should be active
            
            # stop some manager connections
            for active in activeConnections:
                if (not storedConnections) or (active not in storedConnections):
                    self._deleteManagerConnection(active)
            
            # start some manager connections
            if storedConnections:
                for stored in storedConnections:
                    if stored not in activeConnections:
                        self._addManagerConnection(stored)
                    elif storedConnections[stored]['state'] == DustLinkData.DustLinkData.MANAGERCONNECTION_STATE_INACTIVE:
                        self._deleteManagerConnection(stored)
                        self._addManagerConnection(stored)
    
    def _addManagerConnection(self,connectParam):
        dld = DustLinkData.DustLinkData()
        with dld.dataLock:
            
            assert(connectParam not in self.apiconnectors)
            assert(connectParam not in self.listeners)
            assert(connectParam not in self.netstate)
            assert(connectParam not in self.analyzers)
            assert(connectParam not in self.publishers)
            
            try:
                
                #===== self.apiconnectors
                
                if isinstance(connectParam,str):
                    # connecting to a serial port
                    
                    newConnector = IpMgrConnectorSerial.IpMgrConnectorSerial()
                    newConnector.connect({
                        'port': connectParam,
                    })
                else:
                    # connecting to the serialMux
                    
                    newConnector = IpMgrConnectorMux.IpMgrConnectorMux()
                    newConnector.connect({
                        'host': connectParam[0],
                        'port': connectParam[1],
                    })
            
                # log
                log.info('added apiconnectors {0}'.format(connectParam))
                
                self.apiconnectors[connectParam] = newConnector
                
                dld.updateManagerConnectionState(
                    connectParam,
                    DustLinkData.DustLinkData.MANAGERCONNECTION_STATE_ACTIVE
                )
                
                #===== delete network
                
                try:
                    dld.deleteNetwork(FormatUtils.formatConnectionParams(connectParam))
                except ValueError:
                    pass # happens if network doesn't exist
                
                #===== add network
                
                try:
                    dld.addNetwork(FormatUtils.formatConnectionParams(connectParam))
                except ValueError:
                    pass # happens if network already exists from previous connection
                
                #===== self.listeners
                
                assert(connectParam not in self.listeners)
                self.listeners[connectParam]   = GatewayListener.GatewayListener(
                    self.apiconnectors[connectParam],
                    connectParam,
                )
                log.info('added listener {0}'.format(connectParam))
                
                #===== self.netstate
                
                assert(connectParam not in self.netstate)
                self.netstate[connectParam]   = NetworkState.NetworkState(connectParam)
                log.info('added netstate {0}'.format(connectParam))
                
                #===== self.analyzers
                
                assert(connectParam not in self.analyzers)
                self.analyzers[connectParam]   = NetworkStateAnalyzer.NetworkStateAnalyzer(connectParam)
                log.info('added analyzer {0}'.format(connectParam))
                
                #===== self.publishers
                
                assert(connectParam not in self.publishers)
                self.publishers[connectParam]   = NetworkStatePublisher.NetworkStatePublisher(connectParam)
                log.info('added publisher {0}'.format(connectParam))
            
            except Exception as err:
                
                # log
                log.warning('could not add apiconnectors {0}: {1}'.format(connectParam, err))
                
                # update state
                dld.updateManagerConnectionState(
                    connectParam,
                    DustLinkData.DustLinkData.MANAGERCONNECTION_STATE_FAIL,
                    reason = str(err),
                )
                
                # detelete the connection to the manager
                self._deleteManagerConnection(connectParam)
    
    def _deleteManagerConnection(self, connectParam):
        
        dld = DustLinkData.DustLinkData()
        with dld.dataLock:
            
            #===== NetworkStateAnalyzer
            if connectParam in self.publishers:
                self.publishers[connectParam].tearDown()
                del self.publishers[connectParam]
                log.info('deleted publisher {0}'.format(connectParam))
            
            #===== NetworkStateAnalyzer
            if connectParam in self.analyzers:
                self.analyzers[connectParam].tearDown()
                del self.analyzers[connectParam]
                log.info('deleted analyzer {0}'.format(connectParam))
            
            #===== NetworkState
            if connectParam in self.netstate:
                self.netstate[connectParam].tearDown()
                del self.netstate[connectParam]
                log.info('deleted netstate {0}'.format(connectParam))
            
            #===== GatewayListener
            if connectParam in self.listeners:
                self.listeners[connectParam].tearDown()
                del self.listeners[connectParam]
                log.info('deleted listener {0}'.format(connectParam))
            
            #===== apiconnectors
            if connectParam in self.apiconnectors:
                self.apiconnectors[connectParam].disconnect()
                del self.apiconnectors[connectParam]
                log.info('deleted apiconnector {0}'.format(connectParam))
            
            #===== delete network
            try:
                dld.deleteNetwork(FormatUtils.formatConnectionParams(connectParam))
            except ValueError:
                pass # happens if network was already deleted, e.g. by an earlier call to this function
