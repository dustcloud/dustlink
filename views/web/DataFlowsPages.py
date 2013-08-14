import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('DataFlowsPages')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import random
from dustWeb import web
from DustLinkData import DataVaultException, \
                         DustLinkData

from dustWeb import WebPage
from dustWeb import WebPageDyn
from dustWeb import WebHandler
from dustWeb.viz import VizHtml
from dustWeb.viz import VizTable
from dustWeb.viz import VizFields
from dustWeb.thirdparty import gviz_api

#============================ object ==========================================
        
class DataFlowsPages(WebPageDyn.WebPageDyn):
    
    #===== web handlers (private classes)
    
    class pageDataFlows(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
            global webServer
            global thisWebApp
            
            username    = web.ctx.session.username
            currentPath = WebPage.WebPage.urlStringTolist(web.ctx.path)
            
            page = thisWebApp.createPage(
                username        = username,
                currentPath     = currentPath,
                visualizations  =   [
                                        VizHtml.VizHtml(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = None,
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            return {'rawHtml':'Select a network from the menu.'}
    
    class pageDataFlowsSub(WebPageDyn.WebHandlerDyn):
        
        def getPageDyn(self,dynPath,subResource,username):
            global webServer
            global thisWebApp
            
            username    = web.ctx.session.username
            currentPath = WebPage.WebPage.urlStringTolist(web.ctx.path)
            
            page = thisWebApp.createPage(
                username        = username,
                currentPath     = currentPath,
                visualizations  =   [
                                        VizTable.VizTable(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'dataflows',
                                            title               = 'Dataflows',
                                        ),
                                    ],
            )
            
            return page
        
        def getDataDyn(self,dynPath,subResource,username):
            
            netname = dynPath
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['dataflows']:
                
                dataFlows = dld.getNetworkDataFlows(netname,username=username)
                
                # columnNames
                columnNames = ['mac','ip','direction']
                
                # data
                data =  [
                            [
                                mac,ip,direction
                            ]
                            for (mac,ip,direction) in dataFlows
                        ]
                
                return VizTable.VizTable.formatReturnVal(columnNames,data)
            
            else:
                raise web.notfound()
            
    def subPageLister(self):
        username = str(web.ctx.session.username)
        dld = DustLinkData.DustLinkData()
        
        try:
            return [
                {
                    'url':   n,
                    'title': n,
                }
                for n in dld.getNetnames(username=username)
            ]
        except DataVaultException.Unauthorized:
            return []
    
    def __init__(self, webServer_param):
        global webServer
        global thisWebApp
        
        # local variables
        self.webServer       = webServer_param
        
        # global variables
        webServer            = self.webServer
        thisWebApp           = self
        
        # initialize parent class
        WebPageDyn.WebPageDyn.__init__(self,webServer       = self.webServer,
                                            url             = 'dataflows',
                                            title           = 'DataFlows',
                                            webHandler      = self.pageDataFlows,
                                            subPageLister   = self.subPageLister,
                                            subPageHandler  = self.pageDataFlowsSub)