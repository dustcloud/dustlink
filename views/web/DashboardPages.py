import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('DashboardPages')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

from   pydispatch import dispatcher

from DustLinkData import DustLinkData, \
                         DataVaultException
from dustWeb import web
from dustWeb import WebPage
from dustWeb import WebHandler

#============================ object ==========================================
        
class DashboardPages(WebPage.WebPage):
    
    #===== web handlers (private classes)
    
    class pageDashboard(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
            raise web.seeother('/static/dashboard/index_local.html')
        
        def getData(self,subResource,username):
        
            dld = DustLinkData.DustLinkData()
            
            # obtain a copy of the mirror data
            mirrorData = dispatcher.send(
                    signal        = 'getMirrorData',
                    data          = None,
                )
            
            assert len(mirrorData)==1
            
            returnVal = mirrorData[0][1]
            
            # specify whether user can calibrate
            try:
                # dummy read to validate that user has read privileges on 'system'
                dld.getEnabledPersistence(username=username)
            except DataVaultException.Unauthorized:
                pass # username has not sufficient rights 
            else:
                for row in returnVal:
                    if row['type']=='pressure':
                        row['lastvalue'] = row['lastvalue']+'_calibrate'
            
            # add list of motes running OAPLED app
            motesWithOapLed = []
            with dld.dataLock:
                for mac in dld.getMoteMacs():
                    if 'OAPLED' in dld.getAttachedApps(mac):
                        try:
                            dld.authorize(
                                username,
                                ['motes',mac,'apps','OAPLED'],
                                DustLinkData.DustLinkData.ACTION_PUT
                            )
                        except DataVaultException.Unauthorized:
                            pass # username has not sufficient rights
                        else:
                            returnVal += [
                                {
                                    'source':         DustLinkData.DustLinkData.macToString(mac),
                                    'type':           'led',
                                    'min':            None,
                                    'lastvalue':      None,
                                    'max':            None,
                                    'lastupdated':    None,
                                }
                            ]
                
                # list all MACs currently in network
                macsInNetwork = []
                for netname in dld.getNetnames():
                    macsInNetwork += dld.getNetworkMotes(netname)
                macsInNetwork = [DustLinkData.DustLinkData.macToString(m) for m in macsInNetwork]
            
            # filter to contains only motes currently in network
            returnVal = [r for r in returnVal if r['source'] in macsInNetwork]
            
            return {
                'config': {
                    'showTimeline': True,
                },
                'data': returnVal
            }
        
        def postData(self,receivedData,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            # dummy read to validate that user has read privileges on 'system'
            dld.getEnabledPersistence(username=username)
        
            if receivedData=={'calibrate':'pressure'}:
                dispatcher.send(
                    signal        = 'calibrateMirrorData',
                    data          = 'pressure',
                )
    
    def __init__(self, webServer_param):
        global webServer
        global thisWebApp
        
        # local variables
        self.webServer       = webServer_param
        
        # global variables
        webServer            = self.webServer
        thisWebApp           = self
        
        # initialize parent class
        WebPage.WebPage.__init__(self,webServer       = self.webServer,
                                      url             = 'dashboard',
                                      title           = 'dashboard',
                                      webHandler      = self.pageDashboard,)
        