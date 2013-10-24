from dustWeb import DustWebDoc

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('DustLinkWebDoc')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

from DustLinkData import DustLinkData

class DustLinkWebDoc(DustWebDoc.DustWebDoc):
    '''
    \brief This file contains the text displayed in the help menus throughout
           the DustLink website.
    
    Each text field is cut into two parts:
    - the INTRO part is displayed by default.
    - the MORE part is displayed when the user ask for more documentation.
    
    Each field has to contain valid HTML code. There is no escaping applied
    to the contents.
    
    All text fields are indexed by the URL of the page, and the item in the 
    page.Dynamic URL parts are replaced by an asterisk (*). For example, a
    request to /page/_resource/item is mapped to the tuple ('page', '*',
    'item').
    '''
    
    INTRO     = {} # the intro text for an element
    MORE      = {} # the text displayed in the "more" element, i.e. after in intro
    CLASS     = {} # optional style elements attached to each element
    
    #======================== defines =========================================
    
    WARNING_NOTIMPLEMENTED = '''
    <p class="doc-note">This feature is not yet
    implemented.</p>
    '''
    
    CLASS_DEMO = 'demomode'
    CLASS_ALL  = [CLASS_DEMO]
    
    #======================== Dashboard =======================================
    
    #===== /dashboard
    
    INTRO[('dashboard', )]   = None
    MORE[ ('dashboard', )]   = None
    CLASS[ ('dashboard', )]  = [CLASS_DEMO]
    
    #======================== Motes ===========================================
    
    #===== /motes
    
    INTRO[('motes', )]   = \
    "Manage the motes known to DustLink."
    MORE[ ('motes', )]   = None
    CLASS[ ('motes', )]  = []
    
    #===== /motes/add
    
    INTRO['motes', 'add']   = \
    "Add a mote to the system."
    MORE[ 'motes', 'add']   = '''
    <p>Motes are added automatically as DustLink discovers them. This form is
    intended for internal debugging purposes.</p>
    <p>Once you have created a mote, refresh the page and navigate to the
    sub-page created for that mote.</p>
    '''
    CLASS[ 'motes', 'add'] = []
    
    #===== /motes/delete
    
    INTRO['motes', 'delete']   = \
    "Delete a mote from the system."
    MORE[ 'motes', 'delete']   = '''
    Using this function also removes all the data associated with a mote,
    including the sensor all data received.
    '''
    CLASS[ 'motes', 'delete'] = []
    
    #===== /motes/cleanup
    
    INTRO['motes', 'cleanup']   = \
    "Delete all motes not currently in a network."
    MORE[ 'motes', 'cleanup']   = '''
    <p>All motes that have ever joined the network will be displayed in the mote list.
    Even motes that have gone "Lost", or have been purposely removed will remain on the list.
    This command will ONLY remove motes that have never joined a manager since it was
    last started.</p>
    <p>Enter the word <tt>cleanup</tt> in the form below and click on
    the <tt>submit</tt> button.</p>
    <p>Note that you need to be logged into DustLink as a user with delete
    privileges on the <tt>motes.*</tt> resource.</p>
    '''
    CLASS[ 'motes', 'cleanup'] = []
    
    #===== /motes/*
    
    INTRO['motes', '*']   = \
    "The following is information about this particular mote."
    MORE[ 'motes', '*']   = None
    CLASS[ 'motes', '*'] = []
    
    #===== /motes/*/info
    
    INTRO['motes', '*', 'info']   = \
    "Detailed information about this mote, collected and stored by the manager."
    MORE[ 'motes', '*', 'info']   = '''
    The SmartMesh IP manager maintains information about each mote in the
    network. DustLink periodically retrieves that information and displays it
    below.
    '''
    CLASS[ 'motes', '*', 'info'] = []
    
    #===== /motes/*/apps
    
    WARNING_ATTACHING_APPS = '''
    <p>When an application is attached to a mote in DustLink, it 
    only indicates to DustLink to start looking for data coming from that
    application. It does <strong>not</strong> re-program the mote.</p>
    
    <p class="doc-warning">Attaching an app to a mote only has an effect if 
    DustLink is not running in fast mode.</p>
    '''
    WARNING_DETACHING_APPS = '''
    <p>When an application is detached from a mote in DustLink, it 
    only indicates to DustLink to stop looking for data coming from that
    application. It does <strong>not</strong> re-program the mote.</p>
    
    <p class="doc-warning">Detaching an app from a mote only has an effect if 
    DustLink is not running in fast mode.</p>
    '''
    
    INTRO['motes', '*', 'apps']   = \
    "Applications declared on this mote."
    MORE[ 'motes', '*', 'apps']   = '''
    These applications are the ones the user has <i>declared</i> are
    running on this mote using the Attach/Detach forms below, or which DustLink
    has discovered.<br/>'''+WARNING_ATTACHING_APPS+"<br/>"+WARNING_DETACHING_APPS
    CLASS[ 'motes', '*', 'apps'] = []
    
    #===== /motes/*/attach
    
    INTRO['motes', '*', 'attach']  = \
    "Attach an application to a mote."
    MORE[ 'motes', '*', 'attach']  = WARNING_ATTACHING_APPS
    CLASS[ 'motes', '*', 'attach'] = []
    
    #===== /motes/*/detach
    
    INTRO['motes', '*', 'detach']   = \
    "Detach an application from a mote."
    MORE[ 'motes', '*', 'detach']   = '''
    <p class="doc-note">Detaching an application
    from a mote automatically removes the data received from that mote and
    application from DustLink.</p>
    '''+WARNING_DETACHING_APPS
    CLASS[ 'motes', '*', 'detach'] = []
    
    #======================== Networks ========================================
    
    #===== /networks
    
    INTRO[('networks', )]   = \
    "Manage the networks known to DustLink."
    MORE[ ('networks', )]   = None
    CLASS[ ('networks', )] = [CLASS_DEMO]
    
    #===== /networks/add
    
    INTRO['networks', 'add']   = \
    "Add a network to DustLink."
    MORE[ 'networks', 'add']   = '''
    <p>Networks are added automatically when a manager connection is added.
    This form is intended for internal debugging purposes.</p>
    <p>Once you have created a network, refresh the page and navigate to the
    sub-page created for that network.</p>
    '''
    CLASS[ 'networks', 'add'] = []
    
    #===== /networks/delete
    
    INTRO['networks', 'delete']   = \
    "Delete a network from DustLink."
    MORE[ 'networks', 'delete']   = '''
    Using this function removes all network-related data associated with
    this network, such as topology, user privileges, and info attached to
    each mote. It does not, however, remove the motes contained in that
    network, nor the sensor data received from those motes.
    '''
    CLASS[ 'networks', 'delete'] = []
    
    #===== /networks/*
    
    INTRO['networks', '*']   = \
    "The following is information about this particular network."
    MORE[ 'networks', '*']   = None
    CLASS[ 'networks', '*'] = []
    
    #===== /networks/*/info
    
    INTRO['networks', '*', 'info']   = \
    "Information the manager knows about this network."
    MORE[ 'networks', '*', 'info']   = '''
    The SmartMesh IP manager maintains information about the network.
    DustLink periodically retrieves that information and displays it below.
    <br/>'''+WARNING_NOTIMPLEMENTED
    CLASS[ 'networks', '*', 'info'] = []
    
    #===== /networks/*/topology
    
    INTRO['networks', '*', 'topology']   = \
    "Display the active links of the network."
    MORE[ 'networks', '*', 'topology']   = '''
    <p>The topology displays the different devices and the paths
    interconnecting them.</p>
    
    <p>The following color-coding is used:</p>
    <ul>
    <li>
        <span style="background-color:#ACF;">blue</span>: SmartMesh IP manager.
    </li>
    <li>
        <span style="background-color:#FFF;">white</span>: SmartMesh IP mote,
        connected to the network and in "Operational" state.
    </li>
    <li>
        <span style="background-color:#CCC;">gray</span>: SmartMesh IP mote,
        disconnected from the network and in the "Lost" state.
    </li>
    </ul>
    
    <p>Interact with the topology:</p>
    <ul>
        <li><strong>Scroll</strong> up/down to zoom in/out.</li>
        <li><strong>Hover</strong> over the motes and paths to get information.</li>
        <li><strong>Click</strong> on a mote to access its page.</li>
    </ul>
    
    <p>Mote Information:</p>
    <ul>
        <li><strong>Good Neighbors</strong> are neighbors with a link quality better than 60%.</li>
        <li><strong>Reliability</strong> is the portion of packets sent by the mote which reach the manager.</li>
    </ul>
    
    <p>Path Information:</p>
    <ul>
        <li><strong>Quality</strong> corresponds to the path stability.</li>
        <li><strong>RSSI</strong> is the Received Signal Strength Indicator for both directions in the path. That is, for path "a / b", it is displayed as the RSSI value for "a->b / b->a", where "a->b" representing the links from mote a to mote b.</li>
    </ul>
    '''
    CLASS[ 'networks', '*', 'topology'] = [CLASS_DEMO]
    
    #===== /networks/*/motes
    
    INTRO[ 'networks', '*', 'motes'] = \
    "The list of motes which are part of this network."
    MORE[  'networks', '*', 'motes'] = None
    CLASS[ 'networks', '*', 'motes'] = [CLASS_DEMO]
    
    #===== /networks/*/paths
    
    INTRO[  'networks', '*', 'paths'] = \
    "The paths in this network."
    MORE[   'networks', '*', 'paths'] = '''
    The SmartMesh IP manager maintains information about each path in the
    network. DustLink periodically retrieves that information and displays it
    below.
    '''
    CLASS[ 'networks', '*', 'paths'] = []
    
    #======================== Apps ============================================
    
    WARNING_ADDING_APPS = '''
    When you add an application trough this web interface, you are
    only indicating to DustLink how to interact with a mote running this
    application. It does <strong>not</strong> re-program the mote.
    '''
    WARNING_DELETING_APPS = '''
    When you delete an application trough this web interface, you are
    only asking DustLink to "forget" how to interact with this application if
    running on a mote. It does <strong>not</strong> re-program the mote.
    '''
    
    #===== /apps
    
    INTRO[ ('apps', )] = \
    "Manage the applications known to DustLink."
    MORE[  ('apps', )] = '''
    <p>Motes run applications which send and receive data from a manager or
    other applications on the Internet. to the manager and react
    to command received from the manager/Internet.<p>
    
    <p>Use this page to indicate to DustLink which applications are running
    inside your motes in the network. Using this information, DustLink is able 
    to parse incomming data received from those applications as well as format
    commands to send out.</p>
    '''
    CLASS[('apps', )] = []
    
    #===== /apps/add
    
    INTRO[  'apps', 'add'] = \
    "Add a new application to DustLink."
    MORE[   'apps', 'add'] = '''
    <p>To add an application to DustLink, enter its name in this form and click
    "Submit".</p>
    <p>Once you have created a network, refresh the page and navigate to the
    sub-page created for that network.</p>
    '''
    CLASS[ 'apps', 'add'] = []
    
    #===== /apps/delete
    
    INTRO[  'apps', 'delete'] = \
    "Remove an existing application from DustLink."
    MORE[   'apps', 'delete'] = '''
    <p>To remove an application from DustLink, select its name from the
    drop-down menu and click "Submit".</p>
    
    <p class="doc-note">Deleting an application
    automatically detaches it from all the motes it was attached to. This, in
    turn, causes all data received from that application to be lost.</p>
    '''
    CLASS[ 'apps', 'delete'] = []
    
    #===== /apps/*
    
    INTRO[  'apps', '*'] = \
    "Update the information about a particular application."
    MORE[   'apps', '*'] = '''
    <p class="doc-warning">Updating the fields received from an application only has an
    effect if DustLink is not running in fast mode.</p>
    '''
    CLASS[ 'apps', '*'] = []
    
    #===== /apps/*/appfields
    
    INTRO[ 'apps', '*', 'appfields'] = None
    MORE[  'apps', '*', 'appfields'] = None
    CLASS[ 'apps', '*', 'appfields'] = []
    
    #======================== health ==========================================
    
    #===== /health
    
    INTRO[ ('health', )] = \
    "Network health monitoring page."
    MORE[  ('health', )] = '''
    <p>DustLink periodically assesses the overall health of each network it is
    connected to by running a series of tests. Each test will display a status, when it
    was last run, and PASS/FAIL results.<p>
    
    <p>Click on a network in the menu on your left to display its test rusults and status.<p>
    '''
    CLASS[('health', )] = [CLASS_DEMO]
    
    #===== /health/*
    
    INTRO[  'health', '*'] = \
    "Network health information for the selected network."
    MORE[   'health', '*'] = '''
    <p>DustLink periodically assesses the overall health of each network it is
    connected to by running a series of tests. Each test will display a status, when it
    was last run, and PASS/FAIL results.</p>
    
    <p>Assessing the health of the network consists in the following steps:</p>
    <ul>
        <li>Retrieving information about the motes and paths from the manager.</li>
        <li>Running a number of tests on the collected data.</li>
    </ul>
    '''
    CLASS[ 'health', '*'] = []
    
    #===== /health/*/testschedule
    
    INTRO[  'health', '*', 'testschedule'] = \
    "Test schedule controls."
    MORE[   'health', '*', 'testschedule'] = '''
    <p>This form displays the following;</p>
    <ul>
        <li><tt>period (min)</tt>: The interval between test runs, in minutes (smallest interval is 1 minute).</li>
        <li><tt>next test in</tt>: Counts down to the next test run (updates automatically).</li>
        <li><tt>Run test now</tt>: Click this button to kick off an test execution cycle immediately.</li>
    </ul>
    '''
    CLASS[ 'health', '*',  'testschedule'] = [CLASS_DEMO]
    
    #===== /health/*/testresults
    
    INTRO[  'health', '*', 'testresults'] = \
    "Test results and status. Click on any item for details."
    MORE[   'health', '*', 'testresults'] = '''
    <p>The report is divided into 6 sections as follows;</p>
    <ul>
        <li><tt>S</tt>: Status, Pass/Fail status of the last time a test was run.</li>
        <li><tt>W</tt>: Weather, displayed as a consolidation of the last 5 times the test was run.</li>
        <li><tt>Test Name</tt>: The name of the test.</li>
        <li><tt>Last Run</tt>: Date and time when test was last run.</li>
        <li><tt>Last Success</tt>: Date and time when test last passed.</li>
        <li><tt>Last Failure</tt>: Date and time when test last failed.</li>
    </ul>
    
    <p>The following is the list of tests that are run to gauge your network's health.</p>
    <ul>
        <li><tt>oneSingleParentMote</tt>: Verifies that there is only one mote with a single parent in the network.</li>
        <li><tt>numLinks</tt>: Verifies that the mote is assigned less links that the maximum number it can support.</li>
        <li><tt>multipleJoins</tt>: Verifies that motes have not reset, i.e. left the network and then re-joined.</li>
        <li><tt>stabilityVsRSSI</tt>: Verifies that path stabilities are expected, given their RSSI.</li>
        <li><tt>networkReliability</tt>: Verifies reliability of delivering packets.</li>
        <li><tt>numGoodNeighbors</tt>: Verifies that each mote has enough potential neighbors to guarantee a reliable mesh network.</li>
        <li><tt>networkAvailability</tt>: Verifies that the network as a whole has enough bandwidth available for data traffic.</li>
        <li><tt>perMoteAvailability</tt>: Verifies that the motes' own packet generation is appropriate for its connection.</li>
    </ul>
    '''
    CLASS[ 'health', '*', 'testresults'] = [CLASS_DEMO]
    
    #===== /health/*/testreset
    
    INTRO[  'health', '*', 'testreset'] = \
    "Reset all test statuses and results."
    MORE[   'health', '*', 'testreset'] = '''
    <p>This function resets all the test results and restarts them. You can use
    this after a test had failed and appropriate action was taken to remedy the
    situation.</p>
    
    <p>To do so, enter <tt>reset</tt> in the form below, and click
    <tt>Submit</tt>.</p>
    
    <p><u>Note</u>: you need to be logged in as a user which has delete
    privileges on this network.</p>
    '''
    CLASS[ 'health', '*', 'testreset'] = []

    
    #======================== Users ===========================================
    
    #===== /users
    
    INTRO[ ('users', )] = \
    "Manage the users known to DustLink."
    MORE[  ('users', )] = '''
    <p>DustLink uses users to grant or deny access to parts of the data and
    allow certain configuration changes. In the web interface, users are
    required to enter their password in the login form.</p>
    '''
    CLASS[('users', )] = []
    
    #===== /users/add
    
    INTRO[  'users', 'add'] = \
    "Add a new user."
    MORE[   'users', 'add'] = '''
    <p>The username can be any string, with the following restrictions:</p>
    
    <ul>
    <li>
        You can not create a user called <b>admin</b>. This user always exists
        and has full access. You need to manage this user through the system
        section.
    </li>
    <li>
        A visitor who is not logged in gets assigned the username 
        <b>anonymous</b>. You can create this username and assign privileges to 
        visitors who do not log in.
    </li>
    </ul>
    
    <p>Once you have created a user, refresh the page and navigate to the
    sub-page created for that user.</p>
    '''
    CLASS[ 'users', 'add'] = []
    
    #===== /users/delete
    
    INTRO[ 'users', 'delete'] = \
    "Delete an existing user."
    MORE[  'users', 'delete'] = '''
    Deleting a user erases the user's associated information, such as
    privileges.
    '''
    CLASS[ 'users', 'delete'] = []
    
    #===== /users/*
    
    INTRO[ 'users', '*'] = \
    "Update the information about a particular user."
    MORE[  'users', '*'] = None
    CLASS[ 'users', '*'] = []
    
    #===== /users/*/authentication
    
    INTRO[ 'users', '*', 'authentication'] = \
    "Update the authentication method of this user."
    MORE[  'users', '*', 'authentication'] = '''
    <p>Select the authentication method.</p>
    
    <p class="doc-note">The "ssl" method is not yet implemented.</p>
    '''
    CLASS[ 'users', '*', 'authentication'] = []
    
    #===== /users/*/password
    
    INTRO[ 'users', '*', 'password'] = \
    "Reset a user's password."
    MORE[  'users', '*', 'password'] = '''
    <p>Enter both the current and the new password to make the change.  If you are logged in as
    admin making changes to this user, the currect password is not required... leave blank.</p>
    '''
    CLASS[ 'users', '*', 'password'] = []
    
    #===== /users/*/privileges
    
    INTRO[ 'users', '*', 'privileges'] = \
    "Privileges currently granted to this user."
    MORE[  'users', '*', 'privileges'] = '''
    <p>Use the forms below to grant and deny services to this user.</p>
    
    <p>DustLink has a number of "resources" which can be read, changed or
    deleted. These three actions are called <tt>get</tt>, <tt>put</tt>, and
    <tt>delete</tt>, respectively.</p>
    
    <p>All actions are performed by the user that is currently logged in. Only
    when the user has been granted the corresponding privilege can the action
    be executed successfully.</p>
    
    <p>For example, for user <tt>someUser</tt> to read the data generated by
    application <tt>someApp</tt> on mote <tt>11-11-11-11-11-11-11-11</tt>,
    someUser needs to be granted the <tt>get</tt> privilege on both mote
    <tt>11-11-11-11-11-11-11-11</tt> and application <tt>someApp</tt>.</p>
    
    <p>The default rule is to deny all privileges. That is, when a user is just
    created and the table below is empty, it has no privileges on any resource.
    </p>
    '''
    CLASS[ 'users', '*', 'privileges'] = []
    
    #===== /users/*/grant
    
    INTRO[ 'users', '*', 'grant'] = \
    "Grant a specific privilege to this user."
    MORE[  'users', '*', 'grant'] = '''
    <p>The wildcard (<tt>*</tt>) is used to grant privileges to all
    sub-resources.</p>
    
    <p>That is, if you grant the <tt>get</tt> privilege to a user on resource
    <tt>motes.*</tt>, this privilege covers all motes known by DustLink. Note
    that this includes motes currently in the system, and motes that might be
    added in the future.</p>
    '''
    CLASS[ 'users', '*', 'grant'] = []
    
    #===== /users/*/deny
    
    INTRO[ 'users', '*', 'deny'] = \
    "Deny a specific privilege from this user."
    MORE[  'users', '*', 'deny'] = '''
    The wildcard (<tt>*</tt>) is used to deny privileges from all
    sub-resources.
    '''
    CLASS[ 'users', '*', 'deny'] = []
    
    #======================== System ==========================================
    
    #===== /system
    
    INTRO[ ('system', )] = "Modify system settings."
    MORE[  ('system', )] = None
    CLASS[('system', )] = [CLASS_DEMO]
    
    #===== /system/welcome/systemevents
    
    INTRO['system', 'welcome'] = None
    MORE[ 'system', 'welcome'] = None
    CLASS[ 'system', 'welcome'] = [CLASS_DEMO]
    
    #===== /system/welcome/welcome
    # Directly accessed via VizHtml
    INTRO['system', 'welcome', 'welcome'] = None
    MORE[ 'system', 'welcome', 'welcome'] = '''
    
    <h2>About DustLink</h2>
    
    <p>DustLink is a web-based SmartMesh IP management system with the
    following features:</p>

    <ul>
        <li>Connects to an arbitrary number of SmartMesh IP managers.</li>
        <li>Gathers and displays information about motes, managers and networks.</li>
        <li>Displays the topology of the low-power wireless mesh networks.</li>
        <li>Stores and displays sensor data from arbitrary applications.</li>
        <li>Monitors the health of all connected networks.</li>
        <li>Bridges to the Xively cloud service as well as Google Spreadsheet to publish data.</li>
        <li>Uses advanced privileges for fine-grained user access management.</li>
    </ul> 
    
    <h2>Using DustLink for demos</h2>
    
    <p>DustLink running on a small embedded Linux platform (DemoBox) is a
    simple Demo vehicle. The system comes pre-configured for demos, requiring
    no configuration or installation of software. Connect the little DemoBox to
    your computer, open a browser to this webpage, connect your SmartMesh IP
    eval kit manager to the DemoBox, turn on the motes and you're ready to do
    a demo.</p>
    
    <p>For using DustLink for demos, use only the menu items and page sections
    highlighted <span style='color:green;font-weight:600'>green</span>. All
    non-highlighted items are for advanced use.</p>
    
    <h3>DemoBox Quick Start</h3>
    <ol>
        <li>
            Connect your SmartMesh IP manager to one of the 3 USB connectors
            on the DemoBox.
        </li>
        <li>
            Open the <a href="/system/managers">Managers</a> page and wait until
            the connection corresponding to your manager becomes <tt>active</tt>. 
        </li>
        <li>
            From the top menu (you might have to refresh your page), select the
            network correponding to your connection under "NETWORKS". This page
            displays the topology of your network.
        </li>
        <li>
            Navigate to the
            <a href="/static/dashboard/index_local.html">Dashboard</a> to see
            the data generated by the motes:
            <ul>
                <li>
                    You can move the widgets around by dragging them anywhere on the page.
                </li><li>
                    You can change the temperature sampling period of any mote by
                    clicking on the configure icon (small wrench).
                </li><li>
                    You can toggle the LED on the motes by clicking on the
                    light bulb (note: on your motes, the LED jumper must be set
                    for the LED to be visible).
                </li>
            </ul>
            <p class="doc-warning">
                The DemoBox may become sluggish if doing a demo
                where many motes are publishing data at high rates (e.g. 1
                pkt/sec each) because this is a very low cost and resource
                limited system. To minimize this, make sure to only have one
                browser window open to the DemoBox, OR set the system to
                <a href="/system/fastmode">Fast Mode</a>.
            </p>
            <p class="doc-warning">
                In Fast Mode, data is not logged into the system's SD card, so data
                time-lines will not be updated. Fast data updates in the
                <a href="/dashboard">Dashboard</a> will continue to be displayed. This mode
                will not affect data publishing to an external service such as Xively.
            </p>
        </li>
        
        <p>Quick Demo platform reset steps:</p>
        <li>
            <p class="doc-warning">You need to log in as the <tt>admin</tt>
            user to be able to do the following.</p>
            <p>To prevent leaving your demo platform in an unknown state, or
            starting a demo that way, the DemoBox and the connected network can
            be easily reset to factory defaults by the following steps.
            Navigate to the <a href="/system/factoryreset">Factory Reset</a>
            utility and reset the system using the forms in the following
            order:</p>
            <ol>
                <li>Reset the motes using the <a href="/system/factoryreset">Factory Reset</a> utility's "Reset Motes" form.</li>
                <li>On the <a href="/system/managers">Managers</a> page, remove the manager using the "Delete" form.</li>
                <li>Reset the manager using the <a href="/system/factoryreset">Factory Reset</a> utility's "Reset Manager" form.</li>
                <li>Unplug the manager from the DemoBox.</li>
                <li>Reset the DustLink website using the <a href="/system/factoryreset">Factory Reset</a> utility's "Reset DustLink" form.</li>
            </ol>
            <p class="doc-warning">Wait for each of these three steps to
            complete before starting the next one.</p>
        </li>
    </ol>
    
    <p class="doc-warning">While you can read system configurations by default,
    you need to log in as the <tt>admin</tt> user to change most settings</p>
    
    <h2>Using DustLink when developing firmware</h2>
    
    <p>When developing mote firmware which generates sensor data:</p>
    
    <ol>
        <li>Declare the format of your application payload at 
           <a href="/apps">apps</a>.</li>
        <li>Attach this application to your mote at 
           <a href="/motes">motes</a>.</li>
        <li>Watch your data come in.</li>
    </ol>
    '''
    CLASS[ 'system', 'welcome', 'welcome'] = [CLASS_DEMO]
    
    #===== /system/welcome/systemevents
    
    INTRO['system', 'welcome', 'systemevents'] = \
    " "
    MORE[ 'system', 'welcome', 'systemevents'] = '''
    <p>If you're logged in as a user with <tt>get</tt> privileges on the
    <tt>system</tt> resource, the table below indicates major system-wide
    events:</p>
    
    <ul>
        <li>
            <tt>'''+DustLinkData.DustLinkData.SYSEVENT_BACKUPDATACORRUPTED+'''</tt>:
            This event is created each time, upon starting up, the application finds
            a backup file, but that file can not be read, or is corrupted.
            
            When this happens, that file is renamed with the
            <tt>.corrupted-</tt><i>timestamp</i> suffix, and a new backup file
            is created with default data. In addition the
            <tt>'''+DustLinkData.DustLinkData.SYSEVENT_DEFAULTDATALOADED+'''</tt>
            event is generated.<br/>
            
            You need to have access to the filesystem of the machine running this
            website to retrieve the corrupted backup file.
        </li>
        <li>
            <tt>'''+DustLinkData.DustLinkData.SYSEVENT_BACKUPDATALOADED+'''</tt>:
            This event is created each time, upon starting up, the application
            finds a backup file, and succesfully loads it content.
        </li>
        <li>
            <tt>'''+DustLinkData.DustLinkData.SYSEVENT_DEFAULTDATALOADED+'''</tt>:
            This event is created each time, upon starting up, the application loads
            default data into its database.<br/>
            
            This can happen for one of the following reasons:
            <ol>
                <li>No backup data file was found.</li>
                <li>A backup file was found, but could not be read, or was corrupted.
                in this case, a
                <tt>'''+DustLinkData.DustLinkData.SYSEVENT_BACKUPDATACORRUPTED+'''</tt>
                is also generated.</li>
            </ol>
        </li>
        <li>
            <tt>'''+DustLinkData.DustLinkData.SYSEVENT_CONFIGLOADED+'''</tt>:
            This event is created each time you use the <tt>Factory Reset</tt>
            page in the <tt>System</tt> menu.
        </li>
        <li>
            <tt>'''+DustLinkData.DustLinkData.SYSEVENT_FACTORYRESET+'''</tt>:
            This event is created each time you use the <tt>Load Config</tt>
            page in the <tt>System</tt> menu.
        </li>
    </ul>
    
    <p>If you have <tt>delete</tt> privileges on the <tt>system</tt> resource,
    you can click on the <tt>remove</tt> link to remove that event from the
    table. It takes up to 3 seconds for the entry to disappear from the
    table.</p>
    
    <p>A new event of the same kind overwrites the older one.</p>
    '''
    CLASS[ 'system', 'welcome', 'systemevents'] = []
    
    #===== /system/adminpassword
    
    INTRO[ 'system', 'adminpassword'] = \
    "Reset the password of the admin password."
    MORE[  'system', 'adminpassword'] = '''
    Only the admin user can reset the password of the admin user. When
    resetting the password of the admin user, the old password must be
    specified.
    '''
    CLASS[ 'system', 'adminpassword'] = []
    
    INTRO[ 'system', 'adminpassword', 'change'] = None
    MORE[  'system', 'adminpassword', 'change'] = None
    CLASS[ 'system', 'adminpassword', 'change'] = []
    
    #===== /system/managers
    
    INFO_SYSTEMMANAGER_ADDDELAY = '''
    <p>There is a three second delay between the moment you add a connection
    and when it appears in the "Manager Connections" table. It can take up
    to ten seconds for a new connection to transition from the "inactive" to
    "active" state.</p>
    '''
    
    INTRO[ 'system', 'managers'] = \
    "Manage the list of SmartMesh IP managers connected to DustLink."
    MORE[ 'system', 'managers'] = '''
    <p>DustLink can connect to an arbitrary number of SmartMesh IP managers,
    either over a serial port, or the SerialMux.</p>
    
    <p>Once it successfully connects to a SmartMesh IP manager, DustLink:</p>
    <ul>
    <li>
        Creates the corresponding network, named after the connection details.
    </li>
    <li>
        Listens for all notifications ("events") generated by the network, and
        for all data coming from motes.
    </li>
    <li>
        Automatically adds motes it becomes aware of to DustLink, and assign
        them to this network.
    </li>
    </ul>
    '''
    CLASS[ 'system', 'managers'] = [CLASS_DEMO]
    
    INTRO[ 'system', 'managers', 'connections'] = \
    "Registered manager connections."
    MORE[  'system', 'managers', 'connections'] = '''
    <p>Shows all connections to managers entered by the user. The Active
    columns shows whether DustLink was able to open that connection ('active')
    or not ('inactive').</p>'''+INFO_SYSTEMMANAGER_ADDDELAY
    CLASS[ 'system', 'managers', 'connections'] = [CLASS_DEMO]
    
    INTRO[ 'system', 'managers', 'add'] = \
    "Add a new manager connection."
    MORE[  'system', 'managers', 'add'] = '''
    <p>DustLink running on the Demo box is pre-configured to automatically
    recognize one manager connected to serial port <tt>/dev/ttyUSB3</tt>.
    Simply connect a SmartMesh IP manager to any of the 3 USB connectors and it
    will appear as "active" within a few seconds.</p>
    
    <p>To add more managers, first physically connect one, enter the name of
    the new serial port it is connected to, and press <tt>Submit</tt>. On the
    DemoBox, this will be <tt>/dev/ttyUSB7</tt> for the second manager, and
    <tt>/dev/ttyUSB11</tt> for the third. If you are running DustLink on a
    Windows or Linux computer, you will first need to determine the location of
    the manager's API port. This can, for example, be <tt>COM4</tt> on Windows,
    <tt>/dev/ttyUSB3</tt> on Linux, or <tt>127.0.0.1:9900</tt>, the Internet
    address of the SerialMux that the manager is connected to.</p>
    
    <p>These settings are persistent, managers can then be unplugged and
    reconnected, they will be automatically recognized. </p>'''+INFO_SYSTEMMANAGER_ADDDELAY
    CLASS[ 'system', 'managers', 'add'] = [CLASS_DEMO]
    
    INTRO[ 'system', 'managers', 'delete'] = \
    "Delete a manager connection."
    MORE[  'system', 'managers', 'delete'] = '''
    <p>Select the connection to delete from the drop-down and press "Submit".</p>
    
    <p>There is a three second delay between the moment you delete a connection
    and when it disappears from the "Manager Connections" table.</p>
    '''
    CLASS[ 'system', 'managers', 'delete'] = [CLASS_DEMO]
    
    INTRO['system', 'managers', 'serialports'] = \
    "Serial ports available on this system."
    MORE[ 'system', 'managers', 'serialports'] = '''
    <p>Lists of currently connected serial ports, provided for information only.
    Each SmartMesh IP evaluation kit manager assembly connected to the system will display
    a set of 4 serial ports, with the 4th typically providing the API interface. Serial
    ports listed are not necessarily connected to a SmartMesh IP device, and are
    not necessarily available.</p>
    
    <p>This list can help you identify the serial port corresponding to
    the manager you wish to connect to. To connect to a particular serial port,
    you need to copy-paste its name (ex: COM5) into the "Add" field above.</p>
    '''
    CLASS[ 'system', 'managers', 'serialports'] = [CLASS_DEMO]
    
    #===== /system/modules
    
    INTRO[ 'system', 'modules'] = \
    "Manage the DustLink modules."
    MORE[  'system', 'modules'] = '''
    <p>DustLink consists of the following modules:</p>
    <ul>
    <li>
        The <b>GATEWAY</b> module connects DustLink to an arbitrary number
        of managers. This module must be activated to connect
        SmartMesh IP manager(s) to the computer running DustLink.
    </li>
    <li>
        The <b>LBR</b> module enables SmartMesh IP devices to be addressed directly from the
        internet via their IPv6 addresses. This module is NOT implemented at this time.</li>
    <li>
        The <b>DATACONNECTOR</b> module receives data from motes and
        stores/displays that data. This module must be enabled if motes will
        exchange data with DustLink.
    </li>
    </ul>
    
    <p class="doc-note">The LBR modules is not yet
    implemented. Enabling the LBR module therefore has no effect.</p>
    '''
    CLASS[ 'system', 'modules'] = []
    
    INTRO[ 'system', 'modules', 'activated'] = \
    "Enable/disable modules."
    MORE[  'system', 'modules', 'activated'] = '''
    <p>The modules whose checkbox is checked are active. Click on its checkbox
    to activate/disable a module.</p>
    
    <p>It can take up to ten seconds for a change in the table below to be
    taken into account by DustLink.</p>
    '''
    CLASS[ 'system', 'modules', 'activated'] = []
    
    #===== /system/persistence
    
    INTRO[ 'system', 'persistence'] = \
    "Manage how DustLink backs up its internal database."
    MORE[  'system', 'persistence'] = '''
    <p>All the data managed by DustLink (user, mote data, applications) can be
    backed-up periodically to a file.</p>
    
    <p>When starting, the DustLink application retrieves the data from this
    back-up and resumes where it left off.</p>
    
    <p>We therefore recommend to keep file persistence enabled.</p>
    '''
    CLASS[ 'system', 'persistence'] = []
    
    INTRO[ 'system', 'persistence', 'activated'] = \
    "Enable/Disable persistence methods."
    MORE[  'system', 'persistence', 'activated'] = None
    CLASS[ 'system', 'persistence', 'activated'] = []
    
    #===== /system/publishers
    
    WARNING_CLEARTEXTCREDENTIALS = '''
    <p class="doc-warning">The Xively API key, as well as the Google username
    and password, are stored in the clear in the database of the DustLink
    website. Anybody with access to the computer running the DustLink
    application will have no problem reading these credentials from the
    database. We therefore recommend you create a Xively and Google accounts
    specifically for this application rather than using personal accounts.</p>
    '''
    
    INTRO[ 'system', 'publishers'] = \
    "Manage publication of sensor data to external services."
    MORE[  'system', 'publishers'] = '''
    <p>Independently from storing received data in its internal data, DustLink
    keeps the latest values received from the following applications in its
    "mirror"</p>
    
    <ul>
        <li><tt>OAPLED</tt></li>
        <li><tt>OAPTemperature</tt></li>
        <li><tt>DC2126A</tt></li>
        <li><tt>LIS331</tt></li>
        <li><tt>GPIONet</tt></li>
        <li><tt>SPIPressure</tt></li>
    </ul>
    
    <p>This is the data that can be seen through the
    <a href="/static/dashboard/index_local.html">dashboard</a>.</p>
    
    <p>Optionally, DustLink can also publish that data either to
    <a href="https://xively.com/">Xively</a>, or a Google spreadsheet.</p>
    <ul>
    <li>To publish to Xively, you need to indicate a master Xively API key;
    DustLink will use that to create the products and devices, then push the
    data.</li>
    <li>To publish to a Google Spreadsheet, you need to tell DustLink where
    to which spreadsheet to send the data, and using which Google user account.
    DustLink will then continuously synchronize the data received in its
    "mirror" with that Google Spreadsheet.</li>
    </ul>
    '''+WARNING_CLEARTEXTCREDENTIALS
    CLASS[ 'system', 'publishers'] = [CLASS_DEMO]
    
    INTRO[ 'system', 'publishers', 'xivelyconfiguration'] = \
    "Xively service feed configuration (Requires an active Xively account)."
    MORE[  'system', 'publishers', 'xivelyconfiguration'] = '''
    <p>A Xively account must first be created as follows</p>
    
    <p>Create a new developer account with Xively at <a href="http://www.xively.com" target="_new">http://www.xively.com</a>:</p>
    <ul>
        <li>From the Web Tools dropdown, select "Settings".</li>
        <li>Under the <b>Settings</b> section, select <b>Master Keys</b>.</li>
        <li>Click on <b>Add Master Key</b>.</li>
        <li>Enter a title for the key, and select all boxes, i.e. <tt>READ</tt>, <tt>CREATE</tt>, <tt>UPDATE</tt>, <tt>DELETE</tt>, and <tt>Access Private Fields</tt>.</li>
    </ul>
    
    <p>On Dustlink:</p>
    <ul>
        <li>Make sure you are logged as a user with write privileges to the systems resource, for example <tt>admin</tt>.</li>
        <li>Copy the Master Key created in the previous steps into the <tt>xivelyApiKey</tt> box below, and click "Submit".</li>
    </ul>
    
    <p>Dustlink will now automatically:</p>
    <ul>
        <li>Connect to your Xively account using the Master key you entered.</li>
        <li>Create the product on Xively corresponding to your SmartMesh IP kit.</li>
        <li>Create a device for each mote in your kit (not the manager).</li>
        <li>Create a datastream called "temperature" corresponding to the temperature sensor of your SmartMesh IP evaluation kit mote.</li>
    </ul>
    
    <p><u>Note</u>: a device and datastream is only created when the corresponding mote publishes temperature readings.</p>
    
    <p>To view the product and device on Xively:</p>
    <ul>
        <li>Make sure you are logged in at <a href="http://www.xively.com" target="_new">http://www.xively.com</a>.</li>
        <li>Select <b>Manage</b> from the Web Tools drop-down. A product called "SmartMesh IP Starter Kit" is not now available.</li>
        <li>Click on it to view the devices corresponding to the motes in your SmartMesh IP network.</li>
        <li>Click on a device to view the datastream and sensor readings.</li>
    </ul>
    
    <p>(optional) Making the feeds public: You may want to to make the feeds "public", for easy access with smart phones during demonstrations for example.
    To make a device public:</p>
    
    <ul>
        <li>From the SmartMesh IP Starter Kit page in <a href="http://www.xively.com" target="_new">http://www.xively.com</a>, click on a device feed.</li>
        <li>Select the little pencil (Edit) at the end of the "SmartMesh IP Starter Kit" name at the top.</li>
        <li>Select "Public Device" under the Privacy section.</li>
    </ul>
    
    <p>All the device data streams in this project will now be public.</p>
    '''+WARNING_CLEARTEXTCREDENTIALS
    
    CLASS[ 'system', 'publishers', 'xivelyconfiguration'] = [CLASS_DEMO]
    
    INTRO[ 'system', 'publishers', 'xivelystatus'] = \
    "Status the Xively publisher."
    MORE[  'system', 'publishers', 'xivelystatus'] = '''
    <p>The list below contains information about the state of the Xively
    publisher.</p>
    
    <ul>
        <li>
            <tt>status</tt> indicates the current state of the publisher:
            <ul>
                <li><tt>CONNECTED</tt> indicates the publisher is currently connected to Xively, ready to send data.</li>
                <li><tt>CONNECTION FAILED</tt> indicates there was a problem connecting. Please verify the API key you are using.</li>
                <li><tt>DISCONNECTED</tt> indicates the publisher is currently not connected to Xively. This is the normal state when no API key has been entered.</li>
           </ul>
        </li>
        <li>
            <tt>numConnectionsFailed</tt> is the number of times the publisher tried to connect to Xively but was unsuccessful. Failure might be due to a wrong API key being used, or networking issues.
        </li>
        <li>
            <tt>numPublishedOK</tt> is the number of data datapoints that were published successfully to Xively.
        </li>
        <li>
            <tt>apiKeySet</tt> indicates whether an API key was entered. For security reasons, this API key is not displayed in the form above.
        </li>
        <li>
            <tt>lastConnected</tt> is the timestamp of the last successful connection to Xively.
        </li>
        <li>
            <tt>numConnectionsOK</tt> is the number of times the publisher successfully connected to Xively.
        </li>
        <li>
            <tt>numPublishedFail</tt> is the number of data datapoints that were published unsuccessfully to Xively. Failure to publish might be due to the wrong API key being used.
        </li>
        <li>
            <tt>lastDisconnected</tt> is the timestamp the last disconnection from Xively.
        </li>
    </ul>
    '''
    CLASS[ 'system', 'publishers', 'xivelystatus'] = [CLASS_DEMO]
    
    INTRO[ 'system', 'publishers', 'googleconfiguration'] = \
    "Information about the Google Spreadsheet to synchronize mirror data to."
    MORE[  'system', 'publishers', 'googleconfiguration'] = '''
    <p>Enter the information and press "Submit" for DustLink to start
    synchronizing its mirror data to a Google Spreadsheet.</p>
    
    <p>You can stop the synchronization by clearing the fields and pressing 
    "Submit"</p>
    
    <ul>
    <li>
        <tt>spreadsheetKey</tt> is the identifier of the Google Spreadsheet to
        synchronize the data to. For example, the spreasheetKey for the spreadsheet 
        at <a href="https://docs.google.com/spreadsheet/ccc?key=0AlATqW9wxWYldHBrRF8yZ3RpQklJcHd5X3FtNXJCN1E" target="_new">https://docs.google.com/spreadsheet/ccc?key=0AlATqW9wxWYldHBrRF8yZ3RpQklJcHd5X3FtNXJCN1E</a>
        is <tt>0AlATqW9wxWYldHBrRF8yZ3RpQklJcHd5X3FtNXJCN1E</tt>.
    </li>
    <li>
        <tt>worksheetName</tt> is the name of Tab in that spreadsheet you want
        the data to be synchronized to.
    </li>
    <li>
        <tt>googleUsername</tt> is a Google username which has write
        privileges to that spreadsheet. DustLink will connect using that username
        to the spreadsheet.
    </li>
    <li>
        <tt>googlePassword</tt> is the password associated with that username.
    </li>
    </ul>
    '''+WARNING_CLEARTEXTCREDENTIALS
    CLASS[ 'system', 'publishers', 'googleconfiguration'] = []
    
    INTRO[ 'system', 'publishers', 'googlestatus'] = \
    "Status the Google publisher."
    MORE[  'system', 'publishers', 'googlestatus'] = '''
    <p>The list below contains information about the state of the Google
    publisher.</p>
    
    <ul>
        <li>
            <tt>status</tt> indicates the current state of the publisher:
            <ul>
                <li><tt>CONNECTED</tt> indicates the publisher is currently connected to Google, ready to send data.</li>
                <li><tt>CONNECTION FAILED</tt> indicates there was a problem connecting. Please verify the API key you are using.</li>
                <li><tt>DISCONNECTED</tt> indicates the publisher is currently not connected to Google. This is the normal state when no API key has been entered.</li>
           </ul>
        </li>
        <li>
            <tt>numConnectionsFailed</tt> is the number of times the publisher tried to connect to Google but was unsuccessful. Failure might be due to a wrong Google username/password, or networking issues.
        </li>
        <li>
            <tt>numPublishedOK</tt> is the number of time the publisher successfully synchronized its data to Google. This counter does <b>not</b> represent the number of datapoints sent, as multiple datapoints can be sent to Google in one synchronization activity.
        </li>
        <li>
            <tt>passwordSet</tt> indicates whether a Goggle password was entered. For security reasons, this password is not displayed in the form above.
        </li>
        <li>
            <tt>lastConnected</tt> is the timestamp of the last successful connection to Google.
        </li>
        <li>
            <tt>numConnectionsOK</tt> is the number of times the publisher successfully connected to Google.
        </li>
        <li>
            <tt>usernameSet</tt> indicates whether a Goggle username was entered. For security reasons, this username is not displayed in the form above.
        </li>
        <li>
            <tt>numPublishedFail</tt> is the number of synchronization activities to Google that failed.
        </li>
        <li>
            <tt>lastDisconnected</tt> is the timestamp the last disconnection from Google.
        </li>
    </ul>
    '''
    CLASS[ 'system', 'publishers', 'googlestatus'] = []
    
    #===== /system/demomode
    
    INTRO[ 'system', 'demomode'] = \
    "Enable/Disable the demo mode."
    MORE[  'system', 'demomode'] = '''
    <p>When the demo mode is enabled, all motes in the network are automatically added to
    DustLink as they appear, and the applications built into the
    default SmartMesh IP mote firmware are automatically associated.</p>
    
    <p class="doc-warning">The demo mode is enabled when resetting the system.</p>
    
    <p>Use this mode when you are demoing a SmartMesh IP network where all
    motes run the default firmware.</p>
    
    <p>When enabling the demo mode, the following changes are applied to DustLink:</p>
    <ul>
        <li>The <tt>OAPLED</tt> application is created.</li>
        <li>The <tt>OAPTemperature</tt> application is created.</li>
        <li>The GET, PUT, DELETE privileges on all motes and all applications are granted to the anonymous user.</li>
        <li>GET privileges on all networks are granted to the anonymous user.</li>
        <li>GET privileges on all test results are granted to the anonymous user.</li>
        <li>GET privileges on system settings are granted to the anonymous user.</li>
        <li>A manager is added on serial port <tt>/dev/ttyUSB3</tt>, which is the default serial port on the DemoBox.</li>
    </ul>
    <p class="doc-warning">Enabling the demo mode allows public access to
    all motes, applications and networks!</p>
    '''
    CLASS[ 'system', 'demomode'] = []
    
    INTRO[ 'system', 'demomode', 'enable'] = None
    MORE[  'system', 'demomode', 'enable'] = None
    CLASS[ 'system', 'demomode', 'enable'] = []
    
    #===== /system/fastmode
    
    INTRO[ 'system', 'fastmode'] = \
    "Enable/Disable the fast mode."
    MORE[  'system', 'fastmode'] = '''
    <p>The fast mode speeds up the execution of DustLink by removing some
    features:</p>
    
    <ul>
        <li>
            With fast mode activated, data received from motes is not
            stored in the DustLink database. Only the last value is kept, and
            shown in the dashboard. This will improve performance if running on a small embedded
            computer that uses only FLASH.
        </li>
        <li>
            With fast mode activated, the application attached to a mote is
            cached. That is, you need to disable the fast mode if you
            want to attach/detach an application to/from a mote.
        </li>
        <li>
            With fast mode activated, the application fields are cached.
            That is, you need to disable the fast mode if you want to
            change the fields of an application.
        </li>
    </ul>
    
    <p>Use this mode when running DustLink on a very constrained FLASH based computer.</p>
    '''
    CLASS[ 'system', 'fastmode'] = []
    
    INTRO[ 'system', 'fastmode', 'enable'] = None
    MORE[  'system', 'fastmode', 'enable'] = None
    CLASS[ 'system', 'fastmode', 'enable'] = []
    
    #===== /system/factoryreset
    
    INTRO[ 'system', 'factoryreset'] = \
    "Reset different elements to their factory (default) settings."
    MORE[  'system', 'factoryreset'] = '''
    You can use this page to reset the motes, DustLink website and manager to 
    their default settings. This is useful e.g. when repeating a demo, or when 
    receiving a set of motes and manager which are in an unknown state.
    '''
    CLASS[ 'system', 'factoryreset'] = [CLASS_DEMO]
    
    INTRO[ 'system', 'factoryreset', 'motes'] = \
    "Reset the application layer of the motes to their default settings."
    MORE[  'system', 'factoryreset', 'motes'] = '''
    <p class="doc-warning">The motes are reset wirelessly, so they need to be
    switched on and have joined their network before you can use this
    command.</p>
    
    <p>This command can be used to reset all of the applications built into
    the SmartMesh IP motes back to factory defaults.  This is especially useful
    after having done a demo where, for example, temperature reporting rates on
    the devices have been changed. Application settings are persistent, so
    simply doing a power cycle will not reset them to factory default.</p>
    
    <p>Running this command triggers a series of wireless commands to switch
    off those data generators on all motes currently connected to DustLink. The
    following is the list of actions that will take place for each connected
    mote.</p>
    
    <ul>
        <li>Disables the <tt>digital_in</tt> data sources: <tt>D1</tt>, <tt>D2</tt>, <tt>D3</tt>, <tt>D4</tt>.</li>
        <li>Sets the <tt>digital_out</tt> pins low: <tt>D5</tt>, <tt>D6</tt>, <tt>INDICATOR_0</tt> LED.</li>
        <li>Disables the <tt>analog</tt> data sources: <tt>A1</tt>, <tt>A2</tt>, <tt>A3</tt>, <tt>A4</tt>.</li>
        <li>Enables the temperature sensor, and has it report data every 30 seconds (this is the default behavior).</li>
        <li>Disables the <tt>pkgen</tt> application.</li>
    </ul>
    
    <p>In the command field below, enter <tt>reset</tt> then click on the
    <tt>Submit</tt> button.</p>
    
    <p>You can follow the progress of the reset in the \"Progress\" section
    below.</p>
    
    <p class="doc-note">To use this command, you need to be logged in with a
    user who has <tt>delete</tt> privileges on the <tt>system</tt>.</p>
    '''
    CLASS[ 'system', 'factoryreset', 'motes'] = [CLASS_DEMO]
    
    INTRO[ 'system', 'factoryreset', 'dustlink'] = \
    "Reset this DustLink website to its default settings."
    MORE[  'system', 'factoryreset', 'dustlink'] = '''
    <p>This command allows you to reset this DustLink website. Note that this
    results in the deletion of <i>all</i> the internal data, including
    users, motes and networks.</p>
    
    <p>In the command field below, enter <tt>reset</tt> then click on the
    <tt>Submit</tt> button.</p>
    
    <p class="doc-warning">Resetting DustLink will switch on demo mode.</p>
    
    <p class="doc-note">To use this command, you need to be logged in with a
    user who has <tt>delete</tt> privileges on the <tt>system</tt>.</p>
    '''
    CLASS[ 'system', 'factoryreset', 'dustlink'] = [CLASS_DEMO]
    
    INTRO[ 'system', 'factoryreset', 'manager'] = \
    "Reset a manager to its default settings."
    MORE[  'system', 'factoryreset', 'manager'] = '''
    <p class="doc-warning">The manager needs to be physically connected to the
    computer running this website.</p>
    
    <p class="doc-warning">Before running this command, follow the steps below:</p>
    <ul>
        <li>
            Navigate to the <a href="/system/managers">Managers</a> page.
        </li>
        <li>
            In the "Delete" section, select all the manager connections and
            click <tt>Submit</tt>.
        </li>
    </ul>
    <p>This will ensure that DustLink is not receiving data from the manager
    while this utility is resetting it.</p>
    
    <p>In the command field below, enter the serial port this manager is
    connected to (e.g. <tt>/dev/ttyUSB3</tt> if you are using the DemoBox),
    or the SerialMux connection details (e.g. <tt>127.0.0.1:9900</tt>), then
    click on the <tt>Submit</tt> button.</p>
    
    <p>You can follow the progress of the reset in the \"Progress\" section
    below.</p>
    
    <p class="doc-note">To use this command, you need to be logged in with a
    user who has <tt>delete</tt> privileges on the <tt>system</tt>.</p>
    '''
    CLASS[ 'system', 'factoryreset', 'manager'] = [CLASS_DEMO]
    
    INTRO[ 'system', 'factoryreset', 'progress'] = \
    "Follow the progress of a reset manager/motes command."
    MORE[  'system', 'factoryreset', 'progress'] = '''
    <p>The contents of this table is reset each time you issue a new reset
    command.</p>
    '''
    CLASS[ 'system', 'factoryreset', 'progress'] = [CLASS_DEMO]
    
    INTRO[ 'system', 'factoryreset', 'serialports'] = \
    "List of serial ports know to the system."
    MORE[  'system', 'factoryreset', 'serialports'] = '''
    <p>Lists of currently connected serial ports, provided for information only.
    Each SmartMesh IP evaluation kit manager assembly connected to the system will display
    a set of 4 serial ports, with the 4th typically providing the API interface. Serial
    ports listed are not necessarily connected to a SmartMesh IP device, and are
    not necessarily available.</p> 
    '''
    CLASS[ 'system', 'factoryreset', 'serialports'] = [CLASS_DEMO]
    
    #===== /system/loadconfig
    
    WARNING_LOADCONFIG = '''
    <p class="doc-note">Loading a configuration file
    is equivalent to resetting DustLink, then applying a number of
    configurations. This results in the deletion of <i>all</i> the
    internal data, including users, motes and networks.</p>
    '''
    
    INTRO[ 'system', 'loadconfig'] = \
    "Reset and load a full configuration from a file on your computer."
    MORE[  'system', 'loadconfig'] = '''
    <p>Instead of having to go through a number of configuration steps to fully
    configure DustLink, you can use this page to upload a configuration file
    which will do all the configuration steps simultaneously.</p>
    
    <p>This configuration file is a normal text file with the following syntax:
    </p>
    <ul>
        <li>
            Empty lines are ignored.
        </li>
        <li>
            Lines starting with a <tt>#</tt> are ignored; you can use them for
            commenting your configuration files.
        </li>
    </ul>
    
    <p>The following commands are supported:</p>
    <ul>
        <li>
            To reset the admin password to "somePassword":<br/>
            <pre>type="adminPassword" password="somePassword"</pre>
        </li>
        <li>
            To add the application GPIONet on port 60102:<br/>
            <pre>type="app" appName="GPIONet" transport="UDP.60102" fieldsFromMote="b=pinVal" fieldsToMote=""</pre> 
        </li>
        <li>
            To enable the fast mode:<br/>
            <pre>type="fastMode" value="true"</pre>
        </li>
        <li>
            To enable the demo mode:<br/>
            <pre>type="demoMode" value="true"</pre>
        </li>
        <li>
            To enter publisher settings:<br/>
            <pre>type="publisher" spreadsheetKey="someKey" worksheetName="someName" googleUsername="someUser" googlePassword="somePassword"</pre>
        </li>
        <li>
            To add a mote:<br/>
            <pre>type="mote" mac="00-17-0D-00-00-38-13-EA"</pre>
        </li>
        <li>
            To attach an application to a mote:<br/>
            <pre>type="attachApp" mac="00-17-0D-00-00-38-13-EA" appName="OAPTemperature"</pre>
        </li>
        <li>
            To create a network:<br/>
            <pre>type="network" netname="-dev-ttyUSB3"</pre>
        </li>
        <li>
            To create a user:<br/>
            <pre>type="user" username="someUser"</pre>
        </li>
        <li>
            To grant a privilege to a user:<br/>
            <pre>type="grantPrivilege" username="someUser" resource="motes.00-17-0D-00-00-38-13-EA" action="get"</pre>
        </li>
    </ul>
    '''+WARNING_LOADCONFIG
    CLASS[ 'system', 'loadconfig'] = []
    
    INTRO[ 'system', 'loadconfig', 'load'] = \
    "Upload a config file."
    MORE[  'system', 'loadconfig', 'load'] = '''
    <p>Select a file from on your computer using the "Choose File" button,
    then click the "Submit" button to upload and apply that configuration
    file.</p>
    '''+WARNING_LOADCONFIG
    CLASS[ 'system', 'loadconfig', 'load'] = []
    
    #===== /system/restarts
    
    INTRO[ 'system', 'restarts'] = \
    "Display information about the restarts of the system."
    MORE[  'system', 'restarts'] = None
    CLASS[ 'system', 'restarts'] = []
    
    INTRO[ 'system', 'restarts', 'upTimeRestarts'] = \
    "Display information about the number of Dustlink restarts."
    MORE[  'system', 'restarts', 'upTimeRestarts'] = '''
    <p><tt>UpTime</tt> is the amount of time DustLink has been running
    since it was last restarted.</p>
    <p><tt>number of restarts</tt> is how many times DustLink was started.</p>
    '''
    CLASS[ 'system', 'restarts', 'upTimeRestarts'] = []
    
    INTRO[ 'system', 'restarts', 'lastRestarts'] = \
    "Only the last ten restarts are displayed."
    MORE[  'system', 'restarts', 'lastRestarts'] = None
    CLASS[ 'system', 'restarts', 'lastRestarts'] = []
    
    #===== /system/sessions
    
    INTRO[ 'system', 'sessions'] = None
    MORE[  'system', 'sessions'] = None
    CLASS[ 'system', 'sessions'] = []
    
    INTRO[ 'system', 'sessions', 'active'] = \
    " "
    MORE[  'system', 'sessions', 'active'] = '''
    DustLink maintains a session for every user accessing the system.
    '''
    CLASS[ 'system', 'sessions', 'active'] = []
    
    #===== /system/profiling
    
    INTRO[ 'system', 'profiling'] = \
    "This page is used for internal debugging purposes only."
    MORE[  'system', 'profiling'] = None
    CLASS[ 'system', 'profiling'] = []
    
    INTRO[ 'system', 'profiling', 'yappi'] = \
    "Enabling/Disabling the profiler."
    MORE[  'system', 'profiling', 'yappi'] = '''
    Yappi is a Python profiler which indicates how many resources each thread
    and function is using.
    '''
    CLASS[ 'system', 'profiling', 'yappi'] = []
    
    INTRO[ 'system', 'profiling', 'threads'] = None
    MORE[  'system', 'profiling', 'threads'] = None
    CLASS[ 'system', 'profiling', 'threads'] = []
    
    INTRO[ 'system', 'profiling', 'functions'] = None
    MORE[  'system', 'profiling', 'functions'] = None
    CLASS[ 'system', 'profiling', 'functions'] = []
    
    #===== /system/eventbus
    
    INTRO[ 'system', 'eventbus'] = \
    "This page is used for internal debugging purposes only."
    MORE[  'system', 'eventbus'] = None
    CLASS[ 'system', 'eventbus'] = []
    
    INTRO[ 'system', 'eventbus', 'stats'] = None
    MORE[  'system', 'eventbus', 'stats'] = None
    CLASS[ 'system', 'eventbus', 'stats'] = []
    
    INTRO[ 'system', 'eventbus', 'connections'] = None
    MORE[  'system', 'eventbus', 'connections'] = None
    CLASS[ 'system', 'eventbus', 'connections'] = []
    
    #===== /system/rawdata
    
    INTRO[ 'system', 'rawdata'] = \
    "This page is used for internal debugging purposes only."
    MORE[  'system', 'rawdata'] = None
    CLASS[ 'system', 'rawdata'] = []
    
    INTRO[ 'system', 'rawdata', 'rawdata'] = None
    MORE[  'system', 'rawdata', 'rawdata'] = None
    CLASS[ 'system', 'rawdata', 'rawdata'] = []
    
    #===== /system/about
    
    INTRO[ 'system', 'about'] = None
    MORE[  'system', 'about'] = None
    CLASS[ 'system', 'about'] = [CLASS_DEMO]
    
    INTRO[ 'system', 'about', 'version'] = None
    MORE[  'system', 'about', 'version'] = None
    CLASS[ 'system', 'about', 'version'] = [CLASS_DEMO]
    
    INTRO[ 'system', 'about', 'license'] = None
    MORE[  'system', 'about', 'license'] = None
    CLASS[ 'system', 'about', 'license'] = []
    
    INTRO[ 'system', 'about', 'thirdparty'] = None
    MORE[  'system', 'about', 'thirdparty'] = None
    CLASS[ 'system', 'about', 'thirdparty'] = []
    
    #======================== motedata ========================================
    
    #===== /motedata
    
    INTRO[ ('motedata', )] = \
    "Interact with a particular application installed on a particular mote."
    MORE[  ('motedata', )] = None
    CLASS[('motedata', )] = []
    
    #===== /motedata/received
    
    INTRO[ ('motedata', 'received')] = \
    "Displays <b>raw un-interpreted</b> received field values."
    MORE[  ('motedata', 'received')] = '''
    <p>The graph below shows a timeline of the raw field values received from 
    a particular application running on a particular mote.</p>
    
    <p>These values are <b>un-interpreted</b>, and presented as the values
    read from a data packet's fields. For some application, some interpretation
    is done before displaying the data in the dashboard.</p>
    
    <p>For example, temperature is reported by the <tt>OAPTemperature</tt>
    application is 1/100th degrees C. Before being published on the dashboard,
    DustLink modifies the unit to degrees C.</p>
    
    <p>In this case, it is <b>normal</b> that the value in the dashboard is not
    the same as the value displayed in the timeline below.</p>
    
    <p class="doc-warning">Data only shows up below if DustLink is not
    running in fast mode.</p>
    '''
    CLASS[('motedata', 'received')] = []
    
    #===== /motedata/clear
    
    INTRO[ ('motedata', 'clear')] = \
    "Clear data received from this application."
    MORE[  ('motedata', 'clear')] = '''
    To clear the data from received from this application running on this mote,
    enter <tt>clear</tt> in the form below and click <tt>Submit</tt>.
    
    Note that you need to be logged in as a user which has <tt>delete</tt>
    privileges on both this application and this mote.
    '''
    CLASS[('motedata', 'clear')] = []
    
    #===== /motedata/send
    
    INTRO[ ('motedata', 'send')] = \
    "Send arbitrary data to the application."
    MORE[  ('motedata', 'send')] = None
    CLASS[('motedata', 'send')]  = []
    
    #======================== methods =========================================
    
    _singleton = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._singleton:
            cls._instance = super(DustLinkWebDoc, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def _mapDoc(self, what, where):
        whatLen = len(what)
        def _mapDict(dictObj):
            for i, v in dictObj.items():
                if len(i) >= whatLen and all(a==b for a, b in zip(i, what)):
                    target = tuple(where + list(i[whatLen:]))
                    dictObj[target] = v
        _mapDict(self.INTRO)
        _mapDict(self.MORE)
        _mapDict(self.CLASS)

    def __init__(self):
        '''
        Constructor
        '''
        self._mapDoc(('system', 'managers'), ['system'])

    def getIntro(self, path):
        path = self._removePathSuffix(path)
        try:
            return self.INTRO[path]
        except KeyError:
            if log.isEnabledFor(logging.WARNING):
                log.warning("Missing documentation (intro) for {PATH}".format(PATH=str(path)))
            return None
    
    def getMore(self, path):
        path = self._removePathSuffix(path)
        try:
            return self.MORE.get(path)
        except KeyError:
            if log.isEnabledFor(logging.WARNING):
                log.warning("Missing documentation (more) for {PATH}".format(PATH=str(path)))
            return None
    
    def getClass(self, path):
        path = self._removePathSuffix(path)
        try:
            return ' '.join(self.CLASS.get(path,[]))
        except KeyError:
            if log.isEnabledFor(logging.WARNING):
                log.warning("Missing labels for {PATH}".format(PATH=str(path)))
            return ''
    
    def _removePathSuffix(self,path):
        '''
        \brief Removes the suffix of a path.
        
        Some paths can contain a suffix, i.e. the text following the '?' in the
        URL.
        
        For example, the following URL
        http://127.0.0.1:8080/motedata?mac=11-11-11-11-11-11-11-11&app=app1
        
        translates, by default, into path
        ('motedata?mac=11-11-11-11-11-11-11-11&app=app1',)
        
        This function removes the suffix, i.e. the path becomes
        ('motedata',)
        
        \param path The path to remove the suffix from, a tuple of strings.
        
        \returns The path without the suffix.
        '''
        return tuple([p.split('?')[0] for p in path])
