var xivelyMasterApiKey   = null;
var xivelyFeeds          = null;
var xivelyData           = [];
var xivelyIdx            = 0;
var googleSpreadsheetKey = null;
var googleWorksheetId    = null;

//=========================== initialization ==================================

function initInputSelection(options) {
   
   try {
      xivelyMasterApiKey   = options.xivelyMasterApiKey;
   } catch (e) {}
   try {
      xivelyFeeds          = options.xivelyFeeds;
   } catch (e) {}
   try {
      googleSpreadsheetKey = options.googleSpreadsheetKey;
   } catch (e) {}
   try {
      googleWorksheetId    = options.googleWorksheetId;
   } catch (e) {}
   
   // add a div to contain input selector form
   $('body').prepend(
      '<div id="inputselector">'+
      '</div>'
   );
   
   if        (xivelyMasterApiKey && xivelyFeeds) {
      // retrieving data from Xively
      
      xivelyConnect();
      
   } else if (googleSpreadsheetKey && googleWorksheetId) {
      // retrieving data from Google
      
      inputSelected('google');
      
   } else {
      // no data source specified
      
      // ask user
      $('#inputselector').html(
         '<table class="inputselection">'+
            '<tr>'+
               '<td colspan=2>Where is your mote data published?</td>'+
            '</tr>'+
            '<tr>'+
               '<td onClick="inputSelected(\'xively\')" class="link"><img src="logo_xively.png" /></td>'+
               '<td onClick="inputSelected(\'google\')" class="link"><img src="logo_google.png" /></td>'+
            '</tr>'+
            '<tr class="inputtablerow">'+
               '<td onClick="inputSelected(\'xively\')" class="link">Xively</td>'+
               '<td onClick="inputSelected(\'google\')" class="link">Google</td>'+
            '</tr>'+
         '</table>'
      );
   }
}

function inputSelected(input) {
   
   switch (input) {
      
      case 'xively':
         
         // display form
         $('#inputselector').addClass("displaytopmiddle");
         $('#inputselector').html(
            '<table id="xivelyInputForm" class="inputform">'+
               '<tr>'+
                  '<td colspan="4">xivelyMasterApiKey:</td>'+
               '</tr>'+
               '<tr>'+
                  '<td colspan="4"><input id="xivelyMasterApiKey" type="text"></input></td>'+
               '</tr>'+
               '<tr>'+
                  '<td colspan="4">Feeds:</td>'+
               '</tr>'+
               '<tr>'+
                  '<td colspan="4">'+
                     '<p>'+
                     'List the feeds you want to display on the dashboard.<br/>'+
                     'Leave <tt>readApiKey</tt> and <tt>updateApiKey</tt> empty to use <tt>xivelyMasterApiKey</tt>.'+
                     '</p>'+
                  '</td>'+
               '</tr>'+
               '<tr>'+
                  '<th>feedId</th>'+
                  '<th>readApiKey</th>'+
                  '<th>updateApiKey</th>'+
                  '<th></th>'+
               '</tr>'+
           '</table>'
         );
         addXivelyFeedRow();
         $('#inputselector').append('<button id="button" onClick="submitXivelyInputForm()">Submit</button>');
         
         break;
      
      case 'google':
         
         // display form
         $('#inputselector').html(
            '<table>'+
               '<tr>'+
                  '<td>Spreadsheet Key:</td>'+
                  '<td><input id="spreadsheetkey" type="text" onchange="googleSpreadsheetKeyEntered()"></input></td>'+
                  '<td><a id="spreadsheeturl" target="_new">raw data</a></td>'+
               '</tr>'+
               '<tr>'+
                  '<td>'+
                     '<select id="worksheetdropdown" onChange="googleWorksheetSelected()"></select>'+
                  '</td>'+
               '</tr>'+
            '</table>'
         );
         
         // fill in form programmatically if data already there
         if (googleSpreadsheetKey!=null) {
            $('#spreadsheetkey').val(googleSpreadsheetKey);
            $('#spreadsheetkey').change();
         }
         
         break;
      
      default:
         console.log("ERROR: unexpected input "+input);
         break;
   }
}

//=========================== input selection =================================

/*
xivelyData = [
   {
      feedId:                <feedId>,
      readApiKey:            <readApiKey>,
      updateApiKey:          <updateApiKey>,
      mac:                   <mac>,
      datastreams: [
         {
            id:              <id>,
            lastvalue:       <lastvalue>,
            lastupdated:     <lastupdated>,
         },
      ],
   }
]

dashboardData = {
   data: [
      {
         mac:                <mac>,
         type:               <type>,
         lastvalue:          <lastvalue>,
         lastupdated:        <lastupdated>,
         linkText:           <linkText>,
         linkUrl:            <linkUrl>,
      },
      {
         mac:                <mac>,
         type:               <type>,
         lastvalue:          <lastvalue>,
         lastupdated:        <lastupdated>,
         linkText:           <linkText>,
         linkUrl:            <linkUrl>,
      },
   ],
}
*/

//===== Xively

