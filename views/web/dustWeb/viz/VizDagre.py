import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizDagre')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import Viz

class VizDagre(Viz.Viz):
    
    #======================== libraries =======================================
    
    libraries      = [Viz.Viz.LIBRARY_DAGRE, Viz.Viz.LIBRARY_JQUERY, Viz.Viz.LIBRARY_D3, Viz.Viz.LIBRARY_VIZ,]