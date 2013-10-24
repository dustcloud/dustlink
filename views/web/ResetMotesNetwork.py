#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ResetMotesNetwork')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import time
import threading
import traceback

from pydispatch                 import dispatcher

from DustLinkData               import DustLinkData
from SmartMeshSDK.protocols.oap import OAPMessage

class ResetMotesNetwork(threading.Thread):
    
    MAXWAITFOROAPRESPONSE    = 30      ##< number of seconds to wait for an OAP response
    
    def __init__(self):
        
        # store params
        
        # local variables
        self.waitForResponseEvent      = threading.Event()
        self.responseBufLock           = threading.Lock()
        self.responseBuf               = None
        
        # initialize parent
        threading.Thread.__init__(self)
        self.name                      = 'ResetMotesNetwork'
        
        dispatcher.connect(
            self._dataIndication,
            signal = 'notifData',
            weak   = False,
        )
        
        # start itself
        self.start()
    
    def run(self):
        
        try:
        
            dld = DustLinkData.DustLinkData()
            dld._resetScratchpad()
            
            dld._addScratchpad("<p class=\"doc-header\">Resetting motes.</p>")
            
            for targetMac in dld.getMoteMacs():
                
                dld._addScratchpad("<p class=\"doc-header\">resetting {0}.</p>".format(DustLinkData.DustLinkData.macToString(targetMac)))
                
                moteInfo = dld.getMoteInfo(targetMac)
                
                if moteInfo and ('isAP' in moteInfo) and moteInfo['isAP']==0:
                    
                    #===== find netname
                    
                    targetNet = None
                    for netname in dld.getNetnames():
                        if targetMac in dld.getNetworkMotes(netname):
                            targetNet = netname
                            break
                    
                    if targetNet:
                        dld._addScratchpad("<p>mote is part of network {0}.</p>".format(targetNet))
                    else:
                        dld._addScratchpad("<p>mote is not of any network, skipping.</p>".format(targetNet))
                        continue
                    
                    #===== disabling digital_in
                    
                    for digitalPort in range(4):
                    
                        dld._addScratchpad("<p>disabling digital_in D{0}.</p>".format(digitalPort+1))
                        
                        try:
                            self._sendOapCommand(
                                targetNet   = targetNet,
                                targetMac   = targetMac,
                                oapAddress  = [2,digitalPort],       # 2=digital_in
                                oapTags     = [OAPMessage.TLVByte(t=0,v=0)],
                            )
                        except Exception as err:
                            dld._addScratchpad("<p class=\"doc-warning\">failed: {0}.</p>".format(err))
                        else:
                            dld._addScratchpad("<p class=\"doc-success\">success.</p>")
                    
                    #===== digital_out to 0
                    
                    for pin in range(3):
                    
                        dld._addScratchpad("<p>digital_out pin {0} to zero.</p>".format(pin))
                        
                        try:
                            self._sendOapCommand(
                                targetNet   = targetNet,
                                targetMac   = targetMac,
                                oapAddress  = [3,pin],               # 3=digital_out
                                oapTags     = [OAPMessage.TLVByte(t=0,v=0)],
                            )                            
                        except Exception as err:
                            dld._addScratchpad("<p class=\"doc-warning\">failed: {0}.</p>".format(err))
                        else:
                            dld._addScratchpad("<p class=\"doc-success\">success.</p>")
                    
                    #===== disabling analog
                    
                    for analogPort in range(4):
                    
                        dld._addScratchpad("<p>disabling analog A{0}.</p>".format(analogPort+1))
                        
                        try:
                            self._sendOapCommand(
                                targetNet   = targetNet,
                                targetMac   = targetMac,
                                oapAddress  = [4,analogPort],        # 4=analog
                                oapTags     = [OAPMessage.TLVByte(t=0,v=0)],
                            )
                        except Exception as err:
                            dld._addScratchpad("<p class=\"doc-warning\">failed: {0}.</p>".format(err))
                        else:
                            dld._addScratchpad("<p class=\"doc-success\">success.</p>")
                    
                    #===== enabling temperature, set rate to default
                    
                    dld._addScratchpad("<p>enabling temperature, set rate to default.</p>")
                    
                    try:
                        self._sendOapCommand(
                            targetNet   = targetNet,
                            targetMac   = targetMac,
                            oapAddress  = [5],                       # 5=temperature
                            oapTags     = [OAPMessage.TLVByte(t=0,v=1),
                                           OAPMessage.TLVLong(t=1,v=30000),],
                        )
                    except Exception as err:
                        dld._addScratchpad("<p class=\"doc-warning\">failed: {0}.</p>".format(err))
                    else:
                        dld._addScratchpad("<p class=\"doc-success\">success.</p>")
                    
                    #===== disabling pkgen
                    
                    dld._addScratchpad("<p>disabling pkgen.</p>")
                    
                    try:
                        self._sendOapCommand(
                            targetNet   = targetNet,
                            targetMac   = targetMac,
                            oapAddress  = [254],                     # 254=pkgen
                            oapTags     = [OAPMessage.TLVByte(t=1,v=0),],
                        )
                    except Exception as err:
                        dld._addScratchpad("<p class=\"doc-warning\">failed: {0}.</p>".format(err))
                    else:
                        dld._addScratchpad("<p class=\"doc-success\">success.</p>")
                
                else:
                    dld._addScratchpad("<p>mote is AP, skipping.</p>")
            
            dld._addScratchpad("<p class=\"doc-header\">done.</p>")
            
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
        
        finally:
            dispatcher.disconnect(
                self._dataIndication,
                signal = 'notifData',
                weak   = False,
            )
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _sendOapCommand(self,targetNet,targetMac,oapAddress,oapTags):
        
        #===== send
        
        dataToSend =    OAPMessage.build_oap(
                                            0,                       # seq_num
                                            0,                       # session_id
                                            OAPMessage.CmdType.PUT,  # command
                                            oapAddress,              # address 254=pkgen
                                            tags=oapTags,            # parameters,
                                            sync=True,
                                        )
        
        dataToSend = [ord(b) for b in dataToSend]
                        
        # dispatch
        dispatcher.send (
            signal        = 'dataToMesh_{0}'.format(targetNet),
            data          = {
                'mac':         targetMac,
                'priority':    0,
                'srcPort':     DustLinkData.DustLinkData.WKP_OAP,
                'dstPort':     DustLinkData.DustLinkData.WKP_OAP,
                'options':     0,
                'data':        dataToSend,
            },
        )
        
        #===== compute expected ACK
        
        expectedAck = [0x02,0x00,0xff,len(oapAddress)]+oapAddress
        
        #===== wait for ACK
        
        waitStartTime   = time.time()
        self.waitForResponseEvent.clear()
        
        while True:
            
            # calculate how much time left to wait for response
            timeToWait = self.MAXWAITFOROAPRESPONSE - (time.time()-waitStartTime)
            if timeToWait<0:
                timeToWait = None
            
            # wait for a response
            if self.waitForResponseEvent.wait(timeToWait):
                # I received a response
                
                self.waitForResponseEvent.clear()
                
                with self.responseBufLock:
                    
                    if (self.reponseBuf['mac']==targetMac                      and
                        self.reponseBuf['srcPort']==OAPMessage.OAP_PORT        and 
                        self.reponseBuf['destPort']==OAPMessage.OAP_PORT       and
                        len(self.reponseBuf['payload'])==len(expectedAck)+2    and
                        self.reponseBuf['payload'][-len(expectedAck):]==expectedAck
                        ):
                        return
                
            else:
                # timeout
                raise SystemError("OAP Timeout: no ACK received after {0}s".format(self.MAXWAITFOROAPRESPONSE))
     
    def _dataIndication(self,sender,signal,data):
        
        # write the response in the responseBuf
        with self.responseBufLock:
            self.reponseBuf = data
        
        # signal that I received a response
        self.waitForResponseEvent.set()
    
    #======================== helpers =========================================
    