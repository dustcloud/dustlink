import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizForm')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import VizjQuery

class VizForm(VizjQuery.VizjQuery):
    
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
    
    //======================= get form ========================================
    
    function getData_{VIZID}() {{
        
        var statusDivId;
        
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
                        drawForm_{VIZID}(response);
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
    
    function drawForm_{VIZID}(data) {{
        var cells,
            thisCell,
            fieldId;
        
        // clear old contents
        document.getElementById('chart_div_{VIZID}').innerHTML = '';
        
        // draw new table
        $('<table/>', {{
            'class': 'formTable_{VIZID}'
        }}).appendTo('#chart_div_{VIZID}');
        for (var i = 0; i < data.length; i++) {{
            cells             = [];
            // name
            thisCell          = '';
            thisCell         += '<td>';
            thisCell         += data[i].name;
            thisCell         += '</td>';
            cells.push(thisCell);
            // field
            fieldId = 'fieldTable_{VIZID}_'+data[i].name
            if         (data[i].type=='text') {{
                thisCell      = '';
                thisCell     += '<td>';
                thisCell     += '<input type="text"';
                thisCell     += ' id="'+fieldId+'"';
                thisCell     += ' name="'+data[i].name+'"';
                thisCell     += ' value="'+data[i].value+'"';
                thisCell     += ' class="formElems_{VIZID}"';
                thisCell     += '/>';
                thisCell     += '</td>';
            }} else if (data[i].type=='password') {{
                thisCell      = '';
                thisCell     += '<td>';
                thisCell     += '<input type="password"';
                thisCell     += ' id="'+fieldId+'"';
                thisCell     += ' name="'+data[i].name+'"';
                thisCell     += ' value="'+data[i].value+'"';
                thisCell     += ' class="formElems_{VIZID}"';
                thisCell     += '/>';
                thisCell     += '</td>';
            }} else if (data[i].type=='boolean') {{
                thisCell      = '';
                thisCell     += '<td>';
                thisCell     += '<input type="checkbox"';
                thisCell     += ' id="'+fieldId+'"';
                thisCell     += ' name="'+data[i].name+'"';
                thisCell     += ' class="formElems_{VIZID}"';
                if (data[i].value==true) {{
                    thisCell += ' checked ';
                }}
                thisCell     += '/>';
                thisCell     += '</td>';
            }} else if (data[i].type=='select') {{
                thisCell      = '';
                thisCell     += '<td>';
                thisCell     += '<select';
                thisCell     += ' id="'+fieldId+'"';
                thisCell     += ' name="'+data[i].name+'"';
                thisCell     += ' class="formElems_{VIZID}"';
                thisCell     += '>';
                for (var optidx = 0; optidx < data[i].optionDisplay.length; optidx++) {{
                    thisCell += '<option value="'+data[i].optionValue[optidx]+'"';
                    if (data[i].optionValue[optidx]==data[i].value) {{
                        thisCell += ' selected="selected"';
                    }}
                    thisCell += '>';
                    thisCell += data[i].optionDisplay[optidx];
                    thisCell += '</option>';
                }}
                thisCell     += '</select>';
                thisCell     += '</td>';
            }} else {{
                thisCell      = '';
                thisCell     += '<td>';
                thisCell     += 'WARNING unknown type: '+data[i].type;
                thisCell     += '</td>';
            }}
            cells.push(thisCell);
            // status
            thisCell          = '';
            thisCell         += '<td>';
            thisCell         += '<div id="'+fieldId+'_status"></div>';
            thisCell         += '</td>';
            cells.push(thisCell);
            $('<tr/>', {{
                html: cells.join('')
            }}).appendTo('.formTable_{VIZID}');
        }}
        
        $('<tr/>', {{
            html: '<button onclick="postFormData_{VIZID}()">Submit</button>'
        }}).appendTo('.formTable_{VIZID}');
    }}
    
    //======================= post from data ==================================
    
    function postFormData_{VIZID}() {{
        
        var statusDivId,
            formElems,
            dataToSend,
            i,
            fieldName,
            fieldValue;
        
        // update the status message
        statusDivId = 'status_div_{VIZID}';
        updateStatus(statusDivId,'busy', '');
        
        // build data to send
        
        formElems = document.getElementsByClassName('formElems_{VIZID}');
        
        dataToSend = {{}};
        
        for (i=0; i<formElems.length; i++) {{
            fieldName  = formElems[i].name;
            if         (formElems[i].type=='text') {{
                fieldValue = formElems[i].value;
            }} else if (formElems[i].type=='password') {{
                fieldValue = formElems[i].value;
            }} else if (formElems[i].type=='checkbox') {{
                fieldValue = formElems[i].checked;
            }} else if (formElems[i].type=='select-one') {{
                fieldValue = formElems[i].options[formElems[i].selectedIndex].value;
            }} else {{
                console.log('WARNING: in post, unexpected type '+formElems[i].type);
            }}
            dataToSend[fieldName] = fieldValue;
        }}
        
        jQuery.ajax({{
            type:       'POST',
            url:        '/{RESOURCE}/',
            timeout:    5*1000,
            data:       JSON.stringify(dataToSend),
            statusCode: {{
                200: function() {{
                    updateStatus(statusDivId,'success', '');
                    location.reload();
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
    
</script>
'''

    def __init__(self, **kw):
        super(VizForm, self).__init__(forbidAutorefresh=True, autorefresh=False, **kw)
