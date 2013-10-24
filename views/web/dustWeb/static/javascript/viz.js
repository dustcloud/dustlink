var STATUS = {
      BUSY    : 'busy',
      FAILURE : 'failure',
      SUCCESS : 'success'
}

function Viz(VIZID, RESOURCE, reloadPeriod) {
   Viz.prototype.init.call(this, VIZID, RESOURCE, reloadPeriod);
}
Viz.prototype.init = function(VIZID, RESOURCE, reloadPeriod) {
   this.VIZID = VIZID;
   this.RESOURCE = RESOURCE;
   this.reloadPeriod = reloadPeriod;
}

Viz.prototype.getVizID = function() {
   return this.VIZID;
}
Viz.prototype.getResource = function() {
   return this.RESOURCE;
}
Viz.prototype.getReloadPeriod = function() {
   return this.reloadPeriod;
}

Viz.prototype.setStatus = function(status, message) {
   updateStatus('status_div_' + this.getVizID(), status, message);
}

//=========================== VizTopology =====================================

function Topology(VIZID, RESOURCE, reloadPeriod) {
   Topology.prototype.init.call(this, VIZID, RESOURCE, reloadPeriod);
}
Topology.prototype = new Viz;

Topology.prototype.init = function(VIZID, RESOURCE, reloadPeriod) {
   Viz.call(this, VIZID, RESOURCE, reloadPeriod);
   this.inputGraph = document.querySelector("#input_" + VIZID);
   this.chartError = document.querySelector("#chart_error_" + VIZID);
   this.svg = d3.select("#topology_" + VIZID);
   this.svgGroup = this.svg.append("g").attr("transform", "translate(5, 5)");
   this.oldInputValue = null;

   var that = this;
   $(document).ready(function() {
      that.updateInput();
      // periodically refresh the topology
      setInterval(function() {
         that.updateInput()
      }, 2000);
   });
}

Topology.prototype.spline = function(points) {
   var line = d3.svg.line().x(function(d) {
      return d.x;
   }).y(function(d) {
      return d.y;
   }).interpolate("basis")(points);
   var curves = line.split("C");
   var last = curves.pop();
   line = curves.join("C");
   var points = last.split(",");
   line += "L" + points.slice(points.length - 2).join(",");
   return line;
}

Topology.prototype.updateInput = function() {
   var that = this;

   if (window["autorefresh_" + this.getVizID()]) {
      this.setStatus('busy', '');
      $('#input_' + this.getVizID()).load(this.getResource(), '', function(responseText, textStatus, XMLHttpRequest) {
         if (status == "error") {
            that.setStatus(STATUS.FAILURE, 'Resource not found.');
         } else {
            that.setStatus(STATUS.SUCCESS, '');
            that.tryDraw();
         }
      });
   }
}

