import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('MoteDataPages')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import time
import datetime
import random
from dustWeb import web
import threading
import copy
import json

from pydispatch import dispatcher

from dustWeb import DustWeb
from dustWeb import WebPage
from dustWeb import WebHandler
from dustWeb.viz import VizForm
from dustWeb.viz import VizTimeLine
from dustWeb.viz import VizHtml
from dustWeb.thirdparty import gviz_api

from DustLinkData import DustLinkData

#============================ object ==========================================
        
class MoteDataPages(WebPage.WebPage):
    
    #===== web handlers (private classes)
    
    class pageMoteData(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
            global webServer
            global thisWebApp
            
            dld = DustLinkData.DustLinkData()
            context = self._getContext()
            
            pathSuffix  = []
            pathSuffix += ['?']
            pathSuffix += ['mac={0}'.format(context['mac'])]
            pathSuffix += ['&app={0}'.format(context['app'])]
            pathSuffix  = ''.join(pathSuffix)
            
            username    = web.ctx.session.username
            currentPath = WebPage.WebPage.urlStringTolist(web.ctx.path)
            
            visualizations = []
            
            with dld.dataLock:
                try:
                    dld.getAppDescription(
                        context['app'],
                        username=username,
                    )
                except ValueError:
                    pass # happens when no description
                else:
                    visualizations += [
                        VizHtml.VizHtml(
                            webServer           = webServer,
                            username            = username,
                            resourcePath        = currentPath,
                            subResourcePath     = 'description'+pathSuffix,
                            title               = 'App Description',
                        ),
                    ]
                
                if dld.getAppFields(
                                    context['app'],
                                    DustLinkData.DustLinkData.APP_DIRECTION_FROMMOTE,
                                    username=username,
                                )['fieldNames']:
                    visualizations += [
                        VizTimeLine.VizTimeLine(
                            webServer           = webServer,
                            username            = username,
                            resourcePath        = currentPath,
                            subResourcePath     = 'received'+pathSuffix,
                            title               = 'Received from {0}@{1}'.format(
                                                        context['app'],
                                                        context['mac']
                                                   ),
                        ),
                        VizForm.VizForm(
                            webServer           = webServer,
                            username            = username,
                            resourcePath        = currentPath,
                            subResourcePath     = 'clear'+pathSuffix,
                            title               = 'Clear received data',
                        ),
                    ]
                    
                if dld.getAppFields(
                                    context['app'],
                                    DustLinkData.DustLinkData.APP_DIRECTION_TOMOTE,
                                    username=username,
                                )['fieldNames']:
                    visualizations += [
                        VizForm.VizForm(
                            webServer           = webServer,
                            username            = username,
                            resourcePath        = currentPath,
                            subResourcePath     = 'send'+pathSuffix,
                            title               = 'Send to {0}@{1}'.format(
                                                        context['app'],
                                                        context['mac']
                                                   ),
                        ),
                    ]
            
            page = thisWebApp.createPage(
                username        = username,
                currentPath     = currentPath,
                design          = WebPage.WebPage.DESIGN_ONE_COLUMN,
                visualizations  = visualizations,
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld     = DustLinkData.DustLinkData()
            
            mac     = DustLinkData.DustLinkData.stringToMac(str(web.input().mac.rstrip('/')))
            appName =                                       str(web.input().app.rstrip('/'))
            
            if   subResource==['description']:
                
                # retrieve the description of that application
                try:
                    appDescription = dld.getAppDescription(
                        appName,
                        username=username,
                    )
                except ValueError:
                    return {'rawHtml':''} # happens when no description
                else:
                    return {'rawHtml':appDescription}
            
            elif subResource==['received']:
                
                # retrieve the last data received from the mac/application
                rawData = dld.getLastData(mac,appName,username=username)
                
                if rawData:
                    
                    # assume no data received
                    fieldNames   = []
                    timelineData = []
                    
                    # get field Names
                    fieldNames = rawData[rawData.keys()[0]].keys()
                    
                    # fill in data
                    timestamps = rawData.keys()
                    timestamps.sort()
                    for t in timestamps:
                        thisData = {}
                        thisData['timestamp'] = int(t*1000)
                        for f in fieldNames:
                            thisData[f] = rawData[t][f]
                        timelineData.append(thisData)
                    
                    return {
                        'metadata': {
                            'axis': tuple(fieldNames),
                        },
                        'datapoints': timelineData,
                    }
                
                else:
                    return {
                        'metadata': {
                            'axis': ['nodata'],
                        },
                        'datapoints': [
                            {"timestamp": 0, "nodata": 0},
                        ],
                    }
                
                
            
            elif subResource==['clear']:
                
                return [
                    {
                        'name':           'command',
                        'value':          '',
                        'type':           'text',
                    }
                ]
            
            elif subResource==['send']:
                
                return [
                    {
                        'name':           fieldname,
                        'value':          '',
                        'type':           'text',
                    } for fieldname in  dld.getAppFields(
                                            appName,
                                            DustLinkData.DustLinkData.APP_DIRECTION_TOMOTE,
                                            username=username,
                                        )['fieldNames']
                ]
            
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['send']:
                
                mac     = DustLinkData.DustLinkData.stringToMac(str(web.input().mac.rstrip('/')))
                appName =                                       str(web.input().app.rstrip('/'))
                
                assert isinstance(receivedData,dict)
                assert len(receivedData.keys())==3
                assert 'app' in receivedData.keys()
                del    receivedData['app']
                assert 'mac' in receivedData.keys()
                del    receivedData['mac']
                
                formData = json.loads(receivedData.keys()[0])
                formData = DustWeb.simplifyWebInputFormat(formData)
                
                receivedKeys = formData.keys()
                receivedKeys.sort()
                fieldNames = dld.getAppFields(
                                            appName,
                                            DustLinkData.DustLinkData.APP_DIRECTION_TOMOTE,
                                            username=username,
                                        )['fieldNames']
                fieldNames.sort()
                assert receivedKeys == fieldNames
                
                fields = {}
                for fieldName in fieldNames:
                    fields[fieldName] = formData[fieldName]
                
                dispatcher.send(
                    signal        = 'fieldsToMesh_{0}'.format(appName),
                    data          = {
                        'mac':    mac,
                        'fields': fields,
                    }
                )
            
            elif subResource==['clear']:
                
                mac     = DustLinkData.DustLinkData.stringToMac(str(web.input().mac.rstrip('/')))
                appname =                                       str(web.input().app.rstrip('/'))
                
                assert isinstance(receivedData,dict)
                assert len(receivedData.keys())==3
                assert 'app' in receivedData.keys()
                del receivedData['app']
                assert 'mac' in receivedData.keys()
                del receivedData['mac']
                
                formData = json.loads(receivedData.keys()[0])
                formData = DustWeb.simplifyWebInputFormat(formData)
                receivedKeys = formData.keys()
                
                assert receivedKeys == ['command']
                
                if formData['command']=='clear':
                    dld.deleteData(
                        mac       = mac,
                        appname   = appname,
                        username  = username,
                    )
                
            else:
                raise web.notfound()
        
        def _getContext(self):
            context = {}
            
            try:
                context['mac']    = str(web.input().mac.rstrip('/'))
            except AttributeError:
                context['mac']    = None
            try:
                context['app']    = str(web.input().app.rstrip('/'))
            except AttributeError:
                context['app']    = None
            
            return context
        
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
                                      url             = 'motedata',
                                      title           = 'MoteData',
                                      webHandler      = self.pageMoteData)