function addXivelyFeedRow() {
   $('#xivelyInputForm tr:last').after(
      '<tr>'+
         '<td><input type="text"></input></td>'+
         '<td><input type="text"></input></td>'+
         '<td><input type="text"></input></td>'+
         '<td onClick="addXivelyFeedRow()">add row</td>'+
      '</tr>'
   )
}

function submitXivelyInputForm() {
   
   // retrieve xivelyMasterApiKey
   xivelyMasterApiKey = $('#xivelyMasterApiKey').val();
   
   // retrieve xivelyFeeds
   xivelyFeeds = []
   
   var feedRows = $("#xivelyInputForm tr:gt(4)");
   var feedId;
   var readApiKey;
   var updateApiKey;
   feedRows.each(function(index) {
      
      feedId            = $.trim($("td:nth-child(1) input", this).val());
      readApiKey        = $.trim($("td:nth-child(2) input", this).val());
      if (readApiKey=="") {
         readApiKey     = null;
      }
      updateApiKey      = $.trim($("td:nth-child(3) input", this).val());
      if (updateApiKey=="") {
         updateApiKey   = null;
      }
      
      if (feedId!="") {
         xivelyFeeds.push({
            'feedId':            feedId,
            'readApiKey':        readApiKey,
            'updateApiKey':      updateApiKey
         });
      }
   });
   
   // connect to Xively
   if (xivelyMasterApiKey && xivelyFeeds) {
      xivelyConnect();
   }
}

function xivelyConnect() {
   
   // only display status in input selector
   $('#inputselector').removeClass("displaytopmiddle");
   $('#inputselector').addClass("displaylowerleft");
   $('#inputselector').html(
      '<table class="inputform">'+
         '<tr>'+
            '<td>Status:</td>'+
            '<td id="xivelyStatus"></td>'+
         '</tr>'+
      '</table>'
   );
   
   // retrieve the MAC addresses of the motes
   for (var i=0;i<xivelyFeeds.length; i++) {
      
      // retrieve feedId
      feedId            = xivelyFeeds[i].feedId;
      
      // select read and update key
      if (xivelyFeeds[i].readApiKey!=null) {
         readApiKey     = xivelyFeeds[i].readApiKey;
      } else {
         readApiKey     = xivelyMasterApiKey;
      }
      if (xivelyFeeds[i].updateApiKey!=null) {
         updateApiKey   = xivelyFeeds[i].updateApiKey;
      } else {
         updateApiKey   = xivelyMasterApiKey;
      }
      
      // create xivelyData for this feed
      xivelyData.push({
         feedId:        feedId,
         readApiKey:    readApiKey,
         updateApiKey:  updateApiKey,
         datastreams:   []
      });
   }
   
   // retrieve feed information
   xivelyIdx = 0;
   xively.setKey(xivelyData[xivelyIdx].readApiKey);
   xively.feed.get(
      xivelyData[xivelyIdx].feedId,         // feedId
      xivelyRetrieveFeedInfo_cb             // callback
   );
}

function xivelyRetrieveFeedInfo_cb(data) {
   
   // update status
   output     = "";
   output    += "retrieved information from feedId "+xivelyData[xivelyIdx].feedId+"... ";
   output    += " ("+(xivelyIdx+1)+"/"+xivelyData.length+")";
   $('#xivelyStatus').html(output);
   
   // store mac
   xivelyData[xivelyIdx].mac = data.device_serial;
   
   // store datastreams
   for (var i=0;i<data.datastreams.length; i++) {
      xivelyData[xivelyIdx].datastreams.push({
         id:              data.datastreams[i].id,
         lastvalue:       data.datastreams[i].current_value,
         lastupdated:     data.datastreams[i].at
      });
   }
   
   // increment xivelyIdx
   xivelyIdx += 1;
   
   if (xivelyIdx<xivelyData.length) {
      
      // retrieve next MAC
      xively.setKey(xivelyData[xivelyIdx].readApiKey);
      xively.feed.get(
         xivelyData[xivelyIdx].feedId,      // feedId
         xivelyRetrieveFeedInfo_cb          // callback
      );
      
   } else {
      
      // subscribe to all notifications
      for (var i=0;i<xivelyData.length; i++) {
         xively.setKey(xivelyData[i].readApiKey);
         for (var ds=0;ds<xivelyData[i].datastreams.length; ds++) {
            xively.datastream.subscribe(
               xivelyData[i].feedId,                // feedId
               xivelyData[i].datastreams[ds].id,    // datastream
               xivelyDataSubcribe_cb                // callback
            );
         }
      }
      
      // update status
      $('#xivelyStatus').html("done. subscribed to all updates.");
   }
   
   // update dashboard
   xivelyUpdateDashboard();
}

function xivelyDataSubcribe_cb(event,data) {
   
   // extract feedID, type and value
   feedId          = event.namespace.split('/')[2];
   type            = data.id;
   value           = data.current_value;
   lastupdated     = data.at;
   
   // log
   console.log("INFO: feedId "+feedId+" type \""+type+"\" at "+lastupdated+" value "+value);
   
   // update the local data
   for (var i=0;i<xivelyData.length; i++) {
      for (var ds=0;ds<xivelyData[i].datastreams.length; ds++) {
         if (xivelyData[i].feedId==feedId && xivelyData[i].datastreams[ds].id==type) {
            xivelyData[i].datastreams[ds].lastvalue        = value;
            xivelyData[i].datastreams[ds].lastupdated      = lastupdated;
         }
      }
   }
   
   // update dashboard
   xivelyUpdateDashboard();
}