Topology.prototype.tryDraw = function() {
   var that = this;
   var result;

   if ((this.oldInputValue !== this.inputGraph.value) && this.inputGraph.value) {
      this.oldInputValue = this.inputGraph.value;
      try {
         result = dagre.dot.toObjects(this.inputGraph.value);
      } catch (e) {
         console.log("ERROR: parsing DOT content.");
         console.log(e);
         console.log(this.inputGraph.value);
         //this.chartError.innerHTML = e.toString();
         //this.chartError.setAttribute("class", "error");
      }
   }

   if (result) {
      this.svgGroup.selectAll().remove();
      
      // Get the data in the right form
      var graphNodes = result.nodes;
      var graphEdges = result.edges;
      
      this.svgGroup.selectAll("g").remove();
      this.svgGroup.selectAll("path").remove();
      
      // `nodes` is center positioned for easy layout later
      var nodes = this.svgGroup.selectAll("g .node").data(graphNodes).enter()
            .append("g").attr("class", "node").attr("id", function(d) {
               return "node-" + d.id;
            });
      
      nodes.append("svg:title").text(function(d) {
         return d.description
      });
      
      var edges = this.svgGroup.selectAll("path .edge").data(graphEdges)
            .enter().append("path").attr("class", "edge").attr("id",
                  function(d) {
                     return "edge-" + d.id;
                  });
      // .attr("marker-end", "url(#arrowhead)");
      
      edges.append("svg:title").text(function(d) {
         return d.description
      });
      
      // Append rectangles to the nodes. We do this before laying out the
      // labels
      // because we want the text above the rectangle.
      var rects = nodes.append("rect");
      rects.attr("class", function(d) {
         return ('class' in d) ? d['class'] : '';
      });
      
      // Append labels
      var labels = nodes.append("g").attr("class", "label");
      
      nodes.selectAll("g .label").append("a").attr(
            "xlink:href", function(d) {
               return "/motes/_" + d.macAddress;
            }).append("text").attr("text-anchor", "left").append("tspan").attr(
            "dy", "1em").text(function(d) {
         return d.label;
      }).each(function(d) {
         d.nodePadding = 10;
      });
      
      // We need width and height for layout.
      labels.each(function(d) {
         var bbox = this.getBBox();
         d.bbox = bbox;
         d.width = bbox.width + 2 * d.nodePadding;
         d.height = bbox.height + 2 * d.nodePadding;
      });
      
      rects.attr("x", function(d) {
         return -(d.bbox.width / 2 + d.nodePadding);
      }).attr("y", function(d) {
         return -(d.bbox.height / 2 + d.nodePadding);
      }).attr("width", function(d) {
         return d.width;
      }).attr("height", function(d) {
         return d.height;
      });
      
      labels.attr("transform", function(d) {
         return "translate(" + (-d.bbox.width / 2) + "," + (-d.bbox.height / 2)
               + ")";
      });
      
      dagre.layout().nodeSep(50).edgeSep(10).rankSep(30).nodes(graphNodes)
            .edges(graphEdges).run();

      nodes.attr("transform", function(d) {
         return "translate(" + d.dagre.x + "," + d.dagre.y + ")";
      });
      
      edges.attr("d", function(e) {
         var points = e.dagre.points;
         var source = dagre.util.intersectRect(e.source.dagre,
               points.length > 0 ? points[0] : e.source.dagre);
         var target = dagre.util.intersectRect(e.target.dagre,
               points.length > 0 ? points[points.length - 1] : e.source.dagre);
         points.unshift(source);
         points.push(target);
         return that.spline(points);
      });
      
      // Resize the SVG element
      var svgBBox = this.svg.node().getBBox();
      this.svg.call(d3.behavior.zoom().on(
            "zoom",
            function redraw() {
               that.svgGroup.attr("transform", "translate("
                     + d3.event.translate + ")" + " scale(" + d3.event.scale
                     + ")");
            }));
      
      // Print metrics
      // d3.select("#graphTime").text("Parse time: " + (parseEnd -
      // parseStart) + "ms. Layout time: " + (layoutEnd - layoutStart) +
      // "ms.");

   }
}

//=========================== VizFields =======================================

//===== getting data

function VizFields(VIZID, RESOURCE, reloadPeriod, autoRefresh) {
   VizFields.prototype.init.call(this, VIZID, RESOURCE, reloadPeriod, autoRefresh);
}
VizFields.prototype = new Viz;
VizFields.prototype.init = function(VIZID, RESOURCE, reloadPeriod, autoRefresh) {
   Viz.call(this, VIZID, RESOURCE, reloadPeriod);
   this.autoRefresh = autoRefresh;
   var that = this;
   $(document).ready(function() {
      that.getData();
      // periodically refresh the topology
      if (that.getReloadPeriod() > 0) {
         setInterval(function() {
            if (window["autorefresh_"+that.getVizID()]) {
               that.getData()
            }
         }, that.getReloadPeriod());
      }
   });
}

