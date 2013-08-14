  jQuery(document).ready(function() {
    $('#btn_minimize').mouseover(function() {
        $('#btn_minimize').attr('src','/sites/all/themes/dustnetworks/images/btn_minimize_over.png');
    });
    $('#btn_minimize').mouseout(function() {
        $('#btn_minimize').attr('src','/sites/all/themes/dustnetworks/images/btn_minimize.png');
    });
    $('#btn_maximize').mouseover(function() {
        $('#btn_maximize').attr('src','/sites/all/themes/dustnetworks/images/btn_maximize_over.png');
    });
    $('#btn_maximize').mouseout(function() {
        $('#btn_maximize').attr('src','/sites/all/themes/dustnetworks/images/btn_maximize.png');
    });
    $('#btn_minimize').click(function() {
        $('#bottom_panel').animate({bottom:-165},'slow');
        $('#btn_maximize').fadeIn('fast');
        $('#btn_minimize').fadeOut('fast');
    });
    $('#btn_maximize').click(function() {
        $('#bottom_panel').animate({bottom:0},'slow');
        $('#btn_maximize').fadeOut('fast');
        $('#btn_minimize').fadeIn('fast');
    });
    
    $('#btn_minimize').fadeOut('fast');
    
    if (!Modernizr.inputtypes.search){
    	var cssfile = '<link type="text/css" rel="stylesheet" media="all" href="/sites/all/themes/dustnetworks/searchfield.css" />';
    	$("head").append(cssfile);
    }    
  });

var Win;
function popUp (url, name, width, height, center, resize, scroll, posleft, postop) {

  	if (posleft != 0) { X = posleft }
      if (postop  != 0) { Y = postop  }

      if (!scroll) { scroll = 'yes' }
      if (!resize) { resize = 'yes' }

      if ((parseInt (navigator.appVersion) >= 4 ) && (center)) {
        X = (screen.width  - width ) / 2;
        Y = (screen.height - height) / 2;
      }
      
      if (scroll != 0) { scroll = 1 }

  	if (!Win || Win.closed)
  	{
  	    // display the popup window
  	    var Win = window.open(url, name,'width='+width+',height='+height+',top='+Y+',left='+X+',resizable='+resize+',scrollbars='+scroll+',location=no,directories=no,status=no,menubar=no,toolbar=no');   
  	}
  	else
  	{
  		// window is already open, update with content
  		Win.location = url;
  	}    
      Win.focus();
}
