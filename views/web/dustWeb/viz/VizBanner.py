import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizBanner')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import VizjQuery

class VizBanner(VizjQuery.VizjQuery):
    
    COMMON_BODY    = '''
    '''
    
    #======================== header ==========================================
    
    templateHeader = '''
<style type="text/css">
    
    #banner-div {{
        position:            fixed;
        width:               800px;
        height:              30px;
        top:                 100%;
        left:                50%;
        margin-top:          -30px;
        margin-left:         -400px;
        text-align:          center;
        background-color:    #00667c;
        color:               #ffffff;
        border:              1px solid #00535e !important;
        opacity:             .98;
        z-index:             101;
        visibility:          hidden;
    }}
    
    #banner-div a:link {{
        color:               #ffffff;
        text-decoration:     underline;
    }}
    #banner-div a:visited {{
        color:               #ffffff;
        text-decoration:     underline;
    }}
    #banner-div a:hover {{
        color:               #ffffff;
        text-decoration:     underline;
    }}
    #banner-div a:active {{
        color:               #ffffff;
        text-decoration:     underline;
    }}
    
    #banner-text {{
        position:            absolute;
        width:               750px;
        height:              20px;
        top:                 5px;
        left:                0px;
        z-index:             102;
    }}
    
    #banner-close {{
        position:            absolute;
        width:               50px;
        height:              20px;
        top:                 5px;
        left:                750px;
        z-index:             102;
        text-decoration:     underline;
    }}
    
</style>
'''
    
    #======================== body ============================================
    
    templateBody = '''
    
    
    
<script type='text/javascript'>
    
    // wait for the page to be loaded, before initializing the banner
    $(document).ready(initBanner);
    
    //======================= get form ========================================
    
    function initBanner() {{
        
        // add a banner div to the body of the page
        $("body").prepend(
            '<div id="banner-div">'+
               '<div id="banner-text"></div>'+
               '<div id="banner-close" onClick="closeBanner()">close</div>'+
            '</div>'
        )
        
        // trigger first update of the banner
        getBannerData();
        
        // trigger period updates
        setInterval(getBannerData,{RELOAD_PERIOD});
    }}
    
    function getBannerData() {{
        
        // get updated banner data from the server and execute
        jQuery.ajax({{
            type:       'GET',
            url:        '/{RESOURCE}/',
            timeout:    5*1000,
            statusCode: {{
                200: function(response) {{
                    try {{
                        updateBanner(response);
                    }} catch(err) {{
                        throw err;
                    }}
                }},
                400: function(response) {{
                }},
                401: function() {{
                }},
                404: function() {{
                }},
                500: function() {{
                }}
            }},
            error: function(jqXHR, textStatus, errorThrown) {{
                if (textStatus=='timeout') {{
                }}
            }}
        }});
    }}
    
    function updateBanner(data) {{
        
        // update banner text
        $('#banner-text').html(data);
        
        // toggle banner visibility
        if (data=='') {{
            $('#banner-div').css('visibility', 'hidden');
        }} else {{
            $('#banner-div').css('visibility', 'visible');
        }}
    }}
    
    function closeBanner() {{
        jQuery.ajax({{
            type:       'POST',
            url:        '/{RESOURCE}/',
            data:       'close'
        }});
        $('#banner-div').css('visibility', 'hidden');
    }}
</script>
'''

    def __init__(self, **kw):
        super(VizBanner, self).__init__(forbidAutorefresh=True, autorefresh=False, **kw)
