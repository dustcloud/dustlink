import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizScatterPlot')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import VizGoogleCharts

class VizScatterPlot(VizGoogleCharts.VizGoogleCharts):
    
    #======================== header ==========================================
    
    templateHeader = VizGoogleCharts.VizGoogleCharts.getHeaderTemplate(
                        PACKAGE       = 'corechart',
                        VISUALIZATION = 'ScatterChart',
                        EXTRAOPTIONS  = {
                                            'height': 500,
                                            'hAxis' : '{{title: \'X\'}}',
                                            'vAxis' : '{{title: \'Y\'}}',
                                            'legend': '\'none\'',
                                        }
                     )
