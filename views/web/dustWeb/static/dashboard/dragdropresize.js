var _startX    = 0;              // mouse starting positions
var _startY    = 0;
var _offsetX   = 0;              // current element offset
var _offsetY   = 0;
var _dragElement;                // needs to be passed from OnMouseDown to OnMouseMove
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
   
   // IE uses srcElement, others use target
   var target = e.target != null ? e.target : e.srcElement;
   
   var m = new RegExp('[a-zA-Z]+_([0-9]+)').exec(target.id);
   if (m) {
      target      = document.getElementById('widget_'+m[1]);
      isDraggable = true;
   } else {
      isDraggable = false;
   }
   
   // for IE, left click == 1
   // for Firefox, left click == 0
   if (target && isDraggable && (e.button == 1 &&
            window.event != null || 
            e.button == 0 || e.touches)) {
         // grab the mouse position
         if (e.targetTouches && e.targetTouches.length == 1) {
            e.preventDefault();
            var touch = e.targetTouches[0];
            _startX = touch.pageX;
            _startY = touch.pageY;
            
         } else {
            _startX = e.clientX;
            _startY = e.clientY;
         }
   
         // grab the clicked element's position
         _offsetX = ExtractNumber(target.style.left);
         _offsetY = ExtractNumber(target.style.top);
         
         // bring the clicked element to the front while it is being dragged
         var oldZIndex = parseInt(target.style.zIndex, 10);
         target.style.zIndex = Z_INDEX;
         if (oldZIndex) {
            $(".widget").each(function() {
               var thisZIndex = parseInt($(this).css("z-index"), 10);
               if (thisZIndex >= oldZIndex) {
                  $(this).css("z-index", thisZIndex - 1);
               }
            });
         }
         
         // we need to access the element in OnMouseMove
         _dragElement = target;
         
         // tell our code to start moving the element with the mouse
         document.onmousemove = OnMouseMove;
         document.ontouchmove = OnMouseMove;
         
         // cancel out any text selections
         document.body.focus();
         
         // prevent text selection in IE
         document.onselectstart = function () { return false; };
         // prevent IE from trying to drag an image
         target.ondragstart = function() { return false; };
         
         // prevent text selection (except IE)
         return false;
      }
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
   _dragElement.style.left = (_offsetX + posX - _startX) + 'px';
   _dragElement.style.top  = (_offsetY + posY - _startY) + 'px';
}

function OnMouseUp(e) {
   if (_dragElement != null) {
      
      // we're done with these events until the next OnMouseDown
      document.onmousemove     = null;
      document.onselectstart   = null;
      _dragElement.ondragstart = null;

      // this is how we know we're not dragging      
      _dragElement = null;
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