function xivelyUpdateDashboard() {
   
   // filter through xivelyData, showing only mote with mac and lastvalue
   dashBoardData = []
   for (var i=0;i<xivelyData.length; i++) {
      for (var ds=0;ds<xivelyData[i].datastreams.length; ds++) {
         dashBoardData.push({
            mac:                xivelyData[i].mac,
            type:               xivelyData[i].datastreams[ds].id,
            lastvalue:          xivelyData[i].datastreams[ds].lastvalue,
            lastupdated:        xivelyData[i].datastreams[ds].lastupdated,
            linkText:           'view on Xively',
            linkUrl:            'https://xively.com/feeds/'+xivelyData[i].feedId
         })
      }
   }
   
   // trigger the dashboard to refresh
   refreshDashboard_cb(
      {
         'data':                  dashBoardData,
         'config': {
         }
      }
   );
}

//===== Google

function googleSpreadsheetKeyEntered() {
   
   // get key entered
   googleSpreadsheetKey = $('#spreadsheetkey').val();
   
   // update url link
   $('#spreadsheeturl').attr('href','https://docs.google.com/spreadsheet/ccc?key='+googleSpreadsheetKey);
   
   // populate the demo selector
   googlePopulateWorksheetSelector();
}

function googlePopulateWorksheetSelector() {
   // retrieve list of worksheets from spreadsheet
   $.support.cors = true;
   $.ajax({
      url:         'https://spreadsheets.google.com/feeds/worksheets/'+googleSpreadsheetKey+'/public/basic?alt=json',
      dataType:    'jsonp',
      success:     googlePopulateWorksheetSelector_cb
   });
}
function googlePopulateWorksheetSelector_cb(data) {
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
      }).appendTo('#worksheetdropdown');
   }
   
   // trigger an 'onchange' event
   document.getElementById('worksheetdropdown').onchange();
}

function googleWorksheetSelected() {
   if (googleSpreadsheetKey) {
      googleWorksheetId = $('#worksheetdropdown').val();
   }
}

//=========================== get data ========================================

function getNewDashboardData() {
   if (googleSpreadsheetKey && googleWorksheetId) {
      // retrieving data from Google
      
      $.ajax({
         url:      'https://spreadsheets.google.com/feeds/list/'+googleSpreadsheetKey+'/'+googleWorksheetId+'/public/basic?alt=json',
         dataType: 'jsonp',
         success:  googleGetNewDashboardData_cb
      });
   }
}
function googleGetNewDashboardData_cb(data) {
   
   // turn returned value in json string
   json = eval(data);
   
   // parse the json to build new dashboard data
   dashBoardData = [];
   for (var i = 0; i < json.feed.entry.length; i++) {
      thisRow = {};
      thisRow.mac                 = json.feed.entry[i].title.$t;
      thisRow.linkText            = 'view on Google';
      thisRow.linkUrl             = 'https://docs.google.com/spreadsheet/ccc?key='+googleSpreadsheetKey;
      var m = new RegExp('type: ([a-zA-Z0-9\_]+), min: ([0-9\-]*), lastvalue: ([a-zA-Z0-9_.\-]*), max: ([0-9\-]*), lastupdated: ([0-9\-]+)').exec(json.feed.entry[i].content.$t);
      if (m) {
         thisRow.type             = m[1];
         thisRow.lastvalue        = m[3];
         thisRow.lastupdated      = m[5];
      } else {
         var m = new RegExp('type: ([a-zA-Z0-9\_]+), lastvalue: ([a-zA-Z0-9_.\-]*), lastupdated: ([0-9\-]+)').exec(json.feed.entry[i].content.$t);
         if (m) {
            thisRow.type          = m[1];
            thisRow.lastvalue     = m[2];
            thisRow.lastupdated   = m[3];
         }
      }
      dashBoardData.push(thisRow);
   }
   
   // log
   console.log("INFO: updated data from Google");
   
   refreshDashboard_cb(
      {
         'data':   dashBoardData,
         'config': {
         }
      }
   );
}

//=========================== set data ========================================

// post to set the mote's LED
function changeLEDstate(mac,ledStatus) {
   
   if        (xivelyMasterApiKey && xivelyFeeds) {
      for (var i=0;i<xivelyData.length; i++) {
         for (var ds=0;ds<xivelyData[i].datastreams.length; ds++) {
            if (xivelyData[i].mac==mac && xivelyData[i].datastreams[ds].id=='led') {
               
               // modify value on Xively
               xively.setKey(xivelyData[i].updateApiKey);
               xively.datastream.update(
                  xivelyData[i].feedId,             // feedID
                  'led',                            // datastreamID
                  { "current_value": ledStatus }    // data
               );
               
               // modify value locally
               xivelyData[i].datastreams[ds].lastvalue     = ledStatus;
            }
         }
      }
      
      
   }
}
