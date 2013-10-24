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
            returnData = mirrorData[0][1]
            
            # set whether configurable
            for d in returnData:
                if d['type']=='temperature':
                    try:
                        dld.authorize(
                            username,
                            ['motes',d['mac'],'apps','OAPTemperature'],
                            DustLinkData.DustLinkData.ACTION_PUT
                        )
                    except DataVaultException.Unauthorized:
                        d['isConfigurable'] = False
                    else:
                        d['isConfigurable'] = True
            
            # convert MAC addresses to string
            for d in returnData:
                d['mac']            = DustLinkData.DustLinkData.macToString(d['mac'])
            
            # specify whether user can calibrate
            try:
                # dummy read to validate that user has read privileges on 'system'
                dld.getEnabledPersistence(username=username)
            except DataVaultException.Unauthorized:
                pass # username has not sufficient rights 
            else:
                for row in returnData:
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
                            returnData += [
                                {
                                    'mac':            DustLinkData.DustLinkData.macToString(mac),
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
            
            # add link
            for r in returnData:
                
                linkUrl = None
                if   r['type']=='led':
                   linkUrl  = '/motedata?mac={0}&app=OAPLED'.format(r['mac'])
                elif r['type']=='temperature':
                    linkUrl  = '/motedata?mac={0}&app=OAPTemperature'.format(r['mac'])
                elif r['type']=='voltage':
                    linkUrl  = '/motedata?mac={0}&app=DC2126A'.format(r['mac'])
                elif r['type']=='acceleration':
                    linkUrl  = '/motedata?mac={0}&app=LIS331'.format(r['mac'])
                
                if linkUrl:
                    r['linkText'] = 'view locally'
                    r['linkUrl']  = linkUrl
            
            # filter to contains only motes currently in network
            returnData = [r for r in returnData if r['mac'] in macsInNetwork]
            
            return {
                'data': returnData
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
        