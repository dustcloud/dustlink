import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('HealthPages')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import random

from pydispatch    import dispatcher

from SmartMeshSDK  import FormatUtils
from DustLinkData import DataVaultException, \
                         DustLinkData
from dustWeb       import web,              \
                          WebPage,          \
                          WebPageDyn,       \
                          WebHandler
from dustWeb.viz   import VizFields,        \
                          VizForm,          \
                          VizTestResults

#============================ object ==========================================

class HealthPages(WebPageDyn.WebPageDyn):
    
    #===== web handlers (private classes)
    
    class pageHealth(WebHandler.WebHandler):
        
        def getPage(self,subResource,username):
            global webServer
            global thisWebApp
            
            username    = web.ctx.session.username
            currentPath = WebPage.WebPage.urlStringTolist(web.ctx.path)
            
            page = thisWebApp.createPage(
                username        = username,
                currentPath     = currentPath,
                visualizations  = [],
            )
            
            return page
    
    class pageHealthSub(WebPageDyn.WebHandlerDyn):
        
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
                        subResourcePath     = 'testschedule',
                        title               = 'Test schedule',
                    ),
                    VizTestResults.VizTestResults(
                        webServer           = webServer,
                        username            = username,
                        resourcePath        = currentPath,
                        subResourcePath     = 'testresults',
                        title               = 'Test Results',
                    ),
                    VizForm.VizForm(
                        webServer           = webServer,
                        username            = username,
                        resourcePath        = currentPath,
                        subResourcePath     = 'testreset',
                        title               = 'Reset tests',
                    ),
                ],
            )
            
            return page
        
        def getDataDyn(self,dynPath,subResource,username):
            
            netname = FormatUtils.unquote(dynPath)
            dld     = DustLinkData.DustLinkData()
            
            if   subResource==['testschedule']:
                
                period_min    = float(dld.getTestPeriod(netname,username=username))/60.0
                
                secondsToNextRaw = dispatcher.send(
                    signal        = 'timeToNextSnapShot_{0}'.format(netname),
                    data          = None,
                )
                assert len(secondsToNextRaw)==1
                secondsToNext = secondsToNextRaw[0][1]
                
                return [
                    {
                        'name':             'period (min)',
                        'value':            period_min,
                        'type':             'text',
                        'editable':         True,
                    },
                    {
                        'name':             'next test in',
                        'value':            '{0}s'.format(secondsToNext),
                        'type':             'text',
                        'editable':         False,
                    },
                    {
                        'name':             ' ',
                        'value':            'Run tests now',
                        'type':             'button',
                    },
                ]
            
            elif subResource==['testresults']:
                
                testResults = dld.getResults(netname,username=username)
                
                # fill in data
                data = []
                if testResults:
                    for (testName,res) in testResults.items():
                        
                        # outcomeIcon
                        if   res['last']['outcome']==dld.TEST_OUTCOME_PASS:
                            outcomeIcon = 'pass.png'
                        elif res['last']['outcome']==dld.TEST_OUTCOME_FAIL:
                            outcomeIcon = 'fail.png'
                        elif res['last']['outcome']==dld.TEST_OUTCOME_NOTRUN:
                            outcomeIcon = 'notrun.png'
                        else:
                            SystemError("outcome {0} not expected".format(res['outcome']))
                        
                        # outcomeDesc
                        outcomeDesc = res['last']['outcome']
                        
                        # weatherIcon
                        numPass = res['history'].count(dld.TEST_OUTCOME_PASS)
                        numFail = res['history'].count(dld.TEST_OUTCOME_FAIL)
                        if numFail==0 and numFail==0:
                            weatherScore = 1.0
                        else:
                            weatherScore = float(numPass)/float(numPass+numFail)
                        if   weatherScore>0.8:
                            weatherIcon = 'weather-80plus.png'
                        elif weatherScore>0.6:
                            weatherIcon = 'weather-60to79.png'
                        elif weatherScore>0.4:
                            weatherIcon = 'weather-40to59.png'
                        elif weatherScore>0.2:
                            weatherIcon = 'weather-20to39.png'
                        else:
                            weatherIcon = 'weather-00to19.png'
                        
                        # weatherDesc
                        weatherDesc    = []
                        weatherDesc   += ['<ul>']
                        weatherDesc   += ['<li>{0} tests PASS</li>'.format(numPass)]
                        weatherDesc   += ['<li>{0} tests FAIL</li>'.format(numFail)]
                        weatherDesc   += ['</ul>']
                        weatherDesc    = '\n'.join(weatherDesc)
                        
                        # testName
                        testName = testName.replace('_nettest_','',1)
                        
                        # testDesc
                        testDesc = res['description']
                        
                        # lastRun
                        lastRun  = DustLinkData.DustLinkData.timestampToStringShort(
                            res['last']['timestamp']
                        )
                        
                        # lastRunDesc
                        lastRunDesc = res['last']['description']
                        
                        # lastSuccess
                        if res['lastSuccess']['timestamp']:
                            lastSuccess = DustLinkData.DustLinkData.timestampToStringShort(
                                res['lastSuccess']['timestamp']
                            )
                        else:
                            lastSuccess = 'N/A'
                        
                        # lastSuccessDesc
                        lastSuccessDesc = res['lastSuccess']['description']
                        
                        # lastFailure
                        if res['lastFailure']['timestamp']:
                            lastFailure = DustLinkData.DustLinkData.timestampToStringShort(
                                res['lastFailure']['timestamp']
                            )
                        else:
                            lastFailure = 'N/A'
                        
                        # lastFailureDesc
                        lastFailureDesc = res['lastFailure']['description']
                        
                        data += [
                            {
                                'outcomeIcon':        outcomeIcon,
                                'outcomeDesc':        outcomeDesc,
                                'weatherIcon':        weatherIcon,
                                'weatherDesc':        weatherDesc,
                                'testName':           testName,
                                'testDesc':           testDesc,
                                'lastRun':            lastRun,
                                'lastRunDesc':        lastRunDesc,
                                'lastSuccess':        lastSuccess,
                                'lastSuccessDesc':    lastSuccessDesc,
                                'lastFailure':        lastFailure,
                                'lastFailureDesc':    lastFailureDesc,
                            },
                        ]
                
                return data
            
            elif subResource==['testreset']:
                
                return [
                    {
                        'name':           'command',
                        'value':          '',
                        'type':           'text',
                    }
                ]
            
            else:
                raise web.notfound()
        
        def postDataDyn(self,receivedData,dynPath,subResource,username):
            
            netname = FormatUtils.unquote(dynPath)
            dld     = DustLinkData.DustLinkData()
            
            if   subResource==['testschedule']:
                
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['fieldName','fieldValue']
                
                if   receivedData['fieldName']=='period (min)':
                    assert type(receivedData['fieldValue'])==int
                    period_seconds = 60*int(receivedData['fieldValue'])
                    dld.setTestPeriod(netname,period_seconds,username=username)
                elif receivedData['fieldName']==' ':
                    
                    # dummy read to make sure user has GET privileges on testResults
                    dld.getTestPeriod(netname,username=username)
                    
                    # trigger a snapshot
                    secondsToNextRaw = dispatcher.send(
                        signal        = 'snapShotNow_{0}'.format(netname),
                        data          = None,
                    )
                    
                else:
                    raise web.notfound()
                
            elif subResource==['testreset']:
                
                assert isinstance(receivedData,dict)
                assert receivedData.keys()==['command']
                assert isinstance(receivedData['command'],str)
                
                if receivedData['command']=='reset':
                
                    # log
                    log.info("deleting testResults for network {0}".format(netname))
                    
                    # erase all test results
                    dld.delete(['testResults',netname,'results'],username=username) # as user (to verify privileges)
                    dld.put(   ['testResults',netname,'results'],None)              # as ADMIN
                    
                    # reset 'numOperationalEvents' counter of all motes in the network
                    motes = dld.getNetworkMotes(netname)
                    for mote in motes:
                        try:
                            dld.delete(['motes',mote,'info','numOperationalEvents'])
                        except DataVaultException.NotFound:
                            # happens when mote has not 'numOperationalEvents' counter
                            pass
            else:
                raise web.notfound()
        
    def subPageLister(self):
        username = str(web.ctx.session.username)
        dld = DustLinkData.DustLinkData()
        try:
            return [
                {
                    'url':   FormatUtils.quote(n),
                    'title': n,
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
        WebPageDyn.WebPageDyn.__init__(
            self,
            webServer       = self.webServer,
            url             = 'health',
            title           = 'Health',
            webHandler      = self.pageHealth,
            subPageLister   = self.subPageLister,
            subPageHandler  = self.pageHealthSub,
        )