var _startX    = 0;              // mouse starting positions
var _startY    = 0;
var _offsetX   = 0;              // current element offset
var _offsetY   = 0;
var _dragWidget;                 // needs to be passed from OnMouseDown to OnMouseMove
var _oldZIndex = 0;              // we temporarily increase the z-index during drag

InitDragDropResize();

function InitDragDropResize() {
   document.onmousedown = OnMouseDown;
   document.onmouseup   = OnMouseUp;
   window.onresize      = OnResize;
}

// The z-index of the topmost widget, all others have a lower z-index.
var Z_INDEX = 1000;

function OnMouseDown(e) {
   
   // pass the event object for IE
   if (e == null) {
      e = window.event;
   }
   
   // retrieve clicked element
   // IE uses srcElement, others use target
   var clickedElem = e.target != null ? e.target : e.srcElement;
   
   // stop if clicked element is attached class 'nodrag'
   if ($('#'+clickedElem.id).hasClass('nodrag')) {
      return;
   }
   
   // from that name, determine the vizId
   var m = new RegExp('[a-zA-Z]+_([0-9]+)').exec(clickedElem.id);
   if (m) {
      vizId       = m[1];
   } else {
      vizId       = null;
   }
   
   // stop if no vizId found
   if (!vizId) {
      return;
   }
   
   // determine clickWidget
   clickWidget = document.getElementById('widget_'+vizId);
   
   // stop if no clickWidget
   if (!clickWidget) {
      return;
   }
   
   // stop if not a click
   // for IE, left click == 1
   // for Firefox, left click == 0
   if (
         !(e.button==1 && window.event!=null) &&
         !(e.button==0)                       &&
         !(e.touches) 
      ) {
       return;
   }
   
   // if you get here, drag the widget
   
   // get the mouse position
   if (e.targetTouches && e.targetTouches.length == 1) {
      e.preventDefault();
      var touch = e.targetTouches[0];
      _startX = touch.pageX;
      _startY = touch.pageY;
   } else {
      _startX = e.clientX;
      _startY = e.clientY;
   }

   // grab the clicked widget's position
   _offsetX = ExtractNumber(clickWidget.style.left);
   _offsetY = ExtractNumber(clickWidget.style.top);
   
   // bring the clicked element to the front while it is being dragged
   var oldZIndex = parseInt(clickWidget.style.zIndex, 10);
   clickWidget.style.zIndex = Z_INDEX;
   if (oldZIndex) {
      $(".widget").each(function() {
         var thisZIndex = parseInt($(this).css("z-index"), 10);
         if (thisZIndex >= oldZIndex) {
            $(this).css("z-index", thisZIndex - 1);
         }
      });
   }
   
   // remember which widget to drag
   _dragWidget = clickWidget;
   
   // enable move events
   document.onmousemove = OnMouseMove;
   document.ontouchmove = OnMouseMove;
   
   // cancel out any text selections
   document.body.focus();
   
   // prevent text selection in IE
   document.onselectstart = function () { return false; };
   // prevent IE from trying to drag an image
   clickWidget.ondragstart = function() { return false; };
   
   // prevent text selection (except IE)
   return false;
}

function OnMouseMove(e) {
   
   if (e == null) {
      var e = window.event; 
   }
   
   var posX, posY;
   if (e.targetTouches && e.targetTouches.length == 1) {
      var target = e.targetTouches[0];
      posX = target.pageX;
      posY = target.pageY;
   } else {
      posX = e.clientX;
      posY = e.clientY;
   }
   
   // this is the actual drag code
   _dragWidget.style.left = (_offsetX + posX - _startX) + 'px';
   _dragWidget.style.top  = (_offsetY + posY - _startY) + 'px';
}

function OnMouseUp(e) {
   
   if (_dragWidget != null) {
      
      // we're done with these events until the next OnMouseDown
      document.onmousemove     = null;
      document.onselectstart   = null;
      _dragWidget.ondragstart = null;

      // this is how we know we're not dragging      
      _dragWidget = null;
   }
}

function OnResize(e) {
   
   // re-position the logo
   positionLogo();
}

function ExtractNumber(value) {
   var n = parseInt(value);
   return n == null || isNaN(n) ? 0 : n;
}