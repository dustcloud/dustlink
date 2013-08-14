#!/usr/bin/python

import os
import sys
temp_path = sys.path[0]
sys.path.insert(0, os.path.join(temp_path, '..', '..'))
sys.path.insert(0, os.path.join(temp_path, '..', '..', 'DustLink'))
sys.path.insert(0, os.path.join(temp_path, '..', '..', 'protocols'))
sys.path.insert(0, os.path.join(temp_path, '..', '..', 'SmartMeshSDK'))
sys.path.insert(0, os.path.join(temp_path, '..', '..', 'views', 'web'))
sys.path.insert(0, os.path.join(temp_path, '..', '..', 'views', 'cli'))

import logging
import logging.handlers

import DustLink
from   DustLinkData import DustLinkData
import DustLinkCli
import DustLinkWeb

#============================ defines =========================================

LOG_FORMAT         = "%(asctime)s [%(name)s:%(levelname)s] %(message)s"
DEFAULT_KEY_FILE   = os.path.join('keys','serverkey.pem')
DEFAULT_CERT_FILE  = os.path.join('keys','servercert.pem')

#============================ logging =========================================

logFileName    = os.path.join('..','..','views','web','dustWeb','logs','system.log')
logHandler = logging.handlers.RotatingFileHandler(logFileName,
                                                  maxBytes=2000000,
                                                  backupCount=5,)
logHandler.setFormatter(logging.Formatter(LOG_FORMAT))
for loggerName in [# admin
                   'EventBusClient',
                   # core
                   'DustLink',
                   'DustLinkData',
                   'PersistenceEngine',
                   'PersistenceEngineFile',
                   'PersistenceEngineNone',
                   # GATEWAY
                   'Gateway',
                   'GatewayListener',
                   'NetworkStateAnalyzer',
                   'SerialConnector',
                   'Hdlc',
                   # LBR
                   # DATACONNECTOR
                   'DataConnector',
                   'ListenerUdp',
                   'AppIdentifier',
                   'AppPayloadParser',
                   'AppDataPublisher',
                   'MirrorEngine',
                   'GoogleSyncEngine',
                   # interfaces
                   'DustLinkCli',
                   'DustLinkWeb',
                   'WebHandler',
                   # resetters
                   'ResetManager',
                   'ResetMotesNetwork',
                   ]:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.INFO)
    temp.addHandler(logHandler)

#============================ main ============================================

def mainTearDown():
    global dustLink
    global dustLinkWeb
    global dustLinkCli
    
    # stop web server (Note: CLI killed automatically)
    dustLinkWeb.stop()
    # delete DustLink
    dustLink.tearDown()
    # delete DustLinkData
    DustLinkData.DustLinkData().close()

def main():
    global dustLink
    global dustLinkWeb
    global dustLinkCli
    
    # change to the dustWeb/ directory
    os.chdir(os.path.join('..','..','views','web','dustWeb'))
    
    #----- dustLinkData
    # create singleton
    dustLinkData   = DustLinkData.DustLinkData(
                        persistenceType=DustLinkData.DustLinkData.PERSISTENCE_FILE,
                        persistenceLocation=os.path.join('logs','database.backup'),
                    )
    assert isinstance(dustLinkData,DustLinkData.DustLinkData)
    
    # manipulate dustLinkData
    DustLinkData.DustLinkData().indicateNewStart()
    
    #----- start DustLink
    dustLink  = DustLink.DustLink()
    
    #----- start cli interface
    dustLinkCli    = DustLinkCli.DustLinkCli(quit_cb=mainTearDown)
    dustLinkCli.start()
    
    #----- start web interface
    if os.path.exists(DEFAULT_KEY_FILE):
        keyFile    = DEFAULT_KEY_FILE
    else:
        keyFile    = None
    if os.path.exists(DEFAULT_CERT_FILE):
        certFile   = DEFAULT_CERT_FILE
    else:
        certFile   = None
    dustLinkWeb    = DustLinkWeb.DustLinkWeb(keyFile,certFile)
    dustLinkWeb.start()
            
if __name__ == "__main__":
    main()
