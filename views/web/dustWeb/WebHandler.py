import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('WebHandler')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import web
import json
import traceback

import WebPage
import DustWeb

try:
    from DustLinkData import DataVaultException
    UnauthorizedException = DataVaultException.Unauthorized
except ImportError:
    UnauthorizedException = Exception

class WebHandler(object):
    
    ALREADY_JSONIFIED = 'already JSON\'ified'
    
    def GET(self,subResource=''):
        
        '''
        print 'GET {0} {1} (subR={2})'.format(web.ctx.session.username,
                                              web.ctx.path,
                                              subResource)
        '''
        
        subResource = WebPage.WebPage.urlStringTolist(subResource)
        username    = str(web.ctx.session.username)
        
        if not self._isDataUrl():
            try:
                return self.getPage(subResource,username)
            except UnauthorizedException:
                raise web.HTTPError('401 unauthorized',{},'not autorized')
            except web.seeother:
                raise
            except web.HTTPError:
                raise
            except Exception as err:
                # log
                log.error('error processing user request.\nerror:{0}\ntraceback:{1}'.format(
                        err,
                        traceback.format_exc(),
                    )
                )
                
                # return HTTP error
                raise web.HTTPError(
                        '500 internal error',
                        {},
                        traceback.format_exc(),
                      )
        else:
            try:
                dataToAnswer = self.getData(subResource,username)
                if   isinstance(dataToAnswer,(dict,list)):
                    web.header('Content-Type', 'text/json')
                    return json.dumps(dataToAnswer)
                elif isinstance(dataToAnswer,tuple) and len(dataToAnswer)==2:
                    data                = dataToAnswer[0]
                    handlingInstruction = dataToAnswer[1]
                    if handlingInstruction==self.ALREADY_JSONIFIED:
                        return data
                    else:
                        raise SystemError('unexpected handlingInstruction={0}'.format(handlingInstruction))
                else:
                    raise SystemError("Unexpected dataToAnswer={0} {1}".format(dataToAnswer,type(dataToAnswer)))
            except UnauthorizedException:
                raise web.HTTPError('401 unauthorized',{},'not autorized')
            except web.HTTPError:
                raise
            except Exception as err:
                # log
                log.error('error processing user request.\nerror:{0}\ntraceback:{1}'.format(
                        err,
                        traceback.format_exc(),
                    )
                )
                
                # return HTTP error
                raise web.HTTPError(
                        '500 internal error',
                        {},
                        traceback.format_exc(),
                      )
    
    def POST(self,subResource=''):
        
        '''
        print 'POST {0} {1}'.format(web.ctx.session.username, web.ctx.path)
        '''
        
        subResource = WebPage.WebPage.urlStringTolist(subResource)
        username    = str(web.ctx.session.username)
        
        keys = web.input().keys()
        
        if len(keys)==1 and not web.input()[keys[0]]:
            # handle JSON decode errors.
            try:
                rawWebInput = json.loads(keys[0])
            except ValueError, err:
                raise web.HTTPError("400 Bad Request", {}, str(err))
        else:
            rawWebInput = web.input()
            
        if isinstance(rawWebInput,dict):
            webInput = DustWeb.simplifyWebInputFormat(rawWebInput)
        elif isinstance(rawWebInput,list):
            webInput = []
            for e in rawWebInput:
                webInput.append(DustWeb.simplifyWebInputFormat(e))
        else:
            webInput = rawWebInput
        
        if self._isDataUrl():
            try:
                return self.postData(webInput,subResource,username)
            except UnauthorizedException:
                raise web.HTTPError('401 unauthorized',{},'not autorized')
            except web.seeother:
                raise
            except web.HTTPError:
                raise
            except ValueError as err:
                log.error('error processing user request.\nerror:{0}\ntraceback:{1}'.format(
                        err,
                        traceback.format_exc(),
                    )
                )
                raise web.HTTPError('400 Bad Request',{},str(err))
            except Exception as err:
                # log
                log.error('error processing user request.\nerror:{0}\ntraceback:{1}'.format(
                        err,
                        traceback.format_exc(),
                    )
                )
                
                # return HTTP error
                raise web.HTTPError(
                        '500 internal error',
                        {},
                        traceback.format_exc(),
                      )

        else:
            raise SystemError("Unexpected POST on URL {0}".format(web.ctx.path))
    
    #======================== abstract methods ================================
    
    def getPage(self,subResource,username):
        raise web.notfound()
    
    def getData(self,subResource,username):
        raise web.notfound()
    
    def postData(self,receivedData,subResource,username):
        raise web.notfound()
    
    #======================== private =========================================
    
    def _isDataUrl(self):
        urlList = web.ctx.path.split('/')
        urlList = [u for u in urlList if u]
        
        return 'json' in urlList