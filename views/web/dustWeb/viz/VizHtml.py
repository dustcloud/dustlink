import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizHtml')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import VizjQuery

class VizHtml(VizjQuery.VizjQuery):
    
    #======================== header ==========================================
    
    templateHeader = '''
<style type="text/css">
</style>
'''
    
    #======================== body ============================================
    
    templateBody = '''
<script type='text/javascript'>
    
    // wait for the page to be loaded, then update the fields for the first time
    $(document).ready(getData_{VIZID});
    setInterval(getData_{VIZID},{RELOAD_PERIOD});
    
    function getData_{VIZID}() {{
        
        var statusDivId;
        
        if (autorefresh_{VIZID}) {{
            
            // update the status message
            statusDivId = 'status_div_{VIZID}';
            updateStatus(statusDivId,'busy','');
            
            // get updated data from the server and execute
            jQuery.ajax({{
                type:       'GET',
                url:        '/{RESOURCE}/',
                timeout:    5*1000,
                statusCode: {{
                    200: function(response) {{
                        try {{
                            updateHtml_{VIZID}(response);
                        }} catch(err) {{
                            throw err;
                        }}
                        updateStatus(statusDivId,'success','');
                    }},
                    400: function() {{
                        updateStatus(statusDivId,'failure','Malformed.');
                    }},
                    401: function() {{
                        updateStatus(statusDivId,'failure','Access denied.');
                    }},
                    404: function() {{
                        updateStatus(statusDivId,'failure','Resource not found.');
                    }},
                    500: function() {{
                        updateStatus(statusDivId,'failure','Internal server error.');
                    }}
                }},
                error: function(jqXHR, textStatus, errorThrown) {{
                    if (textStatus=='timeout') {{
                        updateStatus(statusDivId,'failure','Server unreachable.');
                    }}
                }}
            }});
        }};
    }}
    
    function updateHtml_{VIZID}(data) {{
        document.getElementById('chart_div_{VIZID}').innerHTML = data.rawHtml;
        if ( {AUTOREFRESH}==false ) {{
            disableAutoRefresh('{VIZID}');
        }}
    }}
</script>
'''
