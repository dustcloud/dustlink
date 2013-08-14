import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('FirewallPages')
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
        
class FirewallPages(WebPageDyn.WebPageDyn):
    
    #===== web handlers (private classes)
    
    class pageFirewall(WebHandler.WebHandler):
        
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
        
    class pageFirewallSub(WebPageDyn.WebHandlerDyn):
        
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
                                            subResourcePath     = 'defaultrule',
                                            title               = 'Default Rule',
                                        ),
                                        VizTable.VizTable(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'rules',
                                            title               = 'Rules',
                                        ),
                                        VizForm.VizForm(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'add',
                                            title               = 'Add a Rule',
                                        ),
                                        VizForm.VizForm(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'delete',
                                            title               = 'Delete a Rule',
                                        ),
                                    ],
            )
            
            return page
        
        def getDataDyn(self,dynPath,subResource,username):
            
            netname = dynPath
            dld     = DustLinkData.DustLinkData()
            
            if   subResource==['defaultrule']:
                return [
                    {
                        'name':             'Default Rule',
                        'value':            dld.getDefaultFirewallRule(
                                                netname,
                                                username=username
                                            ),
                        'optionDisplay':    [c.split()[-1] for c in DustLinkData.DustLinkData.FIREWALL_RULE_ALL],
                        'optionValue':      DustLinkData.DustLinkData.FIREWALL_RULE_ALL,
                        'type':             'select',
                        'editable':         True,
                    },
                ]
            
            elif subResource==['rules']:
                
                rules = dld.getFirewallRules(netname,username=username)
                
                # columnNames
                columnNames = ['mote','host','direction','transport','resource','rule']
                
                # data
                if rules:
                    data =  [
                                [
                                    DustLinkData.DustLinkData.macToString(k[0]),
                                    DustLinkData.DustLinkData.ipToString(k[1]),
                                    k[2],
                                    k[3],
                                    k[4],
                                    v,
                                ]
                                for (k,v) in rules.items()
                            ]
                else:
                    data =  []
                
                return VizTable.VizTable.formatReturnVal(columnNames,data)
            
            elif subResource==['add']:
                macsInNetwork = [DustLinkData.DustLinkData.macToString(mac) \
                                 for mac in dld.getNetworkMotes(netname,username=username)]
                return [
                    {
                        'name':           'moteMAC',
                        'value':          None,
                        'optionDisplay':  macsInNetwork,
                        'optionValue':    macsInNetwork,
                        'type':           'select',
                        'editable':       True,
                    },
                    {
                        'name':           'hostIP',
                        'value':          '',
                        'type':           'text',
                    },
                    {
                        'name':           'direction',
                        'value':          None,
                        'optionDisplay':  DustLinkData.DustLinkData.DATA_DIRECTION_ALL,
                        'optionValue':    DustLinkData.DustLinkData.DATA_DIRECTION_ALL,
                        'type':           'select',
                        'editable':       True,
                    },
                    {
                        'name':           'dataType',
                        'value':          None,
                        'optionDisplay':  DustLinkData.DustLinkData.APP_TRANSPORT_ALL,
                        'optionValue':    DustLinkData.DustLinkData.APP_TRANSPORT_ALL,
                        'type':           'select',
                        'editable':       True,
                    },
                    {
                        'name':           'resource',
                        'value':          '',
                        'type':           'text',
                    },
                    {
                        'name':           'rule',
                        'value':          None,
                        'optionDisplay':  DustLinkData.DustLinkData.FIREWALL_RULE_ALL,
                        'optionValue':    DustLinkData.DustLinkData.FIREWALL_RULE_ALL,
                        'type':           'select',
                        'editable':       True,
                    },
                ]
            
            elif subResource==['delete']:
                
                rules = dld.getFirewallRules(netname,username=username)
                
                ruleStrings = []
                if rules:
                    for (k,v) in rules.items():
                        thisRule  = []
                        thisRule += [DustLinkData.DustLinkData.macToString(k[0])]
                        thisRule += [DustLinkData.DustLinkData.ipToString(k[1])]
                        thisRule += [str(k[2])]
                        thisRule += [str(k[3])]
                        thisRule += [str(k[4])]
                        ruleStrings.append(' '.join(thisRule))
                
                return [
                    {
                        'name':           'rule',
                        'value':          None,
                        'optionDisplay':  ruleStrings,
                        'optionValue':    ruleStrings,
                        'type':           'select',
                        'editable':       True,
                    },
                ]
            
            else:
                raise web.notfound()
        
        def postDataDyn(self,receivedData,dynPath,subResource,username):
            
            netname = dynPath
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['defaultrule']:
                
                dld.setDefaultFirewallRule(
                    netname,
                    receivedData['fieldValue'],
                    username=username,
                )
            
            elif subResource==['add']:
                assert isinstance(receivedData,dict)
                keys = receivedData.keys()
                keys.sort()
                assert keys==['dataType','direction','hostIP','moteMAC','resource','rule']
                
                receivedData['moteMAC'] = DustLinkData.DustLinkData.stringToMac(receivedData['moteMAC'])
                receivedData['hostIP']  = DustLinkData.DustLinkData.stringToIp(receivedData['hostIP'])
                
                dld.addFirewallRule(
                    netname=netname,
                    username=username,
                    **receivedData
                )
            
            elif subResource==['delete']:
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['rule']
                
                ruleItems = receivedData['rule'].split()
                assert len(ruleItems)==5
                
                moteMAC      = DustLinkData.DustLinkData.stringToMac(ruleItems[0])
                hostIP       = DustLinkData.DustLinkData.stringToIp(ruleItems[1])
                direction    = ruleItems[2]
                assert direction in DustLinkData.DustLinkData.DATA_DIRECTION_ALL
                dataType     = ruleItems[3]
                assert dataType in DustLinkData.DustLinkData.DATATYPE_ALL
                if   dataType in [DustLinkData.DustLinkData.APP_TRANSPORT_UDP,
                                  DustLinkData.DustLinkData.APP_TRANSPORT_MOTERUNNER]:
                    resource = int(ruleItems[4])
                elif dataType in [DustLinkData.DustLinkData.APP_TRANSPORT_OAP]:
                    resource = tuple([int(b) for b in ruleItems[4].split('.')])
                elif dataType in [DustLinkData.DustLinkData.APP_TRANSPORT_COAP]:
                    resource = tuple([str(b) for b in ruleItems[4].split('.')])
                else:
                    raise SystemError('unexpected dataType={0}'.format(dataType))
                
                output  = []
                output += ['moteMAC={0}'.format(moteMAC)]
                output += ['hostIP={0}'.format(hostIP)]
                output += ['direction={0}'.format(direction)]
                output += ['dataType={0}'.format(dataType)]
                output += ['resource={0}'.format(resource)]
                print '\n'.join(output)
                
                dld.deleteFirewallRule(
                    netname   = netname,
                    moteMAC   = moteMAC,
                    hostIP    = hostIP,
                    direction = direction,
                    dataType  = dataType,
                    resource  = resource,
                    username  = username,
                )
            
            else:
                raise web.notfound()
        
    def subPageLister(self):
        dld = DustLinkData.DustLinkData()
        try:
            return [
                {
                    'url':   n,
                    'title': n,
                }
                for n in dld.getNetnames(str(web.ctx.session.username))
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
                                            url             = 'firewall',
                                            title           = 'Firewall',
                                            webHandler      = self.pageFirewall,
                                            subPageLister   = self.subPageLister,
                                            subPageHandler  = self.pageFirewallSub)