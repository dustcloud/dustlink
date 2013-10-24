import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('AppsPages')
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
from dustWeb.viz import VizAppFields
from dustWeb.thirdparty import gviz_api

#============================ object ==========================================
        
class AppsPages(WebPageDyn.WebPageDyn):
    
    #===== web handlers (private classes)
    
    class pageApps(WebHandler.WebHandler):
        
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
                                            subResourcePath     = 'add',
                                            title               = 'Add an Application',
                                        ),
                                        VizForm.VizForm(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'delete',
                                            title               = 'Delete an Application',
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['add']:
                return [
                    {
                        'name':           'appname',
                        'value':          '',
                        'type':           'text',
                    },
                ]
            elif subResource==['delete']:
                appnames = dld.getAppNames(username=username)
                
                return [
                    {
                        'name':           'appname',
                        'value':          None,
                        'optionDisplay':  appnames,
                        'optionValue':    appnames,
                        'type':           'select',
                        'editable':       True,
                    },
                ]
            else:
                raise web.notfound()
        
        def postData(self,receivedData,subResource,username):
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['add']:
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['appname']
                assert isinstance(receivedData['appname'],str)
                
                dld.addApp(
                    receivedData['appname'],
                    username=username,
                )
            elif subResource==['delete']:
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['appname']
                assert isinstance(receivedData['appname'],str)
                
                dld.deleteApp(
                    receivedData['appname'],
                    username=username,
                )
            else:
                raise web.notfound()
        
    class pageAppsSub(WebPageDyn.WebHandlerDyn):
        
        #==================== GET =============================================
        
        def getPageDyn(self,dynPath,subResource,username):
            global webServer
            global thisWebApp
            
            username    = web.ctx.session.username
            currentPath = WebPage.WebPage.urlStringTolist(web.ctx.path)
            
            page = thisWebApp.createPage(
                username        = username,
                currentPath     = currentPath,
                visualizations  =   [
                                        VizAppFields.VizAppFields(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'appfields',
                                            forbidAutorefresh   = True,
                                            autorefresh         = False,
                                            title               = self.getDynPath()
                                        ),
                                    ],
            )
            
            return page
        
        def getDataDyn(self,dynPath,subResource,username):
            
            appname = dynPath
            
            dld = DustLinkData.DustLinkData()
            if   subResource==['appfields']:
                with dld.dataLock:
                    return {
                        'description':  dld.getAppDescription(appname,username=username),
                        'transport':    self._transportDbToWeb(
                                            dld.getAppTransport(
                                                appname,
                                                username=username,
                                            )
                                        ),
                        'fromMote':     self._fieldsDbToWeb(
                                            dld.getAppFields(
                                                appname,
                                                DustLinkData.DustLinkData.APP_DIRECTION_FROMMOTE,
                                                username=username,
                                            )
                                        ),
                        'toMote':       self._fieldsDbToWeb(
                                            dld.getAppFields(
                                                appname,
                                                DustLinkData.DustLinkData.APP_DIRECTION_TOMOTE,
                                                username=username,
                                            )
                                        ),
                    }
            else:
                raise web.notfound()
        
        #==================== POST ============================================
        
        def postDataDyn(self,receivedData,dynPath,subResource,username):
            
            appname = dynPath
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['appfields']:
                with dld.dataLock:
                    # description
                    self._postDataDynDescription(
                        appname,
                        receivedData['description'],
                        username,
                    )
                    
                    # transport
                    self._postDataDynTransport(
                        appname,
                        receivedData['transport'],
                        username,
                    )
                    
                    # fromMote
                    self._postDataDynFields(
                        appname,
                        DustLinkData.DustLinkData.APP_DIRECTION_FROMMOTE,
                        receivedData['fromMote'],
                        username,
                    )
                    
                    # toMote
                    self._postDataDynFields(
                        appname,
                        DustLinkData.DustLinkData.APP_DIRECTION_TOMOTE,
                        receivedData['toMote'],
                        username,
                    )
                
            else:
                raise web.notfound()
        
        def _postDataDynDescription(self,appname,description,username):
            dld = DustLinkData.DustLinkData()
            
            dld.setAppDescription(
                appname=appname,
                description=description,
                username=username,
            )
        
        def _postDataDynTransport(self,appname,receivedData,username):
            
            (dbType,dbResource) = self._transportWebToDb(receivedData)
            dld = DustLinkData.DustLinkData()
            
            dld.setAppTransport(
                appname=appname,
                transportType=dbType,
                resource=dbResource,
                username=username,
            )
        
        def _postDataDynFields(self,appname,direction,receivedData,username):
            
            updatefields = True
            dbFields = self._fieldsWebToDb(receivedData)
            
            dld = DustLinkData.DustLinkData()
            with dld.dataLock:
                if direction==DustLinkData.DustLinkData.APP_DIRECTION_FROMMOTE:
                    # get the current fields setting for FROMMOTE direction (as admin)
                    currentFromFields = dld.getAppFields(
                                            appname,
                                            DustLinkData.DustLinkData.APP_DIRECTION_FROMMOTE
                                        )
                    
                    updatefields = (not (currentFromFields==dbFields))
                    
                    if currentFromFields==dbFields:
                        updatefields = False
                
                # update fields
                if updatefields:
                    
                    # update DustLinkData (do first)
                    dld.setAppFields(
                        appname=appname,
                        direction=direction,
                        fieldFormats=dbFields['fieldFormats'],
                        fieldNames=dbFields['fieldNames'],
                        username=username
                    )
                    
                    if direction==DustLinkData.DustLinkData.APP_DIRECTION_FROMMOTE:
                        # the format of the data received from this application has
                        # changed. This means that data already received from apps
                        # using that application has been parsed incorrectly. It is
                        # hard to convert old to new parsed data, so we delete the
                        # data received from that application, on all motes. We do
                        # this as admin
                        
                        for mac in dld.getMoteMacs():
                            try:
                                dld.deleteData(mac,appname)
                            except ValueError:
                                pass # happens when app not attached to mote
        
        #==================== helpers =========================================
        
        structToString = [
            ('b', 'INT8'  ),
            ('B', 'INT8U' ),
            ('h', 'INT16' ),
            ('H', 'INT16U'),
            ('l', 'INT32' ),
            ('L', 'INT32U'),
        ]
        
        @classmethod
        def _transportDbToWeb(self,dbTransport):
            '''
            \brief Convert the transport description as read from DustLinkData
                   into a format usable by the VizAppFields visualization.
            
            \param dbTransport The transport description of the app, as 
                               returned by DustLinkData.getAppTransport(), i.e.
                               a tuple (transport,resource).
            
            \returns The same transport information, formatted as a dictionary,
                     e.g.   {
                               'type':       'UDP',
                               'resource':   61626,
                            }
            '''
            transportType     = dbTransport[0]
            transportResource = dbTransport[1]
            if transportType:
                transportTypeString     = transportType
            else:
                transportTypeString     = ''
            if not transportResource:
                transportResourceString = ''
            elif isinstance(transportResource,tuple):
                transportResourceString = ','.join([str(r) for r in transportResource])
            else:
                transportResourceString = str(transportResource)
            
            return {
               'type':       transportTypeString,
               'resource':   transportResourceString,
            }
        
        @classmethod
        def _fieldsDbToWeb(self,dbFields):
            '''
            \brief Convert the field description as read from DustLinkData
                   into a format usable by the VizAppFields visualization.
            
            \param dbFields The fields description of the app, as 
                            returned by DustLinkData.getAppFields().
            
            \returns The same field information, formatted as a dictionary,
                     e.g.   {
                                'endianness':     'little-endian',
                                'fieldRows': [
                                    {
                                        'format': 'INT16',
                                        'name':   'toMote1',
                                    },
                                    {
                                        'format': 'INT32',
                                        'name':   'toMote2',
                                    },
                                    {
                                        'format': 'INT32U',
                                        'name':   'toMote3',
                                    },
                                ],
                            }
            '''
            returnVal = {}
            
            fieldFormats     = dbFields['fieldFormats']
            fieldNames       = dbFields['fieldNames']
            
            # endianness
            if fieldFormats:
                if   fieldFormats.startswith('<'):
                    returnVal['endianness']      = 'little-endian'
                    fieldFormats                 = fieldFormats[1:]
                elif fieldFormats.startswith('>'):
                    returnVal['endianness']      = 'big-endian'
                    fieldFormats                 = fieldFormats[1:]
                else:
                    raise SystemError("No endianness specified in format \"{0}\"".format(fieldFormats))
            else:
                returnVal['endianness']          = None
            
            # fieldRows
            returnVal['fieldRows']          = []
            if fieldFormats:
                for c in fieldFormats:
                    thisField = {}
                    
                    for s in self.structToString:
                        if s[0]==c:
                            thisField['format'] = s[1]
                    
                    thisField['name']           = fieldNames[len(returnVal['fieldRows'])]
                    
                    returnVal['fieldRows'].append(thisField)
                
            return returnVal
        
        @classmethod
        def _transportWebToDb(self,webTransport):
            
            # type
            if not webTransport['type']:
                dbType = None
            else:
                dbType = str(webTransport['type'])
            
            # resource
            if not webTransport['resource']:
                dbResource = None
            elif dbType == DustLinkData.DustLinkData.APP_TRANSPORT_OAP:
                dbResource = []
                for c in webTransport['resource'].split(','):
                    if c:
                        dbResource += [int(c)]
                dbResource = tuple(dbResource)
            else:
                dbResource = int(webTransport['resource'])
            
            return (dbType,dbResource)
        
        @classmethod
        def _fieldsWebToDb(self,webFields):
            returnVal                 = {}
            returnVal['fieldFormats'] = ''
            returnVal['fieldNames']   = []
            
            # endianness
            if   webFields['endianness']=='little-endian':
                returnVal['fieldFormats'] += '<'
            elif webFields['endianness']=='big-endian':
                returnVal['fieldFormats'] += '>'
            elif (not webFields['endianness']):
                returnVal['fieldFormats'] += '>'
            else:
                raise SystemError("unexpected endianness {0}".format(webFields['endianness']))
            
            # fieldRows
            for f in webFields['fieldRows']:
                for s in self.structToString:
                    if s[1]==f['format']:
                        returnVal['fieldFormats'] += str(s[0])
                returnVal['fieldNames'].append(str(f['name']))
            
            if (not returnVal['fieldFormats']) or (returnVal['fieldFormats']=='<') or (returnVal['fieldFormats']=='>'):
                returnVal['fieldFormats']   = None
            if not returnVal['fieldNames']:
                returnVal['fieldNames']     = None
            
            return returnVal
        
    def subPageLister(self):
        username = str(web.ctx.session.username)
        dld = DustLinkData.DustLinkData()
        
        try:
            return [
                {
                    'url':   u,
                    'title': u,
                }
                for u in dld.getAppNames(username=username)
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
                                            url             = 'apps',
                                            title           = 'Apps',
                                            webHandler      = self.pageApps,
                                            subPageLister   = self.subPageLister,
                                            subPageHandler  = self.pageAppsSub)