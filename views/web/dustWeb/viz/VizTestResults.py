import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizTestResults')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import VizjQuery

class VizTestResults(VizjQuery.VizjQuery):
    
    #======================== header ==========================================
    
    templateHeader = '''
<style type="text/css">
    .selectedTest {{
        background-color:    rgb(250, 255, 189);
    }}
    .clickableTest {{
        text-decoration:     underline;
    }}
</style>
'''
    
    #======================== body ============================================
    
    templateBody = '''
<script type='text/javascript'>
    
    // wait for the page to be loaded, then update the fields for the first time
    $(document).ready(getData_{VIZID});
    setInterval(getData_{VIZID},{RELOAD_PERIOD});
    
    //======================= local variables =================================
    
    var numTests_{VIZID}         = 0;
    var desc_outcome_{VIZID}     = [];
    var desc_weather_{VIZID}     = [];
    var desc_test_{VIZID}        = [];
    var desc_lastRun_{VIZID}     = [];
    var desc_lastSuccess_{VIZID} = [];
    var desc_lastFailure_{VIZID} = [];
    
    //======================= show/hide description ===========================
    
    function showDescDiv_{VIZID}(row,colname) {{
        
        // find message
        switch (colname) {{
            case 'outcome':
                msg = desc_outcome_{VIZID}[row];
                break;
            case 'weather':
                msg = desc_weather_{VIZID}[row];
                break;
            case 'test':
                msg = desc_test_{VIZID}[row];
                break;
            case 'lastRun':
                msg = desc_lastRun_{VIZID}[row];
                break;
            case 'lastSuccess':
                msg = desc_lastSuccess_{VIZID}[row];
                break;
            case 'lastFailure':
                msg = desc_lastFailure_{VIZID}[row];
                break;
            default:
                console.log("ERROR: unexpected colname "+colname)
                return;
        }}
        
        // un-highlight header elements
        $('#row_outcome_{VIZID}_'+row    ).removeClass('selectedTest');
        $('#row_weather_{VIZID}_'+row    ).removeClass('selectedTest');
        $('#row_test_{VIZID}_'+row       ).removeClass('selectedTest');
        $('#row_lastRun_{VIZID}_'+row    ).removeClass('selectedTest');
        $('#row_lastSuccess_{VIZID}_'+row).removeClass('selectedTest');
        $('#row_lastFailure_{VIZID}_'+row).removeClass('selectedTest');
        
        // highlight selected element
        $('#row_'+colname+'_{VIZID}_'+row).addClass('selectedTest');
        
        // update callback
        $('#row_'+colname+'_{VIZID}_'+row).attr("onClick","hideDescDiv_{VIZID}("+row+")");
        
        // highlight and show description
        $('#descDiv_{VIZID}_'+row).html(msg).addClass('selectedTest').show();
    }}
    
    function hideDescDiv_{VIZID}(row) {{
        
        // un-highlight header elements
        $('#row_outcome_{VIZID}_'+row    ).removeClass('selectedTest');
        $('#row_weather_{VIZID}_'+row    ).removeClass('selectedTest');
        $('#row_test_{VIZID}_'+row       ).removeClass('selectedTest');
        $('#row_lastRun_{VIZID}_'+row    ).removeClass('selectedTest');
        $('#row_lastSuccess_{VIZID}_'+row).removeClass('selectedTest');
        $('#row_lastFailure_{VIZID}_'+row).removeClass('selectedTest');
        
        // un-highlight and hide description
        $('#descDiv_{VIZID}_'+row).removeClass('selectedTest').hide();
        
        // update all callbacks
        $('#row_outcome_{VIZID}_'+row).attr(    "onClick","showDescDiv_{VIZID}("+row+",\\'outcome\\')");
        $('#row_weather_{VIZID}_'+row).attr(    "onClick","showDescDiv_{VIZID}("+row+",\\'weather\\')");
        $('#row_test_{VIZID}_'+row).attr(       "onClick","showDescDiv_{VIZID}("+row+",\\'test\\')");
        $('#row_lastRun_{VIZID}_'+row).attr(    "onClick","showDescDiv_{VIZID}("+row+",\\'lastRun\\')");
        $('#row_lastSuccess_{VIZID}_'+row).attr("onClick","showDescDiv_{VIZID}("+row+",\\'lastSuccess\\')");
        $('#row_lastFailure_{VIZID}_'+row).attr("onClick","showDescDiv_{VIZID}("+row+",\\'lastFailure\\')");
    }}
    
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
                            updateTestResults_{VIZID}(response);
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
    
    function redrawTestResults_{VIZID}(numTests) {{
        
        // clear old contents
        document.getElementById('chart_div_{VIZID}').innerHTML = '';
        
        // start table
        $('<table/>', {{
            'class': 'testResultsTable_{VIZID}'
        }}).appendTo('#chart_div_{VIZID}');
        
        // headers
        $('<tr/>', {{
            html: '<th>S</th><th>W</th><th>Test Name</th><th>Last Run</th><th>Last Success</th><th>Last Failure</th>'
        }}).appendTo('.testResultsTable_{VIZID}');
        
        // rows
        for (var row = 0; row < numTests; row++) {{
            cells             = [];
            
            // outcome
            thisCell          = '';
            thisCell         += '<td id="row_outcome_{VIZID}_'+row+'">';
            thisCell         += '</td>';
            cells.push(thisCell);
            
            // weather
            thisCell          = '';
            thisCell         += '<td id="row_weather_{VIZID}_'+row+'">';
            thisCell         += '</td>';
            cells.push(thisCell);
            
            // test
            thisCell          = '';
            thisCell         += '<td id="row_test_{VIZID}_'+row+'"             class="clickableTest">';
            thisCell         += '</td>';
            cells.push(thisCell);
            
            // lastRun
            thisCell          = '';
            thisCell         += '<td id="row_lastRun_{VIZID}_'+row+'"          class="clickableTest">';
            thisCell         += '</td>';
            cells.push(thisCell);
            
            // lastSuccess
            thisCell          = '';
            thisCell         += '<td id="row_lastSuccess_{VIZID}_'+row+'"      class="clickableTest">';
            thisCell         += '</td>';
            cells.push(thisCell);
            
            // lastFailure
            thisCell          = '';
            thisCell         += '<td id="row_lastFailure_{VIZID}_'+row+'"      class="clickableTest">';
            thisCell         += '</td>';
            cells.push(thisCell);
            
            $('<tr/>', {{
                html: cells.join('')
            }}).appendTo('.testResultsTable_{VIZID}');
            
            // descDiv
            $('<tr/>', {{
                html: '<td colspan="6"><div id="descDiv_{VIZID}_'+row+'"></div></td>'
            }}).appendTo('.testResultsTable_{VIZID}');
            
            // hide description and set up onClick callbacks
            hideDescDiv_{VIZID}(row);
        }}
    }}
    
    function updateTestResults_{VIZID}(data) {{
        var divMsg;
        
        // draw for the first time
        if (data.length!=numTests_{VIZID}) {{
            numTests_{VIZID} = data.length;
            redrawTestResults_{VIZID}(data.length);
        }}
        
        // reset data
        desc_outcome_{VIZID}      = [];
        desc_weather_{VIZID}      = [];
        desc_test_{VIZID}         = [];
        desc_lastRun_{VIZID}      = [];
        desc_lastSuccess_{VIZID}  = [];
        desc_lastFailure_{VIZID}  = [];
        
        // update table
        for (var i = 0; i < data.length; i++) {{
            
            // outcome
            elem = $('#row_outcome_{VIZID}_'+i);
            desc = data[i].outcomeDesc
            elem.html('<img src="/static/testicons/'+data[i].outcomeIcon+'">');
            if (elem.hasClass('selectedTest')) {{
                divMsg = desc;
            }}
            desc_outcome_{VIZID}.push(desc);
            
            // weather
            elem = $('#row_weather_{VIZID}_'+i);
            desc = data[i].weatherDesc
            elem.html('<img src="/static/testicons/'+data[i].weatherIcon+'">');
            if (elem.hasClass('selectedTest')) {{
                divMsg = desc;
            }}
            desc_weather_{VIZID}.push(desc);
            
            // test
            elem = $('#row_test_{VIZID}_'+i   );
            desc = data[i].testDesc
            elem.html(data[i].testName);
            if (elem.hasClass('selectedTest')) {{
                divMsg = desc;
            }}
            desc_test_{VIZID}.push(desc);
            
            // lastRun
            elem = $('#row_lastRun_{VIZID}_'+i);
            desc = data[i].lastRunDesc
            elem.html(data[i].lastRun);
            if (elem.hasClass('selectedTest')) {{
                divMsg = desc;
            }}
            desc_lastRun_{VIZID}.push(desc);
            
            // lastSuccess
            elem = $('#row_lastSuccess_{VIZID}_'+i);
            desc = data[i].lastSuccessDesc
            elem.html(data[i].lastSuccess);
            if (elem.hasClass('selectedTest')) {{
                divMsg = desc;
            }}
            desc_lastSuccess_{VIZID}.push(desc);
            
            // lastFailure
            elem = $('#row_lastFailure_{VIZID}_'+i);
            desc = data[i].lastFailureDesc
            elem.html(data[i].lastFailure);
            if (elem.hasClass('selectedTest')) {{
                divMsg = desc;
            }}
            desc_lastFailure_{VIZID}.push(desc);
            
        }}
        
        // update description
        $('#descDiv_{VIZID}_'+i).html(divMsg)
        
        if ( {AUTOREFRESH}==false ) {{
            disableAutoRefresh('{VIZID}');
        }}
    }}
    
</script>
'''
