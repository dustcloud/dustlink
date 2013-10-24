#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('DustLinkData')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import re
import time
import random
import struct
import hashlib
import threading

import DataVault
import DataVaultException
import DustLinkDataException

from DataVault import synchronized

##
# \defgroup DustLinkData DustLinkData
# \{
#

class DustLinkData(DataVault.DataVault):
    
    USER_ADMIN                    = DataVault.DataVault.USER_ADMIN
    USER_SYSTEM                   = DataVault.DataVault.USER_SYSTEM
    USER_ANONYMOUS                = DataVault.DataVault.USER_ANONYMOUS
    
    DEFAULT_ADMIN_PASSWORD        = 'admin'
    
    ON                            = 'on'
    OFF                           = 'off'
    
    YES                           = 'yes'
    NO                            = 'no'
    
    DEFAULT_MANAGER_CONNECTIONS   = ['/dev/ttyUSB3']
    
    RESOURCE_SYSTEM               = 'system'
    RESOURCE_USERS                = 'users'
    RESOURCE_APPS                 = 'apps'
    RESOURCE_MOTES                = 'motes'
    RESOURCE_NETWORKS             = 'networks'
    RESOURCE_TESTRESULTS          = 'testResults'
    RESOURCE_FIREWALL             = 'firewall'
    RESOURCE_DATAFLOWS            = 'dataflows'
    RESOURCE_ALL                  = set([RESOURCE_SYSTEM,
                                         RESOURCE_USERS,
                                         RESOURCE_APPS,
                                         RESOURCE_MOTES,
                                         RESOURCE_NETWORKS,
                                         RESOURCE_TESTRESULTS,
                                         RESOURCE_FIREWALL,
                                         RESOURCE_DATAFLOWS])
    RESOURCE_WILDCARD             = '*'
    
    #======================== singleton pattern ===============================
    
    _instance = None
    _init     = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            log.info("creating instance")
            cls._instance = super(DustLinkData, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self,  *args, **kwargs):
        if not self._init:
            self.authCache             = AuthCache()
            self.timestampCacheLock    = threading.Lock()
            self.timestampCache        = {}
            self.scratchpad            = []
            self.banner                = ''
            
            # initialize the DataVault (includes loading backup file)
            DataVault.DataVault.__init__(self, *args, **kwargs)
            
            # delete old networks. Will be re-discovered.
            netnames = self.getNetnames()
            for netname in netnames:
                try:
                    self.deleteNetwork(netname)
                except ValueError:
                    pass # happens if network was already deleted
    
    #======================== parent methods ==================================
    
    def _indicateLoadedDefaultData(self):
        # indicate system event
        self.setSystemEvent(self.SYSEVENT_DEFAULTDATALOADED)
        
        # enable demo Mode
        if self.setDemoModeByDefault:
            self.setDemoMode(True)
        
    def _indicatePersistenceCorrupted(self):
        # indicate system event
        self.setSystemEvent(self.SYSEVENT_BACKUPDATACORRUPTED)
    
    def _indicatePersistenceLoaded(self):
        # indicate system event
        self.setSystemEvent(self.SYSEVENT_BACKUPDATALOADED)
    
    def _putDefaultData(self):
        # format the data
        self._system_putDefaultData()
        self._users_putDefaultData()
        self._apps_putDefaultData()
        self._motes_putDefaultData()
        self._networks_putDefaultData()
        self._testResults_putDefaultData()
        self._firewall_putDefaultData()
        self._dataflows_putDefaultData()

    def _validateDataIntegrity(self):
        try:
            self._system_validateDataIntegrity()
            self._users_validateDataIntegrity()
            self._apps_validateDataIntegrity()
            self._motes_validateDataIntegrity()
            self._networks_validateDataIntegrity()
            self._testResults_validateDataIntegrity()
            self._firewall_validateDataIntegrity()
            self._dataflows_validateDataIntegrity()
        except DataVaultException.DataVaultException as err:
            output = "part of data missing {0}".format(err)
            log.critical(output)
            raise DustLinkDataException.Malformed(output)

    @synchronized
    def authorize(self,username,resource,action):
        '''
        \note Data is already locked.
        '''
            
        # the ADMIN has all rights
        if self._isPriviledged(username):
            return
            
        if not resource:
            resource = []
        cacheEntry = username, tuple(resource), action
        oldException = self.authCache.getEntry(cacheEntry)
        if oldException:
            if isinstance(oldException, Exception):
                raise oldException
            else:
                return
        cacheValue = True
        try:
            if type(username)!=str:
                raise ValueError("username should be a string, {0} is {1}".format(username,type(username)))
            if resource and not isinstance(resource,(list,str)):
                raise ValueError("resource must be a list or a string, {0} is not".format(resource))
            if action not in self.ACTION_ALL:
                raise ValueError("unknown action {0}".format(action))
            
            # adapt the 'granularity' of the resource
            if resource and len(resource)>0:
                if resource[0] in (self.RESOURCE_SYSTEM,
                                   self.RESOURCE_USERS):
                    resource = resource[0]
                if resource[0] in (self.RESOURCE_APPS,
                                   self.RESOURCE_MOTES,
                                   self.RESOURCE_NETWORKS,
                                   self.RESOURCE_TESTRESULTS,
                                   self.RESOURCE_FIREWALL,
                                   self.RESOURCE_DATAFLOWS):
                    if len(resource)==1:
                        if username!=self.USER_ADMIN:
                            raise DataVaultException.Unauthorized("only admin can access the root of {0}, not {1}".format(
                                resource[0],
                                username))
                    else:
                        resource = [resource[0],resource[1]]
            
            # make sure there is a user table
            try:
                self.checkExists([self.RESOURCE_USERS])
            except DataVaultException.NotFound:
                raise DataVaultException.Unauthorized("no user table")
            
            # if you get here, there is a users table, and we assume that it is
            # formatted as
            # users[username]['privileges'][resource][...][GET|PUT|DELETE] = YES|NO
            
            # make sure the user exists
            try:
                self.checkExists([self.RESOURCE_USERS,username])
            except DataVaultException.NotFound:
                raise DataVaultException.Unauthorized("no user called {0}".format(username))
            
            # make sure it can access the resource
            try:
                if self.getDataAtResource([self.RESOURCE_USERS,
                                           username,
                                           'privileges',
                                           resource,
                                           action])!=self.YES:
                    raise DataVaultException.Unauthorized("{0} can not {1} {2}".format(username,action,resource))
            except DataVaultException.NotFound:
                try:
                    if self.getDataAtResource([self.RESOURCE_USERS,
                                               username,
                                               'privileges',
                                               resource[:-1],
                                               self.RESOURCE_WILDCARD,
                                               action])!=self.YES:
                        raise DataVaultException.Unauthorized("{0} can not {1} {2}".format(username,action,resource))
                except DataVaultException.NotFound:
                    raise DataVaultException.Unauthorized("no privileges for {0} for user {1}, assume denied".format(resource,username))
        except Exception, e:
            cacheValue = e
            raise e
        finally:
            self.authCache.addEntry(cacheEntry, cacheValue)
    
    #======================== public ==========================================
    
    #========== scratchpad
    
    ##
    # \defgroup scratchpad scratchpad
    # \ingroup DustLinkData
    # \{
    #
    
    #--- defines
    
    @synchronized
    def _resetScratchpad(self):
        self.scratchpad  = []
    
    @synchronized
    def _addScratchpad(self,stringToAdd):
        self.scratchpad += [(time.time(),stringToAdd)]
    
    @synchronized
    def _getScratchpad(self):
        return self.scratchpad
    
    #--- admin
    
    #--- helpers
    
    ##
    # \}
    #
    
    #========== banner
    
    ##
    # \defgroup banner banner
    # \ingroup DustLinkData
    # \{
    #
    
    #--- defines
    
    @synchronized
    def _resetBanner(self):
        self.banner  = ''
    
    @synchronized
    def _setBanner(self,bannerText):
        self.banner  = bannerText
    
    @synchronized
    def _getBanner(self):
        return self.banner
    
    #--- admin
    
    #--- helpers
    
    ##
    # \}
    #
    
    ##
    # \defgroup system system
    # \ingroup DustLinkData
    # \{
    #
    
    #========== system
    
    #--- defines
    
    SYSEVENT_BACKUPDATACORRUPTED            = 'backup data corrupted'
    SYSEVENT_BACKUPDATALOADED               = 'backup data loaded'
    SYSEVENT_CONFIGLOADED                   = 'config file loaded'
    SYSEVENT_DEFAULTDATALOADED              = 'default data loaded'
    SYSEVENT_FACTORYRESET                   = 'factory reset'
    SYSEVENT_ALL                            = (SYSEVENT_BACKUPDATACORRUPTED,
                                               SYSEVENT_BACKUPDATALOADED,
                                               SYSEVENT_CONFIGLOADED,
                                               SYSEVENT_DEFAULTDATALOADED,
                                               SYSEVENT_FACTORYRESET)
    
    MAXNUMRESTARTSSTORED                    = 10
    MODULE_GATEWAY                          = 'module GATEWAY'
    MODULE_LBR                              = 'module LBR'
    MODULE_DATACONNECTOR                    = 'module DATACONNECTOR'
    MODULE_ALL                              = (MODULE_GATEWAY,
                                               MODULE_LBR,
                                               MODULE_DATACONNECTOR)
    MANAGERCONNECTION_STATE_INACTIVE        = 'inactive'
    MANAGERCONNECTION_STATE_CONNECTING      = 'connecting'
    MANAGERCONNECTION_STATE_ACTIVE          = 'active'
    MANAGERCONNECTION_STATE_DISCONNECTING   = 'disconnecting'
    MANAGERCONNECTION_STATE_FAIL            = 'fail'
    MANAGERCONNECTION_STATE_ALL             = (MANAGERCONNECTION_STATE_INACTIVE,
                                               MANAGERCONNECTION_STATE_CONNECTING,
                                               MANAGERCONNECTION_STATE_ACTIVE,
                                               MANAGERCONNECTION_STATE_DISCONNECTING,
                                               MANAGERCONNECTION_STATE_FAIL)
    
    PUBLISHER_XIVELY                        = 'xively'
    PUBLISHER_GOOGLE                        = 'google'
    PUBLISHER_ALL                           = (PUBLISHER_XIVELY,
                                               PUBLISHER_GOOGLE)
    
    PUBLISHER_XIVELY_KEY_XIVELYAPIKEY       = 'xivelyApiKey'
    PUBLISHER_XIVELY_KEY_ALL                = (
        PUBLISHER_XIVELY_KEY_XIVELYAPIKEY,
    )
    
    PUBLISHER_GOOGLE_KEY_SPREADSHEETKEY     = 'spreadsheetKey'
    PUBLISHER_GOOGLE_KEY_WORKSHEETNAME      = 'worksheetName'
    PUBLISHER_GOOGLE_KEY_GOOGLEUSERNAME     = 'googleUsername'
    PUBLISHER_GOOGLE_KEY_GOOGLEPASSWORD     = 'googlePassword'
    PUBLISHER_GOOGLE_KEY_ALL                = (
        PUBLISHER_GOOGLE_KEY_SPREADSHEETKEY,
        PUBLISHER_GOOGLE_KEY_WORKSHEETNAME,
        PUBLISHER_GOOGLE_KEY_GOOGLEUSERNAME,
        PUBLISHER_GOOGLE_KEY_GOOGLEPASSWORD,
    )
    
    #--- admin
    
    def _system_putDefaultData(self):
        self.put(['system','info','starttimes','totalnumrestarts'],       0)
        self.put(['system','info','starttimes','maxnumrestartsstored'],   self.MAXNUMRESTARTSSTORED)
        self.put(['system','info','starttimes','laststarttimes'],         None)
        self.put(['system','info','adminpassword'],                       hashlib.sha1(self.DEFAULT_ADMIN_PASSWORD).hexdigest())
        self.put(['system','modules',    self.MODULE_GATEWAY],            self.ON)
        self.put(['system','modules',    self.MODULE_LBR],                self.OFF)
        self.put(['system','modules',    self.MODULE_DATACONNECTOR],      self.ON)
        for k in self.PUBLISHER_XIVELY_KEY_ALL:
            self.put(['system','publishers',self.PUBLISHER_XIVELY,k],     None)
        for k in self.PUBLISHER_GOOGLE_KEY_ALL:
            self.put(['system','publishers',self.PUBLISHER_GOOGLE,k],     None)
        self.put(['system','persistence',self.PERSISTENCE_FILE],          self.ON)
        self.put(['system','managerConnections'],                         None)
        self.put(self.DB_FAST_MODE,                                       False)
        self.put(self.DB_DEMO_MODE,                                       False)
        self.put(['system','systemevents'],                               None)
        try:
            del self._demoMode
        except AttributeError:
            pass # fails if the _demoMode cache has never been used.
    
    def _system_validateDataIntegrity(self):
        self.get(['system','info','starttimes','totalnumrestarts'])
        self.get(['system','info','starttimes','maxnumrestartsstored'])
        self.get(['system','info','starttimes','laststarttimes'])
        self.get(['system','info','adminpassword'])
        self.get(['system','modules',self.MODULE_GATEWAY])
        self.get(['system','modules',self.MODULE_LBR])
        self.get(['system','modules',self.MODULE_DATACONNECTOR])
        for k in self.PUBLISHER_XIVELY_KEY_ALL:
            self.get(['system','publishers',self.PUBLISHER_XIVELY,k])
        for k in self.PUBLISHER_GOOGLE_KEY_ALL:
            self.get(['system','publishers',self.PUBLISHER_GOOGLE,k])
        self.get(['system','persistence',self.PERSISTENCE_FILE])
        self.get(['system','managerConnections'])
        self.get(self.DB_FAST_MODE)
        self.get(self.DB_DEMO_MODE)
        self.get(['system','systemevents'])
    
    #--- public
    
    @synchronized
    def getNumberOfRestarts(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the number of restarts of the system.
        
        \note This returned value only reflects reality if you are using data
              persistence.
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        return self.get(['system','info','starttimes','totalnumrestarts'],
                        username=username)
    
    @synchronized
    def getLastStartTimes(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the timestamps associated with the last restarts.
        
        \note This returned value only reflects reality if you are using data
              persistence.
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        
        \returns A list of start times, formatted as a number seconds since
                 epoch.
        '''
        starttimes = self.get(['system','info','starttimes','laststarttimes'],
                              username=username, createCopy=False)
        if starttimes:
            returnVal = starttimes.keys()
            returnVal.sort()
            return returnVal
        else:
            return []
    
    @synchronized
    def indicateNewStart(self,timestamp=None,username=USER_SYSTEM):
        '''
        \brief Indicate a new start time to the system.
        
        \param timestamp The time when the system started, in epoch. If you don't
                         specify this parameter, the current time will be used.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        
        # authorize
        self.authorize(username,['system'],self.ACTION_PUT)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        if timestamp==None:
            timestamp=time.time()
        
        # increment the total number of restarts
        self.put(['system','info','starttimes','totalnumrestarts'],
                 self.get(['system','info','starttimes','totalnumrestarts'])+1)
        
        # remove older restart time, if needed
        while len(self.getLastStartTimes())> \
                self.get(['system','info','starttimes','maxnumrestartsstored'])-1:
            self._system_deleteOldestStarttime()
        
        # remember this start time
        self.put(['system','info','starttimes','laststarttimes',timestamp],
                 None)
    
    @synchronized
    def getSystemEvents(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the list of unseen system events.
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        
        \returns A dictionory with key the name of the event and value the
                 timestamp at which this event was generated.
        '''
        return self.get(['system','systemevents'],username=username)
    
    @synchronized
    def setSystemEvent(self,event,username=USER_SYSTEM):
        '''
        \brief Sets a system event flag to the list of unviewed system events.
        
        System events are timestamped. If an event happens more than once, only
        its last occurence appears in the system event flags. The timestamp is
        set to the system time when this function is called.
        
        \param event     The new system event. Must be part of SYSEVENT_ALL.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if event not in self.SYSEVENT_ALL:
            raise ValueError("{0} is not a value system event".format(event))
        
        return self.put(['system','systemevents',event],time.time(),username=username)
    
    @synchronized
    def clearSystemEvent(self,event,username=USER_SYSTEM):
        '''
        \brief Clears a system event flag.
        
        This function will remove the flag from the list of system events. This
        is typically used when an administrator indicate that he/she has seen
        the flag..
        
        \param event     The system event to be removed. Must be part of
                         SYSEVENT_ALL.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        
        if event not in self.SYSEVENT_ALL:
            raise ValueError("{0} is not a value system event".format(event))
        
        # authorize access
        self.authorize(username,['system'],self.ACTION_DELETE)
        
        if event not in self.getSystemEvents():
            raise ValueError("{0} is not an unseen event".format(event))
        
        return self.delete(['system','systemevents',event],username=username)
    
    @synchronized
    def getEnabledModules(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the list of enabled modules.
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        return [k for (k,v) in self.get(['system','modules'],username=username, createCopy=False).items() if v==self.ON]
    
    @synchronized
    def enableModule(self,moduleName,username=USER_SYSTEM):
        '''
        \brief Enable a module of the system.
        
        \param moduleName The name of the module to enable.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if moduleName not in self.MODULE_ALL:
            raise ValueError("unsupported module {0}".format(moduleName))
        self.put(['system','modules',moduleName],
                 self.ON,
                 username=username)
    
    @synchronized
    def disableModule(self,moduleName,username=USER_SYSTEM):
        '''
        \brief Disable a module of the system.
        
        \param moduleName The name of the module to disable.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if moduleName not in self.MODULE_ALL:
            raise ValueError("unsupported module {0}".format(moduleName))
        self.put(['system','modules',moduleName],
                 self.OFF,
                 username=username)
    
    @synchronized
    def getEnabledPersistence(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the list of enabled data persistence.
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        return [k for (k,v) in self.get(['system','persistence'],username=username).items() if v==self.ON]
    
    @synchronized
    def enablePersistence(self,persistenceType,username=USER_SYSTEM):
        '''
        \brief Enable one form of persistence.
        
        \note You can enable multiple types of persistence at the same time.
        
        \param persistenceType The type of persistence to enable.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if persistenceType not in self.PERSISTENCE_ALL:
            raise ValueError("unsupported persistence {0}".format(persistenceType))
        self.put(['system','persistence',persistenceType],
                 self.ON,
                 username=username)
    
    @synchronized
    def disablePersistence(self,persistenceType,username=USER_SYSTEM):
        '''
        \brief Disable one form of persistence.
        
        \param persistenceType The type of persistence to disable.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if persistenceType not in self.PERSISTENCE_ALL:
            raise ValueError("unsupported persistence {0}".format(persistenceType))
        self.put(['system','persistence',persistenceType],
                 self.OFF,
                 username=username)

    DB_FAST_MODE = ['system', 'fastMode']
    
    @synchronized
    def getFastMode(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the current fast mode setting..
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        try:
            return self._fastMode
        except AttributeError:
            pass
        self._fastMode = self.get(self.DB_FAST_MODE,username=username, createCopy=False)
        return self._fastMode
    
    @synchronized
    def setFastMode(self, fastMode, username=USER_SYSTEM):
        '''
        \brief Enable fast mode.
        
        \param fastMode the new fast mode setting.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if not fastMode in (True, False):
            raise ValueError("fast mode must be a boolean, found {0}".format(fastMode))

        self.put(self.DB_FAST_MODE, fastMode, username=username)
        self._fastMode = fastMode
    
    DB_DEMO_MODE       = ['system', 'demoMode']
    
    @synchronized
    def getDemoMode(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the current demo mode setting..
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        try:
            return self._demoMode
        except AttributeError:
            pass
        self._demoMode = self.get(self.DB_DEMO_MODE,username=username, createCopy=False)
        return self._demoMode
    
    @synchronized
    def setDemoMode(self, demoMode, username=USER_SYSTEM):
        '''
        \brief Enable demo mode.
        
        \param demoMode the new demo mode setting.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if not demoMode in (True, False):
            raise ValueError("demo mode must be a boolean, found {0}".format(demoMode))

        self.put(self.DB_DEMO_MODE, demoMode, username=username)
        
        # cache the setting
        self._demoMode = demoMode
        
        if self._demoMode:
            
            # add user anonymous
            try:
                self.addUser(self.USER_ANONYMOUS)
            except ValueError:
                pass # user already exists
            
            # add default demoMode apps
            for k,v in self.DEMO_MODE_APPS.items():
                if k not in self.getAppNames():
                    self.addApp(k)
                    if 'description' in v:
                        self.setAppDescription(k, v['description'])
                    if 'transport' in v:
                        self.setAppTransport(k, v['transport'][0], v['transport'][1])
                    if 'fromMoteFields' in v:
                        self.setAppFields(k, self.APP_DIRECTION_FROMMOTE, v['fromMoteFields'][0], v['fromMoteFields'][1])
                    if 'toMoteFields' in v:
                        self.setAppFields(k, self.APP_DIRECTION_TOMOTE,   v['toMoteFields'][0],   v['toMoteFields'][1])
            
            # grant privileges to user anonymous
            self.grantPrivilege(['apps',       '*'], self.USER_ANONYMOUS, self.ACTION_GET)
            self.grantPrivilege(['apps',       '*'], self.USER_ANONYMOUS, self.ACTION_PUT)
            self.grantPrivilege(['apps',       '*'], self.USER_ANONYMOUS, self.ACTION_DELETE)
            self.grantPrivilege(['motes',      '*'], self.USER_ANONYMOUS, self.ACTION_GET)
            self.grantPrivilege(['motes',      '*'], self.USER_ANONYMOUS, self.ACTION_PUT)
            self.grantPrivilege(['motes',      '*'], self.USER_ANONYMOUS, self.ACTION_DELETE)
            self.grantPrivilege(['networks',   '*'], self.USER_ANONYMOUS, self.ACTION_GET)
            self.grantPrivilege(['system'         ], self.USER_ANONYMOUS, self.ACTION_GET)
            self.grantPrivilege(['testResults','*'], self.USER_ANONYMOUS, self.ACTION_GET)
            self.grantPrivilege(['testResults','*'], self.USER_ANONYMOUS, self.ACTION_DELETE)
            
            # add default demoMode manager connections
            if self.addDefaultManagerConnections:
                for mc in self.DEFAULT_MANAGER_CONNECTIONS:
                    self.addManagerConnection(mc)
    
    @synchronized
    def getManagerConnections(self,username=USER_SYSTEM):
        '''
        \brief Get the manager connections.
        
        \returns A dictionary with key the description of the managerConnection,
                 and as value the state.
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        return self.get(['system','managerConnections'],
                        username=username)
    
    @synchronized
    def addManagerConnection(self,desc,username=USER_SYSTEM):
        '''
        \brief Add a manager connection.
        
        \param desc      The description of the connection. Can be either a string
                         representing a serial port (e.g. 'COM1'), or a tuple 
                         (\<ip address\>,\<tcp port\>) when connecting over
                         serial mux.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        self._validateManagerConnectionDescriptor(desc)
        
        mgrConnections = self.getManagerConnections()
        if mgrConnections:
            if desc in mgrConnections:
                raise ValueError("descriptor {0} already exists".format(desc))
        
        self.put(['system','managerConnections',desc,'state'],
                 self.MANAGERCONNECTION_STATE_INACTIVE,
                 username=username)
        self.put(['system','managerConnections',desc,'reason'],
                 '',
                 username=username)
    
    @synchronized
    def updateManagerConnectionState(self,desc,newState,reason='',username=USER_SYSTEM):
        '''
        \brief Change the state of an existing manager connection.
        
        \param desc      The description of the connection. Can be either a string
                         representing a serial port (e.g. 'COM1'), or a tuple 
                         (\<ip address\>,\<tcp port\>) when connecting over
                         serial mux.
        \param newState  The new state of the manager connection. Must be in 
                         MANAGERCONNECTION_STATE_ALL.
        \param reason    The reason for the manager's connection state change.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        self._validateManagerConnectionDescriptor(desc)
        if newState not in self.MANAGERCONNECTION_STATE_ALL:
            raise ValueError("invalid state {0}".format(newState)) 
        if not isinstance(reason,str):
            raise ValueError("reason must be a string, {0} is not".format(reason)) 
        
        managerConnections = self.getManagerConnections()
        if (not managerConnections) or (desc not in managerConnections):
            raise ValueError("descriptor {0} unknown".format(desc))
        
        self.put(['system','managerConnections',desc,'state'],
                 newState,
                 username=username)
        self.put(['system','managerConnections',desc,'reason'],
                 reason,
                 username=username)
    
    @synchronized
    def deleteManagerConnection(self,desc,username=USER_SYSTEM):
        '''
        \brief Delete a manager connection.
        
        \param desc      The description of the connection. Can be either a string
                         representing a serial port (e.g. 'COM1'), or a tuple 
                         (\<ip address\>,\<tcp port\>) when connecting over
                         serial mux.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        self._validateManagerConnectionDescriptor(desc)
        
        if desc not in self.getManagerConnections():
            raise ValueError("descriptor {0} unknown".format(desc))
        
        self.delete(['system','managerConnections',desc],username)
    
    @synchronized
    def getPublishersSettings(self,publisherName,username=USER_SYSTEM):
        '''
        \brief Retrieve the currently used publisher setting.
        
        \param publisherName The name of the publisher. Acceptable values
            are <tt>xively</tt> and <tt>google</tt>.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        
        \note The following fields do not contain the actual value, only True
            if the field is set, False otherwise:
            - xivelyApiKey
            - googleUsername
            - googlePassword
        
        \returns A dictionary with keys corresponding to the settings of the
            selected publisher. 
        '''
        if not publisherName in self.PUBLISHER_ALL:
            raise ValueError("invalid publisherName {0}".format(publisherName))
        
        # get all details
        returnVal = self.get(['system','publishers',publisherName],username)
        
        # remove clear-text credentials
        for k in [
                self.PUBLISHER_XIVELY_KEY_XIVELYAPIKEY,
                self.PUBLISHER_GOOGLE_KEY_GOOGLEUSERNAME,
                self.PUBLISHER_GOOGLE_KEY_GOOGLEPASSWORD,
            ]:
            if k in returnVal:
                returnVal[k] = (returnVal[k]!=None and returnVal[k]!='')
        
        return returnVal
    
    @synchronized
    def setPublisherSettings(self,publisherName,settings,username=USER_SYSTEM):
        '''
        \brief Set the settings for the publishers.
        
        \note The xivelyApiKey, googleUsername and googlePassword, while they
            cannot be read from the web interface, are store in clear in the
            database. For security reasons, we recommend to set up a Xively or
            Google account specifically for managing demo data.
            DO NOT USE YOUR PERSONAL ACCOUNT. 
        
        \param publisherName The name of the publisher. Acceptable values
            are <tt>xively</tt> and <tt>google</tt>.
        \param settings The new parameters, a dictionary.
            For Xively, must contain exactly the following key:
                - <tt>xivelyApiKey</tt>, a Xively API master key with
                    privileges to create and activate devices, create
                    datastreams, and create data points.
            For Google, must contain exactly the following keys:
                - <tt>spreadsheetKey</tt>, the key of the Google spreadsheet,
                    a string.
                - <tt>worksheetName</tt>, the name of the worksheet of interest
                    in the spreadsheet, a string.
                - <tt>googleUsername</tt>, the Google username associated with
                    that spreadsheet. This user needs to be able to write to
                    the spreadsheet.
                - <tt>googlePassword</tt>, the passsword associated with that
                    username.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        
        # validate params
        if   publisherName==self.PUBLISHER_XIVELY:
            if sorted(settings.keys())!=sorted(self.PUBLISHER_XIVELY_KEY_ALL):
                raise ValueError(
                    "wrong keys, got {0}, expected {1}".format(
                        sorted(settings.keys()),
                        sorted(self.PUBLISHER_XIVELY_KEY_ALL)
                    )
                )
        elif publisherName==self.PUBLISHER_GOOGLE:
            if sorted(settings.keys())!=sorted(self.PUBLISHER_GOOGLE_KEY_ALL):
                raise ValueError(
                    "wrong keys, got {0}, expected {1}".format(
                        sorted(settings.keys()),
                        sorted(self.PUBLISHER_GOOGLE_KEY_ALL)
                    )
                )
        else:
            raise ValueError("invalid publisherName {0}".format(publisherName))
        for (k,v) in settings.items():
            if type(v)!=str:
                raise ValueError(
                    "{0} should be a string, {1} is a {2}".format(
                        k,
                        v,
                        type(v),
                    )
                )
        
        # update database
        for (k,v) in settings.items():
            self.put(
                ['system','publishers',publisherName,k],
                v,
                username=username
            )
    
    @synchronized
    def factoryReset(self,username=USER_SYSTEM):
        '''
        \brief Reset the system to factory settings.
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        
        # authorize access
        self.authorize(username,['system'],self.ACTION_DELETE)
        
        # reset timestamp cache
        with self.timestampCacheLock:
            self.timestampCache   = {}
        
        # reset authorization cache
        self.authCache.reset()
        
        # reset datavault (causes default data to be loaded)
        self._factoryReset()
    
    #--- helpers
    
    def _system_deleteOldestStarttime(self):
        self.delete(['system','info','starttimes','laststarttimes',self.getLastStartTimes()[0]])
    
    def _validateManagerConnectionDescriptor(self,desc):
        if not isinstance(desc,(str,tuple)):
            raise ValueError("descriptor should be string or tuple, {0} is not".format(desc))
        if isinstance(desc,tuple):
            if len(desc)!=2:
                raise ValueError("descriptor should have exactly two elements, {0} does not".format(desc))
            if not isinstance(desc[0],str):
                raise ValueError("IP address should be str, {0} is not".format(desc[0]))
            if not isinstance(desc[1],int):
                raise ValueError("TCP port should be int, {0} is not".format(desc[1]))
    
    ##
    # \}
    #
    
    #========== users
    
    ##
    # \defgroup users users
    # \ingroup DustLinkData
    # \{
    #
    
    #--- defines
    
    MAXNUMCONNECTIONSSTORED            = 10
    
    AUTHLEVEL_NONE                     = 'authlevel none'
    AUTHLEVEL_PASSWORD                 = 'authlevel password'
    AUTHLEVEL_SSL                      = 'authlevel ssl'
    AUTHLEVEL_ALL                      = set([AUTHLEVEL_NONE,
                                          AUTHLEVEL_PASSWORD,
                                          AUTHLEVEL_SSL])
    
    CONNECTIONTYPE_CLI                 = 'cli'
    CONNECTIONTYPE_WEB                 = 'web'
    CONNECTIONTYPE_LBR                 = 'lbr'
    CONNECTIONTYPE_ALL                 = set([CONNECTIONTYPE_CLI,
                                          CONNECTIONTYPE_WEB,
                                          CONNECTIONTYPE_LBR])
    
    CONNECTIONSTATUS_CONNECTING        = 'connecting'
    CONNECTIONSTATUS_CONNECTED         = 'connected'
    CONNECTIONSTATUS_DISCONNECTING     = 'disconnecting'
    CONNECTIONSTATUS_DISCONNECTED      = 'disconnected'
    CONNECTIONSTATUS_ALL               = set([CONNECTIONSTATUS_CONNECTING,
                                          CONNECTIONSTATUS_CONNECTED,
                                          CONNECTIONSTATUS_DISCONNECTING,
                                          CONNECTIONSTATUS_DISCONNECTED])
    
    #--- admin
    
    def _users_putDefaultData(self):
        self.put(['users'],None)
    
    def _users_validateDataIntegrity(self):
        self.get(['users'])
    
    #--- public
    
    @synchronized
    def addUser(self,newUser,username=USER_SYSTEM):
        '''
        \brief Add a user.
        
        \param newUser   Name of the new user.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if newUser in self.getUserNames():
            raise ValueError("user {0} already exists".format(newUser))
        if newUser in self.RESTRICTED_USERNAMES:
            raise ValueError("restricted username")
        
        self.put(['users',newUser,'info','authlevel'],self.AUTHLEVEL_NONE,username)
        self.put(['users',newUser,'info','password'], None,username)
        self.put(['users',newUser,'info','ssl'],      None,username)
        
        self.put(['users',newUser,'activeConnections'],None,username)
        
        self.put(['users',newUser,'connectionHistory','maxConnectionsStored'],
                 self.MAXNUMCONNECTIONSSTORED,
                 username)
        self.put(['users',newUser,'connectionHistory','numConnections',self.CONNECTIONTYPE_CLI],
                 0,
                 username)
        self.put(['users',newUser,'connectionHistory','numConnections',self.CONNECTIONTYPE_WEB],
                 0,
                 username)
        self.put(['users',newUser,'connectionHistory','numConnections',self.CONNECTIONTYPE_LBR],
                 0,
                 username)
        self.put(['users',newUser,'connectionHistory','lastConnections'],
                 None,
                 username)
        self.put(['users',newUser,'privileges'],None,username)
    
    @synchronized
    def getUserNames(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the list of user names.
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        all_users = self.get(['users'],username=username, createCopy=False)
        if not all_users:
            return []
        else:
            returnVal = all_users.keys()
            returnVal.sort()
            return returnVal
    
    @synchronized
    def getConnectedUsers(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the list of currently connected users.
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if self.get('users',username=username):
            return [k for (k,v) in self.get('users',username=username, createCopy=False).items() if v['activeConnections']]
        else:
            return []
    
    @synchronized
    def getUserAuthlevel(self,usernameToExamine,username=USER_SYSTEM):
        '''
        \brief Retrieve the authentication level associated with a user.
        
        \param usernameToExamine The user of interest.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if usernameToExamine not in self.getUserNames():
            raise ValueError('unknown user {0}'.format(usernameToExamine))
        
        return self.get(['users',usernameToExamine,'info','authlevel'],username)
    
    @synchronized
    def setUserAuthlevel(self,usernameToExamine,newAuthLevel,username=USER_SYSTEM):
        '''
        \brief Set the authentication level associated with a user.
        
        \param usernameToExamine The user of interest.
        \param newAuthLevel The new authentication level for that user.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if usernameToExamine not in self.getUserNames():
            raise ValueError('unknown user {0}'.format(usernameToExamine))
        if newAuthLevel not in self.AUTHLEVEL_ALL:
            raise ValueError("invalid authentication level {0}".format(newAuthLevel))
        
        # refuse to switch to password authentication if no password is present
        if newAuthLevel==self.AUTHLEVEL_PASSWORD:
            if self.get(['users',usernameToExamine,'info','password'],username)==None:
                raise ValueError("can not switch, no password on record")
        
        # refuse to switch to ssl authentication if no ssl keying is present
        if newAuthLevel==self.AUTHLEVEL_SSL:
            if self.get(['users',usernameToExamine,'info','ssl'],username)==None:
                raise ValueError("can not switch, no ssl key on record")
        
        return self.put(['users',usernameToExamine,'info','authlevel'],newAuthLevel,username)
    
    @synchronized
    def passwordAuthenticate(self,usernameToAuthenticate,password):
        '''
        \brief Authenticate the user with a provided password.
        
        \exception DataVaultException.Unauthorized if authentication fails.
        
        \param usernameToAuthenticate The user to authenticate.
        \param password  The password (challenge) presented by the user.
        '''
        if not isinstance(password,str):
            raise ValueError('password should be a string, {0} is not'.format(password))
        if not usernameToAuthenticate==self.USER_ADMIN:
            if usernameToAuthenticate not in self.getUserNames():
                raise DataVaultException.Unauthorized('wrong username or password')
        
        hash_presented  = hashlib.sha1(password).hexdigest()
        if usernameToAuthenticate==self.USER_ADMIN:
            hash_expected   = self.get(['system','info','adminpassword'])
        else:
            hash_expected   = self.get(['users',usernameToAuthenticate,'info','password'])
        
        if hash_presented!=hash_expected:
            raise DataVaultException.Unauthorized('wrong username or password')
    
    @synchronized
    def setUserPassword(self,usernameToAuthenticate,oldPassword,newPassword,username=USER_SYSTEM):
        '''
        \brief Set the password associated with a user.
        
        \note A hash of the password is stored, never the clear-text password.
        
        \param usernameToAuthenticate The user of interest.
        \param oldPassword  The old password of the user. This is ignored
                         if no password is presented.
        \param newPassword  The new password of the user.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if oldPassword:
            if not isinstance(oldPassword,str):
                raise ValueError('oldPassword should be a string, {0} is not'.format(oldPassword))
        if not isinstance(newPassword,str):
            raise ValueError('newPassword should be a string, {0} is not'.format(newPassword))
        if not usernameToAuthenticate==self.USER_ADMIN:
            if usernameToAuthenticate not in self.getUserNames():
                raise ValueError('unknown username {0}'.format(usernameToAuthenticate))
        
        # authorize
        if usernameToAuthenticate==self.USER_ADMIN:
            if not username==self.USER_ADMIN:
               raise DataVaultException.Unauthorized('only admin can reset admin\'s password')
        else:
            self.authorize(username,['users',usernameToAuthenticate],self.ACTION_PUT)
        
        # if you get here, authorization is granted
        
        if usernameToAuthenticate==self.USER_ADMIN:
            if not oldPassword:
                raise DataVaultException.Unauthorized('you need to pass current password to reset admin\'s.')
            self.passwordAuthenticate(usernameToAuthenticate,oldPassword)
        else:
            if username!=self.USER_ADMIN:
                if self.get(['users',usernameToAuthenticate,'info','password'])!=None:
                    self.passwordAuthenticate(usernameToAuthenticate,oldPassword)
        
        # if you get here, the old password is correct (or not needed)
        
        hashed_newPassword = hashlib.sha1(newPassword).hexdigest()
        
        if usernameToAuthenticate==self.USER_ADMIN:
            self.put(['system','info','adminpassword'],hashed_newPassword,username)
        else:
            self.put(['users',usernameToAuthenticate,'info','password'],hashed_newPassword,username)
    
    @synchronized
    def getUserSsl(self,usernameToAuthenticate,username=USER_SYSTEM):
        '''
        \brief Get the public ssl key of a user.
        
        \param usernameToAuthenticate The user of interest.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        
        if usernameToAuthenticate not in self.getUserNames():
            raise ValueError('unknown user {0}'.format(usernameToAuthenticate))
        
        return self.get(['users',usernameToAuthenticate,'info','ssl'],username)
    
    @synchronized
    def setUserSsl(self,usernameToAuthenticate,ssl,username=USER_SYSTEM):
        '''
        \brief Set the password associated with a user.
        
        \note A hash of the password is stored, never the clear-text password.
        
        \param usernameToAuthenticate The user of interest.
        \param ssl       The user's public key.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        
        if not isinstance(ssl,str):
            raise ValueError('ssl should be a string, {0} is not'.format(ssl))
        
        if usernameToAuthenticate not in self.getUserNames():
            raise ValueError('unknown username {0}'.format(usernameToAuthenticate))
        
        self.put(['users',usernameToAuthenticate,'info','ssl'], ssl,username)
    
    @synchronized
    def getUserPrivileges(self,usernameToExamine,username=USER_SYSTEM):
        '''
        \brief Retrieve the privileges associated with a user.
        
        \param usernameToExamine The user of interest.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        return self.get(['users',usernameToExamine,'privileges'],username)
    
    @synchronized
    def grantPrivilege(self,resource,usernameToGrant,action,username=USER_SYSTEM):
        '''
        \brief Grant a privilege to a user.
        
        \param resource  The resource of interest. Note that the last element
                         can be a wildcard.
        \param usernameToGrant The user of interest.
        \param action    The action to grant, taken from ACTION_ALL.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        self.authCache.reset()
        self._users_validate_privilegeResource(resource)
        if usernameToGrant not in self.getUserNames():
            raise ValueError("unknown username {0}".format(usernameToGrant))
        if action not in self.ACTION_ALL:
            raise ValueError("unsuppored action {0}".format(action))
        
        # abort if user is already granted all resources
        try:
            alreadyGranted = self.get(['users',usernameToGrant,'privileges']+resource[:-1])
        except DataVaultException.NotFound:
            pass # happens when no privileges on this resource
        else:
            if  (
                    alreadyGranted                                        and
                    (self.RESOURCE_WILDCARD in alreadyGranted)            and 
                    (action in alreadyGranted[self.RESOURCE_WILDCARD])    and 
                    (alreadyGranted[self.RESOURCE_WILDCARD][action]==self.YES)
                ):
                    return
        
        # if we're granting to all resources, not to have duplicates, remove
        # what's there now (will be replaced with a wildcard below)
        if resource[-1]==self.RESOURCE_WILDCARD:
            if self.get(resource[:-1]):
                allResources = self.get(resource[:-1]).keys()
            else:
                allResources = []
            for r in allResources:
                try:
                    self.denyPrivilege(resource[:-1]+[r],usernameToGrant,action)
                except DataVaultException.NotFound:
                    pass # happens when privilege was not granted
        
        # prepare the full source path
        resourcePath  = []
        resourcePath += ['users',usernameToGrant,'privileges']
        resourcePath += resource
        resourcePath += [action]
        
        # grant access
        self.put(resourcePath,self.YES,username)
    
    @synchronized
    def denyPrivilege(self,resource,usernameToDeny,action,username=USER_SYSTEM):
        '''
        \brief Deny a privilege from a user.
        
        \param resource  The resource of interest.
        \param usernameToDeny The user of interest.
        \param action    The action to grant, taken from ACTION_ALL.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        self.authCache.reset()
        self._users_validate_privilegeResource(resource)
        if usernameToDeny not in self.getUserNames():
            raise ValueError("unknown username {0}".format(usernameToDeny))
        if action not in self.ACTION_ALL:
            raise ValueError("unsuppored action {0}".format(action))
        
        # authorize
        self.authorize(username,['users',usernameToDeny,'privileges'],self.ACTION_PUT)
        
        # if you get here, access was granted
        
        # if we were assigned a wildcard on that resource, replace by individual ones
        try:
            alreadyGranted = self.get(['users',usernameToDeny,'privileges']+resource[:-1])
        except DataVaultException.NotFound:
            pass # happens when no privileges on this resource
        else:
            if  (
                    (self.RESOURCE_WILDCARD in alreadyGranted)            and 
                    (action in alreadyGranted[self.RESOURCE_WILDCARD])    and 
                    (alreadyGranted[self.RESOURCE_WILDCARD][action]==self.YES)
                ):
                    
                    if self.get(resource[:-1]):
                        allResources = self.get(resource[:-1]).keys()
                    else:
                        allResources = []
                    
                    self.delete(['users',usernameToDeny,'privileges']+resource[:-1]+[self.RESOURCE_WILDCARD])
                    for r in allResources:
                        self.grantPrivilege(resource[:-1]+[r],usernameToDeny,action)
        
        deletedResources = []
        
        # deny privilege
        if resource[-1]==self.RESOURCE_WILDCARD:
            # remove "action" privileges to all resources
            try:
                alreadyGranted = self.get(['users',usernameToDeny,'privileges']+resource[:-1])
            except DataVaultException.NotFound:
                pass # happens when no privileges
            else:
                if alreadyGranted:
                    for r in alreadyGranted.keys():
                        if (action in alreadyGranted[r]) and (alreadyGranted[r][action]==self.YES):
                            resourceToDelete = ['users',usernameToDeny,'privileges']+resource[:-1]+[r]
                            self.delete(resourceToDelete+[action])
                            deletedResources += [resourceToDelete]
            
        else:
            # remove the exact resource
            resourceToDelete = ['users',usernameToDeny,'privileges']+resource
            self.delete(resourceToDelete+[action])
            deletedResources += [resourceToDelete]
        
        # clean-up
        for dr in deletedResources:
            # apply a clean delete is no resources left
            if not self.get(dr):
                self.delete(dr)
            
            # if no actions left on a granted resource, remove the resource
            if len(dr)==5 and not self.get(dr[:-1]):
                self.delete(dr[:-1])
    
    @synchronized
    def getUserActiveConnections(self,usernameToExamine,username=USER_SYSTEM):
        '''
        \brief Retrieve the connection currently active for a given user.
        
        \param usernameToExamine The user of interest.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        return self.get(['users',usernameToExamine,'activeConnections'],username)
    
    @synchronized
    def getUserConnectionHistory(self,usernameToExamine,username=USER_SYSTEM):
        '''
        \brief Retrieve the connection history associated with a user.
        
        \param usernameToExamine The user of interest.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        return self.get(['users',usernameToExamine,'connectionHistory'],username)
    
    @synchronized
    def indicateUserConnection(self,usernameToExamine,connectionType,connectionStatus,connectionDetails=None,connectionToken=None,username=USER_SYSTEM):
        '''
        \brief Indicate a change in connection status for a given user.
        
        \param usernameToExamine The user of interest.
        \param connectionType The type of connection.
        \param connectionStatus The new status of that connection.
        \param connectionDetails The details of that connection.
        \param connectionToken  If modifying the state of a previously
                                established connection, the token associated
                                with that connection.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if usernameToExamine not in self.getUserNames():
            raise ValueError("unknown username {0}".format(usernameToExamine))
        if connectionType not in self.CONNECTIONTYPE_ALL:
            raise ValueError("connectionType {0} not in {1}".format(connectionType,self.CONNECTIONTYPE_ALL))
        if connectionStatus not in self.CONNECTIONSTATUS_ALL:
            raise ValueError("connectionStatus {0} not in {1}".format(connectionStatus,self.CONNECTIONSTATUS_ALL))
        
        # authorize
        self.authorize(username,['users',usernameToExamine],self.ACTION_PUT)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        nowTimestamp = time.time()
        
        if connectionStatus in [self.CONNECTIONSTATUS_DISCONNECTED]:
            # move connection from active to history
            activeConnections = self.getUserActiveConnections(usernameToExamine)
            if connectionToken not in activeConnections:
                raise ValueError("not active connection with token {0}".format(connectionToken))
            if activeConnections[connectionToken]['type']!=connectionType:
                raise ValueError("connection with token {0} is of type {1}, not {2}".format(
                        connectionToken,
                        activeConnections[connectionToken]['type'],
                        connectionType
                    ))
            
            startTime = activeConnections[connectionToken]['startTime']
            
            # increment connection counters
            currentCounter = self.get(['users',usernameToExamine,'connectionHistory','numConnections',connectionType],username)
            self.put(['users',usernameToExamine,'connectionHistory','numConnections',connectionType],
                     currentCounter+1)
            
            # remove old lastConnections, if needed
            while (
                   self.get(['users',usernameToExamine,'connectionHistory','lastConnections'])
                   and
                   len(self.get(['users',usernameToExamine,'connectionHistory','lastConnections']))> \
                      self.get(['users',usernameToExamine,'connectionHistory','maxConnectionsStored'])-1
                  ):
                self._users_deleteOldestConnection(usernameToExamine)
            
            # add this connection to the last connections
            self.put(['users',usernameToExamine,'connectionHistory','lastConnections',(startTime,nowTimestamp)],
                     connectionType)
            
            # remove this connection from the current connections
            self.delete(['users',usernameToExamine,'activeConnections',connectionToken])
            
        else:
            
            connectionToken = self._users_getConnectionToken(usernameToExamine) # do as admin
            self.put(['users',usernameToExamine,'activeConnections',connectionToken,'startTime'],
                     nowTimestamp)
            self.put(['users',usernameToExamine,'activeConnections',connectionToken,'type'],
                     connectionType)
            self.put(['users',usernameToExamine,'activeConnections',connectionToken,'status'],
                     connectionStatus)
            self.put(['users',usernameToExamine,'activeConnections',connectionToken,'details'],
                     connectionDetails)
            return connectionToken
    
    @synchronized
    def deleteUser(self,userToDelete,username=USER_SYSTEM):
        '''
        \brief Delete a user.
        
        \param userToDelete   Name of the user to delete.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if userToDelete not in self.getUserNames():
            raise ValueError("user {0} does not exist".format(userToDelete))
        
        self.delete(['users',userToDelete],username)
    
    #--- helpers
    
    def _users_getConnectionToken(self,usernameToExamine,username=USER_SYSTEM):
        activeConnections = self.get(['users',usernameToExamine,'activeConnections'],username)
        if activeConnections:
            currentTokens = activeConnections.keys()
        else:
            currentTokens = []
        returnVal = None
        while (not returnVal) or (returnVal in currentTokens):
            returnVal = random.randint(0,0xffff)
        return returnVal
    
    def _users_deleteOldestConnection(self,usernameToExamine):
        # find the index of the oldest connection in the history
        # Note: oldest by date of disconnection
        startStopTimes = self.getUserConnectionHistory(usernameToExamine)['lastConnections'].keys()
        oldestStartStop = None
        for startStopTime in startStopTimes:
            if (not oldestStartStop) or (startStopTime[1]<oldestStartStop[1]):
                oldestStartStop = startStopTime
        
        # delete that entry
        self.delete(['users',usernameToExamine,'connectionHistory','lastConnections',oldestStartStop])
    
    def _users_validate_privilegeResource(self,resource):
        if not resource:
            raise ValueError("resource can not be empty")
        if not isinstance(resource,list):
            raise ValueError("resource must be a list")
        
        if   resource[0] in (self.RESOURCE_SYSTEM,
                             self.RESOURCE_USERS):
            
            # test correct number of subresources
            if len(resource)!=1:
                raise ValueError("no subresource for {0}, you asked {1}".format(
                                        resource[0],
                                        resource))
        
        elif resource[0] in (self.RESOURCE_APPS):
            
            # test correct number of subresources
            if len(resource)!=2:
                raise ValueError("exactly 1 subresource for {0}, you asked {1}".format(
                                        resource[0],
                                        resource
                                        ))
            
            # test subresource value
            if resource[1] not in self.getAppNames()+[self.RESOURCE_WILDCARD]:
                raise ValueError("unknown app {0}".format(resource[1]))
        
        elif resource[0] in (self.RESOURCE_MOTES):
            
            # test correct number of subresources
            if len(resource)!=2:
                raise ValueError("exactly 1 subresource for {0}, you asked {1}".format(
                                        resource[0],
                                        resource
                                        ))
            
            # test subresource value
            if resource[1] not in self.getMoteMacs()+[self.RESOURCE_WILDCARD]:
                raise ValueError("unknown MAC {0}".format(resource[1]))
        
        elif resource[0] in (self.RESOURCE_NETWORKS,
                             self.RESOURCE_TESTRESULTS,
                             self.RESOURCE_FIREWALL,
                             self.RESOURCE_DATAFLOWS):
            
            # test correct number of subresources
            if len(resource)!=2:
                raise ValueError("exactly 1 subresource for {0}, you asked {1}".format(
                                        resource[0],
                                        resource
                                        ))
            
            # test subresource value
            if resource[1] not in self.getNetnames()+[self.RESOURCE_WILDCARD]:
                raise ValueError("unknown netname {0}".format(resource[1]))
        
        else:
            raise ValueError("unknown resource {0}".format(resource[0]))
    
    ##
    # \}
    #
    
    #========== apps
    
    ##
    # \defgroup apps apps
    # \ingroup DustLinkData
    # \{
    #
    
    #--- defines
    
    WKP_OAP                  = 0xf0b9
    WKP_COAP                 = 5683
    WKP_MOTERUNNER           = 0xf0b9
    
    APP_TRANSPORT_UDP        = 'UDP'
    APP_TRANSPORT_OAP        = 'OAP'
    APP_TRANSPORT_COAP       = 'CoAP'
    APP_TRANSPORT_MOTERUNNER = 'moteRunner'
    APP_TRANSPORT_ALL        = set([APP_TRANSPORT_UDP,
                                APP_TRANSPORT_OAP,
                                APP_TRANSPORT_COAP,
                                APP_TRANSPORT_MOTERUNNER])
    
    APP_DIRECTION_FROMMOTE   = 'fromMote'
    APP_DIRECTION_TOMOTE     = 'toMote'
    APP_DIRECTION_ALL        = (APP_DIRECTION_FROMMOTE,
                                APP_DIRECTION_TOMOTE)
    
    #--- admin
    
    def _apps_putDefaultData(self):
        self.put(['apps'],None)
    
    def _apps_validateDataIntegrity(self):
        self.get(['apps'], createCopy=False)
    
    #--- public
    
    @synchronized
    def getAppNames(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the names of the apps this user has privileges to.
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        # get all the apps (as ADMIN)
        all_apps = self.get(['apps'], createCopy=False)
        
        # return if none
        if not all_apps:
            return []
        
        # format as a (sorted) list
        all_apps = all_apps.keys()
        all_apps.sort()
        
        if self._isPriviledged(username):
            return all_apps
         
        # remove the ones this user is not authorized to GET, PUT and DELETE
        returnVal = []
        for appname in all_apps:
            # canGet
            try:
                self.authorize(username,['apps',appname],self.ACTION_GET)
            except:
                canGet = False
            else:
                canGet = True
            # canPut
            try:
                self.authorize(username,['apps',appname],self.ACTION_PUT)
            except:
                canPut = False
            else:
                canPut = True
            # canDelete
            try:
                self.authorize(username,['apps',appname],self.ACTION_DELETE)
            except:
                canDelete = False
            else:
                canDelete = True
            
            if canGet or canPut or canDelete:
                returnVal.append(appname)
        
        return returnVal
    
    @synchronized
    def addApp(self,appname,username=USER_SYSTEM):
        '''
        \brief Add an app to the system.
        
        \param appname   The name of the app to add. This needs to be a string,
                         unique among all apps in the system.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if appname in self.getAppNames():
            raise ValueError("app {0} already exists".format(appname))
        if not isinstance(appname,str):
            raise ValueError("appname needs to be a string, {0} is a {1}".format(appname,type(appname)))
        
        self.put(['apps',appname,'description'],'',username)
        
        self.put(['apps',appname,'transport'],  None,username)
        self.put(['apps',appname,'resource'],   None,username)
        
        self.put(['apps',appname,'fromMote','dataFields','fieldFormats'],   None,username)
        self.put(['apps',appname,'fromMote','dataFields','fieldNames'],   None,username)
        
        self.put(['apps',appname,'toMote','dataFields','fieldFormats'],   None,username)
        self.put(['apps',appname,'toMote','dataFields','fieldNames'],   None,username)
        
    @synchronized
    def getAppDescription(self,appname,username=USER_SYSTEM):
        '''
        \brief Retrieve the description of an app.
        
        \param appname   The name of the app of interest.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if appname not in self.getAppNames():
            raise ValueError("unknown app {0}".format(appname))
        
        return self.get(['apps',appname,'description'],username)
    
    @synchronized
    def setAppDescription(self,appname,description,username=USER_SYSTEM):
        '''
        \brief Add a description associated with an app.
        
        \note Calling this function replaces any previous values.
        
        \param appname   The name of the app of interest.
        \param description The description of the app.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if appname not in self.getAppNames():
            raise ValueError("unknown app {0}".format(appname))
        
        self.put(['apps',appname,'description'],description,username)
    
    @synchronized
    def getAppTransport(self,appname,username=USER_SYSTEM):
        '''
        \brief Retrieve the transport method associated with an app.
        
        \param appname   The name of the app of interest.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        
        \returns A tuple (transport,resource).
        '''
        if appname not in self.getAppNames():
            raise ValueError("unknown app {0}".format(appname))
        
        transport = self.get(['apps',appname,'transport'],username)
        resource = self.get(['apps',appname,'resource'],username)
        return (transport,resource)
    
    @synchronized
    def setAppTransport(self,appname,transportType,resource,username=USER_SYSTEM):
        '''
        \brief Add a transport destails associated with an app.
        
        \note Calling this function replaces any previous values.
        
        \param appname   The name of the app of interest.
        \param transportType The type of transport associated with this app.
        \param resource The resource associated with this app.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if transportType not in self.APP_TRANSPORT_ALL:
            raise ValueError("unknown transport type {0}".format(transportType))
        self._validateResource(transportType,resource)
        
        if appname not in self.getAppNames():
            raise ValueError("unknown app {0}".format(appname))
        
        self.put(['apps',appname,'transport'],transportType,username)
        self.put(['apps',appname,'resource'],resource,username)
    
    @synchronized
    def getAppFields(self,appname,direction,username=USER_SYSTEM, **kw):
        '''
        \brief Retrieve the fields associated with an app.
        
        \param appname   The name of the app of interest.
        \param direction The direcion, taken from APP_DIRECTION_ALL.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        
        \returns A dict with keys 'fieldFormats','fieldNames'.
        '''
        if self._doValidation(username):
            if direction not in self.APP_DIRECTION_ALL:
                raise ValueError("invalid direction {0}".format(direction))
            if appname not in self.getAppNames():
                raise ValueError("unknown app {0}".format(appname))
        
        return self.get(['apps',appname,direction,'dataFields'],username, **kw)
    
    @synchronized
    def setAppFields(self,appname,direction,fieldFormats,fieldNames,username=USER_SYSTEM):
        '''
        \brief Associate a field format to an app.
        
        \note Calling this function replaces any previous values.
        \note To clear the app fields, set both fieldFormats and fieldNames
              to None.
        
        \param appname   The name of the app of interest.
        \param direction The direcion, taken from APP_DIRECTION_ALL.
        \param fieldFormats The field format of the data received from the app,
                         in Python struct format, e.g. "<bbbHb"
        \param fieldNames The names of the fields, i.e. a list of strings.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if direction not in self.APP_DIRECTION_ALL:
            raise ValueError("invalid direction {0}".format(direction))
        if fieldFormats:
            try:
                struct.Struct(fieldFormats)
            except:
                raise ValueError("{0} is not a valid struct format".format(fieldFormats))
        if fieldNames:
            if not isinstance(fieldNames,list):
                raise ValueError("fieldNames should be a list, {0} is a {1}".format(fieldNames,type(fieldNames)))
            for f in fieldNames:
                if not isinstance(f,str):
                    raise ValueError("fieldNames should strings, {0} from {1} is a {2}".format(f,fieldNames,type(f)))
        if fieldFormats and fieldNames:
            if len(re.sub('[@=<>!]', '', fieldFormats))!=len(fieldNames):
                raise ValueError("fieldFormats={0} suggests fieldNames should contains {1} fields; it contains {2}".format(
                            fieldFormats,
                            struct.Struct(fieldFormats).size,
                            len(fieldNames)))
        if (fieldFormats) and (not fieldNames):
            raise ValueError("fieldFormats={0} specified, but no fieldNames".format(fieldFormats))
        if (not fieldFormats) and (fieldNames):
            raise ValueError("fieldNames={0} specified, but no fieldFormats".format(fieldNames))
        
        self.put(['apps',appname,direction,'dataFields','fieldFormats'],fieldFormats,username)
        self.put(['apps',appname,direction,'dataFields','fieldNames'],fieldNames,username)
    
    @synchronized
    def deleteApp(self,appname,username=USER_SYSTEM):
        '''
        \brief Delete an app from the system.
        
        \note Calling this command will have the following side-effects:
               - you will loose all data associated with this app, on all motes
                 in the system.
               - this app will disappear from all motes where it was associated.
               - all users will loose their privileges to this app
        
        \param appname   The name of the app to delete.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if appname not in self.getAppNames():
            raise ValueError("unknown app {0}".format(appname))
        
        # authorize
        self.authorize(username,['apps',appname],self.ACTION_DELETE)
        
        # delete app from timestampCache
        for (tsMac,tsAppName) in self.timestampCache.keys():
            if tsAppName==appname:
                del self.timestampCache[(tsMac,tsAppName)]
        
        # delete app from motes
        for mac in self.getMoteMacs():
            if appname in self.getAttachedApps(mac):
                self.detachAppFromMote(mac,appname)
        
        # delete app from apps
        self.delete(['apps',appname])
    
    #--- helpers
    
    def _validateResource(self,type,resource):
        if type in [self.APP_TRANSPORT_UDP]:
            if not isinstance(resource,int):
                raise ValueError("resource for UDP must be an int, {0} is not".format(resource))
            if (resource>65535 or resource<1024):
                raise ValueError("UDP port must be between 1024 and 65535, {0} is not".format(resource))
        if type in [self.APP_TRANSPORT_OAP]:
            if not isinstance(resource,tuple):
                raise ValueError("OAP resource must be a tuple, {0} is not".format(resource))
            for r in resource:
                if not isinstance(r,int):
                    raise ValueError("OAP resource must be a tuple of integers, {0} from {1} is not".format(r,resource))
        if type in [self.APP_TRANSPORT_COAP]:
            if not isinstance(resource,tuple):
                raise ValueError("COAP resource must be a tuple, {0} is not".format(resource))
            for r in resource:
                if not isinstance(r,str):
                    raise ValueError("OAP resource must be a tuple of strings, {0} from {1} is not".format(r,resource))
        if type in [self.APP_TRANSPORT_MOTERUNNER]:
            if not isinstance(resource,int):
                raise ValueError("resource for moteRunner must be an int, {0} is not".format(resource))
    
    ##
    # \}
    #
    
    #========== motes
    
    ##
    # \defgroup motes motes
    # \ingroup DustLinkData
    # \{
    #
    
    #--- defines
    
    MAXNUMDATAPOINTSSTORED  = 100
    
    #--- admin
    
    def _motes_putDefaultData(self):
        self.put(['motes'],None)
    
    def _motes_validateDataIntegrity(self):
        self.get(['motes'])
    
    #--- public
    
    @synchronized
    def getMoteMacs(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the MAC addresses of all motes this user has privileges
               to.
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        # get all the macs (as ADMIN)
        all_macs = self.get(['motes'], createCopy=False)
        
        # return if none
        if not all_macs:
            return []
        
        # format as a (sorted) list
        all_macs = all_macs.keys()
        all_macs.sort()
        
        if self._isPriviledged(username):
            return all_macs
        
        # remove the ones this user is not authorized to GET, PUT and DELETE
        returnVal = []
        for mac in all_macs:
            # canGet
            try:
                self.authorize(username,['motes',mac],self.ACTION_GET)
            except:
                canGet = False
            else:
                canGet = True
            # canPut
            try:
                self.authorize(username,['motes',mac],self.ACTION_PUT)
            except:
                canPut = False
            else:
                canPut = True
            # canDelete
            try:
                self.authorize(username,['motes',mac],self.ACTION_DELETE)
            except:
                canDelete = False
            else:
                canDelete = True
            
            if canGet or canPut or canDelete:
                returnVal.append(mac)
        
        return returnVal
    
    @synchronized
    def addMote(self,mac,username=USER_SYSTEM):
        '''
        \brief Add a mote.
        
        \param mac       The MAC address of the new mote.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if self._doValidation(username):
            self._validateFormatMac(mac)
        
        if mac in self.getMoteMacs():
            raise ValueError("mote {0} already exists".format(mac))
        
        self.put(['motes',mac,'info'],None,username)
        self.put(['motes',mac,'apps'],None,username)
    
    @synchronized
    def getMoteInfo(self,mac,username=USER_SYSTEM):
        '''
        \brief Get the info elements of a mote.
        
        \param mac       The MAC address of the mote.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if self._doValidation(username):
            self._validateFormatMac(mac)
            if mac not in self.getMoteMacs():
                raise ValueError("mote {0} does not exist".format(mac))
        
        return self.get(['motes',mac,'info'],username)
    
    @synchronized
    def setMoteInfo(self,mac,infoKey,infoVal,username=USER_SYSTEM):
        '''
        \brief Set an info value of a mote.
        
        \param mac       The MAC address of the mote.
        \param infoKey   The name of the information element.
        \param infoVal   The value of the information element.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if self._doValidation(username):
            self._validateFormatMac(mac)
            if mac not in self.getMoteMacs():
                raise ValueError("mote {0} does not exist".format(mac))
        
        self.put(['motes',mac,'info',infoKey],infoVal,username)
    
    @synchronized
    def deleteMoteInfo(self,mac,username=USER_SYSTEM):
        '''
        \brief Delete the info section of a particular mote.
        
        \param mac       The MAC address of the mote.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if self._doValidation(username):
            self._validateFormatMac(mac)
            if mac not in self.getMoteMacs():
                raise ValueError("mote {0} does not exist".format(mac))
        
        self.delete(['motes',mac,'info'],username)    # do this as user
        self.put(   ['motes',mac,'info'],None)        # do this as SYSTEM (to reset entry)
    
    @synchronized
    def attachAppToMote(self,mac,appname,username=USER_SYSTEM):
        '''
        \brief Attache an app to a mote.
        
        \param mac       The MAC address of the mote.
        \param appname   The name of the new app.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        self._validateFormatMac(mac)
        if mac not in self.getMoteMacs():
            raise ValueError("unknown mac {0}".format(mac))
        if appname not in self.getAppNames():
            raise ValueError("unknown app {0}".format(appname))
        if appname in self.getAttachedApps(mac):
            raise ValueError("app {0} already attached to mote {1}".format(appname,mac))
        
        self.put(['motes',mac,'apps',appname,'numDataPointsReceived'],0,username)
        self.put(['motes',mac,'apps',appname,'maxNumDataPointsStored'],self.MAXNUMDATAPOINTSSTORED,username)
        self.put(['motes',mac,'apps',appname,'appData'],None,username)
    
    @synchronized
    def getAttachedApps(self,mac,username=USER_SYSTEM):
        '''
        \brief Retrive the list of apps attached to a given mote.
        
        \param mac       The MAC address of the mote.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if self._doValidation(username):
                self._validateFormatMac(mac)
                if mac not in self.getMoteMacs():
                    raise ValueError("unknown mac {0}".format(mac))
        
        mote_apps = self.get(['motes',mac,'apps'],username, createCopy=False)
        if not mote_apps:
            return []
        else:
            return mote_apps.keys()
    
    @synchronized
    def detachAppFromMote(self,mac,appname,username=USER_SYSTEM):
        '''
        \brief Detach an app from a mote.
        
        \note If you call this function, you will loose all data generated by
              this app, by this mote.
        
        \param mac       The MAC address of the mote.
        \param appname   The name of the new app.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        self._validateFormatMac(mac)
        if mac not in self.getMoteMacs():
            raise ValueError("unknown mac {0}".format(mac))
        if username!=self.USER_ADMIN:
            try:
                self.authorize(username,['motes',mac],self.ACTION_GET)
            except:
                canGet = False
            else:
                canGet = True
            try:
                self.authorize(username,['motes',mac],self.ACTION_PUT)
            except:
                canPut = False
            else:
                canPut = True
            if (not canGet) and (not canPut):
                raise DataVaultException.Unauthorized("{0} has neither GET nor PUT privileges on {1}".format(
                            username,
                            mac))
        if appname not in self.getAttachedApps(mac):
            raise ValueError("app {0} not attached to mote {1}".format(appname,mac))
        
        # do a dummy write, to validate user privileges
        self.put(['motes',mac,'apps',appname],'dummy',username)
        
        # if you get here, privileges has been verified, continue as ADMIN 
        
        self.delete(['motes',mac,'apps',appname])
    
    @synchronized
    def getNumDataPoints(self,mac,appname,username=USER_SYSTEM):
        '''
        \brief Retrieve the number of data points received.
        
        \note Depending on the depth of the buffer, this number can be larger
              than the datapoints actually stored.
        
        \param mac       The MAC address of the mote of interest.
        \param appname   The name of the app of interest.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if self._doValidation(username):
            self._validateFormatMac(mac)
            if mac not in self.getMoteMacs():
                raise ValueError("unknown mac {0}".format(mac))
            if appname not in self.getAttachedApps(mac,username):
                raise ValueError("app {0} not attached to mote {1}".format(appname,mac))
        
        return self.get(['motes',mac,'apps',appname,'numDataPointsReceived'],username)
    
    @synchronized
    def getLastData(self,mac,appname,numEntries=MAXNUMDATAPOINTSSTORED,username=USER_SYSTEM, **kw):
        '''
        \brief Retrieve the data produced by an app on a mote.
        
        \param mac       The MAC address of the mote of interest.
        \param appname   The name of the app of interest.
        \param numEntries How many entries to return. When passed, returns only
                         the last numEntries data points. If this parameters is
                         omitted, all the data is returned.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if self._doValidation(username):
            self._validateFormatMac(mac)
            if mac not in self.getMoteMacs():
                raise ValueError("unknown mac {0}".format(mac))
            if appname not in self.getAttachedApps(mac,username):
                raise ValueError("app {0} not attached to mote {1}".format(appname,mac))
        
        allData = self.get(['motes',mac,'apps',appname,'appData'],username, **kw)
        
        if allData and numEntries<len(allData):
            returnData = {}
            allDataTimestamps = allData.keys()
            allDataTimestamps.sort(reverse=True)
            for i in range(numEntries):
                returnData[allDataTimestamps[i]]=allData[allDataTimestamps[i]]
        else:
            returnData = allData
        
        return returnData
    
    @synchronized
    def indicateData(self,mac,appname,dataVal,timestamp=None,username=USER_SYSTEM):
        '''
        \brief Indicate data received from that mote/app.
        
        \exception ValueError if the mote 'mac' does not exist.
        \exception ValueError if the application 'appname' does not exist.
        \exception TypeError if the dataVal does not comply with the format defined
                          in the corresponding app.
        
        \param mac       The MAC address of the mote which generated that data.
        \param appname   The name of the app which generated the data.
        \param dataVal   The newly received value.
        \param timestamp The timestampe associated with this data. If this
                         parameters is omitted, the current time is used.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        
        # authorize
        self.authorize(username,['motes',mac],self.ACTION_PUT)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        if timestamp==None:
            timestamp=time.time()
        
        self._validateFormatMac(mac)
        if mac not in self.getMoteMacs():
            raise ValueError("unknown mac {0}".format(mac))
        if appname not in self.getAttachedApps(mac):
            raise ValueError("app {0} not attached to mote {1}".format(appname,mac))
        if not isinstance(dataVal,dict):
            raise ValueError("dataVal has to be a dictionary, {0} is a {1}".format(dataVal,type(dataVal)))
        
        fieldsDataPassed   = dataVal.keys()
        if fieldsDataPassed:
            fieldsDataPassed.sort()
        fieldsDataExpected = self.getAppFields(appname,self.APP_DIRECTION_FROMMOTE, createCopy=False)['fieldNames']
        if fieldsDataExpected:
            fieldsDataExpected = sorted(fieldsDataExpected)
        
        if fieldsDataPassed!=fieldsDataExpected:
            raise ValueError("malformed data, expected fields {0}, got {1}".format(fieldsDataExpected,fieldsDataPassed))
        
        # increment total number of data points received
        self.put(['motes',mac,'apps',appname,'numDataPointsReceived'],
            self.get(['motes',mac,'apps',appname,'numDataPointsReceived'],)+1)
        
        # remove oldest data, if necessary
        with self.timestampCacheLock:
            
            # populate the timestamp cache for this (mac,app), if necessary
            if (mac,appname) not in self.timestampCache.keys():
                lastData = self.getLastData(mac,appname, createCopy=False)
                if lastData:
                    dataTimestamps = lastData.keys()
                    dataTimestamps.sort()
                else:
                    dataTimestamps = []
                self.timestampCache[(mac,appname)] = dataTimestamps
            
            # remove the data item corresponding to the oldest data point, if necessary
            if len(self.timestampCache[(mac,appname)])>self.get(['motes',mac,'apps',appname,'maxNumDataPointsStored'])-1:
                oldestTimestamp = self.timestampCache[(mac,appname)].pop(0)
                self.delete(['motes',mac,'apps',appname,'appData',oldestTimestamp])
            
            # add the new timestamp to the timestamp cache
            self.timestampCache[(mac,appname)].append(timestamp)
            
        # add new data
        self.put(['motes',mac,'apps',appname,'appData',timestamp],dataVal)
    
    @synchronized
    def deleteData(self,mac,appname,username=USER_SYSTEM):
        '''
        \brief Removes all the data reveived from that mote/app.
        
        Note that this function only clears the buffer of last received data
        points, it does not remove the application from the mote, or reset the
        numDataPointsReceived counter.
        
        \exception ValueError if the mote 'mac' does not exist.
        \exception ValueError if the application 'appname' does not exist.
        
        \param mac       The MAC address of the mote which generated that data.
        \param appname   The name of the app which generated the data.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        
        # authorize
        self.authorize(username,['apps',appname], self.ACTION_DELETE)
        self.authorize(username,['motes',mac],    self.ACTION_DELETE)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        self._validateFormatMac(mac)
        if mac not in self.getMoteMacs():
            raise ValueError("unknown mac {0}".format(mac))
        if appname not in self.getAttachedApps(mac):
            raise ValueError("app {0} not attached to mote {1}".format(appname,mac))
        
        with self.timestampCacheLock:
            # clear data buffer
            try:
                self.put(['motes',mac,'apps',appname,'appData'],None)
            except KeyError:
                pass # happens when no appData
            
            # clear the timestampCache
            try:
                del self.timestampCache[(mac,appname)]
            except KeyError:
                pass # happens when no appData
    
    @synchronized
    def deleteMote(self,mac,username=USER_SYSTEM):
        '''
        \brief Delete a mote from the system.
        
        \note Calling this command will have the following side-effects:
               - you will loose all data received from this mote.
               - this mote will disappear from all networks which include this mote.
               - all users will loose their privileges to this mote.
        
        \param mac       The MAC address of the mote to be deleted.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        self._validateFormatMac(mac)
        if mac not in self.getMoteMacs():
            raise ValueError("unknown mac {0}".format(mac))
        
        # authorize
        self.authorize(username,['motes',mac],self.ACTION_DELETE)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        # delete mote from timestampCache
        for (tsMac,tsAppName) in self.timestampCache.keys():
            if tsMac==mac:
                del self.timestampCache[(tsMac,tsAppName)]
        
        # delete mote from firewall
        for netname in self.getNetnames():
            rules = self.getFirewallRules(netname)
            if rules:
                for rule in rules:
                    if mac==rule[0]:
                        self.deleteFirewallRule(netname,*rule)
        
        # delete mote from dataflows
        for netname in self.getNetnames():
            flows = self.getNetworkDataFlows(netname)
            if flows:
                for dataflow in flows:
                    if mac==dataflow[0]:
                        self.deleteDataflow(netname,*dataflow)
        
        # delete mote from privileges
        users = self.getUserNames()
        if users:
            for u in users:
                p = self.getUserPrivileges(u)
                if p and ('motes' in p) and (mac in p['motes']):
                    self.delete(['users',u,'privileges','motes',mac])
        
        # delete mote from networks (motes and paths)
        netnames = self.getNetnames()
        if netnames:
            for netname in netnames:
                if mac in self.getNetworkMotes(netname):
                    self.deleteNetworkMote(netname,mac)
        
        # delete mote from motes
        self.delete(['motes',mac])
    
    #--- helpers
    
    ##
    # \}
    #
    
    #========== networks
    
    ##
    # \defgroup networks networks
    # \ingroup DustLinkData
    # \{
    #
    
    #--- defines
    
    #--- admin
    
    def _networks_putDefaultData(self):
        self.put(['networks'],None)
    
    def _networks_validateDataIntegrity(self):
        self.get(['networks'])
    
    #--- public
    
    @synchronized
    def getNetnames(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the names of the networks this user has read privileges
               to. 
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        # get all the netnames (as ADMIN)
        all_netnames = self.get(['networks'], createCopy=False)
        
        # return if none
        if not all_netnames:
            return []
        
        # format as a (sorted) list
        all_netnames = all_netnames.keys()
        all_netnames.sort()
        
        if self._isPriviledged(username):
            return all_netnames
        
        # remove the ones this user is not authorized to GET, PUT and DELETE
        returnVal = []
        for netname in all_netnames:
            # canGet
            try:
                self.authorize(username,['networks',netname],self.ACTION_GET)
            except:
                canGet = False
            else:
                canGet = True
            # canPut
            try:
                self.authorize(username,['networks',netname],self.ACTION_PUT)
            except:
                canPut = False
            else:
                canPut = True
            # canDelete
            try:
                self.authorize(username,['networks',netname],self.ACTION_DELETE)
            except:
                canDelete = False
            else:
                canDelete = True
            
            if canGet or canPut or canDelete:
                returnVal.append(netname)
        
        return returnVal
    
    @synchronized
    def addNetwork(self,netname,username=USER_SYSTEM):
        '''
        \brief Add a network to the system.
        
        \param netname   The name of the network to add.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        
        if netname in self.getNetnames():
            raise ValueError("network {0} already exists".format(netname))
        
        # add to network
        self.put(['networks',netname,'info'],None,username)
        self.put(['networks',netname,'motes'],None,username)
        self.put(['networks',netname,'paths'],None,username)
        
        # as a side-effect, add to other resources (as ADMIN)
        self._addTestResultsNetname(netname)     # testResults
        self._addFirewallNetname(netname)        # firewall
        self._addDataflowsNetname(netname)       # dataflows
    
    @synchronized
    def getNetworkInfo(self,netname,username=USER_SYSTEM):
        '''
        \brief Retrieve the info about a given network.
        
        \param netname   The name of the network of interest.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        
        \returns A dictionnary of value=key elements.
        '''
        if netname not in self.getNetnames():
            raise ValueError("unknown network {0}".format(netname))
        
        return self.get(['networks',netname,'info'],username)
    
    @synchronized
    def setNetworkInfo(self,netname,infoKey,infoVal,username=USER_SYSTEM):
        '''
        \brief Set an info value of a network.
        
        \param netname   The name of the network of interest.
        \param infoKey   The name of the information element.
        \param infoVal   The value of the information element.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if netname not in self.getNetnames():
            raise ValueError("unknown network {0}".format(netname))
        
        self.put(['networks',netname,'info',infoKey],infoVal,username)
    
    @synchronized
    def getNetworkMotes(self,netname,username=USER_SYSTEM):
        '''
        \brief Retrieve the list of motes participating in a network.
        
        \param netname   The name of the network of interest.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        
        \returns A list of MAC addresses.
        '''
        if netname not in self.getNetnames():
            raise ValueError("unknown network {0}".format(netname))
        
        net_motes = self.get(['networks',netname,'motes'],username)
        if not net_motes:
            return []
        else:
            return net_motes.keys()
    
    @synchronized
    def addNetworkMote(self,netname,mac,username=USER_SYSTEM):
        '''
        \brief Add a mac to a network.
        
        \param netname   The name of the network.
        \param mac       The MAC address of the mote to add.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        
        # authorize
        self.authorize(username,['networks',netname],self.ACTION_PUT)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        if self._doValidation(username):
            if netname not in self.getNetnames():
                raise ValueError("unknown network {0}".format(netname))
            if mac not in self.getMoteMacs():
                raise ValueError("unknown mac {0}".format(mac))
        
        if mac in self.getNetworkMotes(netname):
            output  = []
            output += ["mote "]
            output += [str(mac)]
            output += [" already in network "]
            output += [netname]
            raise ValueError(''.join(output))
        
        self.put(['networks',netname,'motes',mac],None,username)
    
    @synchronized
    def deleteNetworkMote(self,netname,mac,username=USER_SYSTEM):
        '''
        \brief Delete a mac from a network.
        
        \note Calling this command will have the following side-effects:
               - you will loose all path data for path associated with that
                 mote.
        \note Calling this command does NOT affect the motes. It is OK to have
              mote not associated with any network.
        
        \param netname   The name of the network.
        \param mac       The MAC address of the mote to delete.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        self._validateFormatMac(mac)
        
        # authorize
        self.authorize(username,['networks',netname],self.ACTION_DELETE)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        if netname not in self.getNetnames():
            raise ValueError("unknown network {0}".format(netname))
        if mac not in self.getNetworkMotes(netname):
            raise ValueError("mac {0} not in network {1}".format(mac,netname))
        
        # remove from paths
        for p in self.getNetworkPaths(netname):
            if mac in p:
                self.deletePath(netname,*p)
        # remove from motes
        self.delete(['networks',netname,'motes',mac],username)
    
    @synchronized
    def getNetworkPaths(self,netname,username=USER_SYSTEM):
        '''
        \brief Retrieve the list of (directed) paths in the network.
        
        \param netname   The name of the network of interest.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        
        \returns A list of tuples of the form (fromMAC,toMAC).
        '''
        if self._doValidation(username):
            if netname not in self.getNetnames():
                raise ValueError("unknown network {0}".format(netname))
        
        net_paths = self.get(['networks',netname,'paths'],username, createCopy=False)
        if not net_paths:
            return []
        else:
            return net_paths.keys()
    
    @synchronized
    def addPath(self,netname,fromMAC,toMAC,username=USER_SYSTEM):
        '''
        \brief Add a path to the network.
        
        \param netname   The name of the network of interest.
        \param fromMAC   The MAC address of source mote of the path.
        \param toMAC     The MAC address of destination mote of the path.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        
        # authorize
        self.authorize(username,['networks',netname],self.ACTION_PUT)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        if self._doValidation(username):
            if netname not in self.getNetnames():
                raise ValueError("unknown network {0}".format(netname))
            self._validateFormatMac(fromMAC)
            if fromMAC not in self.getNetworkMotes(netname):
                raise ValueError("fromMAC {0} not in network {1}".format(fromMAC,netname))
            self._validateFormatMac(toMAC)
            if toMAC not in self.getNetworkMotes(netname):
                raise ValueError("toMAC {0} not in network {1}".format(toMAC,netname))
            if (fromMAC,toMAC) in self.getNetworkPaths(netname):
                raise ValueError("path ({0},{1}) already in network {2}".format(fromMAC,toMAC,netname))
        
        self.put(['networks',netname,'paths',(fromMAC,toMAC),'info'],None)
        self.put(['networks',netname,'paths',(fromMAC,toMAC),'links'],None)
        self.put(['networks',netname,'paths',(fromMAC,toMAC),'actions'],None)
    
    @synchronized
    def getPathInfo(self,netname,fromMAC,toMAC,username=USER_SYSTEM):
        '''
        \brief Retrieve the information associated with a given path.
        
        \param netname   The name of the network of interest.
        \param fromMAC   The MAC address of source mote of the path.
        \param toMAC     The MAC address of destination mote of the path.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        
        \returns A list of tuples of the form (fromMAC,toMAC).
        '''
        
        if self._doValidation(username):
            if netname not in self.getNetnames():
                raise ValueError("unknown network {0}".format(netname))
            self._validateFormatMac(fromMAC)
            if fromMAC not in self.getNetworkMotes(netname,username):
                raise ValueError("fromMAC {0} not in network {1}".format(fromMAC,netname))
            self._validateFormatMac(toMAC)
            if toMAC not in self.getNetworkMotes(netname,username):
                raise ValueError("toMAC {0} not in network {1}".format(toMAC,netname))
            if (fromMAC,toMAC) not in self.getNetworkPaths(netname,username):
                raise ValueError("path ({0},{1}) not in network {2}".format(fromMAC,toMAC,netname))
        
        return self.get(['networks',netname,'paths',(fromMAC,toMAC),'info'],username)
    
    @synchronized
    def setPathInfo(self,netname,fromMAC,toMAC,infoKey,infoVal,username=USER_SYSTEM):
        '''
        \brief Retrieve the information associated with a given path.
        
        \param netname   The name of the network of interest.
        \param fromMAC   The MAC address of source mote of the path.
        \param toMAC     The MAC address of destination mote of the path.
        \param infoKey   The info key to set.
        \param infoVal   The value to set the info key to.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        
        \returns A list of tuples of the form (fromMAC,toMAC).
        '''
        
        # authorize
        self.authorize(username,['networks',netname],self.ACTION_PUT)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        if self._doValidation(username):
            if netname not in self.getNetnames():
                raise ValueError("unknown network {0}".format(netname))
            self._validateFormatMac(fromMAC)
            if fromMAC not in self.getNetworkMotes(netname,):
                raise ValueError("fromMAC {0} not in network {1}".format(fromMAC,netname))
            self._validateFormatMac(toMAC)
            if toMAC not in self.getNetworkMotes(netname):
                raise ValueError("toMAC {0} not in network {1}".format(toMAC,netname))
            if (fromMAC,toMAC) not in self.getNetworkPaths(netname):
                raise ValueError("path ({0},{1}) not in network {2}".format(fromMAC,toMAC,netname))
        
        self.put(['networks',netname,'paths',(fromMAC,toMAC),'info',infoKey],infoVal)
    
    @synchronized
    def deletePath(self,netname,fromMAC,toMAC,username=USER_SYSTEM):
        '''
        \brief Delete a path from the network.
        
        \param netname   The name of the network of interest.
        \param fromMAC   The MAC address of source mote of the path.
        \param toMAC     The MAC address of destination mote of the path.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        
        # authorize
        self.authorize(username,['networks',netname],self.ACTION_DELETE)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        if self._doValidation(username):
            if netname not in self.getNetnames():
                raise ValueError("unknown network {0}".format(netname))
            self._validateFormatMac(fromMAC)
            if fromMAC not in self.getNetworkMotes(netname):
                raise ValueError("fromMAC {0} not in network {1}".format(fromMAC,netname))
            self._validateFormatMac(toMAC)
            if toMAC not in self.getNetworkMotes(netname):
                raise ValueError("toMAC {0} not in network {1}".format(toMAC,netname))
            if (fromMAC,toMAC) not in self.getNetworkPaths(netname):
                raise ValueError("path ({0},{1}) not in network {2}".format(fromMAC,toMAC,netname))
        
        self.delete(['networks',netname,'paths',(fromMAC,toMAC)])
    
    @synchronized
    def deleteNetwork(self,netname,username=USER_SYSTEM):
        '''
        \brief Delete a network from the system.
        
        \note Calling this command will have the following side-effects:
            - you will loose all path data associated with that network.
            - all users will loose their privileges to this network.
            - the 'info' attached to each of the motes in the network is deleted.
        
        \note Calling this command does NOT affect the motes. It is OK to have
              mote not associated with any network.
        
        \param netname   The name of the network to delete.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        
        # authorize
        self.authorize(username,['networks',netname],self.ACTION_DELETE)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        if netname not in self.getNetnames():
            raise ValueError("unknown network {0}".format(netname))
        
        # delete info section of all motes in the network
        for moteMac in self.getNetworkMotes(netname):
            self.deleteMoteInfo(moteMac)
        
        # delete network from privileges
        users = self.getUserNames()
        if users:
            for u in users:
                p = self.getUserPrivileges(u)
                if p and ('networks' in p) and (netname in p['networks']):
                    self.delete(['users',u,'privileges','networks',netname])
        
        # delete network from firewall
        if netname in self._getFirewallNetnames():
            self.delete(['firewall',netname])
        
        # delete network from testResults
        if netname in self._getTestResultsNetnames():
            self.delete(['testResults',netname])
        
        # delete network from dataFlows
        if netname in self._getDataflowsNetnames():
            self.delete(['dataflows',netname])
        
        # delete network from networks
        self.delete(['networks',netname])
    
    #--- helpers
    
    ##
    # \}
    #
    
    #========== testResults
    
    ##
    # \defgroup testResults testResults
    # \ingroup DustLinkData
    # \{
    #
    
    #--- defines
    
    TEST_OUTCOME_PASS   = 'PASS'
    TEST_OUTCOME_FAIL   = 'FAIL'
    TEST_OUTCOME_NOTRUN = 'NOTRUN'
    TEST_OUTCOME_ALL    = [TEST_OUTCOME_PASS,
                           TEST_OUTCOME_FAIL,
                           TEST_OUTCOME_NOTRUN]
    TEST_HISTORY_LENGTH = 5
    
    TESTPERIOD_DEFAULT  = 60*60
    
    #--- admin
    
    def _testResults_putDefaultData(self):
        self.put(['testResults'],None)
    
    def _testResults_validateDataIntegrity(self):
        self.get(['testResults'])
    
    #--- public
    
    @synchronized
    def setTestPeriod(self,netname,testPeriod,username=USER_SYSTEM):
        '''
        \brief Set the test period for a particular network.
        
        \param netname   The network name.
        \param testPeriod The new test period, in seconds.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        
        if netname not in self.getNetnames(username):
            raise ValueError("unknown network {0}".format(netname))
        if type(testPeriod)!=int:
            raise ValueError("testPeriod needs to be an int, {0} is {1}".format(testPeriod,type(testPeriod)))
            
        return self.put(['testResults',netname,'info','testperiod'],
                        testPeriod,
                        username=username)
    
    @synchronized
    def getTestPeriod(self,netname,username=USER_SYSTEM):
        '''
        \brief Retrieve the test period for a particular network.
        
        \param netname   The network name.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        
        \return The test period for that network, in seconds.
        '''
        
        if netname not in self.getNetnames(username):
            raise ValueError("unknown network {0}".format(netname))
        
        return self.get(['testResults',netname,'info','testperiod'],
                        username=username)
    
    @synchronized
    def addResult(self,netname,testName,testDesc,outcome,timestamp=None,description='',username=USER_SYSTEM):
        '''
        \brief Add a test result for a given network.
        
        \param netname   The name of the network of interest.
        \param testName  The name of the test that just ran.
        \param outcome   The outcome of the text. Needs to be one of
                         TEST_OUTCOME_ALL.
        \param timestamp The timestamp of when the test ran, or now when 
                         ommited.
        \param description An optional description of the test and/or its
                         outcome.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if not isinstance(testName,str):
            raise ValueError("testName should be a string, {0} is {1}".format(testName,type(testName)))
        if outcome not in self.TEST_OUTCOME_ALL:
            raise ValueError("invalid outcome {0}".format(outcome))
        
        # authorize
        self.authorize(username,['testResults',netname],self.ACTION_PUT)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        if timestamp==None:
            timestamp=time.time()
        
        if netname not in self._getTestResultsNetnames():
            raise ValueError("netname {0} not in testResults".format(netname))
        
        # add testName if needed
        try:
            self.checkExists(['testResults',netname,'results',testName])
        except DataVaultException.NotFound:
            
            # 'description'
            self.put(['testResults',netname,'results',testName,'description'],  None,username)
            
            # 'last'
            self.put(['testResults',netname,'results',testName,'last','timestamp'],  None,username)
            self.put(['testResults',netname,'results',testName,'last','outcome'],    None,username)
            self.put(['testResults',netname,'results',testName,'last','description'],None,username)
            
            # 'lastSuccess' and 'lastFailure'
            for category in ['lastSuccess','lastFailure']:
                self.put(['testResults',netname,'results',testName,category,'timestamp'],  None,username)
                self.put(['testResults',netname,'results',testName,category,'description'],None,username)
            
            # 'history'
            self.put(['testResults',netname,'results',testName,'history'],[],username)
        
        # record description
        self.put(['testResults',netname,'results',testName,'description'],   testDesc)
        
        # record last
        self.put(['testResults',netname,'results',testName,'last','timestamp'],   timestamp)
        self.put(['testResults',netname,'results',testName,'last','outcome'],     outcome)
        self.put(['testResults',netname,'results',testName,'last','description'], description)
        
        # update 'lastSuccess' or 'lastFailure'
        category  = None
        if outcome==self.TEST_OUTCOME_PASS:
            category = 'lastSuccess'
        if outcome==self.TEST_OUTCOME_FAIL:
            category = 'lastFailure'
        if category:
            self.put(['testResults',netname,'results',testName,category,'timestamp'],   timestamp)
            self.put(['testResults',netname,'results',testName,category,'description'], description)
        
        # record history
        history    = self.get(['testResults',netname,'results',testName,'history'])
        history   += [outcome]
        while len(history)>self.TEST_HISTORY_LENGTH:
            history.pop(0)
        self.put(['testResults',netname,'results',testName,'history'],history)
    
    @synchronized
    def getResults(self,netname,username=USER_SYSTEM):
        '''
        \brief Get the latest results.
        
        \param netname   The name of the network of interest.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if not isinstance(netname,str):
            raise ValueError("netname should be a string, {0} is {1}".format(netname,type(netname)))
        
        # authorize
        self.authorize(username,['testResults',netname],self.ACTION_GET)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        if netname not in self._getTestResultsNetnames():
            raise ValueError("netname {0} not in testResults".format(netname))
        
        return self.get(['testResults',netname,'results'],username=username)
    
    #--- private
    
    def _addTestResultsNetname(self,netname,username=USER_SYSTEM):
        '''
        \brief Add a new network to the test results.
        
        \param netname   The name of the new network.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if netname not in self.getNetnames(username):
            raise ValueError("unknown network {0}".format(netname))
        if netname in self._getTestResultsNetnames(username):
            raise ValueError("netname {0} already in testResults".format(netname))
        
        self.put(['testResults',netname,'info','testperiod'],self.TESTPERIOD_DEFAULT,username)
        self.put(['testResults',netname,'results'],None,username)
    
    def _getTestResultsNetnames(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the list of networks for which there are testResults.
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        net_names = self.get(['testResults'],username=username)
        if not net_names:
            return []
        else:
            return net_names.keys()
    
    #--- helpers
    
    ##
    # \}
    #
    
    #========== firewall
    
    ##
    # \defgroup firewall firewall
    # \ingroup DustLinkData
    # \{
    #
    
    #--- defines
    
    DATATYPE_ICMPv6          = 'firewall dataType ICMPv6'
    DATATYPE_UDP             = APP_TRANSPORT_UDP
    DATATYPE_OAP             = APP_TRANSPORT_OAP
    DATATYPE_COAP            = APP_TRANSPORT_COAP
    DATATYPE_MOTERUNNER      = APP_TRANSPORT_MOTERUNNER
    DATATYPE_ALL             = [DATATYPE_ICMPv6,
                                DATATYPE_UDP,
                                DATATYPE_OAP,
                                DATATYPE_COAP,
                                DATATYPE_MOTERUNNER]
    
    DATA_DIRECTION_INET2MESH = 'toMesh' 
    DATA_DIRECTION_MESH2INET = 'toInternet'
    DATA_DIRECTION_ALL       = [DATA_DIRECTION_INET2MESH,
                                DATA_DIRECTION_MESH2INET]
    
    FIREWALL_RULE_ACCEPT     = 'accept'
    FIREWALL_RULE_DENY       = 'deny'
    FIREWALL_RULE_ALL        = [FIREWALL_RULE_ACCEPT,
                                FIREWALL_RULE_DENY]
    
    FIREWALL_RULE_DEFAULT    = FIREWALL_RULE_DENY
    
    #--- admin
    
    def _firewall_putDefaultData(self):
        self.put(['firewall'],None)
    
    def _firewall_validateDataIntegrity(self):
        self.get(['firewall'])
    
    #--- public
    
    @synchronized
    def getDefaultFirewallRule(self,netname,username=USER_SYSTEM):
        '''
        \brief Retrieve the default firewall rules associated with a network.
        
        \param netname   The name of the network of interest.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if netname not in self._getFirewallNetnames():
            raise ValueError("netname {0} not in firewall".format(netname))
        
        return self.get(['firewall',netname,'info','defautRule'],username)
    
    @synchronized
    def setDefaultFirewallRule(self,netname,defaultRule,username=USER_SYSTEM):
        '''
        \brief Set the default firewall rule associated with a network.
        
        \param netname   The name of the network of interest.
        \param defaultRule The new default rule for this network.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if netname not in self._getFirewallNetnames():
            raise ValueError("netname {0} not in firewall".format(netname))
        if defaultRule not in self.FIREWALL_RULE_ALL:
            raise ValueError("invalid default firewall rule {0}".format(defaultRule))
        
        self.put(['firewall',netname,'info','defautRule'],defaultRule,username)
    
    @synchronized
    def getFirewallRules(self,netname,username=USER_SYSTEM):
        '''
        \brief Retrieve the firewall rules associated with a network.
        
        \param netname   The name of the network of interest.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        if netname not in self._getFirewallNetnames():
            raise ValueError("netname {0} not in firewall".format(netname))
        
        return self.get(['firewall',netname,'rules'],username)
    
    @synchronized
    def addFirewallRule(self,netname,moteMAC,hostIP,direction,dataType,resource,rule,username=USER_SYSTEM):
        '''
        \brief Add a new firewall rule to this network.
        
        \param netname   The name of the network of interest.
        \param moteMAC   MAC address of a mote in the mesh. '*' is the
                         wildcard and can replace any of the 8 bytes in the
                         tuple representing the MAC address.
        \param hostIP    IPv6 address of a host on the Internet. '*' is the
                         wildcard and can replace any of the 16 bytes in the
                         tuple representing the IPv6 address.
        \param direction The direction of the data. Possible values listed in
                         DATA_DIRECTION_ALL.
        \param dataType  Type of data. Possible values listed in
                         DATATYPE_ALL.
        \param resource  The resource on the mote this rule applies to.
        \param rule      Rule to apply. Possible values listed in
                         FIREWALL_RULE_ALL.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        self._firewall_validateParamsFormat(moteMAC,hostIP,direction,dataType,resource,rule)
        if netname not in self._getFirewallNetnames():
            raise ValueError("netname {0} not in firewall".format(netname))
        if moteMAC not in self.getNetworkMotes(netname):
            raise ValueError("mote {0} not in network {1}".format(moteMAC,netname))
        
        self.put(['firewall',netname,'rules',(moteMAC,hostIP,direction,dataType,resource)],rule,username)
    
    @synchronized
    def deleteFirewallRule(self,netname,moteMAC,hostIP,direction,dataType,resource,username=USER_SYSTEM):
        '''
        \brief Delete an existing firewall rule from this network.
        
        \param netname   The name of the network of interest.
        \param moteMAC   MAC address of a mote in the mesh. '*' is the
                         wildcard and can replace any of the 8 bytes in the
                         tuple representing the MAC address.
        \param hostIP    IPv6 address of a host on the Internet. '*' is the
                         wildcard and can replace any of the 16 bytes in the
                         tuple representing the IPv6 address.
        \param direction The direction of the data.
        \param dataType  Type of data.
        \param resource  The resource on the mote this rule applies to.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        self._firewall_validateParamsFormat(moteMAC,hostIP,direction,dataType,resource)
        if netname not in self._getFirewallNetnames():
            raise ValueError("netname {0} not in firewall".format(netname))
        if moteMAC not in self.getNetworkMotes(netname):
            raise ValueError("mote {0} not in network {1}".format(moteMAC,netname))
        if (moteMAC,hostIP,direction,dataType,resource) not in self.getFirewallRules(netname):
            raise ValueError("rule {0} not in rules for network {1}".format(
                        (moteMAC,hostIP,direction,dataType,resource),
                        netname
                    ))
        
        self.delete(['firewall',netname,'rules',(moteMAC,hostIP,direction,dataType,resource)],username)
    
    #--- private
    
    def _addFirewallNetname(self,netname,username=USER_SYSTEM):
        if netname not in self.getNetnames(username):
            raise ValueError("unknown network {0}".format(netname))
        if netname in self._getFirewallNetnames(username):
            raise ValueError("netname {0} already in firewall".format(netname))
        
        self.put(['firewall',netname,'info','defautRule'],self.FIREWALL_RULE_DEFAULT,username)
        self.put(['firewall',netname,'rules'],None,username)
    
    def _getFirewallNetnames(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the list of networks for which there are firewall rules.
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        net_names = self.get(['firewall'],username=username)
        if not net_names:
            return []
        else:
            return net_names.keys()
    
    #--- helpers
    
    def _firewall_validateParamsFormat(self,moteMAC,hostIP,direction,dataType,resource,rule=None):
        # moteMAC
        if not isinstance(moteMAC,(tuple,list)):
            raise ValueError("MAC should be a tuple, {0} is a {1}".format(
                            moteMAC,
                            type(moteMAC)
                        )
                    )
        if len(moteMAC)!=8:
            raise ValueError("MAC should be of length 8, {0} is of length {1}".format(
                            moteMAC,
                            len(moteMAC)
                        )
                    )
        for b in moteMAC:
            if (not isinstance(b,int)) and b!='*':
                ValueError("MAC should contain only ints and '*', not {0}".format(
                            b,
                        )
                    )
        # hostIP
        if not isinstance(hostIP,(tuple,list)):
            raise ValueError("hostIP should be a tuple, {0} is a {1}".format(
                            hostIP,
                            type(hostIP)
                        )
                    )
        if len(hostIP)!=16:
            raise ValueError("hostIP should be of length 16, {0} is of length {1}".format(
                            hostIP,
                            len(hostIP)
                        )
                    )
        for b in hostIP:
            if (not isinstance(b,int)) and b!='*':
                raise ValueError("hostIP should contain only ints and '*', not {0}".format(
                            b,
                        )
                    )
        # direction
        if direction not in self.DATA_DIRECTION_ALL:
            raise ValueError("invalid direction {0}".format(direction))
        # dataType
        if dataType not in self.DATATYPE_ALL:
            raise ValueError("invalid dataType {0}".format(dataType))
        # resource
        self._validateResource(dataType,resource)
        # rule
        if rule:
            if rule not in self.FIREWALL_RULE_ALL:
                raise ValueError("invalid rule {0}".format(rule))
    
    ##
    # \}
    #
    
    #========== dataflows
    
    ##
    # \defgroup dataflows dataflows
    # \ingroup DustLinkData
    # \{
    #
    
    #--- defines
    
    MAXNUMDATAFLOWS               = 100
    MAXNUMHISTORYACCEPT           = 10
    MAXNUMHISTORYDENY             = 10
    MAXNUMHISTORYERROR            = 10
    
    LBR_OUTCOME_ACCEPT            = FIREWALL_RULE_ACCEPT
    LBR_OUTCOME_DENY              = FIREWALL_RULE_DENY
    LBR_OUTCOME_COMPRESSION_ERROR = 'outcome compression error'
    LBR_OUTCOME_ALL               = [LBR_OUTCOME_ACCEPT,
                                     LBR_OUTCOME_DENY,
                                     LBR_OUTCOME_COMPRESSION_ERROR]
    
    #--- admin
    
    def _dataflows_putDefaultData(self):
        self.put(['dataflows'],None)
    
    def _dataflows_validateDataIntegrity(self):
        self.get(['dataflows'])
    
    #--- public
    
    @synchronized
    def getNetworkDataFlows(self,netname,username=USER_SYSTEM):
        if netname not in self._getDataflowsNetnames():
            raise ValueError("netname {0} not in dataflows".format(netname))
        
        all_flows = self.get(['dataflows',netname,'flows'],username=username)
        if not all_flows:
            return []
        else:
            return all_flows.keys()
    
    @synchronized
    def getNetworkDataFlowDetails(self,netname,flow,username=USER_SYSTEM):
        if netname not in self._getDataflowsNetnames():
            raise ValueError("netname {0} not in dataflows".format(netname))
        if flow not in self.getNetworkDataFlows(netname,username):
            raise ValueError("flow {0} not in dataflows for network {1}".format(flow,netname))
        
        return self.get(['dataflows',netname,'flows',flow],username=username)
    
    @synchronized
    def indicateDataFlow(self,netname,mote,host,direction,outcome,dataType=None,resource=None,rawBytes=None,timestamp=None,username=USER_SYSTEM):
    
        # authorize
        self.authorize(username,['dataflows',netname],self.ACTION_PUT)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        if netname not in self._getDataflowsNetnames():
            raise ValueError("netname {0} not in dataflows".format(netname))
        self._validateFormatMac(mote)
        if mote not in self.getNetworkMotes(netname):
            raise ValueError("mote {0} not in network {1}".format(mote,netname))
        self._validateFormatIp(host)
        if direction not in self.DATA_DIRECTION_ALL:
            raise ValueError("invalid direction {0}".format(direction))
        if outcome not in self.LBR_OUTCOME_ALL:
            raise ValueError("invalid outcome {0}".format(outcome))
        if dataType and (dataType not in self.DATATYPE_ALL):
            raise ValueError("invalid dataType {0}".format(dataType))
        if dataType and resource:
            self._validateResource(dataType,resource)
        if rawBytes:
            if not isinstance(rawBytes,(tuple,list)):
                raise ValueError("rawBytes should be tuple or list, now {0}".format(rawBytes))
            for b in rawBytes:
                if not isinstance(b,int):
                    raise ValueError("rawBytes should be list of int, can not contain {0}".format(b))
        if timestamp:
            if not isinstance(timestamp,(int,float)):
                raise ValueError("timestamp should be number, now {0}".format(timestamp))
        
        if timestamp==None:
            timestamp=time.time()
        
        # give flow an alias
        flow = (mote,host,direction)
        
        # create dataflow, if needed
        if flow not in self.getNetworkDataFlows(netname):
            self.put(['dataflows',netname,'flows',flow,'counters','accept'],0)
            self.put(['dataflows',netname,'flows',flow,'counters','deny'],  0)
            self.put(['dataflows',netname,'flows',flow,'counters','error'], 0)
            self.put(['dataflows',netname,'flows',flow,'history', 'accept'],None)
            self.put(['dataflows',netname,'flows',flow,'history', 'deny'],  None)
            self.put(['dataflows',netname,'flows',flow,'history', 'error'], None)
        
        # give outcome an alias
        if   outcome in [self.LBR_OUTCOME_ACCEPT]:
            outcomeAlias = 'accept'
        elif outcome in [self.LBR_OUTCOME_DENY]:
            outcomeAlias = 'deny'
        elif outcome in [self.LBR_OUTCOME_COMPRESSION_ERROR]:
            outcomeAlias = 'error'
        else:
            raise SystemError('unexpected outcome {0}'.format(outcome))
        
        # update stats about this dataflow
        self.put(['dataflows',netname,'flows',flow,'counters',outcomeAlias],
             self.get(['dataflows',netname,'flows',flow,'counters',outcomeAlias])+1)
        
        # remove old data flow, if needed
        if self.getNetworkDataFlowDetails(netname,flow)['history'][outcomeAlias]:
            while len(self.getNetworkDataFlowDetails(netname,flow)['history'][outcomeAlias])> \
                    self.get(['dataflows',netname,'info','maxNumHistory',outcomeAlias])-1:
                self._dataflows_deleteOldestHistory(netname,flow,outcomeAlias)
        
        # store this flow history
        self.put(['dataflows',netname,'flows',flow,'history',outcomeAlias,timestamp,'dataType'],
                 dataType)
        self.put(['dataflows',netname,'flows',flow,'history',outcomeAlias,timestamp,'resource'],
                 resource)
        self.put(['dataflows',netname,'flows',flow,'history',outcomeAlias,timestamp,'rawBytes'],
                 rawBytes)
    
    @synchronized
    def deleteDataflow(self,netname,mote,host,direction,username=USER_SYSTEM):
        '''
        \brief Delete a specific data flow.
        
        \param netname   The network to delete this flow from.
        \param mote      The mote of the dataflow to remove.
        \param host      The host of the dataflow to remove.
        \param direction The direction of the dataflow to remove.
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        # validate format
        self._validateFormatMac(mote)
        self._validateFormatIp(host)
        
        # authorize
        self.authorize(username,['dataflows',netname],self.ACTION_DELETE)
        
        # if you get here, authorization is granted, do the rest as ADMIN
        
        # validate parameters
        if netname not in self.getNetnames(username):
            raise ValueError("unknown network {0}".format(netname))
        
        flowToRemove = (mote,host,direction)
        
        if flowToRemove not in self.getNetworkDataFlows(netname):
            raise ValueError("no dataflow {0} for network {1}".format(flowToRemove,netname))
        
        # delete flow
        self.delete(['dataflows',netname,'flows',flowToRemove],username=username)
    
    #--- private
    
    def _addDataflowsNetname(self,netname,username=USER_SYSTEM):
        if netname not in self.getNetnames(username):
            raise ValueError("unknown network {0}".format(netname))
        if netname in self._getDataflowsNetnames(username):
            raise ValueError("netname {0} already in dataflows".format(netname))
        
        self.put(['dataflows',netname,'info','maxNumFlows'],           self.MAXNUMDATAFLOWS,username)
        self.put(['dataflows',netname,'info','maxNumHistory','accept'],self.MAXNUMHISTORYACCEPT,username)
        self.put(['dataflows',netname,'info','maxNumHistory','deny'],  self.MAXNUMHISTORYDENY,username)
        self.put(['dataflows',netname,'info','maxNumHistory','error'], self.MAXNUMHISTORYERROR,username)
        self.put(['dataflows',netname,'flows'],                        None,username)
    
    def _getDataflowsNetnames(self,username=USER_SYSTEM):
        '''
        \brief Retrieve the list of networks for which there are dataflow entries.
        
        \param username  The username of the requestor. If you don't
                         specify this parameter, the admin user will be assumed.
        '''
        net_names = self.get(['dataflows'],username=username)
        if not net_names:
            return []
        else:
            return net_names.keys()
    
    #--- helpers
    
    def _dataflows_deleteOldestHistory(self,netname,flow,outcomeAlias):
        # find oldest entry
        timestamps = self.getNetworkDataFlowDetails(netname,flow)['history'][outcomeAlias].keys()
        timestamps.sort()
        
        # delete that entry
        self.delete(['dataflows',netname,'flows',flow,'history',outcomeAlias,timestamps[0]])
    
    ##
    # \}
    #
    
    DEMO_MODE_APPS     = {
        'OAPTemperature': {
            'description':       "This application is built into the default SmartMesh IP mote firmware and reports temperature periodically.",
            'transport':         (APP_TRANSPORT_OAP, (5,)),
            'fromMoteFields':    ('>h', ['temperature']),
            'toMoteFields':      ('>l', ['rate']),
        },
        'OAPLED': {
            'description':       "This application is built into the default SmartMesh IP mote firmware and turns an LED on/off.",
            'transport':         (APP_TRANSPORT_OAP, (2,3)),
            'toMoteFields':      ('>b', ['status']),
        },
        'DC2126A': {
            'description':       "Received and parses data from a DC2126A board.",
            'transport':         (APP_TRANSPORT_UDP, 60102),
            'fromMoteFields':    ('>HLH', ['cmdId','temperature','adcValue']),
        },
        'LIS331': {
            'description':       "Receives and parses data from a mote running the LIS331 application.",
            'transport':         (APP_TRANSPORT_UDP, 60103),
            'fromMoteFields':    ('>hhh', ['x','y','z']),
        },
    }
    
    ##
    # \defgroup utils utils
    # \ingroup DustLinkData
    # \{
    #
    
    #----- mac
    
    @classmethod
    def stringToMac(self,macString,username=USER_SYSTEM):
        
        if not macString:
            return ''
        
        mac = tuple([int(e,16) for e in macString.split('-')])
        
        if self._doValidation(username):
            if not len(mac)==8:
                raise ValueError('mac should contain 8 elements, {0} contains {1}'.format(
                                mac,
                                len(mac)
                            )
                        )
            for m in mac:
                if not m<256:
                    raise ValueError('mac elements should be <256, {0} is not'.format(
                                    m
                                )
                            )
        
        return mac
    
    @classmethod
    def macToString(self,mac,username=USER_SYSTEM):
        
        if self._doValidation(username):
            if not isinstance(mac,tuple):
                raise ValueError('mac should be a tuple, {0} is not'.format(
                                mac,
                            )
                        )
            if not len(mac)==8:
                raise ValueError('mac should contain 8 elements, {0} contains {1}'.format(
                                mac,
                                len(mac)
                            )
                        )
            for m in mac:
                if not m<256:
                    raise ValueError('mac elements should be <256, {0} is not'.format(
                                    m
                                )
                            )
        
        return '-'.join(["%.2x"%m for m in mac])
    
    @classmethod
    def macToShortString(self,mac):
        '''
        if not isinstance(mac,tuple):
            raise ValueError('mac should be a tuple, {0} is not'.format(
                            mac,
                        )
                    )
        if not len(mac)==8:
            raise ValueError('mac should contain 8 elements, {0} contains {1}'.format(
                            mac,
                            len(mac)
                        )
                    )
        for m in mac:
            if not isinstance(m,int):
                raise ValueError('mac elements should int, {0} is not'.format(
                                m
                            )
                        )
        for m in mac:
            if not m<256:
                raise ValueError('mac elements should be <256, {0} is not'.format(
                                m
                            )
                        )
        '''
        
        return '-'.join(["%.2x"%m for m in mac[6:]])
    
    #----- ip
    
    @classmethod
    def stringToIp(self,ipString):
        if not len(ipString)==32:
            raise ValueError('IP should contain 16 characters, {0} contains {1}'.format(
                            ipString,
                            len(ipString)
                        )
                    )
        
        ip = []
        for i in range(16):
            ip.append(int(ipString[i*2:i*2+2],16))
        
        assert len(ip)==16
        
        for b in ip:
            assert b<256
        
        return tuple(ip)
    
    @classmethod
    def ipToString(self,ip):
        if not isinstance(ip,tuple):
            raise ValueError('ip should be a tuple, {0} is not'.format(
                            ip,
                        )
                    )
        if not len(ip)==16:
            raise ValueError('ip should contain 16 elements, {0} contains {1}'.format(
                            ip,
                            len(ip)
                        )
                    )
        for b in ip:
            if not isinstance(b,int):
                raise ValueError('ip elements should int, {0} is not'.format(
                                b
                            )
                        )
        for b in ip:
            if not b<256:
                raise ValueError('ip elements should be <256, {0} is not'.format(
                                b
                            )
                        )
        
        return ''.join(["%.2x"%b for b in ip])
    
    #----- timestamp
    
    @classmethod
    def timestampToString(self,t):
        return time.strftime("%A, %d %B %Y %H:%M:%S", time.localtime(t))
    
    @classmethod
    def timestampToStringShort(self,t):
        return time.strftime("%m/%d/%Y %H:%M:%S", time.localtime(t))
    
    #----- configFile
    @classmethod
    def parseConfigString(self,config):
        
        returnVal = []
        
        for line in config.split('\n'):
            
            if not line:
                # empty line
                continue
            line    = line.strip()
            if line.startswith('#'):
                # comment
                continue
            if len(line)==0:
                # empty line
                continue
            
            lineVal = {}
            
            found   = False
            
            #===== app
            if not found:
            
                m = re.match('type="app"\s+appName="([a-zA-Z0-9]*)"\s+transport="([a-zA-Z0-9.,()]*)"\s+fieldsFromMote="(\S*)"\s+fieldsToMote="(\S*)"\s*', line)
                if m:
                    found = True
                
                    lineVal['type']                   = 'app'
                    lineVal['appName']                = m.group(1)
                    transportString                   = m.group(2)
                    fieldsFromMoteString              = m.group(3)
                    fieldsToMoteString                = m.group(4)
                    
                    transport = None
                    if transportString:
                        m = re.search('([a-zA-Z]+).(\(?[a-zA-Z0-9,]+\)?)', transportString)
                        if not m:
                            output = 'invalid transport string {0}'.format(transportString)
                            log.warning(output)
                            raise ValueError(output)
                        transport = {}
                        transport['type']             = m.group(1)
                        resourceString                = m.group(2).strip()
                        if resourceString.startswith('(') and resourceString.endswith(')'):
                            resourceString=resourceString.lstrip('(').rstrip(')')
                            isTuple = True
                        else:
                            isTuple = False
                        if isTuple:
                            transport['resource']     = []
                            for l in resourceString.split(','):
                                l =  l.strip()
                                try:
                                    l = int(l)
                                except ValueError:
                                    pass
                                transport['resource'].append(l)
                            transport['resource'] = tuple(transport['resource'])
                        else:
                            try:
                                transport['resource'] = int(resourceString)
                            except ValueError:
                                transport['resource'] = resourceString
                    lineVal['transport']              = transport
                    
                    fieldsFromMote = None
                    if fieldsFromMoteString:
                        m = re.search('(\S+)=([a-zA-Z0-9.]+)', fieldsFromMoteString)
                        if not m:
                            output = 'invalid fieldsFromMoteString string {0}'.format(fieldsFromMoteString)
                            log.warning(output)
                            raise ValueError(output)
                        fieldsFromMote = {}
                        fieldsFromMote['fieldFormats']   = m.group(1)
                        fieldsFromMote['fieldNames']  = m.group(2).split('.')
                    lineVal['fieldsFromMote']         = fieldsFromMote
                    
                    fieldsToMote = None
                    if fieldsToMoteString:
                        m = re.search('(\S+)=([a-zA-Z.]+)', fieldsToMoteString)
                        if not m:
                            output = 'invalid fieldsToMoteString string {0}'.format(fieldsToMoteString)
                            log.warning(output)
                            raise ValueError(output)
                        fieldsToMote = {}
                        fieldsToMote['fieldFormats']  = m.group(1)
                        fieldsToMote['fieldNames']    = m.group(2).split('.')
                    lineVal['fieldsToMote']           = fieldsToMote
                    
                    returnVal.append(lineVal)
            
            #===== mote
            if not found:
                pattern  = []
                pattern += ['type="mote"\s+mac="']
                for i in range(7):
                    pattern += ['([a-fA-F0-9]{2})-']
                pattern += ['([a-fA-F0-9]{2})']
                pattern += ['"\s*']
                pattern  = ''.join(pattern)
                m = re.match(pattern, line)
                if m:
                    found = True
                    
                    lineVal['type']    = 'mote'
                    lineVal['mac']     = tuple([int(m.group(i),16) for i in range(1,9)])
                    
                    returnVal.append(lineVal)
                    
            #===== attachApp
            if not found:
                pattern  = []
                pattern += ['type="attachApp"\s+mac="']
                for i in range(7):
                    pattern += ['([a-fA-F0-9]{2})-']
                pattern += ['([a-fA-F0-9]{2})']
                pattern += ['"\s+appName="(\S+)"']
                pattern += ['\s*']
                pattern  = ''.join(pattern)
                m = re.match(pattern, line)
                if m:
                    found = True
                    
                    lineVal['type']    = 'attachApp'
                    lineVal['mac']     = tuple([int(m.group(i),16) for i in range(1,9)])
                    lineVal['appName'] = m.group(9)
                    
                    returnVal.append(lineVal)
            
            #===== network
            if not found:
                pattern  = '\s*type="network"\s+netname="(\S+)"\s*'
                m = re.match(pattern, line)
                if m:
                    found = True
                    
                    lineVal['type']    = 'network'
                    lineVal['netname'] = m.group(1)
                    
                    returnVal.append(lineVal)
            
            #===== user
            if not found:
                pattern  = '\s*type="user"\s+username="(\S+)"\s*'
                m = re.match(pattern, line)
                if m:
                    found = True
                    
                    lineVal['type']         = 'user'
                    lineVal['username']     = m.group(1)
                    
                    returnVal.append(lineVal)
            
            #===== grantPrivilege
            if not found:
                pattern  = '\s*type="grantPrivilege"\s+username="(\S+)"\s+resource="(\S+)"\s+action="(\S+)"\s*'
                m = re.match(pattern, line)
                if m:
                    found = True
                    
                    lineVal['type']         = 'grantPrivilege'
                    lineVal['username']     = m.group(1)
                    resource                = m.group(2).split('.')
                    lineVal['action']       = m.group(3)
                    macpattern         = []
                    for i in range(7):
                        macpattern    += ['([a-fA-F0-9]{2})-']
                    macpattern        += ['([a-fA-F0-9]{2})']
                    macpattern         = ''.join(macpattern)
                    for i in range(len(resource)):
                        m = re.match(macpattern, resource[i])
                        if m:
                            resource[i] = tuple([int(m.group(b),16) for b in range(1,9)])
                    lineVal['resource']     = resource
                    returnVal.append(lineVal)
            
            #===== manager
            if not found:
                pattern  = '\s*type="manager"\s+connectionDetails="(\S+)"\s*'
                m = re.match(pattern, line)
                if m:
                    found = True
                    
                    lineVal['type']                   = 'manager'
                    connectionDetails                 = m.group(1)
                    elems = connectionDetails.split(':') 
                    if len(elems)==2:
                        lineVal['connectionDetails']  = (elems[0],int(elems[1]),)
                    else:
                        lineVal['connectionDetails']  = connectionDetails
                    
                    returnVal.append(lineVal)
            
            #===== publisherXively
            if not found:
            
                m = re.match('type="publisherXively"\s+xivelyApiKey="(\S+)"',line)
                if m:
                    found = True
                
                    lineVal['type']                   = 'publisherXively'
                    lineVal['xivelyApiKey']           = m.group(1)
                    
                    returnVal.append(lineVal)
            
            #===== publisherGoogle
            if not found:
            
                m = re.match('type="publisherGoogle"\s+spreadsheetKey="(\S+)"\s+worksheetName="(\S+)"\s+googleUsername="(\S+)"\s+googlePassword="(\S+)"',line)
                if m:
                    found = True
                
                    lineVal['type']                   = 'publisherGoogle'
                    lineVal['spreadsheetKey']         = m.group(1)
                    lineVal['worksheetName']          = m.group(2)
                    lineVal['googleUsername']         = m.group(3)
                    lineVal['googlePassword']         = m.group(4)
                    
                    returnVal.append(lineVal)
            
            #===== adminPassword
            if not found:
                pattern  = '\s*type="adminPassword"\s+password="(\S+)"\s*'
                m = re.match(pattern, line)
                if m:
                    found = True
                    
                    lineVal['type']         = 'adminPassword'
                    lineVal['password']     = m.group(1)
                    
                    returnVal.append(lineVal)
            
            #===== fastMode
            if not found:
                pattern  = '\s*type="fastMode"\s+value="(\S+)"\s*'
                m = re.match(pattern, line)
                if m:
                    found = True
                    
                    lineVal['type']         = 'fastMode'
                    value                   = m.group(1)
                    if   value=='true':
                        lineVal['value'] = True
                    elif value=='false':
                        lineVal['value'] = False
                    else:
                        return None
                    
                    returnVal.append(lineVal)
            
            #===== demoMode
            if not found:
                pattern  = '\s*type="demoMode"\s+value="(\S+)"\s*'
                m = re.match(pattern, line)
                if m:
                    found = True
                    
                    lineVal['type']         = 'demoMode'
                    value                   = m.group(1)
                    if   value=='true':
                        lineVal['value'] = True
                    elif value=='false':
                        lineVal['value'] = False
                    else:
                        return None
                    
                    returnVal.append(lineVal)
            
            if not found:
                output = 'no match for line the following line ({0} chars)\n{1}'.format(
                    len(line),
                    line,
                )
                log.warning(output)
                raise ValueError(output)
        
        return returnVal
    
    ##
    # \}
    #
    
    #======================== private =========================================
    
    def _validateFormatMac(self,mac):
        if not isinstance(mac,tuple):
            raise ValueError("mac should be a tuple, {0} is a {1}".format(mac,type(mac)))
        if not len(mac)==8:
            raise ValueError("mac should contain 8 elements, {0} contains {1}".format(mac,len(mac)))
        for b in mac:
            if not isinstance(b,int):
                raise ValueError("mac should contain contains only ints, {0} from {1} is not".format(b,mac))
    
    def _validateFormatIp(self,ip):
        if not isinstance(ip,tuple):
            raise ValueError("IPv6 should be a tuple, {0} is not".format(ip))
        if not len(ip)==16:
            raise ValueError("ip should contain 16 elements, {0} contains {1}".format(ip,len(ip)))
        for b in ip:
            if not isinstance(b,int):
                raise ValueError("ip should contain contains only ints, {0} from {1} is not".format(b,ip))
    
    @classmethod
    def _doValidation(self, username):
        '''User requires validation'''
        return DustLinkData.USER_SYSTEM != username
    
    def _isPriviledged(self, username):
        '''User has access to all resources'''
        return DustLinkData.USER_SYSTEM == username or DustLinkData.USER_ADMIN == username

class AuthCache(object):
    '''
    \brief Simple bounded authentication cache.
    '''
    
    BOUND = 1000
    
    def __init__(self):
        self._cache = {}
        self._hit = 0
        self._miss = 0
        self._lock = threading.RLock()
    
    def getEntry(self, at):
        try:
            with self._lock:
                entry = self._cache.get(at)
                if entry:
                    self._hit += 1
                else:
                    self._miss += 1
        except TypeError, e:
            print e
    
    def addEntry(self, at, entry):
        with self._lock:
            if self.getSize() > self.BOUND:
                self.reset()
            self._cache[at] = entry
    
    def reset(self):
        with self._lock:
            self._cache = {}
        
    def getHit(self):
        with self._lock:
            return self._hit
    
    def getMiss(self):
        with self._lock:
            return self._miss
    
    def getSize(self):
        with self._lock:
            return len(self._cache)

##
# \}
#
