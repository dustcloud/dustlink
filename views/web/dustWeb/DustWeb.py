import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('DustWeb')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import os
import copy
import threading
import web
import traceback

import WebPage
import DustWebDoc

import MemSessionStore

#============================ helpers =========================================

def simplifyWebInputFormat(fields):
        
        returnVal = {}
        for (k,v) in fields.items():
            k = str(k)
            if   v     in ['true']:
                returnVal[k] = True
            elif v     in ['false']:
                returnVal[k] = False
            elif 'IP'  in k:
                returnVal[k] = str(v)
            elif 'MAC' in k:
                returnVal[k] = str(v)
            else:
                try:
                    returnVal[k] = int(v)
                except (TypeError,ValueError):
                    if not isinstance(v,(list,dict)):
                        returnVal[k] = str(v)
                    else:
                        returnVal[k] = v
        return returnVal

#============================ pages ===========================================

#===== /

class Index(object):
    
    def GET(self,subResource=''):
        global webServer
        
        if webServer.defaultUrl:
            raise web.seeother(webServer.defaultUrl)
        else:
            raise web.notfound()

#===== /login

class Login(object):
    
    def POST(self):
        global session
        global webServer
        
        # retrieve the information entered by the user
        
        try:
            usernameEntered  = str(web.input().username)
        except AttributeError:
            usernameEntered  = None
        try:
            passwordEntered  = str(web.input().password)
        except AttributeError:
            passwordEntered  = None
        try:
            actionEntered    = str(web.input().action)
        except AttributeError:
            actionEntered    = None
        
        if   actionEntered=='login' and usernameEntered and passwordEntered:
            # validate that this user is allowed
            if webServer._authenticate(usernameEntered, passwordEntered):
                session.username  = usernameEntered
            else:
                session.username  = None
                session.kill()
        elif actionEntered=='logout':
            # kill this users's session if exists
            if session.username:
                session.username  = None
            session.kill()
        
        # redirect to the home page
        raise web.seeother('/')

class DustWeb(threading.Thread,WebPage.WebPage):
    '''
    \brief A pure-Python web interface.
    
    This class handles SSL and user login.
    '''
    
    SESSIONS_DIR = os.path.join('logs','sessions')
    
    def __init__(self,keyFile=None,certFile=None,defaultUrl=None,defaultUsername=None):
        '''
        \brief Initializer.
        
        \param keyFile  Path to a file containing the SSL private key of the
                        server.
                        Defaults to None, in which case HTTP will be used
                        instead of HTTPS.
        \param certFile Path to a file containing the SSL ceritificate of the
                        server.
                        Defaults to None, in which case HTTP will be used
                        instead of HTTPS.
        \param defaultUrl URL loaded as homepage of the site.
        \param defaultUsername The username to use when not logged in.
        '''
        global webServer
        
        # filter errors
        requiredSubDirs = ['keys','logs','static']
        for dir in requiredSubDirs:
            if dir not in os.listdir(os.curdir):
                raise SystemError("The DustWeb application needs the {0}/ subdirectory".format(dir))
        if (keyFile) and (not os.path.exists(keyFile)):
            raise SystemError("keyFile {0} does not exist".format(keyFile))
        if (certFile) and (not os.path.exists(certFile)):
            raise SystemError("certFile {0} does not exist".format(certFile))
        
        # store params
        self.keyFile         = keyFile
        self.certFile        = certFile
        self.defaultUrl      = defaultUrl
        self.defaultUsername = defaultUsername
        
        # log
        output      = []
        output     += ["creating instance"]
        if keyFile:
            output += ["keyFile={0}".format(self.keyFile)]
        if certFile:
            output += ["certFile={0}".format(self.certFile)]
        log.info('\n'.join(output))
        
        # local variables
        self.runningUniqueId = 0
        
        # global variables
        webServer = self
        
        # initialize parent classes
        threading.Thread.__init__(self)
        self.name            = "DustWeb"
        WebPage.WebPage.__init__(self,
                                 webServer  = self,
                                 url        = '',
                                 title      = 'Home',
                                 webHandler = Index,)
        
        # add login page
        self.registerPage(WebPage.WebPage(webServer   = self,
                                          url         = 'login',
                                          title       = 'Login',
                                          webHandler  = Login,
                                          hidden      = True))
        
    def run(self):
        '''
        \brief Start the web server.
        '''
        global session
        global sessionStore
        
        # log
        log.debug("starting server")
        
        # disable debug mode (which prevents sessions)
        web.config.debug = False
        
        # enable SSL, if required
        if self.keyFile and self.certFile:
            from web.wsgiserver import CherryPyWSGIServer
            CherryPyWSGIServer.ssl_private_key = self.keyFile
            CherryPyWSGIServer.ssl_certificate = self.certFile
            log.debug("enable SSL")
        
        # create main application
        self.webApp     = web.application(self.getMappingUrlToHandlerName(),
                                          self.getHandlerNameToHandlerClass())
        
        '''
        for i in range(0,len(self.getMappingUrlToHandlerName()),2):
            print '{0} -> {1}'.format(self.getMappingUrlToHandlerName()[i],self.getMappingUrlToHandlerName()[i+1])
        '''
        
        # customize error handling
        #self.webApp.notfound      = self._notfound
        #self.webApp.internalerror = self._internalerror
        
        # enable sessions
        web.config.session_parameters['cookie_name']      = 'dustLink_session_id'
        web.config.session_parameters['ignore_change_ip'] = False
        sessionStore = MemSessionStore.MemSessionStore()
        session = web.session.Session(self.webApp,
                                      sessionStore,
                                      initializer={'username': self.defaultUsername})
        self.webApp.add_processor(web.loadhook(self._session_hook))
        self.wsgifunc   = self.webApp.wsgifunc() 
        self.wsgifunc   = web.httpserver.StaticMiddleware(self.wsgifunc)
        self.webserver  = web.httpserver.WSGIServer(('0.0.0.0', 8080), self.wsgifunc) 
        
        # start server
        self.webserver.start()
        
        # you reach this line once the server has been stopped
        
        # log
        log.debug("server stopped")
    
    #======================== abstract methods ================================
    
    def _authenticate(self,username,password):
        '''
        \brief Authenticate a user
        
        \note This function is meant to be overloaded by a child class.
        '''
        raise NotImplementedError()    # to be implemented by child class
    
    #======================== public ==========================================
    
    def getSessions(self):
        '''
        \brief Retrieve the active sessions.
        '''
        global sessionStore

        return sessionStore.getData()

    def getSessionStore(self):
        '''
        \brief Retrieve the session store.
        '''
        global sessionStore

        return sessionStore
    
    def getDefaultUserName(self):
        return self.defaultUsername
    
    def getUniqueNumber(self):
        '''
        \brief Returns a unique number.
        
        This can be used to uniquely match display elements in some web page.
        We rely on the width of Python number to never roll over.
        '''
        
        self.runningUniqueId += 1
        return self.runningUniqueId
    
    def stop(self):
        '''
        \brief Stop the web server.
        '''
        
        # log
        log.debug("stopping server")
        
        self.webserver.stop()
    
    #======================== private =========================================
    
    def _notfound(self):
        return web.notfound()
    
    def _internalerror(self):
        return web.internalerror()
    
    def _session_hook(self):
        web.ctx.session = session
        
    def getDocumentation(self):
        return DustWebDoc.DustWebDoc()
