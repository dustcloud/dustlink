#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ResetManager')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import traceback

from DustLinkData                      import DustLinkData
from SmartMeshSDK.IpMgrConnectorSerial import IpMgrConnectorSerial
from SmartMeshSDK.IpMgrConnectorMux    import IpMgrConnectorMux

class ResetManager(threading.Thread):
    
    def __init__(self,connectionParams):
        
        # store params
        self.connectionParams          = connectionParams
        
        # initialize parent
        threading.Thread.__init__(self)
        self.name                      = 'ResetManager'
        
        # start itself
        self.start()
    
    def run(self):
        
        try:
        
            dld = DustLinkData.DustLinkData()
            dld._resetScratchpad()
            
            dld._addScratchpad("<p class=\"doc-header\">Resetting manager.</p>")
            
            #===== connecting to manager
            
            dld._addScratchpad("<p>connecting to manager at {0}.</p>".format(self.connectionParams))
            try:
                if isinstance(self.connectionParams,tuple):
                    # over serialMux
                    connector = IpMgrConnectorMux.IpMgrConnectorMux()
                    connector.connect({
                        'host': self.connectionParams[0],
                        'port': self.connectionParams[1],
                    })
                else:
                    # over serial
                    connector = IpMgrConnectorSerial.IpMgrConnectorSerial()
                    connector.connect({
                        'port': self.connectionParams,
                    })
            except Exception as err:
                dld._addScratchpad("<p class=\"doc-warning\">connection failed: {0}.</p>".format(err))
                return
            else:
                dld._addScratchpad("<p class=\"doc-success\">connection successful.</p>")
            
            try:
                
                #===== issuing dn_getNetworkConfig()
                
                dld._addScratchpad("<p>issuing dn_getNetworkConfig()</p>")
                try:
                    oldconf = connector.dn_getNetworkConfig()
                except Exception as err:
                    dld._addScratchpad("<p class=\"doc-warning\">failed issuing dn_getNetworkConfig(): {0}.</p>".format(err))
                    return
                else:
                    output  = []
                    output += ["<p class=\"doc-success\">issued dn_getNetworkConfig() succesfully.</p>"]
                    output += ["<p>Received the following fields:</p>"]
                    output += ["<table>"]
                    output += ["<tr><td>{0}</td><td>{1}</td></tr>".format(k,getattr(oldconf,k)) for k in oldconf._fields]
                    output += ["</table>"]
                    output  = ''.join(output)
                    dld._addScratchpad(output)
                
                #===== issuing dn_setNetworkConfig()
                
                newconf = {
                    'networkId'        : oldconf.networkId,
                    'apTxPower'        : 8,
                    'frameProfile'     : 1,
                    'maxMotes'         : 33,
                    'baseBandwidth'    : 9000,
                    'downFrameMultVal' : 1,
                    'numParents'       : 2,
                    'ccaMode'          : 0,
                    'channelList'      : 32767,
                    'autoStartNetwork' : 1,
                    'locMode'          : 0,
                    'bbMode'           : 0,
                    'bbSize'           : 1,
                    'isRadioTest'      : 0,
                    'bwMult'           : 300,
                    'oneChannel'       : 255,
                }
                
                output  = []
                output += ["<p>issuing dn_setNetworkConfig() with the following parameters</p>"]
                output += ["<table>"]
                output += ["<tr><td>{0}</td><td>{1}</td></tr>".format(k,v) for (k,v) in newconf.items()]
                output += ["</table>"]
                output  = ''.join(output)
                dld._addScratchpad(output)
                
                try:
                    connector.dn_setNetworkConfig(**newconf)
                except Exception as err:
                    dld._addScratchpad("<p class=\"doc-warning\">failed issuing dn_setNetworkConfig(): {0}.</p>".format(err))
                    return
                else:
                    dld._addScratchpad("<p class=\"doc-success\">issued dn_setNetworkConfig() succesfully.</p>")
                
                #===== issuing dn_reset()
                
                dld._addScratchpad("<p>issuing dn_reset()</p>")
                try:
                    connector.dn_reset(
                        type       = 0,     # 0 = resetSystem
                        macAddress = [0]*8, # this field is not used when resetting the system
                    )
                except Exception as err:
                    pass # happens since receiving no ACK from manager which is resetting

            finally:                
                #===== disconnect and delete connector
            
                dld._addScratchpad("<p>disconnecting from manager at {0}.</p>".format(self.connectionParams))
                try:
                    connector.disconnect()
                except Exception as err:
                    dld._addScratchpad("<p class=\"doc-warning\">disconnection failed: {0}.</p>".format(err))
                else:
                    dld._addScratchpad("<p class=\"doc-success\">disconnection successful.</p>")
                del connector
            
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
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    