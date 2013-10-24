//========== setup

// make sure IE does not return cached results.
jQuery.ajaxSetup({ cache: false });

//========== defines

var dashboardData  = [];
var dashboardElems = [];

//=========================== admin ===========================================

function refreshDashboard() {
   // get new data
   getNewDashboardData();
}
function refreshDashboard_cb(newInput) {
   var redraw;
   
   newData    = newInput['data'];
   
   // decide whether to update or redraw
   redraw = false;
   if (newData.length==0 || newData.length!=dashboardData.length) {
      redraw = true;
   } else {
      for (var i = 0; i < newData.length; i++) {
         if (
               newData[i].mac    != dashboardData[i].mac   ||
               newData[i].type   != dashboardData[i].type
            ) {
            redraw = true;
            break;
         }
      }
   }
   
   // store newData as dashboardData
   dashboardData = newData;
   
   // refresh the dashboard
   if (redraw) {
      redrawDashboard();
   } else {
      updateDashboard();
   }
}

//=========================== redraw/update ===================================

/*
This functions is needed because one VizPressure widget is used for 2 pressure
readings.
*/
function getPressureViz() {
   returnVal = null;
   for (var e = 0; e < dashboardElems.length; e++) {
      if (dashboardElems[e] instanceof VizPressure) {
         returnVal = dashboardElems[e];
      }
   }
   return returnVal;
}

function redrawDashboard() {
   
   // clear the dashboard
   document.getElementById('demodashboard').innerHTML = '';    // html
   dashboardElems = [];                                        // elems
   
   // create the elements
   for (var i = 0; i < dashboardData.length; i++) {
      switch(dashboardData[i].type) {
         case 'pressure':
            if (getPressureViz()==null) {
               dashboardElems.push(
                  new VizPressure(
                     dashboardData[i]
                  )
               );
            } else {
               dashboardElems.push(null);
            }
            break;
         case 'energysource':
            dashboardElems.push(
               new VizEnergySource(
                  dashboardData[i]
               )
            );
            break;
         case 'temperature':
            dashboardElems.push(
               new VizTemperature(
                  dashboardData[i]
               )
            );
            break;
         case 'voltage':
            dashboardElems.push(
               new VizVoltage(
                  dashboardData[i]
               )
            );
            break;
         case 'acceleration':
            dashboardElems.push(
               new VizAcceleration(
                  dashboardData[i]
               )
            );
            break;
         case 'led':
            dashboardElems.push(
               new VizLed(
                  dashboardData[i]
               )
            );
            break;
         default:
            console.log('WARNING: unexpected data type "'+dashboardData[i].type+'"');
      }
   }
   
   // update the dashboard
   updateDashboard();
}

function updateDashboard() {
   for (var i=0; i<dashboardData.length; i++) {
      if (dashboardData[i].type=='pressure') {
         getPressureViz().update(
            dashboardData[i]
         );
      } else {
         dashboardElems[i].update(
            dashboardData[i]
         );
      }
   }
}

function positionLogo() {
   $('#logo').offset(
      {
         top:  $(window).height()-80-20,
         left: $(window).width()-200-20
      }
   );
   $('#logo').css('z-index',-1);
   
   var theLightbox = $('<div id="lightbox"/>');
   var theShadow = $('<div id="lightbox-shadow"/>');
   $(theShadow).click(function(e){
      lightboxClose();
   });
   $('body').append(theShadow);
   $('body').append(theLightbox);
}

function lightboxClose() {
   $('#lightbox').hide();
   $('#lightbox-shadow').hide();
   $('#lightbox').empty();
}

function lightboxShow() {
   $('#lightbox').css('top', $(window).scrollTop() + 100 + 'px');
   $('#lightbox').show();
   $('#lightbox-shadow').show();
}

//========== visualizations

function toggleColors(vizId) {
   if ($('#viz_'+vizId).css('background-color')=="rgb(0, 150, 0)") {
      $('#viz_'+vizId).css('background-color','rgb(0, 100, 0)');
   } else {
      $('#viz_'+vizId).css('background-color','rgb(0, 150, 0)');
   }
}

