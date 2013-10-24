#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('AppInjector')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import copy
import threading

from   DustLinkData               import DustLinkData
from   EventBus                   import EventBusClient
from   SmartMeshSDK.protocols.oap import OAPMessage

class AppInjector(EventBusClient.EventBusClient):

    def __init__(self,appName):
        
        # store params
        self._appName = appName
        
        # log
        log.info('creating instance')
        
        # initialize parent class
        EventBusClient.EventBusClient.__init__(self,
            'fieldsToMesh_{0}'.format(self._appName),
            self._injectData,
        )
        self.name  = 'DataConnector_AppInjector_{0}'.format(self._appName)
        
        # add stats
        
        # local variables
        
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _injectData(self,sender,signal,data):
        
        try:
            
            # log
            if log.isEnabledFor(logging.DEBUG):
                log.debug('_injectData {0}'.format(data))
            
            dld = DustLinkData.DustLinkData()
            with dld.dataLock:
                (transport,resource) = dld.getAppTransport(self._appName)
                
                if   transport == DustLinkData.DustLinkData.APP_TRANSPORT_UDP:
                    
                    raise NotImplementedError()
                
                elif transport == DustLinkData.DustLinkData.APP_TRANSPORT_OAP:
                    
                    # TODO: handle seq_num and session_id
                    
                    # format data to send
                    if   self._appName=='OAPLED':
                        dataToSend =    OAPMessage.build_oap(
                                            0,                                   # seq_num
                                            0,                                   # session_id
                                            OAPMessage.CmdType.PUT,              # command
                                            [3,2],                               # address
                                            tags=[OAPMessage.TLVByte(t=0,v=data['fields']['status'])],
                                            sync=True
                                        )
                    
                    elif self._appName=='OAPTemperature':
                        dataToSend =    OAPMessage.build_oap(
                                            0,                                   # seq_num
                                            0,                                   # session_id
                                            OAPMessage.CmdType.PUT,              # command
                                            [5],                                 # address
                                            tags=[OAPMessage.TLVByte(t=0,v=1),
                                                  OAPMessage.TLVLong(t=1,v=data['fields']['rate']),],# parameters,
                                            sync=True
                                        )
                        
                    else:
                        raise NotImplementedError()
                    
                    dataToSend = [ord(b) for b in dataToSend]
                    
                    # find netname
                    targetNetname = None
                    for netname in dld.getNetnames():
                        if data['mac'] in dld.getNetworkMotes(netname):
                            targetNetname = netname
                            break
                    
                    if not targetNetname:
                        raise SystemError('no network found which contains {0}'.format(data['mac']))
                    
                    # dispatch
                    self._dispatch (
                        signal        = 'dataToMesh_{0}'.format(targetNetname),
                        data          = {
                            'mac':         data['mac'],
                            'priority':    0,
                            'srcPort':     DustLinkData.DustLinkData.WKP_OAP,
                            'dstPort':     DustLinkData.DustLinkData.WKP_OAP,
                            'options':     0,
                            'data':        dataToSend,
                        },
                    )
                
                elif transport == DustLinkData.DustLinkData.APP_TRANSPORT_COAP:
                    
                    raise NotImplementedError()
                    
                elif transport == DustLinkData.DustLinkData.APP_TRANSPORT_MOTERUNNER:
                    
                    raise NotImplementedError()
                    
                else:
                    
                    raise ValueError('unexpected transport={0}'.format(transport))
        
        except Exception as err:
            import traceback
            traceback.print_exc()
            print err
        