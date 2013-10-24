#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('DustLinkWeb')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

from DustLinkData import DustLinkData, \
                         DataVaultException

from dustWeb import WebPage

import MoteDataPages
import DashboardPages
import MotesPages
import NetworksPages
import AppsPages
import HealthPages
import FirewallPages
import DataFlowsPages
import DustLinkWebDoc
import UsersPages
import SystemPages

from dustWeb import DustWeb

##
# \defgroup DustLinkWeb DustLinkWeb
# \{
#

#===== /banner

class Banner(object):
    
    def GET(self,subResource=''):
        return DustLinkData.DustLinkData()._getBanner()
    
    def POST(self,subResource=''):
        DustLinkData.DustLinkData()._resetBanner()

class DustLinkWeb(DustWeb.DustWeb):
    
    DOC = DustLinkWebDoc.DustLinkWebDoc()
    
    def __init__(self,keyFile=None,certFile=None):
        
        # store params
        self.keyFile    = keyFile
        self.certFile   = certFile
        
        # log
        log.info("creating instance")
        
        # initialize parent class
        DustWeb.DustWeb.__init__(self,keyFile=self.keyFile, 
                                      certFile=self.certFile,
                                      defaultUrl='/system/welcome',
                                      defaultUsername=DustLinkData.DustLinkData.USER_ANONYMOUS)
        
        # add banner
        self.registerPage(
            WebPage.WebPage(
                webServer    = self,
                url          = 'banner',
                title        = 'Banner',
                webHandler   = Banner,
                hidden       = True,
            ),
        )
        
        # add (visible) sub pages
        self.registerPage(MoteDataPages.MoteDataPages(self))
        self.registerPage(DashboardPages.DashboardPages(self))
        self.registerPage(MotesPages.MotesPages(self))
        self.registerPage(NetworksPages.NetworksPages(self))
        self.registerPage(AppsPages.AppsPages(self))
        self.registerPage(HealthPages.HealthPages(self))
        self.registerPage(FirewallPages.FirewallPages(self))
        self.registerPage(DataFlowsPages.DataFlowsPages(self))
        self.registerPage(UsersPages.UsersPages(self))
        self.registerPage(SystemPages.SystemPages(self))
        
        # local variables
    
    #======================== parent methods ==================================
    
    def _authenticate(self,username,password):
        '''
        \brief Authenticate a user.
        '''
        assert isinstance(username,str)
        assert isinstance(password,str)
        
        dld = DustLinkData.DustLinkData()
        
        try:
            dld.passwordAuthenticate(username,password)
        except DataVaultException.Unauthorized:
            log.warning('user {0} fails password authentication'.format(username))
            return False
        else:
            log.info('user {0} passes password authentication'.format(username))
            return True
    
    def getUrlHierarchy(self,parentPath=[]):
        
        dld = DustLinkData.DustLinkData()
        
        # run the parent class' function
        returnVal = super(DustLinkWeb,self).getUrlHierarchy(parentPath)
        
        # page names to hide
        hiddenPageTitles          = []
        hiddenPageTitles         += ['MoteData']
        if DustLinkData.DustLinkData.MODULE_LBR not in dld.getEnabledModules():
            hiddenPageTitles     += ['Firewall','DataFlows']
        
        # modify the children
        i = 0
        while i<len(returnVal['children']):
            if returnVal['children'][i]['title'] in hiddenPageTitles:
                del returnVal['children'][i]
            else:
                i += 1
        
        return returnVal
    
    def getDocumentation(self):
        return self.DOC
##
# \}
#
