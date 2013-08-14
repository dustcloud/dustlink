
function initDemoselection() {
   $('#logo').wrap('<a href="/" />');
}

function getNewDashboardData() {
   $.ajax({
      url:      '/dashboard/json/',
      dataType: 'json',
      success:  refreshDashboard_cb
   });
}
