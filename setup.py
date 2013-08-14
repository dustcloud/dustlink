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
sys.path.append(os.path.join('protocols'))
sys.path.append(os.path.join('SmartMeshSDK'))
sys.path.append(os.path.join('views', 'web'))
sys.path.append(os.path.join('views', 'cli'))

from DustLink import DustLink_version

# Create the DustLink package

SCRIPTS    = ['dustLinkFullWeb/dustLinkFullWeb.py',
             ]

FILES      = [
                ('',                                                    ['DN_LICENSE.txt']),
                ('views/web/dustWeb/keys',                              ['views/web/dustWeb/keys/README.txt']),
                ('views/web/dustWeb/logs',                              ['views/web/dustWeb/logs/README.txt']),
                ('views/web/dustWeb/static',                            ['views/web/dustWeb/static/README.txt']),
                ('views/web/dustWeb/static/dashboard',                  glob.glob(os.path.join('views','web','dustWeb','static','dashboard','*'))),
                ('views/web/dustWeb/static/javascript',                 glob.glob(os.path.join('views','web','dustWeb','static','javascript','*'))),
                ('views/web/dustWeb/static/templates',                  ['views/web/dustWeb/static/templates/README.txt']),
                ('views/web/dustWeb/static/templates/datatables',       ['views/web/dustWeb/static/templates/datatables/README.txt']),
                ('views/web/dustWeb/static/templates/datatables/css',   glob.glob(os.path.join('views','web','dustWeb','static','templates','datatables','css','*'))),
                ('views/web/dustWeb/static/templates/datatables/images',glob.glob(os.path.join('views','web','dustWeb','static','templates','datatables','images','*'))),
                ('views/web/dustWeb/static/templates/dust',             ['views/web/dustWeb/static/templates/dust/README.txt']),
                ('views/web/dustWeb/static/templates/dust/css',         glob.glob(os.path.join('views','web','dustWeb','static','templates','dust','css','*'))),
                ('views/web/dustWeb/static/templates/dust/images',      glob.glob(os.path.join('views','web','dustWeb','static','templates','dust','images','*'))),
                ('views/web/dustWeb/static/templates/dust/javascript',  glob.glob(os.path.join('views','web','dustWeb','static','templates','dust','javascript','*'))),
                ('views/web/dustWeb/templates',                         ['views/web/dustWeb/templates/README.txt']),
                ('views/web/dustWeb/templates/dust',                    glob.glob(os.path.join('views','web','dustWeb','templates','dust','*'))),
                ('views/web/dustWeb/templates/white',                   glob.glob(os.path.join('views','web','dustWeb','templates','white','*'))),
             ]

FUNC_TESTS = ['dummyDataWeb/dummyDataWeb.py',
             ]

setup(name='DustLink',
      version='.'.join([str(v) for v in DustLink_version.VERSION]),
      scripts=[os.path.join('bin', s) for s in SCRIPTS] + [os.path.join('func_tests', s) for s in FUNC_TESTS],
      
      packages=['DataConnector',
                'DustLink',
                'DustLinkData',
                'EventBus',
                'Gateway',
                'Gateway.NetworkTest',
                'Gateway.NetworkTestPublisher',
                'protocols.oap',
                'SmartMeshSDK',
                'SmartMeshSDK.ApiDefinition',
                'SmartMeshSDK.IpMgrConnectorMux',
                'SmartMeshSDK.IpMgrConnectorSerial',
                'SmartMeshSDK.IpMoteConnector',
                'SmartMeshSDK.HartMgrConnector',
                'SmartMeshSDK.HartMoteConnector',
                'SmartMeshSDK.SerialConnector',
                'DustLinkCli',
                'DustLinkCli.dustCli',
                'DustLinkWeb',
                'DustLinkWeb.dustWeb',
                'DustLinkWeb.dustWeb.thirdparty',
                'DustLinkWeb.dustWeb.viz',
                'DustLinkWeb.dustWeb.web',
                'DustLinkWeb.dustWeb.web.contrib',
                'DustLinkWeb.dustWeb.web.wsgiserver',
                ],
                
      package_dir={'':            '.',
                   'DustLinkCli': 'views/cli',
                   'DustLinkWeb': 'views/web',
                   },
      
      data_files = FILES,

      # url=
      author='Linear Technology',
      author_email="dust-support@linear.com",
      license='see DN_LICENSE.txt',

      # py2exe parameters
      console=  [
                    {'script': os.path.join('bin', 'dustLinkFullWeb', 'dustLinkFullWeb.py'),
                    },
                ],
      windows=  [         
                ],
      zipfile=None,
      options={ 'py2exe': { #'bundle_files': 1,
                            'dll_excludes': ['MSVCP90.dll', 'w9xpopen.exe'], },
                },

      )
