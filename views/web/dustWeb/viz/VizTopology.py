import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('VizTopology')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import VizDagre

class VizTopology(VizDagre.VizDagre):
    
    #======================== header ==========================================
    
    templateHeader = '''
<style type="text/css">
.node rect {{
  stroke-width: 0.15em;
  stroke: #333;
  fill: #fff;
}}

svg.topology {{
/*    border: solid grey 1px; */
}}

path.edge {{
  fill: none;
  stroke: #555;
  stroke-width: 0.15em;
}}
path.edge:hover {{
  stroke-width: 0.3em;
  stroke: #8AD;
}}

.node .manager {{
  fill: #aaccff;
}}
.node .disconnected {{
  fill: #CCC;
}}
</style>
'''
    
    #======================== body ============================================
    # based on mbostock.github.com/d3/talk/20111018/tree.html

    templateBody = '''
<svg width="{WIDTH}" height="{HEIGHT}" id="topology_{VIZID}" class="topology">
  <defs>
    <marker id="arrowhead"
            viewBox="0 0 10 10"
            refX="8"
            refY="5"
            markerUnits="strokeWidth"
            markerWidth="8"
            markerHeight="5"
            orient="auto"
            style="fill: #333">
      <path d="M 0 0 L 10 5 L 0 10 z"></path>
    </marker>
  </defs>
</svg>
<textarea id="input_{VIZID}" rows="15" cols="80" style="display: none;" onKeyUp="">
</textarea>
<script type="text/javascript" charset="utf-8">
var topoology_{VIZID} = new Topology('{VIZID}', '/{RESOURCE}/');
</script>
'''
    