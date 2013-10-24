#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('DataConnector')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import time
import traceback

from pydispatch import dispatcher

import ListenerUdp
import AppIdentifier
import AppPayloadParser
import AppDataPublisher
import AppInjector
import MirrorEngine
import GoogleSyncEngine
import XivelySyncEngine
from   DustLinkData  import DustLinkData
from   DustLinkData  import DataVaultException

class DataConnector(threading.Thread):
    
    REFRESH_PERIOD = 10.0 # in seconds
    
    def __init__(self,refresh_period=REFRESH_PERIOD):
        
        # log
        log.info('creating instance')
        
        # store params
        self.refresh_period  = refresh_period
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name                 = 'DataConnector'
        
        # local variables
        self.goOn                 = True
        self.dataLock             = threading.Lock()
        self.udpListeners         = {}
        self.appIdentifier        = AppIdentifier.AppIdentifier()
        self.appPayloadParsers    = {}
        self.appDataPublishers    = {}
        self.appInjectors         = {}
        self.mirrorEngine         = MirrorEngine.MirrorEngine()
        self.googleSyncEngine     = GoogleSyncEngine.GoogleSyncEngine()
        self.xivelySyncEngine     = XivelySyncEngine.XivelySyncEngine()
        
        # connect to dispatcher
        dispatcher.connect(
            self.tearDown,
            signal = 'tearDown',
            weak   = False,
        )
        
        # start itself
        self.start()
    
    def run(self):
        
        #===== main loop
        
        try:
            
            # log
            log.info('thread started')
            
            while self.goOn:
                
                # log
                if log.isEnabledFor(logging.DEBUG):
                    log.debug("updating dataConnector modules")
                
                # update modules
                #self._updateListeners() Note: uncomment this line to start IPv6/UDP listeners
                self._updateAppModules()
                
                # sleep a bit
                time.sleep(self.refresh_period)
            
            #===== kill associated threads
            
            # udpListeners
            for port,listener in self.udpListeners.items():
                listener.tearDown()
            self.udpListeners          = {}
            
            # appIdentifier
            if self.appIdentifier:
                self.appIdentifier.tearDown()
                self.appIdentifier     = None
            
            # appPayloadParsers
            for app,parser in self.appPayloadParsers.items():
                parser.tearDown()
            self.appPayloadParsers     = {}
            
            # appDataPublishers
            for app,publisher in self.appDataPublishers.items():
                publisher.tearDown()
            self.appDataPublishers     = {}
            
            # appInjectors
            for app,injector in self.appInjectors.items():
                injector.tearDown()
            self.appInjectors          = {}
            
            log.debug('killing mirrorEngine')
            
            # mirrorEngine
            self.mirrorEngine.tearDown()
            self.mirrorEngine          = None
            
            log.debug('killing googleSyncEngine')
            
            # googleSyncEngine
            self.googleSyncEngine.tearDown()
            self.googleSyncEngine      = None
            
            log.debug('killing XivelySyncEngine')
            
            # xivelySyncEngine
            self.xivelySyncEngine.tearDown()
            self.xivelySyncEngine   = None
            
            #===== disconnect from dispatcher
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
        
        # kill main thread (will kill associated threads)
        self.goOn = False
    
    #======================== private =========================================
    
    def _updateListeners(self):
        
        dld = DustLinkData.DustLinkData()
        with dld.dataLock:
            # get the UDP ports
            portsToListenTo = []
            for appName in dld.getAppNames():
                try:
                    t = dld.getAppTransport(appName)
                except (ValueError,DataVaultException.NotFound):
                    # can happen if app was deleted in the meantime
                    pass
                else:
                    transport = t[0]
                    resource  = t[1]
                    if transport == DustLinkData.DustLinkData.APP_TRANSPORT_UDP:
                        if resource not in portsToListenTo:
                            portsToListenTo.append(resource)
        
        if log.isEnabledFor(logging.DEBUG):
            log.debug('listening to {0}, need to listen to {1}'.format(self.udpListeners.keys(),portsToListenTo))
        
        # stop some listeners
        for port in self.udpListeners.keys():
            if port not in portsToListenTo:
                log.info('stopping UDP listener on port {0}'.format(port))
                self.udpListeners[port].tearDown()
                del self.udpListeners[port]
        
        # start some listeners
        for port in portsToListenTo:
            if port not in self.udpListeners.keys():
                log.info('starting UDP listener on port {0}'.format(port))
                self.udpListeners[port] = ListenerUdp.ListenerUdp(port)
    
    def _updateAppModules(self):
        
        # get the app names
        dld = DustLinkData.DustLinkData()
        
        currentAppNames = dld.getAppNames()
        
        #===== appPayloadParsers
        
        # stop some parsers
        for app in self.appPayloadParsers.keys():
            if app not in currentAppNames:
                log.info('stopping app parser for {0}'.format(app))
                self.appPayloadParsers[app].tearDown()
                del self.appPayloadParsers[app]
        
        # start some parsers
        for app in currentAppNames:
            if app not in self.appPayloadParsers.keys():
                log.info('starting app parser for {0}'.format(app))
                self.appPayloadParsers[app] = AppPayloadParser.AppPayloadParser(app)
        
        #===== appDataPublishers
        
        # stop some publishers
        for app in self.appDataPublishers.keys():
            if app not in currentAppNames:
                log.info('stopping app publisher for {0}'.format(app))
                self.appDataPublishers[app].tearDown()
                del self.appDataPublishers[app]
        
        # start some publishers
        for app in currentAppNames:
            if app not in self.appDataPublishers.keys():
                log.info('starting app publisher for {0}'.format(app))
                self.appDataPublishers[app] = AppDataPublisher.AppDataPublisher(app)
        
        #===== appInjectors
        
        # stop some injectors
        for app in self.appInjectors.keys():
            if app not in currentAppNames:
                log.info('stopping app injector for {0}'.format(app))
                self.appInjectors[app].tearDown()
                del self.appInjectors[app]
        
        # start some injectors
        for app in currentAppNames:
            if app not in self.appInjectors.keys():
                log.info('starting app injector for {0}'.format(app))
                self.appInjectors[app] = AppInjector.AppInjector(app)
    