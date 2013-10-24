import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizGoogleCharts')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import Viz

class VizGoogleCharts(Viz.Viz):
    
    #======================== libraries =======================================
    
    libraries      = [Viz.Viz.LIBRARY_JSAPI,
                      Viz.Viz.LIBRARY_JQUERY]
    
    #======================== header ==========================================
    
    @classmethod
    def getHeaderTemplate(self,PACKAGE,VISUALIZATION,EXTRAOPTIONS):
        
        extraOptions         = ['                        {0}: {1}'.format(k,v) for (k,v) in EXTRAOPTIONS.items()]
        extraOptions         = ',\n'.join(extraOptions)
        if extraOptions:
            extraOptions     = ',\n'+extraOptions
        
        return '''
            <script type='text/javascript'>
                var chart_{VIZID},
                    options_{VIZID},
                    data_{VIZID},
                    autorefresh_{VIZID};
                
                autorefresh_{VIZID}=true;
                
                google.load('visualization', '1', {{packages:[\''''+PACKAGE+'''\']}});
                
                google.setOnLoadCallback(prepareChart_{VIZID});
                
                function prepareChart_{VIZID}() {{
                    chart_{VIZID} = new google.visualization.'''+VISUALIZATION+'''(document.getElementById('chart_div_{VIZID}'));
                    
                    options_{VIZID} = {{
                        animation: {{
                            duration:   500,
                            easing:     'out',
                        }}'''+extraOptions+'''
                    }};
                    
                    drawChart_{VIZID}();
                    
                    setInterval('drawChart_{VIZID}()', {RELOAD_PERIOD});
                }}
               
                function drawChart_{VIZID}() {{
                
                    var statusDivId;
                    
                    statusDivId = 'status_div_{VIZID}';
                
                    try {{
                        if (autorefresh_{VIZID}) {{
                            
                            updateStatus(statusDivId,'busy','');
                            
                            var JSONObject_{VIZID} = $.ajax({{
                                url:     "/{RESOURCE}/",
                                dataType:"json",
                                async:   false,
                                statusCode: {{
                                    200: function(response) {{
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
                            }}).responseText;
                            
                            data_{VIZID} = new google.visualization.DataTable(JSONObject_{VIZID}, 0.5);
                            
                            chart_{VIZID}.draw(data_{VIZID},options_{VIZID});
                            
                        }}
                    }} catch (err) {{
                        updateStatus(statusDivId,'failure',err.toString());
                    }}
                }}
            </script>
            '''
    
    #======================== body ============================================
    
    templateBody = ''