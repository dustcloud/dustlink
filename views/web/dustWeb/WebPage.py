import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('WebPage')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import os
import urllib
import web
from viz import Viz, \
                VizBanner

TEMPLATE_PATH  = os.path.join('templates')
LOOK_AND_FEEL  = 'dust'

class WebPage(object):
    
    DESIGN_ONE_COLUMN   = 'one_column'
    DESIGN_TWO_COLUMNS  = 'two_columns'
    DESIGN_ALL          = [DESIGN_ONE_COLUMN,DESIGN_TWO_COLUMNS]
    
    LAYOUT_HORIZONTAL   = 'horizontal'
    LAYOUT_VERTICAL     = 'vertical'
    LAYOUT_ALL          = [LAYOUT_HORIZONTAL,LAYOUT_VERTICAL]
    
    def __init__(self,webServer,url,title,webHandler,hidden=False):
        
        # store params
        self.webServer       = webServer
        self.url             = url
        self.title           = title
        self.webHandler      = webHandler
        self.hidden          = hidden
        
        # local variables
        self.children        = []
    
    #======================== public ==========================================
    
    def createPage(self,username=None,
                        currentPath=[],
                        design=DESIGN_TWO_COLUMNS,
                        layout=LAYOUT_VERTICAL,
                        visualizations=[]):
        '''
        \brief Create a full HTML page, ready to be sent back to the client.
        
        \param[in] username The username associated with this client's session.
                            This can be used to display the username in the page.
        \param[in] currentPath Path of the resulting page.
        \param[in] design   The design of the page, i.e. "look-and-feel" to expect.
                            This can translate in different templates.
                            Must be an element of DESIGN_ALL.
        \param[in] layout   The layout of the page, i.e. how the visualizations
                            are arranged inside the page.
                            Must be an element of LAYOUT_ALL.
        \param[in] visualizations List of visualizations this page must contain.
                            Each visualization must be of type Viz.
        '''
        
        # filter errors
        assert (not username) or isinstance(username,str)
        assert isinstance(currentPath,list)
        for p in currentPath:
            assert isinstance(p,str)
        assert design in self.DESIGN_ALL
        assert layout in self.LAYOUT_ALL
        assert isinstance(visualizations,list)
        for v in visualizations:
            assert isinstance(v,Viz.Viz)
        
        # add a banner
        visualizations += [
            VizBanner.VizBanner(
                webServer           = self.webServer,
                username            = username,
                resourcePath        = ['banner'],
            ),
        ]
        
        # get the pageTitle from the current path
        pageTitle       = self.webServer.getPageTitle(currentPath)
        
        # get the template corresponding to the design
        webtemplate     =   web.template.frender(
                                os.path.join(
                                    TEMPLATE_PATH,
                                    LOOK_AND_FEEL,
                                    '{0}.html'.format(design)
                                )
                            )
        
        # create the logFrameCode from the username
        logFrameCode    = self._buildLoginFrame(username)
        
        # get the libraries from the visualizations
        libraries       = []
        for v in visualizations:
            libraries  += v.getLibraries()
        libraries = list(set(libraries)) # remove duplicates
        
        # re-arrange library order to deal with dependencies
        for lib in [Viz.Viz.LIBRARY_JQUERY]:
            if lib in libraries:
                # remove
                libraries.remove(lib)
                # put at front
                libraries.insert(0,lib)
        for lib in [Viz.Viz.LIBRARY_RAPHAEL,Viz.Viz.LIBRARY_MORRIS]:
            if lib in libraries:
                # remove
                libraries.remove(lib)
                # put at end
                libraries.append(lib)
        
        # create unique ID for each visualization
        uniqueId = {}
        for v in visualizations:
            uniqueId[v] = 'id'+str(self.webServer.getUniqueNumber())
        
        # create the headerCode from the visualizations
        headerElems          = []
        for l in libraries:
            headerElems     += ['<script type="text/javascript" src="{0}"></script>'.format(l)]
        for v in visualizations:
            headerElems     += [v.getHeaderCode(uniqueId[v])]
        headerCode      = '\n'.join(headerElems)
        
        # get page level documentation
        pathCopy = list(currentPath)
        pathCopyLast = len(pathCopy) - 1
        if pathCopyLast >= 0 and pathCopy[pathCopyLast].startswith("_"):
            pathCopy[pathCopyLast] = '*'
        pathTuple = tuple(pathCopy)
        documentation = self.webServer.getDocumentation().getDocHTML(pathTuple, "page")
        # create the bodyCode from the visualizations
        bodyElems       = []
        for v in visualizations:
            bodyElems  += [v.getBodyCode(uniqueId[v])]
        bodyCode        = self._layoutElems(bodyElems,layout)
        
        renderedPage    =   webtemplate (
                                pageTitle        = pageTitle,
                                hierarchy        = self.webServer.getUrlHierarchy(),
                                currentPath      = currentPath,
                                logFrameCode     = logFrameCode,
                                headerCode       = headerCode,
                                bodyCode         = bodyCode,
                                documentation    = documentation,
                            )
        return renderedPage
    
    def registerPage(self,newChild):
        
        # filter error
        assert isinstance(newChild,WebPage)
        
        # add to children
        self.children.append(newChild)
    
    def getUrlHierarchy(self,parentPath=[]):
        
        assert not self.url.count('/')
        
        newParentPath = parentPath+[self.url]
        
        classUrl = newParentPath
        if len(classUrl) and not classUrl[0]:
            classUrl = classUrl[1:]
        
        returnVal             = {}
        returnVal['url']      = self.urlListToString(newParentPath)
        returnVal['title']    = self.title
        returnVal['class']    = self.webServer.getDocumentation().getClass(classUrl)
        returnVal['children'] = [c.getUrlHierarchy(newParentPath) for c in self.children if not c.hidden]
        
        return returnVal
    
    def getPageTitle(self,path):
        
        # filter errors
        assert isinstance(path,list)
        for p in path:
            assert isinstance(p,(str,unicode))
        
        if len(path)>0:
            if path[0].startswith('_'):
                return urllib.unquote(urllib.unquote(path[0][1:]))
            else:
                for c in self.children:
                    urlElems = self.urlStringTolist(c.url)
                    if path[0]==urlElems[0]:
                        return c.getPageTitle(path[1:])
                return 'unknown 1'
        elif len(path)==0:
            return self.title
        else:
            return 'unknown 2'
    
    def getHandlerNameToHandlerClass(self,parentUrl=''):
    
        assert not parentUrl.count('/')
        assert not self.url.count('/')
    
        returnVal = {}
        
        # add my webHandler
        returnVal[self.webHandler.__name__] = self.webHandler
        
        # add my children's mapping
        for child in self.children:
            returnVal = dict(returnVal.items() + child.getHandlerNameToHandlerClass().items())
        
        return returnVal
    
    def getMappingUrlToHandlerName(self,parentUrl=''):
        '''
        \brief Return the mapping between URL's and webHandler's
        
        This method returns a tuple, where URL's are in the odd positions and
        webHandler in the even positions, e.g.:
            (
                '',             'rootHandler',
                'level1',       'level1Handler',
                'level1/level2','level2Handler',
            )
        
        This structure can be used directly by a web.py server.
        '''
        
        assert not parentUrl.count('/')
        assert not self.url.count('/')
        
        returnVal = []
        
        # add me
        returnVal +=    [self.urlListToString([parentUrl,self.url],              trailingSlashOption=True),
                         self.webHandler.__name__]
        returnVal +=    [self.urlListToString([parentUrl,self.url,'json','(.*)'],trailingSlashOption=True),
                         self.webHandler.__name__]
        
        # add my children's mapping
        for child in self.children:
            returnVal +=     child.getMappingUrlToHandlerName(parentUrl=self.url)
        
        # return a tuple
        return tuple(returnVal)
    
    #======================== private =========================================
    
    def _buildLoginFrame(self,username):
        if username in [self.webServer.defaultUsername]:
            output  = []
            output += ["<form action=\"/login\" method=\"POST\">"]
            output += ["   <table id=\"login\">"]
            output += ["      <tr>"]
            output += ["         <td>Username:</td>"]
            output += ["         <td><input type=\"text\"     name=\"username\"/></td>"]
            output += ["         <td>Password:</td>"]
            output += ["         <td><input type=\"password\" name=\"password\"/></td>"]
            output += ["         <td><input type=\"hidden\"   name=\"action\" value=\"login\"/></td>"]
            output += ["         <td><input type=\"submit\"   value=\"LOGIN\"/></td>"]
            output += ["      </tr>"]
            output += ["   </table>"]
            output += ["</form>"]
            return '\n'.join(output)
        else:
            output  = []
            output += ["<form action=\"/login\" method=\"POST\">"]
            output += ["   <table>"]
            output += ["      <tr>"]
            output += ["         <td>You are logged in as <b>{0}</b>.</td>".format(username)]
            output += ["         <td><input type=\"hidden\" name=\"action\" value=\"logout\"></td>"]
            output += ["         <td><input type=\"submit\" value=\"LOGOUT\"></td>"]
            output += ["      </tr>"]
            output += ["   </table>"]
            output += ["</form>"]
            return '\n'.join(output)
    
    def _layoutElems(self,elems,layout):
        
        # filter errors
        assert isinstance(elems,list)
        for e in elems:
            assert isinstance(e,str)
        assert layout in self.LAYOUT_ALL
        
        returnVal = []
        
