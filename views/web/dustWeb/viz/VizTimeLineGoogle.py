import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizTimeLine')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import VizGoogleCharts

class VizTimeLine(VizGoogleCharts.VizGoogleCharts):
    
    #======================== header ==========================================
    
    templateHeader = VizGoogleCharts.VizGoogleCharts.getHeaderTemplate(
                        PACKAGE       = 'corechart',
                        VISUALIZATION = 'LineChart',
                        EXTRAOPTIONS  = {
                                            'height': 500,
                                            'chartArea': '{{ width:   700,}}',
                                        }
                     )
