import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizTimeLine')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import VizMorris

class VizTimeLine(VizMorris.VizMorris):
    
    #======================== header ==========================================
    
    templateHeader = '''
<style type="text/css">
</style>
'''
    
    #======================== body ============================================
    
    templateBody = '''
<script type='text/javascript'>
    
    // wait for the page to be loaded, then create the form (once)
    $(document).ready(getData_{VIZID});
    
    var graph_{VIZID},
        autorefresh_{VIZID};
    
    graph_{VIZID}       = 0;
    autorefresh_{VIZID} = true;
    
    //======================= get form ========================================
    
    function getData_{VIZID}() {{
        
        var statusDivId;
        
        try {{
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
                                drawData_{VIZID}(response);
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
            }}
        }} catch (err) {{
            updateStatus(statusDivId,'failure',err.toString());
        }}
    }}
    
    function drawData_{VIZID}(data) {{
        if (graph_{VIZID}==0) {{
            graph_{VIZID} = Morris.Line({{
                element:     'chart_div_{VIZID}',
                data:        data.datapoints,
                xkey:        'timestamp',
                ykeys:       data.metadata.axis,
                labels:      data.metadata.axis,
                xLabels:     "auto",
                hideHover:   true,
            }});
        }} else {{
            graph_{VIZID}.setData(data.datapoints);
        }}
    }}
    
    setInterval(getData_{VIZID},{RELOAD_PERIOD});
    
</script>
'''