VizFields.prototype.getData = function() {
   
   var statusDivId;
   var that = this;
   // update the status message
   this.setStatus(STATUS.BUSY, '');

   // get updated data from the server and execute
   jQuery.ajax({
      type : 'GET',
      url : '/' + this.RESOURCE + '/',
      timeout : 5 * 1000,
      statusCode : {
         200 : function(response) {
            try {
               that.updateDataTable(response);
            } catch (err) {
               if (err == 'unknown cell') {
                  that.drawDataTable(response);
               } else {
                  throw err;
               }
            }
            that.setStatus(STATUS.SUCCESS, '');
         },
         400 : function() {
            that.setStatus(STATUS.FAILURE, 'Malformed.');
         },
         401 : function() {
            that.setStatus(STATUS.FAILURE, 'Access denied.');
         },
         404 : function() {
            that.setStatus(STATUS.FAILURE, 'Resource not found.');
         },
         500 : function() {
            that.setStatus(STATUS.FAILURE, 'Internal server error.');
         }
      },
      error : function(jqXHR, textStatus, errorThrown) {
         if (textStatus == 'timeout') {
            that.setStatus(STATUS.FAILURE, 'Server unreachable.');
         }
      }
   });
}

VizFields.prototype.updateDataTable = function(data) {
   var i,
       optidx,
       elem;

   for (i = 0; i < data.length; i++) {
      elem = document.getElementById('fieldTable_'+this.getVizID()+'_'+data[i].name);
      
      if (elem==null) {
         throw 'unknown cell';
      }
      
      if        (elem.type=='text') {
         elem.value   = data[i].value;
      } else if (elem.type=='checkbox') {
         elem.checked = data[i].value;
      } else if (elem.type=='select-one') {
         for (optidx = 0; optidx < elem.length; optidx++) {
            if (elem.options[optidx].value==data[i].value) {
               elem.selectedIndex = optidx;
            }
         }
      } else if (elem.type=='submit') {
         elem.innerHTML   = data[i].value;
      } else {
         console.log('WARNING update: unexpected elem.type '+elem.type);
      }
   }
}

VizFields.prototype.drawDataTable = function(data) {
   var thisCell, cells = [];
   var that = this;
   
   // clear old contents
   document.getElementById('chart_div_' + this.getVizID()).innerHTML = '';

   // draw new table
   var table = $('<table/>', {
      'class' : 'fieldDataTable_' + this.getVizID()
   }).appendTo('#chart_div_' + this.getVizID());

   for ( var i = 0; i < data.length; i++) {
      var tr = $("<tr />");
      // name
      var td = $('<td />').text(data[i].name);
      tr.append(td);
      // field
      var fieldId = 'fieldTable_' + this.getVizID() + '_' + data[i].name;
      if (data[i].type == 'text') {
         td = $("<td />");
         var input = $("<input />", {
            "id" : fieldId,
            "name" : data[i].name,
            "value" : data[i].value
         });
         if (data[i].editable) {
            input.focusout(function() {
               that.postDataChange(this);
            });
            input.focus(function() {
               disableAutoRefresh(that.getVizID());
            });
         } else {
            input.attr("disabled", "disabled");
         }
         td.append(input);
         tr.append(td);
      } else if (data[i].type == 'boolean') {
         td = $("<td />");
         var input = $("<input/>", {
            "id" : fieldId,
            "name" : data[i].name,
            "type" : "checkbox"
         });

         if (data[i].value == true) {
            input.attr("checked", "checked");
         }
         if (data[i].editable) {
            input.click(function() {
               that.postDataChange(this);
            });
         } else {
            input.attr("disabled", "disabled");
         }
         td.append(input);
         tr.append(td);
      } else if (data[i].type == 'select') {
         td = $("<td />");
         var select = $("<select />", {
            "id" : fieldId,
            "name" : data[i].name
         });
         if (data[i].editable) {
            select.change(function() {
               that.postDataChange(this);
            });
            select.focus(function() {
               disableAutoRefresh(that.getVizID());
            });
         } else {
            select.attr("disabled", "disabled");
         }
         for (var optidx = 0; optidx < data[i].optionDisplay.length; optidx++) {
            var option = $("<option />", {
               "value" : data[i].optionValue[optidx]
            });
            if (data[i].optionValue[optidx] == data[i].value) {
               option.attr("selected", "selected");
            }
            option.text(data[i].optionDisplay[optidx]);
            select.append(option);
         }
         td.append(select);
         tr.append(td);
      } else if (data[i].type == 'button') {
         td = $("<td />");
         var button = $("<button />", {
            "id" :   fieldId,
            "name" : data[i].name,
            "html":  data[i].value
         });
         button.click(function() {
            that.postDataChange(this);
         });
         td.append(button);
         tr.append(td);
      } else {
         td = $("<td />").text('WARNING unknown type: ' + data[i].type);
         tr.append(td);
      }
      // status
      td = $('<td>'+
               '<div id="' + fieldId + '_status">'+
                  '<svg class="hide" width="20" height="16">'+
                    '<circle cx="8" cy="6" r="5" stroke="black" stroke-width="1"/>'+
                  '</svg>'+
                  '<span class="viz-status-message"></span>'+
               '</div>'+
            '</td>');
      
      tr.append(td);
      table.append(tr);
   }
}

