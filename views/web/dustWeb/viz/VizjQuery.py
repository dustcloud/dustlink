import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizjQuery')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import Viz

class VizjQuery(Viz.Viz):
    
    #======================== libraries =======================================
    
    libraries      = [Viz.Viz.LIBRARY_JQUERY, Viz.Viz.LIBRARY_VIZ,]