#        returnVal += ['<table>']
        if   layout in [self.LAYOUT_HORIZONTAL]:
#            returnVal += ['<tr>']
            for e in elems:
#                returnVal += ['<td>']
                returnVal += [e]
#                returnVal += ['</td>']
#            returnVal += ['</tr>']
        elif layout in [self.LAYOUT_VERTICAL]:
            for e in elems:
#                returnVal += ['<tr>']
#                returnVal += ['<td>']
                returnVal += [e]
#                returnVal += ['</td>']
#                returnVal += ['</tr>']
        else:
            raise SystemError('unexpected layout {0}'.format(layout))
#        returnVal += ['</table>']
        
        return '\n'.join(returnVal)
    
    @classmethod
    def urlListToString(self,urlList,trailingSlashOption=False):

        # remove empty elements from urlList 
        urlList = [u for u in urlList if u]
    
        returnVal  = []
        if urlList:
            returnVal += ['/']
        returnVal += ['/'.join(urlList)]
        if trailingSlashOption:
            returnVal += ['/?']
        
        return ''.join(returnVal)
    
    @classmethod
    def urlStringTolist(self,urlString):
        
        # filter errors
        assert isinstance(urlString,(str,unicode))
        
        # split into elements
        urlList = urlString.split('/')
        
        # remove empty elements (can happen with e.g. trailing slash)
        urlList = [u for u in urlList if u]
        
        # convert elements to string (can be unicode)
        urlList = [str(u) for u in urlList]
    
        return urlList