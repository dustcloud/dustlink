import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('SystemPages')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import os
import time
import datetime
import threading
import copy
if os.name=='nt':       # Windows
   import _winreg as winreg
elif os.name=='posix':  # Linux
   import glob
try:
    import yappi
except ImportError:
    yappiLoaded = False
else:
    yappiLoaded = True

from pydispatch import dispatcher

import ResetManager
import ResetMotesNetwork
from dustWeb                 import web, \
                                    DustWeb, \
                                    WebPage, \
                                    WebHandler
from dustWeb.viz             import VizFields, \
                                    VizHtml, \
                                    VizTable, \
                                    VizForm, \
                                    VizTree
from dustWeb.thirdparty      import gviz_api

from DustLink                import DustLink_version
from DustLinkData            import DustLinkData,\
                                    DataVaultException
from SmartMeshSDK            import sdk_version

#============================ object ==========================================

class SystemPages(WebPage.WebPage):
    
    #===== web handlers (private classes)
    class pageWelcome(WebHandler.WebHandler):
        
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
                                            subResourcePath     = 'welcome',
                                            title               = 'Welcome to DustLink',
                                        ),
                                        VizTable.VizTable(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'systemevents',
                                            title               = 'System Events',
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            global webServer
            
            dld = DustLinkData.DustLinkData()
            
            if subResource==['welcome']:
                
                path = 'system', 'welcome', 'welcome'
                returnString = webServer.getDocumentation().getMore(path)
                return {'rawHtml': returnString}
            
            elif subResource == ['systemevents']:
                
                systemevents = dld.getSystemEvents(username=username)
                
                # columnNames
                columnNames = ['event','timestamp','remove']
                
                # data
                data =  [
                            [
                                k,
                                DustLinkData.DustLinkData.timestampToString(v),
                                '<a onClick="jQuery.post(\'welcome/json/systemevents/\', { event: \''+k+'\' });">remove</a>'
                            ]
                            for k,v in systemevents.items()
                        ]
                
                return VizTable.VizTable.formatReturnVal(columnNames,data, [0,0,.1])
            
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if subResource == ['systemevents']:
                
                assert isinstance(receivedData,dict)
                keys = receivedData.keys()
                keys.sort()
                assert keys==['event']
                assert isinstance(receivedData['event'],str)
                
                dld.clearSystemEvent(receivedData['event'],username=username)
                
            else:
                raise web.notfound()
    
    class pageManagers(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
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
                        subResourcePath     = 'connections',
                        title               = 'Manager Connections',
                    ),
                    VizForm.VizForm(
                        webServer           = webServer,
                        username            = username,
                        resourcePath        = currentPath,
                        subResourcePath     = 'add',
                        title               = 'Add',
                    ),
                    VizForm.VizForm(
                        webServer           = webServer,
                        username            = username,
                        resourcePath        = currentPath,
                        subResourcePath     = 'delete',
                        title               = 'Delete',
                    ),
                    VizTable.VizTable(
                        webServer           = webServer,
                        username            = username,
                        resourcePath        = currentPath,
                        subResourcePath     = 'serialports',
                        title               = 'Available Serial Ports',
                    ),
                ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['connections']:
                
                connections = dld.getManagerConnections(username=username)
                if not connections:
                    connections = {}
                
                connectionDisplay = {}
                for k,v in connections.items():
                    if isinstance(k,tuple):
                        connectionDisplay['{0}:{1}'.format(k[0],k[1])] = v
                    else:
                        connectionDisplay[k] = v
                
                # columnNames
                columnNames = ['connection','state','reason']
                
                # data
                data =  [
                            [
                                str(k),
                                v['state'],
                                v['reason'],
                            ]
                            for k,v in connectionDisplay.items()
                        ]
                
                return VizTable.VizTable.formatReturnVal(columnNames,data, [0,0,0.5])
                
            elif subResource==['add']:
                
                return [
                    {
                        'name':           'connection',
                        'value':          '',
                        'type':           'text',
                    },
                ]
                
            elif subResource==['delete']:
                connections = dld.getManagerConnections(username=username)
                if not connections:
                    connections = {}
                
                options = []
                for k in connections:
                    if isinstance(k,tuple):
                        options.append('{0}:{1}'.format(k[0],k[1]))
                    else:
                        options.append(k)
                
                return [
                    {
                        'name':           'connection',
                        'value':          None,
                        'optionDisplay':  options,
                        'optionValue':    options,
                        'type':           'select',
                        'editable':       True,
                    },
                ]
            
            elif  subResource==['serialports']:
                
                # dummy read to validate that user has read privileges on 'system'
                dld.getEnabledPersistence(username=username)
                
                serialports = SystemPages._findSerialPorts()
                
                # columnNames
                columnNames = ['serialport']
                
                # data
                data =  [
                            [
                                p,
                            ]
                            for p in serialports
                        ]
                
                return VizTable.VizTable.formatReturnVal(columnNames,data)
            
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['add']:
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['connection']
                assert isinstance(receivedData['connection'],str)
                
                connection = receivedData['connection']
                connection = SystemPages._createConnectionParams(connection)
                
                dld.addManagerConnection(
                    connection,
                    username=username,
                )
            
            elif subResource==['delete']:
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['connection']
                assert isinstance(receivedData['connection'],str)
                
                connection = receivedData['connection']
                connection = SystemPages._createConnectionParams(connection)
                
                dld.deleteManagerConnection(
                    connection,
                    username=username,
                )
            
            else:
                raise web.notfound()
    
    class pagePublishers(WebHandler.WebHandler):
        
        HIDDEN_FIELD_VALUE = '<hidden>'
        
        def getPage(self,subResource,username):
            global webServer
            global thisWebApp
            
            username    = web.ctx.session.username
            currentPath = WebPage.WebPage.urlStringTolist(web.ctx.path)
            
            page = thisWebApp.createPage(
                username        = username,
                currentPath     = currentPath,
                visualizations  =   [
                    VizForm.VizForm(
                        webServer           = webServer,
                        username            = username,
                        resourcePath        = currentPath,
                        subResourcePath     = 'xivelyconfiguration',
                        title               = 'Xively Configuration',
                    ),
                    VizFields.VizFields(
                        webServer           = webServer,
                        username            = username,
                        resourcePath        = currentPath,
                        subResourcePath     = 'xivelystatus',
                        title               = 'Xively Status',
                    ),
                    VizForm.VizForm(
                        webServer           = webServer,
                        username            = username,
                        resourcePath        = currentPath,
                        subResourcePath     = 'googleconfiguration',
                        title               = 'Google Configuration',
                    ),
                    VizFields.VizFields(
                        webServer           = webServer,
                        username            = username,
                        resourcePath        = currentPath,
                        subResourcePath     = 'googlestatus',
                        title               = 'Google Status',
                    ),
                ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['xivelyconfiguration']:
                
                xivelySettings = dld.getPublishersSettings(
                    publisherName = dld.PUBLISHER_XIVELY,
                    username      = username,
                )
                if xivelySettings['xivelyApiKey']:
                    xivelySettings['xivelyApiKey']    = self.HIDDEN_FIELD_VALUE,
                else:
                    xivelySettings['xivelyApiKey']    = '',
                
                return [
                    {
                        'name':      'xivelyApiKey',
                        'value':     xivelySettings['xivelyApiKey'],
                        'type':      'password',
                        'editable':  True,
                    },
                ]
            
            elif subResource==['xivelystatus']:
                
                xivelystatusRaw = dispatcher.send(
                    signal        = 'xivelystatus',
                    data          = None,
                )
                assert len(xivelystatusRaw)==1
                xivelystatus = xivelystatusRaw[0][1]
                
                return [
                    {
                        'name':             k,
                        'value':            v,
                        'type':             'text',
                        'editable':         False,
                    } for (k,v) in xivelystatus.items()
                ]
            
            elif   subResource==['googleconfiguration']:
                
                googleSettings = dld.getPublishersSettings(
                    publisherName = dld.PUBLISHER_GOOGLE,
                    username      = username,
                )
                if not googleSettings['spreadsheetKey']:
                    googleSettings['spreadsheetKey']  = ''
                if not googleSettings['worksheetName']:
                    googleSettings['worksheetName']   = ''
                if googleSettings['googleUsername']:
                    googleSettings['googleUsername']  = self.HIDDEN_FIELD_VALUE,
                else:
                    googleSettings['googleUsername']  = '',
                if googleSettings['googlePassword']:
                    googleSettings['googlePassword']  = self.HIDDEN_FIELD_VALUE,
                else:
                    googleSettings['googlePassword']  = '',
                
                return [
                    {
                        'name':      'spreadsheetKey',
                        'value':     googleSettings['spreadsheetKey'],
                        'type':      'text',
                        'editable':  True,
                    },
                    {
                        'name':      'worksheetName',
                        'value':     googleSettings['worksheetName'],
                        'type':      'text',
                        'editable':  True,
                    },
                    {
                        'name':      'googleUsername',
                        'value':     googleSettings['googleUsername'],
                        'type':      'password',
                        'editable':  True,
                    },
                    {
                        'name':      'googlePassword',
                        'value':     googleSettings['googlePassword'],
                        'type':      'password',
                        'editable':  True,
                    },
                ]
            
            elif subResource==['googlestatus']:
                
                googlestatusRaw = dispatcher.send(
                    signal        = 'googlestatus',
                    data          = None,
                )
                assert len(googlestatusRaw)==1
                googlestatus = googlestatusRaw[0][1]
                
                return [
                    {
                        'name':             k,
                        'value':            v,
                        'type':             'text',
                        'editable':         False,
                    } for (k,v) in googlestatus.items()
                ]
            
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if     subResource==['xivelyconfiguration']:
                
                # dummy read to validate that user has read privileges on 'system'
                dld.getEnabledPersistence(username=username)
                
                assert isinstance(receivedData,dict)
                assert sorted(receivedData.keys())==sorted(dld.PUBLISHER_XIVELY_KEY_ALL)
                
                if receivedData['xivelyApiKey']==self.HIDDEN_FIELD_VALUE:
                    raise ValueError('invalid xivelyApiKey')
                
                dld.setPublisherSettings(
                    publisherName    = dld.PUBLISHER_XIVELY,
                    settings         = {
                        'xivelyApiKey':     receivedData['xivelyApiKey'],
                    },
                    username=username,
                )
            
            elif   subResource==['googleconfiguration']:
                
                # dummy read to validate that user has read privileges on 'system'
                dld.getEnabledPersistence(username=username)
                
                assert isinstance(receivedData,dict)
                assert sorted(receivedData.keys())==sorted(dld.PUBLISHER_GOOGLE_KEY_ALL)
                
                if receivedData['googleUsername']==self.HIDDEN_FIELD_VALUE:
                    raise ValueError('invalid googleUsername')
                if receivedData['googlePassword']==self.HIDDEN_FIELD_VALUE:
                    raise ValueError('invalid googlePassword')
                
                dld.setPublisherSettings(
                    publisherName    = dld.PUBLISHER_GOOGLE,
                    settings         = {
                        'spreadsheetKey':   receivedData['spreadsheetKey'],
                        'worksheetName':    receivedData['worksheetName'],
                        'googleUsername':   receivedData['googleUsername'],
                        'googlePassword':   receivedData['googlePassword'],
                    },
                    username=username,
                )
                
            else:
                raise web.notfound()
    
    class pageAdminPassword(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
            global webServer
            global thisWebApp
            
            username    = web.ctx.session.username
            currentPath = WebPage.WebPage.urlStringTolist(web.ctx.path)
            
            page = thisWebApp.createPage(
                username        = username,
                currentPath     = currentPath,
                visualizations  =   [
                                        VizForm.VizForm(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'change',
                                            title               = 'Change Admin Password',
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            if subResource==['change']:
                
                return [
                    {
                        'name':           'current password',
                        'value':          '',
                        'type':           'password',
                    },
                    {
                        'name':           'new password',
                        'value':          '',
                        'type':           'password',
                    },
                ]
            
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['change']:
                assert isinstance(receivedData,dict)
                keys = receivedData.keys()
                keys.sort()
                assert keys==['current password','new password']
                assert isinstance(receivedData['current password'],str)
                assert isinstance(receivedData['new password'],str)
                
                dld.setUserPassword(
                    DustLinkData.DustLinkData.USER_ADMIN,
                    receivedData['current password'],
                    receivedData['new password'],
                    username=username
                )
            
            else:
                raise web.notfound()
    
    class pageModules(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
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
                                            subResourcePath     = 'activated',
                                            title               = 'Activated Modules',
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['activated']:
                
                enabledModules = dld.getEnabledModules(username=username)
                
                return [
                    {
                        'name':      m,
                        'value':     m in enabledModules,
                        'type':      'boolean',
                        'editable':  True,
                    }
                    for m in DustLinkData.DustLinkData.MODULE_ALL
                ]
            
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['activated']:
                
                # filter errors
                fields = receivedData.keys()
                fields.sort()
                if fields!=['fieldName','fieldValue']:
                    raise web.HTTPError('400 bad request',{},'wrong fieldnames')
                if receivedData['fieldName'] not in DustLinkData.DustLinkData.MODULE_ALL:
                    raise web.HTTPError('400 bad request',{},'module {0} unknown'.format(receivedData['fieldName']))
                if receivedData['fieldValue'] not in [True,False]:
                    print 'invalid setting {0}'.format(receivedData['fieldValue'])
                
                # enable/disable module
                if receivedData['fieldValue']:
                    dld.enableModule(receivedData['fieldName'],username=username)
                else:
                    dld.disableModule(receivedData['fieldName'],username=username)
            
            else:
                raise web.notfound()
    
    class pagePersistence(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
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
                                            subResourcePath     = 'activated',
                                            title               = 'Activated Persistence',
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['activated']:
                
                enabledPersistence = dld.getEnabledPersistence(username=username)
                allPersistence     = DustLinkData.DustLinkData.PERSISTENCE_ALL[:]
                allPersistence.remove(DustLinkData.DustLinkData.PERSISTENCE_NONE)
                
                return [
                    {
                        'name':      p,
                        'value':     p in enabledPersistence,
                        'type':      'boolean',
                        'editable':  True,
                    }
                    for p in allPersistence
                ]
            
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['activated']:
                
                # filter errors
                fields = receivedData.keys()
                fields.sort()
                if fields!=['fieldName','fieldValue']:
                    raise web.HTTPError('400 bad request',{},'wrong fieldnames')
                if receivedData['fieldName'] not in DustLinkData.DustLinkData.PERSISTENCE_ALL:
                    raise web.HTTPError('400 bad request',{},'module {0} unknown'.format(receivedData['fieldName']))
                if receivedData['fieldValue'] not in [True,False]:
                    print 'invalid setting {0}'.format(receivedData['fieldValue'])
                
                # enable/disable module
                if receivedData['fieldValue']:
                    dld.enablePersistence(receivedData['fieldName'],username=username)
                else:
                    dld.disablePersistence(receivedData['fieldName'],username=username)
            
            else:
                raise web.notfound()
    
    class pageDemoMode(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
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
                                            subResourcePath     = 'enable',
                                            title               = 'Demo Mode',
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['enable']:
                
                return [
                    {
                        'name':      "Demo Mode",
                        'value':     dld.getDemoMode(username=username),
                        'type':      'boolean',
                        'editable':  True,
                    }
                ]
            
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['enable']:
                
                # filter errors
                fields = receivedData.keys()
                fields.sort()
                if fields!=['fieldName','fieldValue']:
                    raise web.HTTPError('400 bad request',{},'wrong fieldnames')
                if receivedData['fieldValue'] not in [True,False]:
                    print 'invalid setting {0}'.format(receivedData['fieldValue'])
                
                # enable/disable module
                dld.setDemoMode(receivedData['fieldValue'], username=username)
            
            else:
                raise web.notfound()
    
    class pageFastMode(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
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
                                            subResourcePath     = 'enable',
                                            title               = 'Fast Mode',
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['enable']:
                
                return [
                    {
                        'name':      "Fast Mode",
                        'value':     dld.getFastMode(username=username),
                        'type':      'boolean',
                        'editable':  True,
                    }
                ]
            
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['enable']:
                
                # filter errors
                fields = receivedData.keys()
                fields.sort()
                if fields!=['fieldName','fieldValue']:
                    raise web.HTTPError('400 bad request',{},'wrong fieldnames')
                if receivedData['fieldValue'] not in [True,False]:
                    print 'invalid setting {0}'.format(receivedData['fieldValue'])
                
                # enable/disable module
                dld.setFastMode(receivedData['fieldValue'], username=username)
            
            else:
                raise web.notfound()
    
    class pageFactoryReset(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
            global webServer
            global thisWebApp
            
            username    = web.ctx.session.username
            currentPath = WebPage.WebPage.urlStringTolist(web.ctx.path)
            
            page = thisWebApp.createPage(
                username        = username,
                currentPath     = currentPath,
                visualizations  =   [
                                        VizForm.VizForm(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'motes',
                                            title               = 'Reset Motes',
                                        ),
                                        VizForm.VizForm(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'manager',
                                            title               = 'Reset Manager',
                                        ),
                                        VizForm.VizForm(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'dustlink',
                                            title               = 'Reset DustLink',
                                        ),
                                        VizTable.VizTable(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'progress',
                                            title               = 'Progress',
                                        ),
                                        VizTable.VizTable(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'serialports',
                                            title               = 'Available Serial Ports',
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['motes']:
                return [
                    {
                        'name':           'command',
                        'value':          '',
                        'type':           'text',
                    },
                ]
            
            elif subResource==['manager']:
                return [
                    {
                        'name':           'connection',
                        'value':          '',
                        'type':           'text',
                    },
                ]
            
            elif subResource==['dustlink']:
                return [
                    {
                        'name':           'command',
                        'value':          '',
                        'type':           'text',
                    },
                ]
            
            elif  subResource==['progress']:
                
                # dummy read to validate that user has read privileges on 'system'
                dld.getEnabledPersistence(username=username)
                
                # columnNames
                columnNames = ['timestamp', 'event']
                
                # data
                data =  [
                            [
                                DustLinkData.DustLinkData.timestampToString(t),
                                e,
                            ]
                            for (t,e) in dld._getScratchpad()
                        ]
                
                return VizTable.VizTable.formatReturnVal(columnNames,data,[0.4,0])
            
            elif  subResource==['serialports']:
                
                # dummy read to validate that user has read privileges on 'system'
                dld.getEnabledPersistence(username=username)
                
                serialports = SystemPages._findSerialPorts()
                
                # columnNames
                columnNames = ['serialport']
                
                # data
                data =  [
                            [
                                p,
                            ]
                            for p in serialports
                        ]
                
                return VizTable.VizTable.formatReturnVal(columnNames,data)
            
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['motes']:
                
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['command']
                assert isinstance(receivedData['command'],str)
                
                # make sure this user had delete privileges on system
                dld.authorize(username,['system'],DustLinkData.DustLinkData.ACTION_DELETE)
                
                command = receivedData['command']
                
                if command=='reset':
                
                    dld._addScratchpad("<p class=\"doc-header\">Resetting DustLink.</p>")
                
                    resetter = ResetMotesNetwork.ResetMotesNetwork()
                    
                    dld._addScratchpad("<p class=\"doc-success\">success.</p>")
                    
                    dld._addScratchpad("<p class=\"doc-header\">done.</p>")
            
            elif subResource==['manager']:
                
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['connection']
                assert isinstance(receivedData['connection'],str)
                
                # make sure this user had delete privileges on system
                dld.authorize(username,['system'],DustLinkData.DustLinkData.ACTION_DELETE)
                
                connectionParams = SystemPages._createConnectionParams(receivedData['connection'])
                
                resetter = ResetManager.ResetManager(connectionParams)
            
            elif subResource==['dustlink']:
            
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['command']
                assert isinstance(receivedData['command'],str)
                
                # make sure this user had delete privileges on system
                dld.authorize(username,['system'],DustLinkData.DustLinkData.ACTION_DELETE)
                
                if receivedData['command'] in ['reset']:
                    with dld.dataLock:
                        # reset the DustLink data
                        dld.factoryReset()
                        dld.setDemoMode(True)
                        
                        # clear the mirror data
                        dispatcher.send(
                            signal        = 'clearMirrorData',
                            data          = None,
                        )
                        
                        webServer.getSessionStore().cleanup(0)
                        
                        # generate system event (as admin)
                        dld.setSystemEvent(DustLinkData.DustLinkData.SYSEVENT_FACTORYRESET)
            
            else:
                raise web.notfound()
        
    class pageLoadConfig(WebHandler.WebHandler):
        
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
                                            subResourcePath     = 'load',
                                            title               = 'Load Configuration File',
                                            autorefresh         = False,
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            if   subResource==['load']:
                
                output  = []
                output += ['<form method="POST" enctype="multipart/form-data" action="/system/loadconfig/json/load/">']
                output += ['<input type="file" name="configfile" />']
                output += ['<input type="submit" />']
                output += ['</form>']
                output  = '\n'.join(output)
                
                return {'rawHtml':output}
            
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['load']:
                
                with dld.dataLock:
                
                    # dummy read to validate that user has read privileges on 'system'
                    dld.getEnabledPersistence(username=username)
                    
                    assert isinstance(receivedData,dict)
                    assert receivedData.keys()==['configfile']
                    assert isinstance(receivedData['configfile'],str)
                    
                    # parse passed file (and make sure it's correctly formatted)
                    try:
                        parsedConfig = DustLinkData.DustLinkData.parseConfigString(receivedData['configfile'])
                    except ValueError as err:
                        raise web.HTTPError('400 bad request',{},'Badly formatted configuration file: {0}'.format(err))
                    
                    # reset DustLink data
                    dld.factoryReset()
                    
                    # clear the mirror data
                    dispatcher.send(
                        signal        = 'clearMirrorData',
                        data          = None,
                    )
                    
                    webServer.getSessionStore().cleanup(0)
                    
                    for line in parsedConfig:
                        if   line['type']=='app':
                            dld.addApp(line['appName'])
                            if line['transport']:
                                dld.setAppTransport(
                                    line['appName'],
                                    line['transport']['type'],
                                    line['transport']['resource'],
                                )
                            if line['fieldsFromMote']:
                                dld.setAppFields(
                                    line['appName'],
                                    DustLinkData.DustLinkData.APP_DIRECTION_FROMMOTE,
                                    line['fieldsFromMote']['fieldFormats'],
                                    line['fieldsFromMote']['fieldNames'],
                                )
                            if line['fieldsToMote']:
                                dld.setAppFields(
                                    line['appName'],
                                    DustLinkData.DustLinkData.APP_DIRECTION_TOMOTE,
                                    line['fieldsToMote']['fieldFormats'],
                                    line['fieldsToMote']['fieldNames'],
                                )
                        elif line['type']=='mote':
                            dld.addMote(
                                line['mac'],
                            )
                        elif line['type']=='network':
                            dld.addNetwork(
                                line['netname'],
                            )
                        elif line['type']=='attachApp':
                            dld.attachAppToMote(
                                line['mac'],
                                line['appName'],
                            )
                        elif line['type']=='user':
                            dld.addUser(
                                line['username'],
                            )
                        elif line['type']=='grantPrivilege':
                            dld.grantPrivilege(
                                line['resource'],
                                line['username'],
                                line['action'],
                            )
                        elif line['type']=='manager':
                            dld.addManagerConnection(
                                line['connectionDetails'],
                            )
                        elif line['type']=='publisherXively':
                            dld.setPublisherSettings(
                                publisherName    = dld.PUBLISHER_XIVELY,
                                settings         = {
                                    'xivelyApiKey':   line['xivelyApiKey'],
                                },
                            )
                        elif line['type']=='publisherGoogle':
                            dld.setPublisherSettings(
                                publisherName    = dld.PUBLISHER_GOOGLE,
                                settings         = {
                                    'spreadsheetKey': line['spreadsheetKey'],
                                    'worksheetName':  line['worksheetName'],
                                    'googleUsername': line['googleUsername'],
                                    'googlePassword': line['googlePassword'],
                                },
                            )
                        elif line['type']=='adminPassword':
                            try:
                                dld.setUserPassword(
                                    DustLinkData.DustLinkData.USER_ADMIN,
                                    DustLinkData.DustLinkData.DEFAULT_ADMIN_PASSWORD,
                                    line['password'],
                                    username=DustLinkData.DustLinkData.USER_ADMIN,
                                )
                            except DataVaultException.Unauthorized:
                                dld.setUserPassword(
                                    DustLinkData.DustLinkData.USER_ADMIN,
                                    line['password'],
                                    line['password'],
                                    username=DustLinkData.DustLinkData.USER_ADMIN,
                                )
                        elif line['type']=='fastMode':
                            dld.setFastMode(line['value'])
                        elif line['type']=='demoMode':
                            dld.setDemoMode(line['value'])
                        else:
                            raise ValueError('unknown command type {0}'.format(line['type']))
                    
                    # generate system event (as admin)
                    dld.setSystemEvent(DustLinkData.DustLinkData.SYSEVENT_CONFIGLOADED)
                    
                    # go to default page
                    raise web.seeother('/')
                
            else:
                raise web.notfound()
        
    class pageRestarts(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
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
                                            subResourcePath     = 'upTimeRestarts',
                                            title               = 'UpTime and Number of Restarts',
                                        ),
                                        VizTable.VizTable(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'lastRestarts',
                                            title               = 'Last Restart Times',
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['upTimeRestarts']:
                
                with dld.dataLock:
                    lastStartTimes = dld.getLastStartTimes(username=username)
                    if lastStartTimes:
                        lastStartTime = lastStartTimes[-1]
                        upTime        = str(datetime.timedelta(seconds=time.time()-lastStartTime))
                        return [
                            {
                                'name':      'UpTime',
                                'value':     upTime,
                                'type':      'text',
                                'editable':  False,
                            },
                            {
                                'name':      'number of restarts',
                                'value':     dld.getNumberOfRestarts(username=username),
                                'type':      'text',
                                'editable':  False,
                            },
                        ]
                    else:
                        return []
                
            elif subResource==['lastRestarts']:
                
                # columnNames
                columnNames = ['starttime']
                
                # data
                data =  [
                            [
                                DustLinkData.DustLinkData.timestampToString(t)
                            ]
                            for t in dld.getLastStartTimes(username=username)
                        ]
                
                return VizTable.VizTable.formatReturnVal(columnNames,data)
                
            else:
                raise web.notfound()
    
    class pageSessions(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
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
                                            subResourcePath     = 'active',
                                            title               = 'Active Web Sessions',
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            global webServer
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['active']:
                
                # dummy read to validate that user has read privileges on 'system'
                dld.getEnabledPersistence(username=username)
                
                # retrieve sessions
                sessions = webServer.getSessions()
                for session in sessions:
                    if not session['username']:
                        session['username'] = DustLinkData.DustLinkData.USER_ANONYMOUS
                
                # columnNames
                columnNames = ['username','ip','session_id']
                
                # data
                data = [
                    [
                        session['username'],
                        session['ip'],
                        session['session_id'],
                    ] for session in sessions
                ]
                
                return VizTable.VizTable.formatReturnVal(columnNames,data)
            
            else:
                raise web.notfound()
    
    class pageProfiling(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
            global webServer
            global thisWebApp
            
            username    = web.ctx.session.username
            currentPath = WebPage.WebPage.urlStringTolist(web.ctx.path)
            
            visualizations      =   []
            if yappiLoaded:
                visualizations +=   [
                                        VizFields.VizFields(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'yappi',
                                            title               = 'Yappi Profiler',
                                        ),
                                    ]
            visualizations  +=      [
                                        VizTable.VizTable(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'threads',
                                            title               = 'Thread Profiling',
                                        ),
                                    ]
            if yappiLoaded:
                visualizations  +=  [
                                        VizTable.VizTable(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'functions',
                                            title               = 'Function Profiling',
                                        ),
                                    ]
            
            page = thisWebApp.createPage(
                username        = username,
                currentPath     = currentPath,
                visualizations  = visualizations,
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            # dummy read to validate that user has read privileges on 'system'
            dld.getEnabledPersistence(username=username)
            
            if   subResource==['yappi']:
                if yappiLoaded:
                    return [
                        {
                            'name':      'enabled',
                            'value':     yappi.is_running(),
                            'type':      'boolean',
                            'editable':  True,
                        }
                    ]
                else:
                    raise web.notfound()
            
            elif subResource==['threads']:
            
                if yappiLoaded and yappi.is_running():
                    
                    self.threadStats = []
                    yappi.enum_thread_stats(self._enumerateThreadStats)
                    
                    assert isinstance(self.threadStats,list)
                    for s in self.threadStats:
                        assert isinstance(s,tuple)
                        assert len(s)==5
                    
                    # columnNames
                    columnNames = ['thread_name','thread_id','last_func','ttot','sched_count']
                    
                    # data
                    data =  [
                                [
                                    stat[0],
                                    stat[1],
                                    stat[2],
                                    stat[3],
                                    stat[4],
                                ]
                                for stat in self.threadStats
                            ]
                    
                    return VizTable.VizTable.formatReturnVal(columnNames,data)
                
                else:
                    
                    threadNames = [t.getName() for t in threading.enumerate()]
                    threadNames.sort()
                    
                    # columnNames
                    columnNames = ['threadname']
                    
                    # data
                    data =  [
                                [
                                    t,
                                ]
                                for t in threadNames
                            ]
                    
                    return VizTable.VizTable.formatReturnVal(columnNames,data)
                
            elif subResource==['functions']:
            
                if yappiLoaded:
                    
                    if yappi.is_running():
                        
                        allStats =  yappi.get_stats(
                                        yappi.SORTTYPE_TTOT,    # sorting key
                                        yappi.SORTORDER_DESC,   # sorting order
                                        20,                     # number of functions returned
                                    )
                        
                        # columnNames
                        columnNames = ['Function Name',
                                       'Number Calls',
                                       'total CPU time',
                                       'sub CPU time',
                                       'average CPU time']
                        
                        # data
                        data =  [
                                    [
                                        stat.name,
                                        stat.ncall,
                                        stat.ttot,
                                        stat.tsub,
                                        stat.tavg,
                                    ]
                                    for stat in allStats.func_stats
                                ]
                        
                        return VizTable.VizTable.formatReturnVal(columnNames,data)
                    
                    else:
                        
                        # columnNames
                        columnNames = ['Warning']
                        
                        # data
                        data =  [
                                    [
                                        'Yappi profiler not enabled.',
                                    ]
                                ]
                        
                        return VizTable.VizTable.formatReturnVal(columnNames,data)
                
                else:
                    
                    raise web.notfound()
            
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            # dummy read to validate that user has read privileges on 'system'
            dld.getEnabledPersistence(username=username)
            
            if   subResource==['yappi']:
                
                if yappiLoaded:
                    # filter errors
                    fields = receivedData.keys()
                    fields.sort()
                    if fields!=['fieldName','fieldValue']:
                        raise web.HTTPError('400 bad request',{},'wrong fieldnames')
                    if receivedData['fieldName'] not in ['enabled']:
                        raise web.HTTPError('400 bad request',{},'fieldName {0} unknown'.format(receivedData['fieldName']))
                    if receivedData['fieldValue'] not in [True,False]:
                        print 'invalid setting {0}'.format(receivedData['fieldValue'])
                    
                    # enable/disable yappi
                    if receivedData['fieldValue']:
                        yappi.start()
                    else:
                        yappi.stop()
                        yappi.clear_stats()
                else:
                    raise web.notfound()
            
            else:
                raise web.notfound()
        
        #==================== helpers =========================================
        
        def _enumerateThreadStats(self,threadStats):
            self.threadStats += [
                threadStats
            ]
    
    class pageEventBus(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
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
                                            subResourcePath     = 'stats',
                                            title               = 'Statistics',
                                        ),
                                        VizTree.VizTree(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'connections',
                                            title               = 'Connections',
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            # dummy read to validate that user has read privileges on 'system'
            dld.getEnabledPersistence(username=username)
                
            if   subResource==['stats']:
                
                allStats = dispatcher.send(
                    signal       = 'getStats',
                    data         = None,
                )
                
                # get the name of the stats
                statsNames = []
                for moduleStats in allStats:
                    stats = moduleStats[1]
                    for k in stats.keys():
                        if k not in statsNames:
                            statsNames.append(k)
                
                # columnNames
                columnNames = ['module']
                for name in ['QueueFill','numQueuedFail','numProcessFailed','numQueuedOk','numIn','numProcessOk','numOut']:
                    if name in statsNames:
                        columnNames.append(name)
                        statsNames.remove(name)
                columnNames += statsNames
                
                # data
                data = []
                for moduleStats in allStats:
                    line = []
                    line.append(moduleStats[0].im_self.name.replace('_',' '))
                    for columnName in columnNames[1:]:
                        try:
                            line.append(moduleStats[1][columnName])
                        except KeyError:
                            line.append('')
                    data.append(line)
                
                return VizTable.VizTable.formatReturnVal(columnNames,data)
            
            elif subResource==['connections']:
                
                return {
                    'name':       'signals',
                    'children':   [
                        {
                            'name': signalName,
                            'children': [
                                {
                                    'name': '{0}.{1}()'.format(r.im_class.__name__,r.__name__)
                                } for r in registrees
                            ],
                        } for (signalName,registrees) in dispatcher.connections[dispatcher.connections.keys()[0]].items()
                    ],
                }
            
            else:
                raise web.notfound()
    
    class pageRawData(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
            global webServer
            global thisWebApp
            
            username    = web.ctx.session.username
            currentPath = WebPage.WebPage.urlStringTolist(web.ctx.path)
            
            page = thisWebApp.createPage(
                username        = username,
                currentPath     = currentPath,
                design          = thisWebApp.DESIGN_ONE_COLUMN,
                visualizations  =   [
                                        VizTree.VizTree(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'rawdata',
                                            title               = 'Raw Data',
                                            width               = 1000,
                                            height              = 1500,
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['rawdata']:
                
                returnVal = self._formatData(dld.get(username=username))
                return {
                    "name":    "root",
                    "children": returnVal
                }
            
            else:
                raise web.notfound()
        
        #==================== helpers =========================================
        
        def _formatData(self,data):
            if isinstance(data,dict):
                returnVal = []
                for (k,v) in data.items():
                    thisItem         = {}
                    thisItem['name'] = k
                    if isinstance(v,dict):
                        thisItem['children'] = self._formatData(v)
                    else:
                        thisItem['value']    = self._formatData(v)
                    returnVal.append(copy.deepcopy(thisItem))
                return returnVal[:]
            else:
                return data
    
    class pageAbout(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
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
                                            subResourcePath     = 'version',
                                            title               = 'Versions',
                                        ),
                                        VizHtml.VizHtml(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'license',
                                            title               = 'License',
                                        ),
                                        VizTable.VizTable(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'thirdparty',
                                            title               = 'Third Party Licenses',
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['version']:
                
                # dummy read to validate that user has read privileges on 'system'
                dld.getEnabledPersistence(username=username)
                
                # columnNames
                columnNames = ['component','version']
                
                # fill in data
                data =  [
                    [
                        'DustLink',
                        self._formatVersion(DustLink_version.VERSION),
                    ],
                    [
                        'SmartMeshSDK',
                        self._formatVersion(sdk_version.VERSION),
                    ],
                ]
                
                return VizTable.VizTable.formatReturnVal(columnNames,data)
            
            elif subResource==['license']:
                
                try:
                    file = open(os.path.join('..','..','..','DN_LICENSE.txt'),'r')
                    licenseString = file.read()
                    file.close()
                except IOError:
                    licenseString = 'See DN_LICENSE.txt file.'
                
                returnString  = []
                returnString += ['<pre>']
                returnString += [licenseString]
                returnString += ['</pre>']
                returnString  = ''.join(returnString)
                
                return {'rawHtml':returnString}
            
            elif subResource==['thirdparty']:
                
                # columnNames
                columnNames = ['Name','Author','Website','License']
                
                # fill in data
                data =  [
                    [
                        'D3js',
                        'Michael Bostock',
                        '<a target="_new" href="http://d3js.org/">website</a>',
                        '<a target="_new" href="/static/javascript/d3.v2.license">license</a>',
                    ],
                    [
                        'dagre',
                        'Chris Pettitt',
                        '<a target="_new" href="https://github.com/cpettitt/dagre">website</a>',
                        '<a target="_new" href="https://github.com/cpettitt/dagre/blob/master/LICENSE">license</a>',
                    ],
                    [
                        'dataTables',
                        'Allan Jardine',
                        '<a target="_new" href="http://datatables.net/">website</a>',
                        '<a target="_new" href="/static/javascript/jquery.dataTables.min.license">license</a>',
                    ],
                    [
                        'Google Visualization Converter',
                        '',
                        '<a target="_new" href="http://code.google.com/p/google-visualization-python/">website</a>',
                        '<a target="_new" href="http://www.apache.org/licenses/LICENSE-2.0">license</a>',
                    ],
                    [
                        'jQuery',
                        '',
                        '<a target="_new" href="http://jquery.com/">website</a>',
                        '<a target="_new" href="/static/javascript/jquery-1.8.0.min.license">license</a>',
                    ],
                    [
                        'Morris.js',
                        'Olly Smith',
                        '<a target="_new" href="http://oesmith.github.com/morris.js/">website</a>',
                        '<a target="_new" href="/static/javascript/morris.min.license">license</a>',
                    ],
                    [
                        'Rapha&euml;l',
                        'Dmitry Baranovskiy',
                        '<a target="_new" href="http://raphaeljs.com/">website</a>',
                        '<a target="_new" href="/static/javascript/raphael-min.license">license</a>',
                    ],
                    [
                        'web.py',
                        'Aaron Swartz',
                        '<a target="_new" href="http://webpy.org/">website</a>',
                        '<a target="_new" href="http://webpy.org/">license</a>',
                    ],
                    [
                        'Xively',
                        '',
                        '<a target="_new" href="https://xively.com/">website</a>',
                        '<a target="_new" href="https://github.com/xively/xively-python/blob/master/LICENSE.md">license</a> (Python)<br/><a target="_new" href="https://github.com/xively/xively-js/blob/master/LICENSE.md">license</a> (Javascript)',
                    ],
                ]
                
                return VizTable.VizTable.formatReturnVal(columnNames,data)
            
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            
            raise web.notfound()
        
        #==================== helpers =========================================
        
        def _formatVersion(self,version):
            return '.'.join([str(b) for b in version])
    
    #======================== helpers =========================================
    
    @classmethod
    def _findSerialPorts(self):
        try:
            serialports = []
            
            if os.name=='nt':
                key  = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'HARDWARE\\DEVICEMAP\\SERIALCOMM')
                for i in range(winreg.QueryInfoKey(key)[1]):
                    try:
                        val = winreg.EnumValue(key,i)
                    except:
                        pass
                    else:
                        if val[0].find('VCP')>-1:
                            serialports.append(str(val[1]))
            elif os.name=='posix':
                serialports = glob.glob('/dev/ttyUSB*')
            
            serialports.sort()
            
            return serialports
        except Exception as err:
            return ['Could not scan for serial port. Error={0}'.format(err)]
    
    @classmethod
    def _createConnectionParams(self,connection):
        if   connection.count(':'):
            connection    = connection.split(':')
            connection[1] = int(connection[1])
            connection    = tuple(connection)
        elif connection.upper().startswith('COM'):
            connection    = connection.upper()
        return connection
    
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
                                      url             = 'system',
                                      title           = 'System',
                                      webHandler      = self.pageWelcome,)
        
        # add sub-pages
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'welcome',
                                          title       = 'Welcome',
                                          webHandler  = self.pageWelcome,))
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'managers',
                                          title       = 'Managers',
                                          webHandler  = self.pageManagers,))
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'publishers',
                                          title       = 'Publishers',
                                          webHandler  = self.pagePublishers,))
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'adminpassword',
                                          title       = 'Admin Password',
                                          webHandler  = self.pageAdminPassword,))
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'modules',
                                          title       = 'Modules',
                                          webHandler  = self.pageModules,))
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'persistence',
                                          title       = 'Persistence',
                                          webHandler  = self.pagePersistence,))
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'demomode',
                                          title       = 'Demo Mode',
                                          webHandler  = self.pageDemoMode,))                                  
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'fastmode',
                                          title       = 'Fast Mode',
                                          webHandler  = self.pageFastMode,))
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'factoryreset',
                                          title       = 'Factory Reset',
                                          webHandler  = self.pageFactoryReset,))
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'loadconfig',
                                          title       = 'Load Config',
                                          webHandler  = self.pageLoadConfig,))
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'restarts',
                                          title       = 'Restarts',
                                          webHandler  = self.pageRestarts,))
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'sessions',
                                          title       = 'Sessions',
                                          webHandler  = self.pageSessions,))
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'profiling',
                                          title       = 'Profiling',
                                          webHandler  = self.pageProfiling,))
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'eventbus',
                                          title       = 'EventBus',
                                          webHandler  = self.pageEventBus,))
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'rawdata',
                                          title       = 'Raw Data',
                                          webHandler  = self.pageRawData,))
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = 'about',
                                          title       = 'About',
                                          webHandler  = self.pageAbout,))
