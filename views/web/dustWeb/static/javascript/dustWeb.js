
function DustWeb() {
   
}

DustWeb.prototype.showVizHelp = function(vizId, show) {
   $(vizId).find('.doc-more').toggleClass("show", show);
   $(vizId).find('.doc-more').toggleClass("hide", !show);
   $(vizId).find('.doc-show-more').toggleClass("show", !show);
   $(vizId).find('.doc-show-more').toggleClass("hide", show);
}

var DUST_WEB = new DustWeb();

function enableAutoRefresh(VIZID) {
   window["autorefresh_"+VIZID] = true;
   $("#autorefreshlink_"+VIZID).attr('checked', true);
}
function disableAutoRefresh(VIZID) {
   window["autorefresh_"+VIZID] = false;
   $("#autorefreshlink_"+VIZID).attr('checked', false);
}
function updateAutoRefresh(VIZID) {
   // update autorefresh_{VIZID} state from checkbox
   window["autorefresh_"+VIZID] = $("#autorefreshlink_"+VIZID).is(":checked")
}

function updateStatus(divId, outcome, message) {
   var statusColor;
   
   // find color
   switch (outcome) {
       case 'busy':
           statusColor = 'yellow';
           break;
       case 'success':
           statusColor = 'green';
           break;
       case 'failure':
           statusColor = 'red';
           break;
       default:
           statusColor = 'blue';
   }
   var div = $('#' + divId);
   div.find('.viz-status-message').text(message);
   div.find('circle').css("fill", statusColor);
   //div.find('svg').toggleClass("hide", false);
   div.find('svg').removeAttr('class'); // workaround since toggleClass() doesn't work on svg
   
}

