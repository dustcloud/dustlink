var spreadsheetKey = null;
var worksheetId    = null;

//=========================== initialization ==================================

function initDemoselection() {
   
   // add a demo selection div at beginning of body
   $('body').prepend(
      '<div>'+
      '<table id="demoselector">'+
         '<tr>'+
            '<td>Spreadsheet Key:</td>'+
            '<td><input id="spreadsheetkey" type="text" onchange="keyEntered()"></input></td>'+
            '<td><a id="spreadsheeturl" target="_new">raw data</a></td>'+
         '</tr>'+
         '<tr>'+
            '<td>'+
               '<select id="demodropdown" onChange="demoSelected()"></select>'+
            '</td>'+
         '</tr>'+
      '</table>'+
   '</div>'
   );

   // try to get the spreadsheetKey from URL
   var m = new RegExp('[\\?&]key=([^&#]*)').exec(window.location.href);
   if (m) {
      spreadsheetKey = m[1];
   } else {
      spreadsheetKey = '0AlATqW9wxWYldHBrRF8yZ3RpQklJcHd5X3FtNXJCN1E';
   }
   
   $('#spreadsheetkey').val(spreadsheetKey);
   $('#spreadsheetkey').change();
}

//=========================== demo selection ==================================

function keyEntered() {
   // get key entered
   spreadsheetKey = $('#spreadsheetkey').val();
   
   // update url link
   $('#spreadsheeturl').attr('href','https://docs.google.com/spreadsheet/ccc?key='+spreadsheetKey);
   
   // populate the demo selector
   populateDemoSelector();
}

function populateDemoSelector() {
   // retrieve list of worksheets from spreadsheet
   $.support.cors = true;
   $.ajax({
      url:         'https://spreadsheets.google.com/feeds/worksheets/'+spreadsheetKey+'/public/basic?alt=json',
      dataType:    'jsonp',
      success:     populateDemoSelector_cb
   });
}
function populateDemoSelector_cb(data) {
   var demonames      = new Array();
   var demoworksheets = new Array();

   // turn returned value in json string
   json = eval(data);
   
   // extract the worksheet names and IDs
   for (var i = 0; i < json.feed.entry.length; i++) {
      demonames.push(json.feed.entry[i].title.$t);
      temp = json.feed.entry[i].id.$t.split('/');
      demoworksheets.push(temp[temp.length-1]);
   }
   
   // put information in drow-down menu
   for (var i = 0; i < demonames.length; i++) {
      $('<option/>', {
         'value': demoworksheets[i],
         html:    demonames[i]
      }).appendTo('#demodropdown');
   }
   
   // trigger an 'onchange' event
   document.getElementById('demodropdown').onchange();
}

function demoSelected() {
   if (spreadsheetKey) {
      worksheetId = $('#demodropdown').val();
   }
}

//=========================== get data ========================================

function getNewDashboardData() {
   if (spreadsheetKey && worksheetId) {
      $.ajax({
         url:      'https://spreadsheets.google.com/feeds/list/'+spreadsheetKey+'/'+worksheetId+'/public/basic?alt=json',
         dataType: 'jsonp',
         success:  getNewDashboardData_cb
      });
   }
}
function getNewDashboardData_cb(data) {
   // turn returned value in json string
   json = eval(data);
   
   // parse the json to build new dashboard data
   newData = new Array();
   for (var i = 0; i < json.feed.entry.length; i++) {
      thisRow = {};
      thisRow['source'] = json.feed.entry[i].title.$t;
      var m = new RegExp('type: ([a-zA-Z0-9\_]+), min: ([0-9\-]*), lastvalue: ([a-zA-Z0-9_.\-]*), max: ([0-9\-]*), lastupdated: ([0-9\-]+)').exec(json.feed.entry[i].content.$t);
      if (m) {
         thisRow['type']               = m[1];
         thisRow['min']                = m[2];
         thisRow['lastvalue']          = m[3];
         thisRow['max']                = m[4];
         thisRow['lastupdated']        = m[5];
      } else {
         var m = new RegExp('type: ([a-zA-Z0-9\_]+), lastvalue: ([a-zA-Z0-9_.\-]*), lastupdated: ([0-9\-]+)').exec(json.feed.entry[i].content.$t);
         if (m) {
            thisRow['type']            = m[1];
            thisRow['min']             = null;
            thisRow['lastvalue']       = m[2];
            thisRow['max']             = null;
            thisRow['lastupdated']     = m[3];
         }
      }
      newData.push(thisRow);
   }
   refreshDashboard_cb(
      {
         'config': {
             'showTimeline': false
         },
         'data':  newData
      }
   );
}
