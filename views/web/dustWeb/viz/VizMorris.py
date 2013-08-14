import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizMorris')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import Viz

class VizMorris(Viz.Viz):
    
    #======================== libraries =======================================
    
    libraries      = [Viz.Viz.LIBRARY_JQUERY,
                      Viz.Viz.LIBRARY_RAPHAEL,
                      Viz.Viz.LIBRARY_MORRIS]