//===== Viz

function Viz(data) {
   Viz.prototype.init.call(this,data);
}
Viz.prototype.init = function(data) {
}
Viz.prototype.createNewWidget = function(data) {
   
   // retrieve a unique identifier for this widget
   vizId = dashboardElems.length;
   
   var widgetId = 'widget_'+vizId;
   
   // widget
   $('<div/>', {
      'id':             widgetId,
      'class':          'draggable widget',
      'ontouchstart':   'OnMouseDown(event)',
      'ontouchmove':    'OnMouseMove(event)',
      'ontouchend':     'OnMouseUp(event)'
   }).appendTo('#demodashboard');

   widgetId = '#' + widgetId;
   
   // viz
   $('<div/>', {
      'id':             'viz_'+vizId,
      'class':          'viz'
   }).appendTo(widgetId);
   
   // mac
   $('<div/>', {
      'id':             'mac_'+vizId,
      'class':          'mac'
   }).appendTo(widgetId);
   
   // link
   if (data.linkText && data.linkUrl) {
      var id = 'datalink_' + vizId;
      $('<div />', {
         'id':          id,
         'class':       'datalink'
      }).appendTo(widgetId);
      $('#'+id).append($('<a >/', {
         'href':        data.linkUrl,
         'target':      '_new'
      }).append(data.linkText));
   }
   
   // configuration
   if (data.isConfigurable) {
      var settingsId = 'settings_' + vizId;
      var that = this;
      $('<div />', {
         'id':          settingsId,
         'class':       'settings'
      }).appendTo(widgetId);
      settingsId = '#' + settingsId;
      $(settingsId).append($('<a >/').click(function(event){
         that.settings(event);
         event.preventDefault();
      }).append('<svg style="overflow: hidden;" height="30" version="1.1" width="30" xmlns="http://www.w3.org/2000/svg"><path style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); opacity: 1; fill-opacity: 1;" fill="white" stroke="none" d="M26.834,14.693C28.65,12.605,29.015,9.754999999999999,28.027,7.359L24.381,11.611L20.787,10.912L19.596,7.45L23.233,3.208C20.731,2.5780000000000003,17.975,3.338,16.167,5.418C14.260000000000002,7.611000000000001,13.948000000000002,10.647,15.128000000000002,13.111L5.624,24.04C4.6129999999999995,25.201999999999998,4.736,26.964,5.898,27.974999999999998C7.06,28.985,8.822,28.863,9.833,27.700999999999997L19.326,16.782999999999998C21.939,17.625,24.918,16.896,26.834,14.693Z" transform="matrix(0.75,0,0,0.75,4,4)" opacity="1" fill-opacity="1"></path></svg>'));
   }
   
   // height
   if (data.vizHeight) {
      increment = data.vizHeight-$('#viz_'+vizId).height();
      $(widgetId).height($(widgetId).height()+increment);
      $('#viz_'+vizId).height($('#viz_'+vizId).height()+increment);
   }
   
   return vizId;
}
Viz.prototype.settings = function(event) {
   
}

//===== VizPressure

