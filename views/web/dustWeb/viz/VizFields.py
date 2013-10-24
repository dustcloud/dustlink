import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizFields')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import VizjQuery

class VizFields(VizjQuery.VizjQuery):
    
    #======================== header ==========================================
    
    templateHeader = '''
<style type="text/css">
</style>
'''
    
    #======================== body ============================================
    
    templateBody = '''
<script type='text/javascript'>
    autorefresh_{VIZID} = {AUTOREFRESH};
    var fields = new VizFields('{VIZID}', '{RESOURCE}', {RELOAD_PERIOD}, {AUTOREFRESH});
</script>
'''
