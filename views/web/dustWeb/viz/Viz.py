import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('Viz')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class Viz(object):
    
    COMMON_HEADER       = '''
<script type='text/javascript'><!--
    var autorefresh_{VIZID}    = true;
-->
</script>
'''
    
    COMMON_BODY         = '''
<div class="container-div" id="container_div_{VIZID}">
    <div class="clear-block viz-header-div">
        <h1 class="viz-header {CLASS}" id="title_div_{VIZID}">{TITLE}</h1>
        <div class="viz-headercommon viz-status" id="status_div_{VIZID}">
            <svg class="hide" xmlns="http://www.w3.org/2000/svg" version="1.1" width="20" height="16">
                <circle cx="8" cy="6" r="5" stroke="black" stroke-width="1"/>
            </svg>
            <span class="viz-status-message"></span>
            <label class="viz-autorefresh">Auto-refresh<input type="checkbox" {CHECKED} {DISABLED} id="autorefreshlink_{VIZID}" onchange="updateAutoRefresh('{VIZID}')"/></label>
        </div>
    </div>
    <div class="container-indent">
        {DOC}
        <div class="" id='chart_div_{VIZID}'></div>
        <div id="chart_error_{VIZID}"></div>
    </div>
</div>
    '''

    ## Javascript libraries which can be loaded in the webpage
    LIBRARY_JSAPI       = 'https://www.google.com/jsapi'
    LIBRARY_JQUERY      = '/static/javascript/jquery-1.8.0.min.js'
    LIBRARY_DATATABLES  = '/static/javascript/jquery.dataTables.min.js'
    LIBRARY_RAPHAEL     = '/static/javascript/raphael-min.js'
    LIBRARY_MORRIS      = '/static/javascript/morris.min.js'
    LIBRARY_D3          = '/static/javascript/d3.v2.js'
    LIBRARY_DAGRE       = '/static/javascript/dagre.js'

    LIBRARY_VIZ       = '/static/javascript/viz.js'

    LIBRARY_ALL         = [LIBRARY_JSAPI,
                           LIBRARY_JQUERY,
                           LIBRARY_DATATABLES,
                           LIBRARY_RAPHAEL,
                           LIBRARY_MORRIS,
                           LIBRARY_D3,
                           LIBRARY_DAGRE,
                           LIBRARY_VIZ,
                           ]
    
    ## number of ms between data reloads
    RELOAD_PERIOD       = 10000
    
    def __init__(self,webServer,username,resourcePath,subResourcePath=None,title='',width=700,height=700,autorefresh=True, forbidAutorefresh=False):
        
        # store variables
        self.webServer       = webServer
        self.username        = username
        self.resourcePath    = resourcePath
        self.subResourcePath = subResourcePath
        self.title           = title
        self.width           = width
        self.height          = height
        self.autorefresh     = autorefresh
        self.forbidAutorefresh = forbidAutorefresh
        
        resource             = self.resourcePath[:]
        resource            += ['json']
        if self.subResourcePath:
            resource        += [self.subResourcePath]
        
        resource             = '/'.join(resource)
        
        # local variables
        if self.autorefresh:
            autorefresh_js = 'true'
        else:
            autorefresh_js = 'false'
        self.common_template_formatters = {
            'TITLE'               : self.title,
            'RESOURCE'            : resource,
            'RELOAD_PERIOD'       : self.RELOAD_PERIOD,
            'WIDTH'               : self.width,
            'HEIGHT'              : self.height,
            'AUTOREFRESH'         : autorefresh_js,
        }
            
    def getLibraries(self):
        return self.libraries
    
    def getHeaderCode(self,uniqueId):
        returnVal  = []
        returnVal += [self.COMMON_HEADER.format(VIZID=uniqueId, **self.common_template_formatters)]
        returnVal += [self.templateHeader.format(VIZID=uniqueId,**self.common_template_formatters)]
        return '\n'.join(returnVal) 
    
    def getBodyCode(self,uniqueId):
        if self.autorefresh:
            checked = 'checked="checked"'
        else:
            checked = ""

        if self.forbidAutorefresh:
            disabled = 'disabled="disabled"'
        else:
            disabled = ""

        docPath = self._getDocumentationPath()
        DOC = self.webServer.getDocumentation().getDocHTML(docPath, uniqueId)
        
        returnVal  = []
        returnVal += [self.COMMON_BODY.format(
                            VIZID=uniqueId,
                            TITLE=self.title,
                            CHECKED=checked,
                            DOC=DOC,
                            CLASS=self.webServer.getDocumentation().getClass(docPath),
                            DISABLED=disabled)
                     ]
        returnVal += [self.templateBody.format(VIZID=uniqueId,**self.common_template_formatters)]
        return '\n'.join(returnVal)
    
    def _getDocumentationPath(self):
        resource = self.resourcePath
        resourceLength = len(resource)
        result = list(resource)
        if resourceLength > 0:
            if str(result[resourceLength-1]).startswith('_'):
                result[resourceLength-1] = '*'
        if self.subResourcePath:
            result += [self.subResourcePath]

        if len(result) > 0:
            return tuple(result)
        else:
            return None