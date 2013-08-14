import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('TestResultsPages')
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
        
class TestResultsPages(WebPageDyn.WebPageDyn):
    
    #===== web handlers (private classes)
    
    class pageTestResults(WebHandler.WebHandler):
        
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
    
    class pageTestResultsSub(WebPageDyn.WebHandlerDyn):
        
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
                                            subResourcePath     = 'numtestresults',
                                            title               = 'Number of Test Results Per Outcome',
                                        ),
                                        VizTable.VizTable(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'lastresults',
                                            title               = 'Last Tests Ran',
                                        ),
                                    ],
            )
            
            return page
        
        def getDataDyn(self,dynPath,subResource,username):
            
            netname = dynPath
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['numtestresults']:
                
                numTestResults = dld.getNumTestResults(netname,username=username)
                
                # columnNames
                columnNames = ['outcome','number']
                
                # fill in data
                data =  [
                            [
                                k,
                                v,
                            ]
                            for (k,v) in numTestResults.items()
                        ]
                
                return VizTable.VizTable.formatReturnVal(columnNames,data)
            
            elif subResource==['lastresults']:
                
                lastResults = dld.getLastResults(netname,username=username)
                
                # columnNames
                columnNames = ['timestamp','name','outcome','description']
                
                # data
                if lastResults:
                    data =  [
                                [
                                    DustLinkData.DustLinkData.timestampToString(k),
                                    v[0],
                                    v[1],
                                    v[2],
                                ]
                                for (k,v) in lastResults.items()
                            ]
                else:
                    data =  []
                
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
                                            url             = 'testresults',
                                            title           = 'TestResults',
                                            webHandler      = self.pageTestResults,
                                            subPageLister   = self.subPageLister,
                                            subPageHandler  = self.pageTestResultsSub)