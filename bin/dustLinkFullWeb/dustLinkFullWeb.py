#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..'))

#============================ imports =========================================

import logging.config

from   DustLink     import DustLink
from   DustLinkData import DustLinkData
from   views.cli    import DustLinkCli
from   views.web    import DustLinkWeb

#============================ defines =========================================

DEFAULT_KEY_FILE   = os.path.join('keys','serverkey.pem')
DEFAULT_CERT_FILE  = os.path.join('keys','servercert.pem')

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
    
    #----- logging
    logging.config.fileConfig('logging.conf')
    
    #----- change working dir to the dustWeb/
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
