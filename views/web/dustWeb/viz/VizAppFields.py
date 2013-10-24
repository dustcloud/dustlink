import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizAppFields')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import VizjQuery

class VizAppFields(VizjQuery.VizjQuery):
    
    #======================== header ==========================================
    
    templateHeader = '''
<style type="text/css">
</style>
'''
    
    #======================== body ============================================
    
    templateBody = '''
<script type='text/javascript'>
    
    // global variables
    var transportOptions_{VIZID}  = ['UDP','OAP'];
    var endiannessOptions_{VIZID} = ['little-endian','big-endian'];
    var fieldFormatOptions_{VIZID}= ['INT8','INT8U','INT16','INT16U','INT32','INT32U'];
    var fieldRowCounter_{VIZID}   = 0;
    
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
                400: function(response) {{
                    updateStatus(statusDivId,'failure','Malformed: ' + response.responseText);
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
        
        // clear old contents
        document.getElementById('chart_div_{VIZID}').innerHTML = '';
        
        // description
        tempDiv = $('<div/>', {{
            'id': 'description_div_{VIZID}'
        }}).appendTo('#chart_div_{VIZID}');
        drawDescription_{VIZID}(tempDiv,data.description);
        
        // transport
        tempDiv = $('<div/>', {{
            'id': 'transport_div_{VIZID}'
        }}).appendTo('#chart_div_{VIZID}');
        drawTransport_{VIZID}(tempDiv,data.transport);
        
        // fromMote
        tempDiv = $('<div/>', {{
            'id': 'fromMote_div_{VIZID}'
        }}).appendTo('#chart_div_{VIZID}');
        drawFields_{VIZID}(tempDiv,'fromMote',data.fromMote);
        
        // toMote
        tempDiv = $('<div/>', {{
            'id': 'toMote_div_{VIZID}'
        }}).appendTo('#chart_div_{VIZID}');
        drawFields_{VIZID}(tempDiv,'toMote',data.toMote);
        
        // button
        $('<button/>', {{
            'onclick': 'postFormData_{VIZID}()',
            'html':    'Submit'
        }}).appendTo('#chart_div_{VIZID}');
    }}
    
    function drawDescription_{VIZID}(divToPopulate,descriptionData) {{
        
        // title
        $('<h1/>', {{
            'html': 'Description'
        }}).appendTo(divToPopulate);
        
        // description
        $('<p/>', {{
            'html': 'Enter a description about your application.<br/>This description is for humans to read, and does not influence the operation of the program.'
        }}).appendTo(divToPopulate);
        
        $('<textarea/>', {{
            'rows':     3,
            'cols':     80,
            'html':     descriptionData,
            'id':       'descriptionElem_{VIZID}'
        }}).appendTo(divToPopulate);
    }}
    
    function drawTransport_{VIZID}(divToPopulate,transportData) {{
        
        var table,
            row,
            cell,
            cellBody,
            optidx;
        
        // title
        $('<h1/>', {{
            'html': 'Transport'
        }}).appendTo(divToPopulate);
        
        // description
        $('<p/>', {{
            'html': 'Select the type of transport your mote application uses to send data.<br/>This website uses the information you enter to "listen" for data from your application.<br/>The meaning of the resource field depends on the type of transport chosen. For <strong>UDP</strong>, it is the port to listen to, i.e. an decimal integer smaller than 65535, e.g. "61626". For <strong>CoAP</strong>, it is a comma-separated list of OAP resources, e.g. "5,3".'
        }}).appendTo(divToPopulate);
        
        // create table
        $('<table/>', {{
            'id': 'transportTable_{VIZID}'
        }}).appendTo(divToPopulate);
        
        // add header
        $('<tr/>', {{
            html: '<th>type</th><th>resource</th>'
        }}).appendTo('#transportTable_{VIZID}');
        
        // populate the body
        // add row
        table                = document.getElementById("transportTable_{VIZID}");
        row                  = table.insertRow(-1);
        // type cell
        cellBody             = '';
        cellBody            += '<select';
        cellBody            += ' id="transportType_{VIZID}"';
        cellBody            += '>';
        for (optidx = 0; optidx < transportOptions_{VIZID}.length; optidx++) {{
            cellBody        += '<option value="'+transportOptions_{VIZID}[optidx]+'"';
            if (transportOptions_{VIZID}[optidx]==transportData.type) {{
                cellBody    += ' selected="selected"';
            }}
            cellBody        += '>';
            cellBody        += transportOptions_{VIZID}[optidx];
            cellBody        += '</option>';
        }}
        cellBody            += '</select>';
        cell                 = row.insertCell(-1);
        cell.innerHTML       = cellBody
        // resource cell
        cellBody             = '';
        cellBody            += '<input type="text"';
        cellBody            += ' id="transportResource_{VIZID}"';
        cellBody            += ' value="'+transportData.resource+'"';
        cellBody            += '/>';
        cell                 = row.insertCell(-1);
        cell.innerHTML       = cellBody
    }}
    
    function drawFields_{VIZID}(divToPopulate,direction,fieldsData) {{
        
        // title
        $('<h1/>', {{
            'html': 'Fields '+direction
        }}).appendTo(divToPopulate);
        
        // description
        $('<p/>', {{
            'html': 'Select whether the multi-byte fields you enter below are encoded little-endian or big-endian.'
        }}).appendTo(divToPopulate);
        
        // endianness
        selector = $('<select/>', {{
            'id': 'endiannessSelector_{VIZID}'
        }}).appendTo(divToPopulate);
        for (optidx = 0; optidx < endiannessOptions_{VIZID}.length; optidx++) {{
            optionString          = ''
            optionString         += '<option value="'+endiannessOptions_{VIZID}[optidx]+'"'
            if (fieldsData.endianness==endiannessOptions_{VIZID}[optidx]) {{
                optionString     += ' selected'
            }}
            optionString         += '>'
            optionString         += endiannessOptions_{VIZID}[optidx]
            optionString         += '</option>'
            selector.append(optionString)
        }}
        selector.appendTo(divToPopulate);
        
        // description
        $('<p/>', {{
            'html': 'Enter the fields present in this application\\'s payload.'
        }}).appendTo(divToPopulate);
        
        // create table
        $('<table/>', {{
            'id': 'fieldsTable_{VIZID}_'+direction
        }}).appendTo(divToPopulate);
        
        // add header
        $('<tr/>', {{
            html: '<th>format</th><th>name</th><th>action</th>'
        }}).appendTo('#fieldsTable_{VIZID}_'+direction);
        
        // "add" row at end
        $('<tr/>', {{
            html: '<td></td><td></td><td><a onClick="addFieldRow_{VIZID}(\\''+direction+'\\',\\'\\',\\'\\',\\'\\')">add</a></td>'
        }}).appendTo('#fieldsTable_{VIZID}_'+direction);
        
        // populate the body (do last)
        for (var i = 0; i < fieldsData.fieldRows.length; i++) {{
            addFieldRow_{VIZID}(
                direction,
                fieldsData.fieldRows[i].format,
                fieldsData.fieldRows[i].name
            );
        }}
    }}
    
    function addFieldRow_{VIZID}(direction,format,name) {{
        var table,
            row,
            cell,
            cellBody
            optidx;
        
        // add row
        table                = document.getElementById("fieldsTable_{VIZID}_"+direction);
        row                  = table.insertRow(table.rows.length-1);
        row.id               = 'fieldsTable_{VIZID}_'+direction+'_row_'+fieldRowCounter_{VIZID};
        
        // format cell
        cellBody             = '';
        cellBody            += '<select';
        cellBody            += ' class="fieldTableElems_{VIZID}_'+direction+'"';
        cellBody            += '>';
        for (optidx = 0; optidx < fieldFormatOptions_{VIZID}.length; optidx++) {{
            cellBody        += '<option value="'+fieldFormatOptions_{VIZID}[optidx]+'"';
            if (fieldFormatOptions_{VIZID}[optidx]==format) {{
                cellBody    += ' selected="selected"';
            }}
            cellBody        += '>';
            cellBody        += fieldFormatOptions_{VIZID}[optidx];
            cellBody        += '</option>';
        }}
        cellBody            += '</select>';
        cell                 = row.insertCell(-1);
        cell.innerHTML       = cellBody
        
        // name cell
        cellBody             = '';
        cellBody            += '<input type="text"';
        cellBody            += ' value="'+name+'"';
        cellBody            += ' class="fieldTableElems_{VIZID}_'+direction+'"';
        cellBody            += '/>';
        cell                 = row.insertCell(-1);
        cell.innerHTML       = cellBody
        
        // action cell
        cellBody             = '';
        cellBody            += '<a onClick="deleteFieldRow_{VIZID}(\\''+direction+'\\','+fieldRowCounter_{VIZID}+')">delete</a>';
        cell                 = row.insertCell(-1);
        cell.innerHTML       = cellBody
        
        fieldRowCounter_{VIZID}++;
    }}
    
    function deleteFieldRow_{VIZID}(direction,rowCounter) {{
        var i,
            found,
            table,
            row;
        
        table           = document.getElementById("fieldsTable_{VIZID}_"+direction);
        found           = false;
        for (i = 0; row = table.rows[i]; i++) {{
            if (row.id=='fieldsTable_{VIZID}_'+direction+'_row_'+rowCounter) {{
                found = true;
                break;
            }}
        }}
        
        if (found) {{
            table.deleteRow(i);
        }} else {{
            console.log('ERROR: row '+rowCounter+' not found.');
        }}
    }}
    
    //======================= post from data ==================================
    
    function postFormData_{VIZID}() {{
        
        var statusDivId,
            fieldElems,
            dataToSend,
            i,
            fieldName,
            fieldValue;
        
        //===== update the status message
        statusDivId = 'status_div_{VIZID}';
        updateStatus(statusDivId,'busy', '');
        
        //===== build data to send
        
        dataToSend = {{}};
        
        // description
        dataToSend['description'] = document.getElementById("descriptionElem_{VIZID}").value;
        
        
        // transport
        dataToSend['transport']             = {{}};
        dataToSend['transport']['type']     = document.getElementById("transportType_{VIZID}").value;
        dataToSend['transport']['resource'] = document.getElementById("transportResource_{VIZID}").value;
        
        // fromMote
        dataToSend['fromMote']                   = {{}};
        dataToSend['fromMote']['endianness']     = document.getElementById("endiannessSelector_{VIZID}").value;
        dataToSend['fromMote']['fieldRows']      = [];
        fieldElems = document.getElementsByClassName('fieldTableElems_{VIZID}_fromMote');
        for (i=0; i<fieldElems.length/2; i++) {{
            dataToSend['fromMote']['fieldRows'].push(
                {{
                    'format':     fieldElems[2*i+0].value,
                    'name':       fieldElems[2*i+1].value
                }}
            )
        }}
        
        // toMote
        dataToSend['toMote']                     = {{}};
        dataToSend['toMote']['endianness']       = document.getElementById("endiannessSelector_{VIZID}").value;
        dataToSend['toMote']['fieldRows']        = [];
        fieldElems = document.getElementsByClassName('fieldTableElems_{VIZID}_toMote');
        for (i=0; i<fieldElems.length/2; i++) {{
            dataToSend['toMote']['fieldRows'].push(
                {{
                    'format':     fieldElems[2*i+0].value,
                    'name':       fieldElems[2*i+1].value
                }}
            )
        }}
        
        //===== send data to server
        jQuery.ajax({{
            type:       'POST',
            url:        '/{RESOURCE}/',
            timeout:    5*1000,
            data:       JSON.stringify(dataToSend),
            statusCode: {{
                200: function() {{
                    updateStatus(statusDivId,'success', '');
                }},
                400: function(response) {{
                    updateStatus(statusDivId,'failure','Malformed: ' + response.responseText);
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
