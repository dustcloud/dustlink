//========== setup

// make sure IE does not return cached results.
jQuery.ajaxSetup({ cache: false });


//========== defines

var dashboardData  = [];
var dashboardElems = [];

//========== admin

function refreshDashboard() {
   // get new data
   getNewDashboardData();
}
function refreshDashboard_cb(newInput) {
   var redraw;
   
   newData = newInput['data'];
   
   // decide whether to update or redraw
   redraw = false;
   if (newData.length==0 || newData.length!=dashboardData.length) {
      redraw = true;
   } else {
      for (var i = 0; i < newData.length; i++) {
         if (
               newData[i].source != dashboardData[i].source ||
               newData[i].type   != dashboardData[i].type   ||
               newData[i].min    != dashboardData[i].min    ||
               newData[i].max    != dashboardData[i].max
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
      redrawDashboard(newInput['config']);
   } else {
      updateDashboard();
   }
}

function getPressureViz() {
   returnVal = null;
   for (var e = 0; e < dashboardElems.length; e++) {
      if (dashboardElems[e] instanceof VizPressure) {
         returnVal = dashboardElems[e];
      }
   }
   return returnVal;
}

function redrawDashboard(config) {
   
   // clear the dashboard
   document.getElementById('demodashboard').innerHTML = '';    // html
   dashboardElems = [];                                        // elems
   
   // create the elements
   for (var i = 0; i < dashboardData.length; i++) {
      switch(dashboardData[i].type) {
         case 'pressure':
            if (getPressureViz()==null) {
               dashboardElems.push(new VizPressure(config));
            } else {
               dashboardElems.push(null);
            }
            break;
         case 'energysource':
            dashboardElems.push(new VizEnergysource(
                                       dashboardData[i].source,
                                       config
                               ));
            break;
         case 'temperature':
            dashboardElems.push(new VizTemperature(
                                       dashboardData[i].source,
                                       dashboardData[i].min,
                                       dashboardData[i].max,
                                       config
                               ));
            break;
         case 'acceleration':
            dashboardElems.push(new VizAcceleration(
                                       dashboardData[i].source,
                                       config
                               ));
            break;
         case 'led':
            dashboardElems.push(new VizLed(
                                       dashboardData[i].source,
                                       config
                               ));
            break;
         default:
            alert('unexpected data type "'+dashboardData[i].type+'"');
      }
   }
   
   // update the dashboard
   updateDashboard();
}

function updateDashboard() {
   for (var i = 0; i < dashboardData.length; i++) {
      if (dashboardData[i].type=='pressure') {
         getPressureViz().update(
            dashboardData[i].source,
            dashboardData[i].lastvalue,
            parseInt(dashboardData[i].lastupdated)
         );
      } else {
         dashboardElems[i].update(
            dashboardData[i].lastvalue,
            parseInt(dashboardData[i].lastupdated)
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

//===== VizWithTimeline
function Viz() {
   Viz.prototype.init.call(this);
}
Viz.prototype.init = function() {
}

Viz.prototype.createNewWidget = function(vizHeight, showTimeline, showSettings) {
   vizId = dashboardElems.length;
   var widgetId = 'widget_'+vizId;
   // widget
   $('<div/>', {
      'id':    widgetId,
      'class': 'draggable widget',
      'ontouchstart': 'OnMouseDown(event)',
      'ontouchmove': 'OnMouseMove(event)',
      'ontouchend': 'OnMouseUp(event)'
   }).appendTo('#demodashboard');

   widgetId = '#' + widgetId;
   
   // viz
   $('<div/>', {
      'id':    'viz_'+vizId,
      'class': 'viz'
   }).appendTo(widgetId);
   
   // source
   $('<div/>', {
      'id':    'source_'+vizId,
      'class': 'source'
   }).appendTo(widgetId);
   
   if (showTimeline) {
      var timelineId = 'timeline_' + vizId;
      $('<div />', {
         'id':  timelineId,
         'class': 'timeline'
      }).appendTo(widgetId);
      timelineId = '#' + timelineId;
      $(timelineId).append($('<a >/', {
         'href': '/motedata?mac=' + this.source + '&app=' + this.appName()
      }).append("timeline"));
   }
   
   if (showSettings) {
      var settingsId = 'settings_' + vizId;
      var that = this;
      $('<div />', {
         'id':  settingsId,
         'class': 'settings'
      }).appendTo(widgetId);
      settingsId = '#' + settingsId;
      $(settingsId).append($('<a >/').click(function(event){
         that.settings(event);
         event.preventDefault();
      }).append('<svg style="overflow: hidden;" height="30" version="1.1" width="30" xmlns="http://www.w3.org/2000/svg"><path style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); opacity: 1; fill-opacity: 1;" fill="white" stroke="none" d="M26.834,14.693C28.65,12.605,29.015,9.754999999999999,28.027,7.359L24.381,11.611L20.787,10.912L19.596,7.45L23.233,3.208C20.731,2.5780000000000003,17.975,3.338,16.167,5.418C14.260000000000002,7.611000000000001,13.948000000000002,10.647,15.128000000000002,13.111L5.624,24.04C4.6129999999999995,25.201999999999998,4.736,26.964,5.898,27.974999999999998C7.06,28.985,8.822,28.863,9.833,27.700999999999997L19.326,16.782999999999998C21.939,17.625,24.918,16.896,26.834,14.693Z" transform="matrix(0.75,0,0,0.75,4,4)" opacity="1" fill-opacity="1"></path></svg>'));
   }
   
   // update height
   if (vizHeight) {
      increment = vizHeight-$('#viz_'+vizId).height();
      $(widgetId).height($(widgetId).height()+increment);
      $('#viz_'+vizId).height($('#viz_'+vizId).height()+increment);
   }
   
   return vizId;
}

Viz.prototype.settings = function(event) {
   
}

//===== VizTimeline
function VizTimeline(source) {
   VizTimeline.prototype.init.call(this, source)
}
VizTimeline.prototype = new Viz;
VizTimeline.prototype.init = function(source) {
   this.source = source;
}
VizTimeline.prototype.getSource = function() {
   return this.source;
}

//===== VizPressure

function VizPressure(config) {
   this.init(config);
}
VizPressure.prototype = new Viz;
VizPressure.prototype.init = function(config) {
   Viz.call(this);
   this.mac_1          = null;
   this.lastvalue_1    = null;
   this.offset_1       = null;
   this.lastupdated_1  = null;
   this.mac_2          = null;
   this.lastvalue_2    = null;
   this.offset_2       = null;
   this.lastupdated_2  = null;
   this.vizId          = this.createNewWidget(600,config['showTimeline'], false);
   
   $('#viz_'+this.vizId).append('<img id="image_'+this.vizId+'" src="pressure.png"/>');
   $('#image_'+this.vizId).css('position',      'absolute');
   $('#image_'+this.vizId).css('left',          ($('#viz_'+this.vizId).width()-128)/2);
}
VizPressure.prototype.update = function(source, valueString, lastupdated) {
   
   // parse valueString into lastvalue and offset
   var m = new RegExp('^([0-9.-]+)_([0-9.-]+)$').exec(valueString);
   if (m) {
      lastvalue = parseInt(m[1]);
      offset    = parseInt(m[2]);
      calibrate = false;
   } else {
      var m = new RegExp('^([0-9.-]+)_([0-9.-]+)_calibrate$').exec(valueString);
      if (m) {
         lastvalue = parseInt(m[1]);
         offset    = parseInt(m[2]);
         calibrate = true;
      } else {
         console.log('could not parse VizPressure update '+this.lastvalue);
         return;
      }
   }
   
   // figure out which mac to update
   macToUpdate = null;
   if ((this.mac_1==null) || (this.mac_1==source)) {
      macToUpdate = 1;
   }
   if ((this.mac_2==null) || (this.mac_2==source)) {
      macToUpdate = 2;
   }
   
   // update data
   wasUpdated = false;
   switch(macToUpdate) {
      case 1:
         this.mac_1          = source;
         this.lastvalue_1    = lastvalue+offset;
         if (lastvalue!=this.lastupdated_1) {
            wasUpdated = true;
         }
         this.lastupdated_1  = lastupdated;
         break;
      case 2:
         this.mac_2          = source;
         this.lastvalue_2    = lastvalue+offset;
         if (lastvalue!=this.lastupdated_2) {
            wasUpdated = true;
         }
         this.lastupdated_2  = lastupdated;
         break;
      default:
         console.log('ERROR unexpected VizPressure source='+source);
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
   
   // update source
   sourceText = ''
   if        ((this.mac_1!=null) && (this.mac_2!=null)) {
      if (this.lastvalue_2>this.lastvalue_1) {
         sourceText = this.mac_1+'<br/>'+this.mac_2;
      } else {
         sourceText = this.mac_2+'<br/>'+this.mac_1;
      }
   } else if ( this.mac_1!=null) {
      sourceText = this.mac_1+'<br/>??';
   } else if ( this.mac_2!=null) {
      sourceText = this.mac_2+'<br/>??';
   }
   $('#source_'+this.vizId).html(sourceText);
   
   // update calibrate button
   if (calibrate) {
      if ($('#button_'+this.vizId+'_nodrag').length==0) {
         $('#viz_'+this.vizId).append('<button id="button_'+this.vizId+'_nodrag"/>');
         $('#button_'+this.vizId+'_nodrag').html('calibrate');
         $('#button_'+this.vizId+'_nodrag').css('position','absolute');
         $('#button_'+this.vizId+'_nodrag').css('bottom',  '0px');
         $('#button_'+this.vizId+'_nodrag').live('click',this.calibrateClick);
      }
   } else {
      $('#button_'+this.vizId+'_nodrag').remove();
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
VizPressure.prototype.appName = function() {
   return 'SPIPressure';
}

//===== VizEnergysource

function VizEnergysource(source,config) {
   this.init(source,config);
}
VizEnergysource.prototype = new VizTimeline;
VizEnergysource.prototype.init = function(source,config) {
   VizTimeline.call(this, source);
   this.lastvalue      = null;
   this.lastupdated    = null;
   this.vizId          = this.createNewWidget(null,config['showTimeline'], false);
   
   $('#viz_'+this.vizId).append('<img id="image_'+this.vizId+'"/>');
   $('#image_'+this.vizId).css('position',      'absolute');
   
   $('#source_'+this.vizId).html(this.source);
}
VizEnergysource.prototype.update = function(lastvalue,lastupdated) {
   if (lastupdated!=this.lastupdated) {
      toggleColors(this.vizId);
   }
   this.lastvalue      = lastvalue;
   this.lastupdated    = lastupdated;
   
   $('#image_'+this.vizId).attr('src',this.lastvalue+'.png');
   $('#image_'+this.vizId).css('left',  ($('#viz_'+this.vizId).width() -128)/2);
   $('#image_'+this.vizId).css('bottom',($('#viz_'+this.vizId).height()-128)/2);
}
VizEnergysource.prototype.appName = function() {
   return 'GPIONet';
}

//===== VizTemperature

function VizTemperature(source,min,max,config) {
   this.init(source,min,max,config);
}
VizTemperature.prototype = new VizTimeline;
VizTemperature.prototype.init = function(source,min,max,config) {
   VizTimeline.call(this, source);
   this.min            = min;
   this.lastvalue      = null;
   this.max            = max;
   this.lastupdated    = null;
   this.vizId          = this.createNewWidget(null,config['showTimeline'], config['showTimeline']);
   
   $('#viz_'+this.vizId).addClass('temperature');
   
   $('#source_'+this.vizId).html(this.source);
}
VizTemperature.prototype.update = function(lastvalue,lastupdated) {
   if (lastupdated!=this.lastupdated) {
      toggleColors(this.vizId);
   }
   this.lastvalue      = lastvalue;
   this.lastupdated    = lastupdated;
   
   $('#viz_'+this.vizId).html(this.lastvalue+'&deg;C');
}
VizTemperature.prototype.appName = function() {
   return 'OAPTemperature';
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
         url:        "/motedata/json/send?mac="+that.getSource()+"&app=OAPTemperature/",
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

//===== VizAcceleration

function VizAcceleration(source,config) {
   this.init(source,config);
}
VizAcceleration.prototype = new VizTimeline;
VizAcceleration.prototype.init = function(source,config) {
   VizTimeline.call(this, source);
   this.lastvalue      = null;
   this.lastupdated    = null;
   this.vizId          = this.createNewWidget(null,config['showTimeline'], false);
   
   $('#viz_'+this.vizId).append('<img id="image_'+this.vizId+'"/>');
   $('#image_'+this.vizId).css('position',      'absolute');
   
   $('#source_'+this.vizId).html(this.source);
}
VizAcceleration.prototype.update = function(lastvalue,lastupdated) {
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
      console.log('could not parse VizAcceleration update '+this.lastvalue);
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
VizAcceleration.prototype.appName = function() {
   return 'SPIAcceleration';
}

//===== VizLed

function VizLed(source,config) {
   this.init(source,config);
}
VizLed.prototype = new VizTimeline;
VizLed.prototype.init = function(source,config) {
   VizTimeline.call(this, source);
   this.vizId          = this.createNewWidget(null, false, false);
   
   $('#viz_'+this.vizId).append('<img name="'+this.source+'" id="image_'+this.vizId+'_nodrag"/>');
   $('#image_'+this.vizId+'_nodrag').attr('src',"led_off.png");
   $('#image_'+this.vizId+'_nodrag').css('position','absolute');
   $('#image_'+this.vizId+'_nodrag').css('left',  ($('#viz_'+this.vizId).width() -128)/2);
   $('#image_'+this.vizId+'_nodrag').css('bottom',($('#viz_'+this.vizId).height()-128)/2);
   $('#image_'+this.vizId+'_nodrag').click(this.click);
   
   $('#source_'+this.vizId).html(this.source);
}
VizLed.prototype.update = function(lastvalue,lastupdated) {
   // nothing to do
}
VizLed.prototype.click = function() {
   
   // retrieve the vizId
   var m = new RegExp('image_([0-9]+)_nodrag').exec(this.id);
   if (m==null) {
      console.log('invalid id '+this.id);
      return;
   }
   vizId = m[1];
   
   // retrieve the MAC
   mac = $('#image_'+vizId+'_nodrag').attr('name');
   
   // toggle the image
   image = $('#image_'+vizId+'_nodrag')
   if (image.attr('src')=='led_on.png') {
      $('#image_'+vizId+'_nodrag').attr('src','led_off.png');
      ledStatus = '0';
   } else {
      $('#image_'+vizId+'_nodrag').attr('src','led_on.png');
      ledStatus = '1';
   }
   
   // post to set the mote's LED
   jQuery.ajax({
      type:       'POST',
      url:        '/motedata/json/send?mac='+mac+'&app=OAPLED/',
      data:       JSON.stringify({'status':ledStatus})
   });
}
VizLed.prototype.appName = function() {
   return 'OAPLED';
}
