import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizBarChart')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import VizGoogleCharts

class VizBarChart(VizGoogleCharts.VizGoogleCharts):
    
    #======================== header ==========================================
    
    templateHeader = VizGoogleCharts.VizGoogleCharts.getHeaderTemplate(
                        PACKAGE       = 'corechart',
                        VISUALIZATION = 'ColumnChart',
                        EXTRAOPTIONS  = {
                                            'height': 500,
                                        }
                     )