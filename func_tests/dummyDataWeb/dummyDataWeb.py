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
import time
import random
import threading
import logging.handlers

from DustLinkData import DustLinkData
import DustLinkWeb
import DustLinkCli

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

#============================ data injector ===================================

class DummyDataInjector(threading.Thread):
    
    TEST_USER1          = 'user1'
    TEST_USER2          = 'user2'
    TEST_USER_ALL       = [TEST_USER1,TEST_USER2]
    
    TEST_APP1           = 'app1'
    TEST_APP2           = 'app2'
    TEST_APP_ALL        = [TEST_APP1,TEST_APP2]
    
    TEST_MOTE1          = (0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11)
    TEST_MOTE2          = (0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22)
    TEST_MOTE_ALL       = [TEST_MOTE1,TEST_MOTE2]
    
    TEST_HOST1          = (0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11)
    TEST_HOST2          = (0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22)
    TEST_HOST_ALL       = [TEST_HOST1,TEST_HOST2]
    
    TEST_INFO1          = 'info1'
    TEST_INFO2          = 'info2'
    TEST_INFO_ALL       = [TEST_INFO1,TEST_INFO2]
    
    TEST_NETWORK1       = 'network1'
    TEST_NETWORK2       = 'network2'
    TEST_NETWORK_ALL    = [TEST_NETWORK1,TEST_NETWORK2]
    
    TEST_RESOURCES      =   [
                                ['system'],
                                ['users'],
                            ]
    
    def __init__(self):
        
        # store params
        
        # initialize parent class
        threading.Thread.__init__(self)
        self.name       = 'DummyDataInjector'
    
        # fill in some data
        dld = DustLinkData.DustLinkData()
        with dld.dataLock:
            #--- system
            dld.indicateNewStart()
            dld.indicateNewStart()
            dld.indicateNewStart()
            for e in DustLinkData.DustLinkData.SYSEVENT_ALL:
                dld.setSystemEvent(e)
            #--- users
            dld.addUser(self.TEST_USER1)
            dld.addUser(self.TEST_USER2)
            dld.indicateUserConnection(self.TEST_USER1,
                                     DustLinkData.DustLinkData.CONNECTIONTYPE_WEB,
                                     DustLinkData.DustLinkData.CONNECTIONSTATUS_CONNECTED)
            #--- apps
            dld.addApp(self.TEST_APP1)
            dld.addApp(self.TEST_APP2)
            dld.setAppDescription(self.TEST_APP1,'description 1')
            dld.setAppDescription(self.TEST_APP2,'description 2')
            dld.setAppTransport(self.TEST_APP1,
                                  DustLinkData.DustLinkData.APP_TRANSPORT_UDP,
                                  60000)
            dld.setAppFields(
                self.TEST_APP1,
                DustLinkData.DustLinkData.APP_DIRECTION_FROMMOTE,
                "<b",
                ['one']
            )
            dld.setAppFields(
                self.TEST_APP2,
                DustLinkData.DustLinkData.APP_DIRECTION_FROMMOTE,
                "<bb",
                ['two','three']
            )
            #--- motes
            dld.addMote(self.TEST_MOTE1)
            dld.addMote(self.TEST_MOTE2)
            dld.setMoteInfo(self.TEST_MOTE1,
                              self.TEST_INFO1,
                              'info1')
            dld.setMoteInfo(self.TEST_MOTE2,
                              self.TEST_INFO2,
                              'info2')
            dld.attachAppToMote(self.TEST_MOTE1,
                                  self.TEST_APP1,)
            dld.attachAppToMote(self.TEST_MOTE1,
                                  self.TEST_APP2,)
            dld.indicateData(self.TEST_MOTE1,
                               self.TEST_APP1,
                               {
                                   'one': 1,
                               })
            dld.indicateData(self.TEST_MOTE1,
                               self.TEST_APP2,
                               {
                                   'two':   2,
                                   'three': 3,
                               })
            #--- networks
            dld.addNetwork(self.TEST_NETWORK1)
            dld.addNetwork(self.TEST_NETWORK2)
            dld.setNetworkInfo(self.TEST_NETWORK1,
                                 self.TEST_INFO1,
                                 'info1')
            dld.addNetworkMote(self.TEST_NETWORK1,
                                 self.TEST_MOTE1)
            dld.addNetworkMote(self.TEST_NETWORK1,
                                 self.TEST_MOTE2)
            dld.addPath(self.TEST_NETWORK1,
                          self.TEST_MOTE1,
                          self.TEST_MOTE2)
            dld.addPath(self.TEST_NETWORK1,
                          self.TEST_MOTE2,
                          self.TEST_MOTE1)
            #--- testResults
            dld.addResult(self.TEST_NETWORK1,
                            'test1',
                            DustLinkData.DustLinkData.TEST_OUTCOME_PASS,
                           )
            dld.addResult(self.TEST_NETWORK1,
                            'test1',
                            DustLinkData.DustLinkData.TEST_OUTCOME_FAIL,
                           )
            #--- firewalls
            dld.addFirewallRule(self.TEST_NETWORK1,
                                  self.TEST_MOTE1,
                                  self.TEST_HOST1,
                                  DustLinkData.DustLinkData.DATA_DIRECTION_INET2MESH,
                                  DustLinkData.DustLinkData.DATATYPE_UDP,
                                  2000,
                                  DustLinkData.DustLinkData.FIREWALL_RULE_ACCEPT)
            
            #--- dataflows
            dld.indicateDataFlow(
                                  self.TEST_NETWORK1,
                                  self.TEST_MOTE1,
                                  self.TEST_HOST1,
                                  DustLinkData.DustLinkData.DATA_DIRECTION_INET2MESH,
                                  DustLinkData.DustLinkData.LBR_OUTCOME_ACCEPT,
                                  )
            #--- user privileges (at end so resources exist)
            dld.grantPrivilege(['system'],
                                 self.TEST_USER1,
                                 DustLinkData.DustLinkData.ACTION_DELETE)
            dld.grantPrivilege(['system'],
                                 self.TEST_USER1,
                                 DustLinkData.DustLinkData.ACTION_GET)
            dld.grantPrivilege(['networks',self.TEST_NETWORK1],
                                 self.TEST_USER2,
                                 DustLinkData.DustLinkData.ACTION_GET)
    
    def run(self):
    
        dld = DustLinkData.DustLinkData()
    
        while True:
            time.sleep(random.uniform(1,3))
            
            with dld.dataLock:
                mac         = None
                app         = None
                found       = False
                retriesLeft = 10
                
                while (not mac) or (not app):
                    retriesLeft -= 1
                    if retriesLeft<=0:
                        break
                    
                    # pick a random MAC
                    macs    = dld.getMoteMacs()
                    if not macs:
                        continue
                    mac = random.choice(macs)
                    
                    # pick a random app
                    apps    = dld.getAttachedApps(mac)
                    if not apps:
                        continue
                    app    = random.choice(apps)
                    
                    # get the names of the fields
                    fieldNames = dld.getAppFields(app,DustLinkData.DustLinkData.APP_DIRECTION_FROMMOTE)['fieldNames']
                    if not fieldNames:
                        continue
                    
                    # if you get here, you found an app!
                    found = True
                    break
                
                if found:
                    # create some random data
                    dataToIndicate = {}
                    for f in fieldNames:
                        dataToIndicate[f] = random.randint(0x00,0xff)
                    
                    # indicate this data
                    dld.indicateData(
                        mac,
                        app,
                        dataToIndicate,
                    )

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
    
    # change to the dustWeb/ directory
    os.chdir(os.path.join('..','..','views','web','dustWeb'))
    
    #----- dustLinkData
    # create singleton
    dld   = DustLinkData.DustLinkData()
    assert isinstance(dld,DustLinkData.DustLinkData)
    
    # start a debug data injector
    injector = DummyDataInjector()
    injector.start()
    
    #----- start DustLink
    # NOTE: no DustLink in this (dummy) application
    
    #----- start cli interface
    dustLinkCli    = DustLinkCli.DustLinkCli(quit_cb=mainTearDown,appName='Dummy Data Functional Test')
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
