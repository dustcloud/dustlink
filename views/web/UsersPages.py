import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('UsersPages')
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
from dustWeb.viz import VizFields
from dustWeb.viz import VizTable
from dustWeb.thirdparty import gviz_api

#============================ object ==========================================
        
class UsersPages(WebPageDyn.WebPageDyn):
    
    #===== web handlers (private classes)
    
    class pageUsers(WebHandler.WebHandler):
        
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
                                            title               = 'Add a User',
                                        ),
                                        VizForm.VizForm(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'delete',
                                            title               = 'Delete a User',
                                        ),
                                    ],
            )
            
            return page
        
        def getData(self,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['add']:
                return [
                    {
                        'name':           'newUser',
                        'value':          '',
                        'type':           'text',
                    },
                ]
            elif subResource==['delete']:
                usernames = dld.getUserNames(username=username)
                
                return [
                    {
                        'name':           'username',
                        'value':          None,
                        'optionDisplay':  usernames,
                        'optionValue':    usernames,
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
                assert receivedData.keys()==['newUser']
                assert isinstance(receivedData['newUser'],str)
                
                dld.addUser(
                    receivedData['newUser'],
                    username=username,
                )
            elif subResource==['delete']:
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['username']
                assert isinstance(receivedData['username'],str)
                
                dld.deleteUser(
                    receivedData['username'],
                    username=username,
                )
            else:
                raise web.notfound()
        
    class pageUsersSub(WebPageDyn.WebHandlerDyn):
        
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
                                            subResourcePath     = 'authentication',
                                            title               = 'Authentication',
                                            autorefresh         = False,
                                            forbidAutorefresh   = True,
                                        ),
                                        VizForm.VizForm(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'password',
                                            title               = 'Set Password',
                                        ),
                                        VizTable.VizTable(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'privileges',
                                            title               = 'Privileges',
                                        ),
                                        VizForm.VizForm(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'grant',
                                            title               = 'Grant a Privilege',
                                        ),
                                        VizForm.VizForm(
                                            webServer           = webServer,
                                            username            = username,
                                            resourcePath        = currentPath,
                                            subResourcePath     = 'deny',
                                            title               = 'Deny a Privilege',
                                        ),
                                    ],
            )
            
            return page
        
        def getDataDyn(self,dynPath,subResource,username):
            
            usernameToExamine = dynPath
            dld = DustLinkData.DustLinkData()
            
            if   subResource==['authentication']:
                with dld.dataLock:
                    ssl = dld.getUserSsl(
                                usernameToAuthenticate=usernameToExamine,
                                username=username
                        )
                    if not ssl:
                        ssl = ''
                    return [
                        {
                            'name':             'Authentication',
                            'value':            dld.getUserAuthlevel(
                                                        usernameToExamine=usernameToExamine,
                                                        username=username
                                                ),
                            'optionDisplay':    [c.split()[-1] for c in DustLinkData.DustLinkData.AUTHLEVEL_ALL],
                            'optionValue':      [c for c in DustLinkData.DustLinkData.AUTHLEVEL_ALL],
                            'type':             'select',
                            'editable':         True,
                        },
                        {
                            'name':             'ssl',
                            'value':            ssl,
                            'type':             'text',
                            'editable':         True,
                        },
                    ]
            
            elif subResource==['privileges']:
                
                userPrivileges = dld.getUserPrivileges(
                                    usernameToExamine=usernameToExamine,
                                    username=username
                                 )
                
                # columnNames
                columnNames = ['resource','get','put','delete']
                
                # fill in data
                if userPrivileges:
                    data = self._formatPrivileges(userPrivileges)
                else:
                    data = []
                
                return VizTable.VizTable.formatReturnVal(columnNames,data, [.4,0,0,0])
            
            elif subResource==['password']:
                return [
                    {
                        'name':           'old password',
                        'value':          '',
                        'type':           'password',
                        'editable':       True,
                    },
                    {
                        'name':           'new password',
                        'value':          '',
                        'type':           'password',
                        'editable':       True,
                    },
                ]
            
            elif subResource==['grant']:
                # generate all possible resources
                resources = self._formatAllResources(username)
                
                return [
                    {
                        'name':           'resource',
                        'value':          None,
                        'optionDisplay':  resources,
                        'optionValue':    resources,
                        'type':           'select',
                        'editable':       True,
                    },
                    {
                        'name':           'action',
                        'value':          None,
                        'optionDisplay':  DustLinkData.DustLinkData.ACTION_ALL,
                        'optionValue':    DustLinkData.DustLinkData.ACTION_ALL,
                        'type':           'select',
                        'editable':       True,
                    },
                ]
            
            elif subResource==['deny']:
                # generate all possible resources
                resources = self._formatAllResources(username)
                
                return [
                    {
                        'name':           'resource',
                        'value':          None,
                        'optionDisplay':  resources,
                        'optionValue':    resources,
                        'type':           'select',
                        'editable':       True,
                    },
                    {
                        'name':           'action',
                        'value':          None,
                        'optionDisplay':  DustLinkData.DustLinkData.ACTION_ALL,
                        'optionValue':    DustLinkData.DustLinkData.ACTION_ALL,
                        'type':           'select',
                        'editable':       True,
                    },
                ]
            
            else:
                raise web.notfound()
        
        def _formatAllResources(self,username):
            dld = DustLinkData.DustLinkData()
            with dld.dataLock:
                returnVal  = []
                returnVal += [DustLinkData.DustLinkData.RESOURCE_SYSTEM]
                returnVal += [DustLinkData.DustLinkData.RESOURCE_USERS]
                for resource in [DustLinkData.DustLinkData.RESOURCE_APPS]:
                    for sub in dld.getAppNames(username=username):
                        returnVal.append('.'.join([resource,sub]))
                    returnVal.append('.'.join([resource,DustLinkData.DustLinkData.RESOURCE_WILDCARD]))
                for resource in  [DustLinkData.DustLinkData.RESOURCE_MOTES]:
                    for sub in dld.getMoteMacs(username=username):
                        returnVal.append('.'.join([resource,DustLinkData.DustLinkData.macToString(sub)]))
                    returnVal.append('.'.join([resource,DustLinkData.DustLinkData.RESOURCE_WILDCARD]))
                for resource in  [DustLinkData.DustLinkData.RESOURCE_NETWORKS,
                                  DustLinkData.DustLinkData.RESOURCE_TESTRESULTS,
                                  DustLinkData.DustLinkData.RESOURCE_FIREWALL,
                                  DustLinkData.DustLinkData.RESOURCE_DATAFLOWS,]:
                    for sub in dld.getNetnames(username=username):
                        returnVal.append('.'.join([resource,sub]))
                    returnVal.append('.'.join([resource,DustLinkData.DustLinkData.RESOURCE_WILDCARD]))
                return returnVal
        
        def _formatPrivileges(self,data):
            temp = {}
            self._formatPrivileges1(data,None,temp)
            return self._formatPrivileges2(temp)
        
        def _formatPrivileges1(self,data,name,output):
            for (k,v) in data.items():
                try:
                    k = DustLinkData.DustLinkData.macToString(k)
                except:
                    pass
            
                if isinstance(v,dict):
                    if name:
                        subname = '.'.join([name,k])
                    else:
                        subname = k
                    self._formatPrivileges1(v,subname,output)
                else:
                    if name not in output:
                        output[name] = {}
                    output[name][k] = v

        def _formatPrivileges2(self,data):
            returnVal = []
            for (k,v) in data.items():
                thisElem = []
                thisElem.append(k)
                for rule in ['get','put','delete']:
                    if rule in v and v[rule]=='yes':
                        thisElem.append('yes')
                    else:
                        thisElem.append('no')
                returnVal.append(thisElem)
            return returnVal
            
        def postDataDyn(self,receivedData,dynPath,subResource,username):
            
            dld = DustLinkData.DustLinkData()
            usernameToExamine = dynPath
            
            if   subResource==['authentication']:
                
                # filter errors
                fields = receivedData.keys()
                fields.sort()
                if fields!=['fieldName','fieldValue']:
                    raise web.HTTPError('400 bad request',{},'wrong fieldnames')
                
                if   receivedData['fieldName'] in ['Authentication']:
                    newAuthLevel = receivedData['fieldValue']
                    if newAuthLevel not in DustLinkData.DustLinkData.AUTHLEVEL_ALL:
                        raise web.HTTPError('400 bad request',{},'invalid authLevel {0}'.format(newAuthLevel))
                    try:
                        dld.setUserAuthlevel(
                            usernameToExamine=usernameToExamine,
                            newAuthLevel=newAuthLevel,
                            username=username)
                    except ValueError as err:
                        raise web.HTTPError('400 bad request',{},str(err))
                elif receivedData['fieldName'] in ['ssl']:
                    dld.setUserSsl(
                        usernameToAuthenticate=usernameToExamine,
                        ssl=receivedData['fieldValue'],
                        username=username)
                else:
                    raise web.HTTPError('400 bad request',{},'unexpected fieldName {0}'.format(receivedData['fieldName']))
            
            elif subResource==['password']:
            
                dld.setUserPassword(
                        usernameToAuthenticate=usernameToExamine,
                        oldPassword=receivedData['old password'],
                        newPassword=receivedData['new password'],
                        username=username)
            
            elif subResource==['grant']:
            
                resourceTemp = receivedData['resource'].split('.')
                resource     = []
                for r in resourceTemp:
                    try:
                        resource.append(DustLinkData.DustLinkData.stringToMac(r))
                    except ValueError:
                        resource.append(r)
                action       = receivedData['action']
            
                dld.grantPrivilege(
                        resource=resource,
                        usernameToGrant=usernameToExamine,
                        action=action,
                        username=username)
            
            elif subResource==['deny']:
            
                resourceTemp = receivedData['resource'].split('.')
                resource     = []
                for r in resourceTemp:
                    try:
                        resource.append(DustLinkData.DustLinkData.stringToMac(r))
                    except ValueError:
                        resource.append(r)
                action       = receivedData['action']
                
                dld.denyPrivilege(
                        resource=resource,
                        usernameToDeny=usernameToExamine,
                        action=action,
                        username=username)
            
            else:
                raise web.notfound()
            
    def subPageLister(self):
        username = str(web.ctx.session.username)
        dld = DustLinkData.DustLinkData()
        try:
            return [
                {
                    'url':   u,
                    'title': u,
                }
                for u in dld.getUserNames(username=username)
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
                                            url             = 'users',
                                            title           = 'Users',
                                            webHandler      = self.pageUsers,
                                            subPageLister   = self.subPageLister,
                                            subPageHandler  = self.pageUsersSub)