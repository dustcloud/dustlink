import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizD3')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import Viz

class VizD3(Viz.Viz):
    
    #======================== libraries =======================================
    
    libraries      = [Viz.Viz.LIBRARY_D3,]