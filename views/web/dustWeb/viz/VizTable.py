import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizTable')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import Viz

class VizTable(Viz.Viz):
    
    #======================== libraries =======================================
    
    libraries      = [Viz.Viz.LIBRARY_JQUERY,
                      Viz.Viz.LIBRARY_DATATABLES]
    
    #======================== public ==========================================
    
    @classmethod
    def formatReturnVal(self,columnNames,data, width=None):
        if not width:
            width = [1./len(columnNames)]*len(columnNames)
        width = ["{:%}".format(w) if w else "auto" for w in width]
        return {
            "aoColumns": [
                {
                    "sTitle": cn,
                    "sWidth": w,
                } for cn, w in zip(columnNames, width)
            ],
            "aaData": data,
        }
    
    #======================== header ==========================================
    
    templateHeader = '''
<script type="text/javascript" src="/static/javascript/dataTables.fnReloadAjax.js"></script>
<link type="text/css" rel="stylesheet" href="/static/templates/datatables/css/jquery.dataTables.css"/>
'''
    
    #======================== body ============================================
    
    templateBody = '''
<script type='text/javascript'>
    
    var table_{VIZID},
        autorefresh_{VIZID};
    
    autorefresh_{VIZID} = true;
    
    $(document).ready(function() {{
        $.fn.dataTableExt.sErrMode = 'throw';
        $('#chart_div_{VIZID}').css('width','700px');
        $('#chart_div_{VIZID}').css('overflow','auto');
        $('#chart_div_{VIZID}').append('<table cellpadding="0" cellspacing="0" border="0" class="display" id="chart_table_{VIZID}"></table>');
        var statusDivId = 'status_div_{VIZID}';
        updateStatus(statusDivId,'busy','');
        $.getJSON( '/{RESOURCE}/', null, function (json) {{
            table_{VIZID} = $('#chart_table_{VIZID}').dataTable({{
                'sAjaxSource':         '/{RESOURCE}/',
                'aoColumns':           json.aoColumns,
                'bFilter':             false,
                'bPaginate':           false
            }});
            updateStatus(statusDivId,'success','');
        }}).error(function (error) {{
            updateStatus(statusDivId, 'failure', error.statusText);
        }});
    }});
    
    function updateTable_{VIZID}() {{
        if (autorefresh_{VIZID} && table_{VIZID}) {{
            var statusDivId = 'status_div_{VIZID}';
            updateStatus(statusDivId,'busy','');
            table_{VIZID}.fnReloadAjax(null, function(event){{
                if (event.jqXHR.status != 200) {{
                    updateStatus(statusDivId, 'failure', event.jqXHR.statusText);
                }} else {{
                    updateStatus(statusDivId,'success','');
                }}
            }});
        }}
    }}
    
    setInterval(updateTable_{VIZID},{RELOAD_PERIOD});
    
</script>
'''
