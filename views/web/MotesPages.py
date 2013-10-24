import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('MotesPages')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import random
from dustWeb import web
from DustLinkData import DataVaultException, \
                         DustLinkData

from dustWeb import WebPage
from dustWeb import WebPageDyn
from dustWeb import WebHandler
from dustWeb.viz import VizForm
from dustWeb.viz import VizHtml
from dustWeb.viz import VizTable
from dustWeb.viz import VizFields
from dustWeb.thirdparty import gviz_api

#============================ object ==========================================
        
class MotesPages(WebPageDyn.WebPageDyn):
    
    #===== web handlers (private classes)
    
    class pageMotes(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
            global webServer
            global thisWebApp
            
            username    = web.ctx.session.username
            currentPath = WebPage.WebPage.urlStringTolist(web.ctx.path)
            
            visualizations  =   [
                VizForm.VizForm(
                    webServer           = webServer,
                    username            = username,
                    resourcePath        = currentPath,
                    subResourcePath     = 'cleanup',
                    title               = 'Cleanup motes',
                ),
            ]
            # enable the following code to be able to add/delete motes by hand.
            '''
            visualizations  =   [
                VizForm.VizForm(
                    webServer           = webServer,
                    username            = username,
                    resourcePath        = currentPath,
                    subResourcePath     = 'add',
                    title               = 'Add a Mote',
                ),
                VizForm.VizForm(
                    webServer           = webServer,
                    username            = username,
                    resourcePath        = currentPath,
                    subResourcePath     = 'delete',
                    title               = 'Delete a Mote',
                ),
            ],
            '''
            
            page = thisWebApp.createPage(
                username        = username,
                currentPath     = currentPath,
                visualizations  = visualizations,
            )
            
            return page
        
        # enable the following code to be able to add/delete motes by hand.
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            # enable the following code to be able to add/delete network by hand.
            '''
            elif subResource==['add']:
                
                return [
                    {
                        'name':           'mac',
                        'value':          '',
                        'type':           'text',
                    },
                ]
                
            elif subResource==['delete']:
                
                macStrings = [DustLinkData.DustLinkData.macToString(mac) \
                              for mac in dld.getMoteMacs(username=username)]
                
                return [
                    {
                        'name':           'mac',
                        'value':          None,
                        'optionDisplay':  macStrings,
                        'optionValue':    macStrings,
                        'type':           'select',
                        'editable':       True,
                    },
                ]
            '''
            
            if   subResource==['cleanup']:
                return [
                    {
                        'name':           'command',
                        'value':          '',
                        'type':           'text',
                    },
                ]
                
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            # enable the following code to be able to add/delete network by hand.
            '''
            if   subResource==['add']:
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['mac']
                assert isinstance(receivedData['mac'],str)
                
                mac = DustLinkData.DustLinkData.stringToMac(receivedData['mac'], username=username)
                
                dld.addMote(mac,username=username)
            elif subResource==['delete']:
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['mac']
                assert isinstance(receivedData['mac'],str)
                
                mac = DustLinkData.DustLinkData.stringToMac(receivedData['mac'])
                
                dld.deleteMote(mac, username=username)
            '''
            
            if   subResource==['cleanup']:
                
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['command']
                assert isinstance(receivedData['command'],str)
                
                # make sure this user had delete privileges on motes
                dld.authorize(username,['motes'],DustLinkData.DustLinkData.ACTION_DELETE)
                
                # do everything as admin from here on
                
                command = receivedData['command']
                
                if command=='cleanup':
                    
                    # get all mote MAC address
                    macs          = dld.getMoteMacs()
                    
                    # get all netnames
                    netnames      = dld.getNetnames()
                    
                    # for each network, remove all motes from 'macs' list
                    for netname in netnames:
                        netmacs   = dld.getNetworkMotes(netname)
                        for mac in netmacs:
                            macs.remove(mac)
                    
                    # delete each mote remaining in 'macs' list
                    for mac in macs:
                        dld.deleteMote(mac)
                
            else:
                raise web.notfound()
        
    
    class pageMotesSub(WebPageDyn.WebHandlerDyn):
        
        def getPageDyn(self,dynPath,subResource,username):
            global webServer
            global thisWebApp
            
            username    = web.ctx.session.username
            currentPath = WebPage.WebPage.urlStringTolist(web.ctx.path)
            
            page = thisWebApp.createPage(
                username        = username,
                currentPath     = currentPath,
                visualizations  =   [
                                        VizFields.VizFields(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'info',
                                            title               = 'Info',
                                        ),
                                        VizTable.VizTable(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'apps',
                                            title               = 'Apps on this Mote',
                                        ),
                                        VizForm.VizForm(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'attach',
                                            title               = 'Attach App',
                                        ),
                                        VizForm.VizForm(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'detach',
                                            title               = 'Detach App',
                                        ),
                                    ],
            )
            
            return page
        
        def getDataDyn(self,dynPath,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            mac = DustLinkData.DustLinkData.stringToMac(dynPath)
            
            if subResource==['info']:
            
                moteInfo = dld.getMoteInfo(mac,username=username)
                
                if moteInfo:
                    returnVal = [
                        {
                            'name':      k,
                            'value':     v,
                            'type':      'text',
                            'editable':  False,
                        }
                        for (k,v) in moteInfo.items()
                    ]
                else:
                    returnVal = []
                
                return returnVal
            
            elif subResource==['apps']:
                
                with dld.dataLock:
                    appnames = dld.getAttachedApps(mac,username=username)
                    appnames.sort()
                    
                    # columnNames
                    columnNames = ['appnane','numreceived','link']
                    
                    # data
                    data =  [
                                [
                                    appname,
                                    dld.getNumDataPoints(mac,appname,username=username),
                                    '<a href="/motedata?mac={0}&app={1}">INTERACT</a>'.format(
                                        DustLinkData.DustLinkData.macToString(mac),
                                        appname
                                    ),
                                ]
                                for appname in appnames
                            ]
                    
                    return VizTable.VizTable.formatReturnVal(columnNames,data)
            
            elif subResource==['attach']:
                
                with dld.dataLock:
                    appsToAttach = dld.getAppNames(username=username)
                    for app in dld.getAttachedApps(mac,username=username):
                        appsToAttach.remove(app)
                
                return [
                    {
                        'name':           'appname',
                        'value':          None,
                        'optionDisplay':  appsToAttach,
                        'optionValue':    appsToAttach,
                        'type':           'select',
                        'editable':       True,
                    },
                ]
            
            elif subResource==['detach']:
                
                appsToDetach = dld.getAttachedApps(mac,username=username)
                
                return [
                    {
                        'name':           'appname',
                        'value':          None,
                        'optionDisplay':  appsToDetach,
                        'optionValue':    appsToDetach,
                        'type':           'select',
                        'editable':       True,
                    },
                ]
            
            else:
                raise web.notfound()
        
        def postDataDyn(self,receivedData,dynPath,subResource,username):
            
            mac = DustLinkData.DustLinkData.stringToMac(dynPath)
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['attach']:
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['appname']
                assert isinstance(receivedData['appname'],str)
                
                dld.attachAppToMote(
                    mac,
                    receivedData['appname'],
                    username=username,
                )
            elif subResource==['detach']:
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['appname']
                assert isinstance(receivedData['appname'],str)
                
                dld.detachAppFromMote(
                    mac,
                    receivedData['appname'],
                    username=username,
                )
            else:
                raise web.notfound()
        
    def subPageLister(self):
        username = str(web.ctx.session.username)
    
        try:
            return [
                {
                    'url':   DustLinkData.DustLinkData.macToString(u),
                    'title': DustLinkData.DustLinkData.macToString(u),
                }
                for u in DustLinkData.DustLinkData().getMoteMacs(username=username)
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
                                            url             = 'motes',
                                            title           = 'Motes',
                                            webHandler      = self.pageMotes,
                                            subPageLister   = self.subPageLister,
                                            subPageHandler  = self.pageMotesSub)