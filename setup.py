# use distutils because it's easier to specify what's included
from distutils.core import setup
try:
    import py2exe
except ImportError:
    pass

# Grab the current version from the version file
import glob
import os
import sys

# edit the path to what the binaries expect
sys.path.append(os.path.join('SmartMeshSDK'))
sys.path.append(os.path.join('views', 'web'))
sys.path.append(os.path.join('views', 'cli'))

from DustLink import DustLink_version

# Create the DustLink package

setup(
    name           = 'DustLink',
    version        = '.'.join([str(v) for v in DustLink_version.VERSION]),
    scripts        = [
        os.path.join('bin',        'dustLinkFullWeb', 'dustLinkFullWeb.py'),
        os.path.join('func_tests', 'dummyDataWeb',    'dummyDataWeb.py'),
    ],
    packages       = [
        'DataConnector',
        'DustLink',
        'DustLinkData',
        'EventBus',
        'Gateway',
        'SmartMeshSDK',
        'SmartMeshSDK.ApiDefinition',
        'SmartMeshSDK.HartMgrConnector',
        'SmartMeshSDK.HartMoteConnector',
        'SmartMeshSDK.IpMgrConnectorMux',
        'SmartMeshSDK.IpMgrConnectorSerial',
        'SmartMeshSDK.IpMoteConnector',
        'SmartMeshSDK.protocols',
        'SmartMeshSDK.protocols.DC2126AConverters',
        'SmartMeshSDK.protocols.oap',
        'SmartMeshSDK.protocols.xivelyConnector',
        'SmartMeshSDK.SerialConnector',
        'views',
        'views.cli',
        'views.cli.dustCli',
        'views.web',
        'views.web.dustWeb',
        'views.web.dustWeb.thirdparty',
        'views.web.dustWeb.viz',
        'views.web.dustWeb.web',
        'views.web.dustWeb.web.contrib',
        'views.web.dustWeb.web.wsgiserver',
    ],
    data_files     = [
        (
            '',
            ['DN_LICENSE.txt']
        ),
        (
            '',
            ['requirements.txt']
        ),
        (
             'bin/dustLinkFullWeb',
            ['bin/dustLinkFullWeb/logging.conf']
        ),
        (
             'views/web/dustWeb/keys',
            ['views/web/dustWeb/keys/README.txt']
        ),
        (
             'views/web/dustWeb/logs',
            ['views/web/dustWeb/logs/README.txt']
        ),
        (
             'views/web/dustWeb/static',
            ['views/web/dustWeb/static/README.txt']
        ),
        (
            'views/web/dustWeb/static/dashboard',
            glob.glob(os.path.join('views','web','dustWeb','static','dashboard','*'))
        ),
        (
            'views/web/dustWeb/static/javascript',
            glob.glob(os.path.join('views','web','dustWeb','static','javascript','*'))
        ),
        (
             'views/web/dustWeb/static/templates',
            ['views/web/dustWeb/static/templates/README.txt']
        ),
        (
             'views/web/dustWeb/static/templates/datatables',
            ['views/web/dustWeb/static/templates/datatables/README.txt']
        ),
        (
            'views/web/dustWeb/static/templates/datatables/css',
            glob.glob(os.path.join('views','web','dustWeb','static','templates','datatables','css','*'))
        ),
        (
            'views/web/dustWeb/static/templates/datatables/images',
            glob.glob(os.path.join('views','web','dustWeb','static','templates','datatables','images','*'))
        ),
        (
             'views/web/dustWeb/static/templates/dust',
            ['views/web/dustWeb/static/templates/dust/README.txt']
        ),
        (
            'views/web/dustWeb/static/templates/dust/css',
            glob.glob(os.path.join('views','web','dustWeb','static','templates','dust','css','*'))
        ),
        (
            'views/web/dustWeb/static/templates/dust/images',
            glob.glob(os.path.join('views','web','dustWeb','static','templates','dust','images','*'))
        ),
        (
            'views/web/dustWeb/static/templates/dust/javascript',
            glob.glob(os.path.join('views','web','dustWeb','static','templates','dust','javascript','*'))
        ),
        (
            'views/web/dustWeb/static/testicons',
            glob.glob(os.path.join('views','web','dustWeb','static','testicons','*'))
        ),
        (
             'views/web/dustWeb/templates',
            ['views/web/dustWeb/templates/README.txt']
        ),
        (
            'views/web/dustWeb/templates/dust',
            glob.glob(os.path.join('views','web','dustWeb','templates','dust','*'))
        ),
        (
            'views/web/dustWeb/templates/white',
            glob.glob(os.path.join('views','web','dustWeb','templates','white','*'))
        ),
    ],
    author         = 'Linear Technology',
    author_email   = "dust-support@linear.com",
    license        = 'see DN_LICENSE.txt',
    # py2exe parameters
    console        =  [
        {'script': os.path.join('bin', 'dustLinkFullWeb', 'dustLinkFullWeb.py'),},
    ],
    windows        = [
    ],
    zipfile        = None,
    options        = {
        'py2exe': {
            #'bundle_files': 1,
            'dll_excludes': ['MSVCP90.dll', 'w9xpopen.exe'], },
    },
)