function VizPressure(data) {
   this.init(data);
}
VizPressure.prototype = new Viz;
VizPressure.prototype.init = function(data) {
   
   // store params
   
   // initialize parent
   Viz.call(this,data);
   
   // local variables
   this.mac_1           = null;
   this.lastvalue_1     = null;
   this.offset_1        = null;
   this.lastupdated_1   = null;
   this.mac_2           = null;
   this.lastvalue_2     = null;
   this.offset_2        = null;
   this.lastupdated_2   = null;
   
   // create widget
   data.vizHeight       = 600;
   this.vizId           = this.createNewWidget(
      data
   );
   
   // customize widget
   $('#viz_'+this.vizId).append('<img id="image_'+this.vizId+'" src="pressure.png"/>');
   $('#image_'+this.vizId).css('position',      'absolute');
   $('#image_'+this.vizId).css('left',          ($('#viz_'+this.vizId).width()-128)/2);
   
   // update
   this.update(data);
}
VizPressure.prototype.update = function(data) {
   
   // parse lastvalue into lastvalue and offset
   var m = new RegExp('^([0-9.-]+)_([0-9.-]+)$').exec(data.lastvalue);
   if (m) {
      lastvalue    = parseInt(m[1]);
      offset       = parseInt(m[2]);
      calibrate    = false;
   } else {
      var m = new RegExp('^([0-9.-]+)_([0-9.-]+)_calibrate$').exec(data.lastvalue);
      if (m) {
         lastvalue = parseInt(m[1]);
         offset    = parseInt(m[2]);
         calibrate = true;
      } else {
         console.log('ERROR: could not parse VizPressure update '+data.lastvalue);
         return;
      }
   }
   
   // figure out which mac to update
   macToUpdate = null;
   if ((this.mac_1==null) || (this.mac_1==data.mac)) {
      macToUpdate = 1;
   }
   if ((this.mac_2==null) || (this.mac_2==data.mac)) {
      macToUpdate = 2;
   }
   
   // update data
   wasUpdated = false;
   switch(macToUpdate) {
      case 1:
         this.mac_1          = data.mac;
         this.lastvalue_1    = lastvalue+offset;
         if (lastvalue!=this.lastupdated_1) {
            wasUpdated = true;
         }
         this.lastupdated_1  = data.lastupdated;
         break;
      case 2:
         this.mac_2          = data.mac;
         this.lastvalue_2    = lastvalue+offset;
         if (lastvalue!=this.lastupdated_2) {
            wasUpdated = true;
         }
         this.lastupdated_2  = data.lastupdated;
         break;
      default:
         console.log('ERROR: unexpected VizPressure mac='+data.mac);
         break;
   }
   
   // toggle color
   if (wasUpdated) {
      toggleColors(this.vizId);
   }
   
   // update viz
   if ((this.lastvalue_1!=null) && (this.lastvalue_2!=null)) {
      diff         = Math.abs(this.lastvalue_2-this.lastvalue_1);
      maxHeight    = $('#viz_'+this.vizId).height()-$('#image_'+this.vizId).height();
      bottomValue  = maxHeight*(diff/7000);
      $('#image_'+this.vizId).css('bottom', bottomValue+'px');
   }
   
   // update mac
   macText = ''
   if        ((this.mac_1!=null) && (this.mac_2!=null)) {
      if (this.lastvalue_2>this.lastvalue_1) {
         macText = this.mac_1+'<br/>'+this.mac_2;
      } else {
         macText = this.mac_2+'<br/>'+this.mac_1;
      }
   } else if ( this.mac_1!=null) {
      macText = this.mac_1+'<br/>??';
   } else if ( this.mac_2!=null) {
      macText = this.mac_2+'<br/>??';
   }
   $('#mac_'+this.vizId).html(macText);
   
   // update calibrate button
   if (calibrate) {
      if ($('#button_'+this.vizId).length==0) {
         $('#viz_'+this.vizId).append('<button id="button_'+this.vizId+'"/>');
         $('#button_'+this.vizId).html('calibrate');
         $('#button_'+this.vizId).css('position','absolute');
         $('#button_'+this.vizId).css('bottom',  '0px');
         $('#button_'+this.vizId).live('click',this.calibrateClick);
      }
   } else {
      $('#button_'+this.vizId).remove();
   }
   
}
VizPressure.prototype.calibrateClick = function(e) {
   // post to trigger a calibration
   jQuery.ajax({
      type:       'POST',
      url:        '/dashboard/json/',
      data:       JSON.stringify({'calibrate':'pressure'})
   });
}

//===== VizEnergySource

