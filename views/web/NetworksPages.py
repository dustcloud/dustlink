import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('NetworksPages')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import random

# For topology string building
from cStringIO import StringIO

from dustWeb import web
from DustLinkData import DataVaultException, \
                         DustLinkData

from ApiDefinition import IpMgrDefinition

from Gateway import FormatUtils

from dustWeb import WebPage
from dustWeb import WebPageDyn
from dustWeb import WebHandler
from dustWeb.viz import VizFields
from dustWeb.viz import VizForm
from dustWeb.viz import VizHtml
from dustWeb.viz import VizTable
from dustWeb.viz import VizTopology
from dustWeb.thirdparty import gviz_api

#============================ object ==========================================

def getFromDict(dic, key, otherwise='?', typeConv=None):
    '''Get an entry from a dict if it is set, otherwise return ?.'''
    if key in dic:
        if typeConv:
            return typeConv(dic[key])
        else:
            return dic[key]
    else:
        return otherwise

class NetworksPages(WebPageDyn.WebPageDyn):
    
    DOT_NODE = '  {ID} [label="{LABEL}", class="{CLASS}", description="{DESCRIPTION}", macAddress="{MACADDRESS}"];'
    DOT_PATH = '  {ID1} -> {ID2} [description="{DESCRIPTION}"];'
    
    #===== web handlers (private classes)
    
    class pageNetworks(WebHandler.WebHandler):
        
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
                                            title               = 'Add a network',
                                        ),
                                        VizForm.VizForm(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'delete',
                                            title               = 'Delete a network',
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if subResource==['add']:
                return [
                    {
                        'name':           'netname',
                        'value':          '',
                        'type':           'text',
                    },
                ]
            elif subResource==['delete']:
                netnames = dld.getNetnames(username=username)
                netnames = [FormatUtils.unquote(n) for n in netnames]
                return [
                    {
                        'name':           'netname',
                        'value':          None,
                        'optionDisplay':  netnames,
                        'optionValue':    netnames,
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
                assert receivedData.keys()==['netname']
                assert isinstance(receivedData['netname'],str)
                
                netname = receivedData['netname']
                netname = FormatUtils.quote(netname)
                dld.addNetwork(netname, username=username)
            
            elif subResource==['delete']:
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['netname']
                assert isinstance(receivedData['netname'],str)
                
                netname = receivedData['netname']
                netname = FormatUtils.quote(netname)
                dld.deleteNetwork(netname, username=username)
            
            else:
                raise web.notfound()
    
    class pageNetworksSub(WebPageDyn.WebHandlerDyn):
        
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
                                        VizTopology.VizTopology(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'topology',
                                            title               = 'Topology',
                                            width               = 500,
                                            height              = 500,
                                        ),
                                        VizTable.VizTable(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'motes',
                                            title               = 'Motes in This Network',
                                        ),
                                        VizTable.VizTable(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'paths',
                                            title               = 'Paths',
                                        ),
                                    ],
            )
            
            return page
        
        def getDataDyn(self,dynPath,subResource,username):
            
            netname = dynPath
            dld     = DustLinkData.DustLinkData()
            
            if   subResource==['info']:
                
                netInfo =  dld.getNetworkInfo(netname,username=username)
                
                if netInfo:
                    return [
                        {
                            'name':      k,
                            'value':     v,
                            'type':      'text',
                            'editable':  False,
                        }
                        for (k,v) in netInfo.items()
                    ]
                else:
                    return []
            
            elif subResource==['topology']:
                
                return (
                    NetworksPages.topologyToDot(netname,username),
                    WebHandler.WebHandler.ALREADY_JSONIFIED,
                )

            elif subResource==['motes']:
                # data
                data = []
                for mac in dld.getNetworkMotes(netname,username=username):
                    data.append([DustLinkData.DustLinkData.macToString(mac)])
                
                # columnNames
                columnNames = ['mac']
                
                return VizTable.VizTable.formatReturnVal(columnNames,data)
            
            elif subResource==['paths']:
                
                with dld.dataLock:
                    pathsToReturn = dld.getNetworkPaths(netname,username=username)
                    
                    # columnNames
                    columnNames = ['from','to','direction']
                    
                    # data
                    if pathsToReturn:
                        data = []
                        for p in pathsToReturn:
                            pathInfo = dld.getPathInfo(netname,p[0],p[1],username=username)
                            if pathInfo and ('direction' in pathInfo):
                                data += [
                                    [
                                        DustLinkData.DustLinkData.macToString(p[0]),
                                        DustLinkData.DustLinkData.macToString(p[1]),
                                        IpMgrDefinition.IpMgrDefinition.fieldOptionToShortDesc(
                                            'pathDirection',
                                            pathInfo['direction']
                                        )
                                    ]
                                ]
                    else:
                        data =  []
                    
                    return VizTable.VizTable.formatReturnVal(columnNames,data)
                
            else:
                raise web.notfound()
        
        def postDataDyn(self,receivedData,dynPath,subResource,username):
            
            netname = dynPath
            
            raise web.notfound()
    
    @classmethod
    def topologyToDot(self,netname,username=DustLinkData.DustLinkData.USER_SYSTEM):
        '''
        \brief Format the topology of a network as a dot string.
        
        Typically, this string is returned to a visualization tool such as 
        dagre (https://github.com/cpettitt/dagre) to be displayed.
        
        \returns A string representing the topology in dot notation.
        '''
        
        #===== variables
        
        dld             = DustLinkData.DustLinkData()
        motes           = {} # a dict of format { <macAddress>: <moteInfo>}
        connectedMotes  = [] # mac addresses of motes that are path of a path
        paths           = {} # a dict of format { (fromMac,toMac) : <pathInfo>}
        
        #===== helpers
        
        def getMoteIdentifier(mac):
            return ''.join(['N',''.join(["%.2x"%m for m in mac])])
        
        def moteToDot(mac):
                
                isManager = getFromDict(motes[mac], 'isAP', False)
                
                # id
                moteId    = getMoteIdentifier(mac)
                
                # label
                moteLabel = DustLinkData.DustLinkData.macToShortString(mac)
                
                # class
                if isManager:
                    moteClass = 'manager'
                elif mac not in connectedMotes:
                    moteClass = 'disconnected'
                else:
                    moteClass = ' '
                
                # description
                
                moteMac   = DustLinkData.DustLinkData.macToString(mac)
                
                if ('packetsReceived' in motes[mac]) and ('packetsLost' in motes[mac]):
                    packetsReceived = motes[mac]['packetsReceived']
                    packetsLost     = motes[mac]['packetsLost']
                    if (packetsReceived + packetsLost) > 0:
                        reliability = 100 * packetsReceived / (packetsReceived + packetsLost)
                    else:
                        reliability = '?'
                else:
                    reliability = '?'
                
                if isManager:
                    ap = ' (AP) '
                else:
                    ap = ' '
                
                description = ''.join([moteLabel, ap,
                                       moteMac,
                                       '\nGood Neighbors: ',
                                       getFromDict(motes[mac], 'numGoodNbrs', '?', str),
                                       '\nReliability: ',
                                       str(reliability),
                                       '%',
                                       ])
                
                kw = {
                    'ID':              moteId,
                    'LABEL':           moteLabel,
                    'CLASS':           moteClass,
                    'DESCRIPTION':     description,
                    'MACADDRESS':      moteMac,
                }
                return NetworksPages.DOT_NODE.format(**kw)
            
        def pathToDot(fromMac,toMac,pathInfo):
            
            description = ''.join(
                [
                    DustLinkData.DustLinkData.macToShortString(fromMac),
                    ' / ',
                    DustLinkData.DustLinkData.macToShortString(toMac),
                    '\n',
                    
                    'Quality: ',
                    str(getFromDict(pathInfo, 'quality', 'N/A')),
                    '\n',
                    
                    'RSSI: ',
                    str(getFromDict(pathInfo, 'rssiSrcDest')),
                    ' / ',
                    str(getFromDict(pathInfo, 'rssiDestSrc'))
                ]
            )

            kw = {
                'ID1':            getMoteIdentifier(fromMac),
                'ID2':            getMoteIdentifier(toMac),
                'DESCRIPTION':    description,
            }
            return NetworksPages.DOT_PATH.format(**kw)
        
        #===== "main"
        
        with dld.dataLock:
            # populate motes
            for macAddress in dld.getNetworkMotes(netname,username=username):
                motes[macAddress] = dld.getMoteInfo(macAddress)
                if not motes[macAddress]:
                    motes[macAddress] = {}

            # populate paths
            for (fromMac,toMac) in dld.getNetworkPaths(netname,username=username):
                pathInfo = dld.getPathInfo(netname,fromMac,toMac,username=username)
                if not pathInfo or ('direction' not in pathInfo):
                    continue
                if   pathInfo['direction'] == 3:
                    paths[(fromMac,toMac)] = pathInfo
                elif pathInfo['direction'] == 2:
                    paths[(toMac,fromMac)] = pathInfo
        
        # populate connectedMotes
        for (fromMac,toMac) in paths:
            connectedMotes.append(fromMac)
            connectedMotes.append(toMac)
        
        # generate dot string
        returnVal       = []
        returnVal      += ["digraph {"]
        for macAddress in sorted(motes.keys()):
            returnVal  += [moteToDot(macAddress)]
        for (fromMac,toMac),pathInfo in paths.items():
            returnVal  += [pathToDot(fromMac,toMac,pathInfo)]
        returnVal      += ["}"]
        
        return '\n'.join(returnVal)
    
    def subPageLister(self):
        username = str(web.ctx.session.username)
        dld      = DustLinkData.DustLinkData()
        try:
            return [
                {
                    'url':   n,
                    'title': FormatUtils.unquote(n),
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
                                            url             = 'networks',
                                            title           = 'Networks',
                                            webHandler      = self.pageNetworks,
                                            subPageLister   = self.subPageLister,
                                            subPageHandler  = self.pageNetworksSub)
