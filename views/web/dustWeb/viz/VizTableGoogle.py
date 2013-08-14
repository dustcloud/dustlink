import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizTable')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import VizGoogleCharts

class VizTable(VizGoogleCharts.VizGoogleCharts):
    
    #======================== header ==========================================
    
    templateHeader = VizGoogleCharts.VizGoogleCharts.getHeaderTemplate(
                        PACKAGE       = 'table',
                        VISUALIZATION = 'Table',
                        EXTRAOPTIONS  = {
                                            'allowHtml':        'true',
                                            'showRowNumber':    'true',
                                            'width' :           700,
                                        }
                     )