function VizEnergySource(data) {
   this.init(data);
}
VizEnergySource.prototype = new Viz;
VizEnergySource.prototype.init = function(data) {
   
   // store params
   this.lastvalue       = data.lastvalue;
   this.lastupdated     = data.lastupdated;
   
   // initialize parent
   Viz.call(this,data);
   
   // local variables
   
   // create widget
   data.vizHeight       = null;
   this.vizId           = this.createNewWidget(
      data
   );
   
   // customize widget
   $('#viz_'+this.vizId).append('<img id="image_'+this.vizId+'"/>');
   $('#image_'+this.vizId).css('position',      'absolute');
   $('#mac_'+this.vizId).html(data.mac);
   
   // update
   this.update(data);
}
VizEnergySource.prototype.update = function(data) {
   
   // toggle color
   if (data.lastupdated!=this.lastupdated) {
      toggleColors(this.vizId);
   }
   
   // store new values
   this.lastvalue      = data.lastvalue;
   this.lastupdated    = data.lastupdated;
   
   // update widget
   $('#image_'+this.vizId).attr('src',this.lastvalue+'.png');
   $('#image_'+this.vizId).css('left',  ($('#viz_'+this.vizId).width() -128)/2);
   $('#image_'+this.vizId).css('bottom',($('#viz_'+this.vizId).height()-128)/2);
}

//===== VizTemperature

function VizTemperature(data) {
   this.init(data);
}
VizTemperature.prototype = new Viz;
VizTemperature.prototype.init = function(data) {
   
   // store params
   this.feedId          = data.feedId;
   this.lastvalue       = data.lastvalue;
   this.lastupdated     = data.lastupdated;
   this.mac             = data.mac;
   
   // initialize parent
   Viz.call(this,data);
   
   // create widget
   data.vizHeight       = null;
   this.vizId           = this.createNewWidget(
      data
   );
   
   // customize widget
   $('#viz_'+this.vizId).addClass('temperature');
   $('#mac_'+this.vizId).html(data.mac);
   
   // update
   this.update(data);
}
VizTemperature.prototype.update = function(data) {
   
   // toggle color
   if (data.lastupdated!=this.lastupdated) {
      toggleColors(this.vizId);
   }
   
   // store new values
   this.lastvalue      = data.lastvalue;
   this.lastupdated    = data.lastupdated;
   
   // update widget
   $('#viz_'+this.vizId).html(parseFloat(this.lastvalue).toFixed(2)+'&deg;C');
}
VizTemperature.prototype.settings = function(event) {
   
   var content = $("<div></div>");
   content.append("<h3>Temperature settings</h3>");
   var form = $("<form />");
   content.append(form);
   var message = $('<span style="color: red;">&nbsp;</span>');
   content.append(message);
   form.append($("<label>", {"for": "rate"}).text("Rate (ms)"));
   var rateInput = $("<input>", {"type": "text", "name": "rate"});
   form.append(rateInput);
   var that = this;
   form.append($("<input>", {"type": "submit"}).click(function(event) {
      event.preventDefault();
      jQuery.ajax({
         type:       'POST',
         url:        "/motedata/json/send?mac="+that.mac+"&app=OAPTemperature/",
         data:       JSON.stringify({'rate': rateInput.val()})
      }).error(function(xhr, ajaxOptions, thrownError) {
         message.text(xhr.statusText + ": " + xhr.responseText);
      }).success(function() {
         lightboxClose();
      });
   }));

   $('#lightbox').append(content);
   lightboxShow();
   rateInput.focus();
}

//===== VizVoltage

function VizVoltage(data) {
   this.init(data);
}
VizVoltage.prototype = new Viz;
VizVoltage.prototype.init = function(data) {
   
   // store params
   this.feedId          = data.feedId;
   this.lastvalue       = data.lastvalue;
   this.lastupdated     = data.lastupdated;
   
   // initialize parent
   Viz.call(this,data);
   
   // create widget
   data.vizHeight       = null;
   this.vizId           = this.createNewWidget(
      data
   );
   
   // customize widget
   $('#viz_'+this.vizId).addClass('temperature');
   $('#mac_'+this.vizId).html(data.mac);
   
   // update
   this.update(data);
}
VizVoltage.prototype.update = function(data) {
   
   // toggle color
   if (data.lastupdated!=this.lastupdated) {
      toggleColors(this.vizId);
   }
   
   // store new values
   this.lastvalue      = data.lastvalue;
   this.lastupdated    = data.lastupdated;
   
   // update widget
   $('#viz_'+this.vizId).html(parseFloat(this.lastvalue).toFixed(1)+'mV');
}