//===== post changes

VizFields.prototype.postDataChange = function(field) {
   
   var statusDivId,
       fieldName,
       fieldValue;
    
   // update the status message
   statusDivId = field.id+'_status';
   updateStatus(statusDivId,'busy', '');
   
   // post the change
   fieldName  = field.name;
   if         (field.type=='text') {
      fieldValue = field.value;
   } else if (field.type=='checkbox') {
      fieldValue = field.checked;
   } else if (field.type=='select-one') {
      fieldValue = field.options[field.selectedIndex].value;
   } else if (field.type=='submit') {
      fieldValue = 1;
   } else {
      console.log('WARNING post: unexpected field.type '+field.type);
   }
   jQuery.ajax({
      type:       'POST',
      url:        '/'+this.RESOURCE+'/',
      timeout:    5*1000,
      data:       {
         fieldName:  fieldName,
         fieldValue: fieldValue
      },
      statusCode: {
         200: function() {
            updateStatus(statusDivId,'success', '');
         },
         400: function() {
            updateStatus(statusDivId,'failure','Malformed.');
         },
         401: function() {
            updateStatus(statusDivId,'failure','Access denied.');
         },
         404: function() {
            updateStatus(statusDivId,'failure','Resource not found.');
         },
         500: function() {
            updateStatus(statusDivId,'failure','Internal server error.');
         }
      },
      error: function(jqXHR, textStatus, errorThrown) {
         if (textStatus=='timeout') {
            updateStatus(statusDivId,'failure','Server unreachable.');
         }
      }
   });
   
   // enable the update
   if (this.autoRefresh) {
      enableAutoRefresh(this.getVizID());
   }
}

//======================= helpers =========================================

VizFields.prototype.drawRawData = function() {
   
   var cells;
   
   $('<table/>', {
      'class': 'rawDataTable_'+this.getVizID()
   }).appendTo('#chart_div_'+this.getVizID());
   
   cells = [];
   $.each(response[0], function(key, val) {
      cells.push('<th>'+ key +'</th>');
   });
   $('<tr/>', {
      html: cells.join('')
   }).appendTo('.rawDataTable_'+this.getVizID());
   
   for (var i = 0; i < response.length; i++) {
      cells = [];
      $.each(response[i], function(key, val) {
         cells.push('<td>'+ val + '</td>');
      });
      $('<tr/>', {
         html: cells.join('')
      }).appendTo('.rawDataTable_'+this.getVizID());
   }
}



