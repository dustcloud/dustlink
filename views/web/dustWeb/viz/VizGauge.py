import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizGauge')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import VizGoogleCharts

class VizGauge(VizGoogleCharts.VizGoogleCharts):
    
    #======================== header ==========================================
    
    templateHeader = VizGoogleCharts.VizGoogleCharts.getHeaderTemplate(
                        PACKAGE       = 'gauge',
                        VISUALIZATION = 'Gauge',
                        EXTRAOPTIONS  = {
                                            'height' :     250,
                                            'width' :      750,
                                            'redFrom' :    90,
                                            'redTo' :      100,
                                            'yellowFrom' : 75,
                                            'yellowTo' :   90,
                                            'minorTicks' : 5,
                                        }
                     )