//===== VizAcceleration

function VizAcceleration(data) {
   this.init(data);
}
VizAcceleration.prototype = new Viz;
VizAcceleration.prototype.init = function(data) {
   
   // store params
   
   // initialize parent
   Viz.call(this,data);
   
   // local variables
   this.lastvalue       = null;
   this.lastupdated     = null;
   
   // create widget
   data.vizHeight       = null;
   this.vizId           = this.createNewWidget(
      data
   );
   
   // customize widget
   $('#viz_'+this.vizId).append('<img id="image_'+this.vizId+'"/>');
   $('#image_'+this.vizId).css('position',      'absolute');
   $('#mac_'+this.vizId).html(data.mac);
   
   // update
   this.update(data);
}
VizAcceleration.prototype.update = function(data) {
   
   lastvalue       = data.lastvalue
   lastupdated     = data.lastupdated
   
   if (lastupdated!=this.lastupdated) {
      toggleColors(this.vizId);
   }
   this.lastvalue      = lastvalue;
   this.lastupdated    = lastupdated;
   
   var m = new RegExp('([0-9.-]+)_([0-9.-]+)_([0-9.-]+)').exec(this.lastvalue);
   if (m) {
      x = parseFloat(m[1]);
      y = parseFloat(m[2]);
      z = parseFloat(m[3]);
   } else {
      console.log('ERROR: could not parse VizAcceleration update '+this.lastvalue);
   }
   
   maxVal = Math.max(Math.abs(x),Math.abs(y),Math.abs(z));
   
   if        (maxVal==Math.abs(x)) {
      image = x>0?'dice_1.png':'dice_6.png';
   } else if (maxVal==Math.abs(y)) {
      image = y>0?'dice_2.png':'dice_5.png';
   } else {
      image = z>0?'dice_4.png':'dice_3.png';
   }
   
   $('#image_'+this.vizId).attr('src',image);
   $('#image_'+this.vizId).css('left',  ($('#viz_'+this.vizId).width() -120)/2);
   $('#image_'+this.vizId).css('bottom',($('#viz_'+this.vizId).height()-120)/2);
}

//===== VizLed

function VizLed(data) {
   this.init(data);
}
VizLed.prototype        = new Viz;
VizLed.prototype.init   = function(data) {
   
   // store params
   this.feedId          = data.feedId;
   this.mac             = data.mac;
   
   // initialize parent
   Viz.call(this,data);
   
   // create widget
   data.vizHeight       = null
   this.vizId           = this.createNewWidget(
      data
   );
   
   // add image
   var that = this;
   $('#viz_'+this.vizId).append('<img name="'+data.mac+'" id="image_'+this.vizId+'"/>');
   $('#image_'+this.vizId).attr('src',"led_off.png");
   $('#image_'+this.vizId).css('position','absolute');
   $('#image_'+this.vizId).css('left',  ($('#viz_'+this.vizId).width() -128)/2);
   $('#image_'+this.vizId).css('bottom',($('#viz_'+this.vizId).height()-128)/2);
   $('#image_'+this.vizId).addClass('nodrag');
   $('#image_'+this.vizId).click(
      function(event){
         that.click(event);
         event.preventDefault();
      }
   );
   
   // add mac
   $('#mac_'+this.vizId).html(data.mac);
   
   // update
   this.update(data);
}
VizLed.prototype.update = function(data) {
   switch (data.lastvalue) {
      case null:
         // nothing to do
         break;
      case '0':
         $('#image_'+this.vizId).attr('src','led_off.png');
         break;
      default:
         $('#image_'+this.vizId).attr('src','led_on.png');
         break;
   }
}
VizLed.prototype.click = function(event) {
   
   // toggle the image
   image = $('#image_'+this.vizId)
   if (image.attr('src')=='led_on.png') {
      $('#image_'+this.vizId).attr('src','led_off.png');
      ledStatus = '0';
   } else {
      $('#image_'+this.vizId).attr('src','led_on.png');
      ledStatus = '1';
   }
   
   // post to set the mote's LED
   changeLEDstate(this.mac,ledStatus);
}
