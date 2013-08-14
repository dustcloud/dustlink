import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('WebPage')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import os
import web
from viz import Viz

import WebPage
import WebHandler

class WebHandlerDyn(WebHandler.WebHandler):
    
    def getPage(self,subResource,username):
        return self.getPageDyn(dynPath=self.getDynPath(),
                               subResource=subResource,
                               username=username)
    
    def getData(self,subResource,username):
        return self.getDataDyn(dynPath=self.getDynPath(),
                               subResource=subResource,
                               username=username)
    
    def postData(self,receivedData,subResource,username):
        return self.postDataDyn(receivedData=receivedData,
                                dynPath=self.getDynPath(),
                                subResource=subResource,
                                username=username)
    
    def getDynPath(self):
        elems = WebPage.WebPage.urlStringTolist(web.ctx.path)
        for e in elems:
            if e.startswith('_'):
                return e[1:]

class WebPageDyn(WebPage.WebPage):
    
    def __init__(self,subPageLister=None,
                      subPageHandler=None,
                      **fvars):
        
        assert callable(subPageLister)
        
        # store params
        self.subPageLister  = subPageLister
        self.subPageHandler = subPageHandler
        
        # initialize parent class
        WebPage.WebPage.__init__(self,**fvars)
        
        # register subPageHandler
        self.registerPage(WebPage.WebPage(webServer   = self.webServer,
                                          url         = '_[.%%\w-]*',
                                          title       = '',
                                          webHandler  = self.subPageHandler))
    
    def getUrlHierarchy(self,parentPath=[]):
            
            # run the parent class' function
            returnVal = WebPage.WebPage.getUrlHierarchy(self,parentPath)
            
            # modify the children
            returnVal['children'] = []
            for sub in self.subPageLister():
                
                classUrl = parentPath+[self.url]+[sub['url']]
                if len(classUrl) and not classUrl[0]:
                    classUrl = classUrl[1:]
                
                returnVal['children'] += [
                    {
                        'url':        self.urlListToString(parentPath+[self.url]+['_'+sub['url']]),
                        'title':      sub['title'],
                        'class':      self.webServer.getDocumentation().getClass(classUrl),
                        'children':   [],
                    }
                ]
            
            return returnVal
    
    