#!/usr/bin/python

import ApiDefinition
import ByteArraySerializer

class IpMoteDefinition(ApiDefinition.ApiDefinition):
    '''
    \ingroup ApiDefinition
    \brief  API definition for the IP mote.
   
    \note   This class inherits from ApiDefinition. It redefines the attributes of
            its parents class, but inherits the methods.
    '''
    
    STRING    = ApiDefinition.FieldFormats.STRING
    BOOL      = ApiDefinition.FieldFormats.BOOL
    INT       = ApiDefinition.FieldFormats.INT
    INTS      = ApiDefinition.FieldFormats.INTS
    HEXDATA   = ApiDefinition.FieldFormats.HEXDATA
    RC        = ApiDefinition.ApiDefinition.RC
    SUBID1    = ApiDefinition.ApiDefinition.SUBID1
    SUBID2    = ApiDefinition.ApiDefinition.SUBID2
    RC_OK     = ApiDefinition.ApiDefinition.RC_OK
    
    def __init__(self):
        self.serializer = ByteArraySerializer.ByteArraySerializer(self)
    
    def default_serializer(self,commandArray,fieldsToFill):
        '''
        \brief IpMgrDefinition-specific implementation of default serializer
        '''
        return self.serializer.serialize(commandArray,fieldsToFill)
        
    def deserialize(self,type,cmdId,byteArray):
        '''
        \brief IpMgrDefinition-specific implementation of deserializer
        '''
        return self.serializer.deserialize(type,cmdId,byteArray)
    
    # We redefine this attribute inherited from ApiDefinition. See
    # ApiDefinition for a full description of the structure of this field.
    fieldOptions = {
        RC: [
            [0x00, 'OK',                    'Command completed successfully'],
            [0x01, 'ERROR',                 'Processing error'],
            [0x03, 'BUSY',                  'Device currently unavailable to perform the operation'],
            [0x04, 'INVALID_LEN',           'Invalid length'],
            [0x05, 'INV_STATE',             'Invalid state'],
            [0x06, 'UNSUPPORTED',           'Unsupported command or operation'],
            [0x07, 'UNKNOWN_PARAM',         'Unknown parameter'],
            [0x08, 'UNKNOWN_CMD',           'Unknown command'],
            [0x09, 'WRITE_FAIL',            'Couldn\'t write to persistent storage'],
            [0x0A, 'READ_FAIL',             'Couldn\'t read from persistent storage'],
            [0x0B, 'LOW_VOLTAGE',           'Low voltage detected'],
            [0x0C, 'NO_RESOURCES',          'Couldn\'t process command due to low resources (e.g. no buffers)'],
            [0x0D, 'INCOMPLETE_JOIN_INFO',  'Incomplete configuration to start joining'],
            [0x0E, 'NOT_FOUND',             'Resource not found'],
            [0x0F, 'INVALID_VALUE',         'Invalid value supplied'],
            [0x10, 'ACCESS_DENIED',         'Access to resource or command is denied'],
        ],
        'serviceType': [
            [0,    'bandwidth',             'Bandwidth-type service'],
        ],
        'serviceState': [
            [0,    'completed',             'Service request completed (idle)'],
            [1,    'pending',               'Service request pending'],
        ],
        'protocolType': [
            [0,    'udp',                   'User Datagram Protocol (UDP)'],
        ],
        'packetPriority': [
            [0,    'low',                   'Low priority'],
            [1,    'medium',                'Medium priority'],
            [2,    'high',                  'High priority'],
        ],
        'moteState': [
            [0,    'init',                  'Initializing'],
            [1,    'idle',                  'Idle, ready to be configured or join'],
            [2,    'searching',             'Searching for network'],
            [3,    'negotiating',           'Sent join request'],
            [4,    'connected',             'Received at least one packet from the Manager'],
            [5,    'operational',           'Configured by Manager and ready to send data'],
            [6,    'disconnected',          'Disconnected from the network'],
            [7,    'radiotest',             'The mote is in radio test mode'],
            [8,    'promiscuous listen',    'The mote received search command and is in promiscuous listen mode.'],
        ],
        'moteEvents': [
            [0x0001, 'boot',                'The mote booted up'],
            [0x0002, 'alarmChange',         'Alarm(s) were opened or closed'],
            [0x0004, 'timeChange',          'UTC time-mapping on the mote changed'],
            [0x0008, 'joinFail',            'Join operation failed'],
            [0x0010, 'disconnected',        'The mote disconnected from the network'],
            [0x0020, 'operational',         'Mote has connection to the network and is ready to send data'],
            [0x0080, 'svcChange',           'Service allocation has changed'],
            [0x0100, 'joinStarted',          'Mote started joining the network'],
        ],
        'moteAlarms': [
            [0x01, 'nvError',               'Detected an error in persistent configuration storage (NV)'],
            [0x04, 'otpError',              'Detected an error in calibration or bsp data in flash'],
        ],
        'radioTestTypes' : [
            [0x00, 'packet',                'Packet transmission'],
            [0x01, 'cm',                    'Continuous modulation'],
            [0x02, 'cw',                    'Continuous Wave'],
        ],
        'packetTransmitStatus': [
            [0x00, 'ok',                    'Packet sent into the network'],
            [0x01, 'fail',                  'packet was dropped due to timeout or lack of route'],
        ],
        'channel': [
            [0,    '2.405GHz',              ''],
            [1,    '2.410GHz',              ''],
            [2,    '2.415GHz',              ''],
            [3,    '2.420GHz',              ''],
            [4,    '2.425GHz',              ''],
            [5,    '2.430GHz',              ''],
            [6,    '2.435GHz',              ''],
            [7,    '2.440GHz',              ''],
            [8,    '2.445GHz',              ''],
            [9,    '2.450GHz',              ''],
            [10,   '2.455GHz',              ''],
            [11,   '2.460GHz',              ''],
            [12,   '2.465GHz',              ''],
            [13,   '2.470GHz',              ''],
            [14,   '2.475GHz',              ''],
            [15,   '2.480GHz',              ''],
        ],
        'ccaMode': [
            [0,    'off',                   ''],
            [1,    'on',                    ''],
        ],
        'mobilityType': [
            [0x00, 'UNUSED',                ''],
            [0x01, 'KNOWN',                 ''],
            [0x02, 'UNKNOWN',               ''],
            [0x03, 'MOBILE',                ''],
        ],
        'txPower': [
            [0,    '0dBm',                  ''],
            [8,    '+8dBm',                 ''],
        ],
    }
    
    subCommandsSet = [
        {
            'id'         : 0x01,
            'name'       : 'macAddress',
            'description': 'This command allows user to overwrite the manufacturer-assigned MAC address of the mote. The new value takes effect after the mote resets.',
            'request'    : [
                ['macAddress',              HEXDATA,  8,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x02,
            'name'       : 'joinKey',
            'description': 'The setParameter<joinKey> command may be used to set the join key in mote\'s persistent storage. Join keys are used by motes to establish secure connection with the network. The join key is used at next join. Note: reading joinKey parameter is prohibited for security reasons.',
            'request'    : [
                ['joinKey',                 HEXDATA,  16,  None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x03,
            'name'       : 'networkId',
            'description': 'This command may be used to set network id of the mote. This setting is persistent and is used on next join attempt. ',
            'request'    : [
                ['networkId',               INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x04,
            'name'       : 'txPower',
            'description': 'The setParameter<txPower> command sets the mote output power. This setting is persistent. The command may be issued at any time and takes effect on next transmission. Refer to product datasheets for supported RF output power values. For example, if the mote has a typical RF output power of +8 dBm when the power amplifier (PA) is enabled, then set the txPower parameter to 8 to enable the PA. Similarly, if the mote has a typical RF output power of -2 dBm when the PA is disabled, then set the txPower parameter to -2 to turn off the PA.',
            'request'    : [
                ['txPower',                 INTS,     1,   True],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x06,
            'name'       : 'joinDutyCycle',
            'description': 'The setParameter<joinDutyCycle> command allows the microprocessor to control the ratio of active listen time to doze time (a low-power radio state) during the period when the mote is searching for the network. If you desire a faster join time at the risk of higher power consumption, use the setParameter<joinDutyCycle> command to increase the join duty cycle up to 100%. This setting is persistent and takes effect immediately.',
            'request'    : [
                ['dutyCycle',               INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x0B,
            'name'       : 'eventMask',
            'description': 'setParameter <eventMask> allows the microprocessor to selectively subscribe to event notifications . The default value of eventMask at mote reset is all 1s -- all events are enabled. This setting is not persistent.',
            'request'    : [
                ['eventMask',               HEXDATA,  4,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x15,
            'name'       : 'otapLockout',
            'description': 'This command allows the microprocessor to control whether Over-The-Air Programming (OTAP) of motes is allowed. This setting is persistent and takes effect immediately.',
            'request'    : [
                ['mode',                    BOOL,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x16,
            'name'       : 'macMicKey',
            'description': 'Set the key used for MAC authentication.',
            'request'    : [
                ['macMicKey',               HEXDATA,  16,  None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x17,
            'name'       : 'moteId',
            'description': 'Set the mote\'s short address.',
            'request'    : [
                ['moteId',                  INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x18,
            'name'       : 'ipv6Address',
            'description': 'Set the mote\'s IPv6 address.',
            'request'    : [
                ['ipv6Address',             HEXDATA,  16,  None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x19,
            'name'       : 'ccaMode',
            'description': '',
            'request'    : [
                ['ccaMode',                 INT,      1,   True],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x1A,
            'name'       : 'Channels',
            'description': '',
            'request'    : [
                ['bitmap',                  INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x1B,
            'name'       : 'advGraph',
            'description': '',
            'request'    : [
                ['graphId',                 INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x1C,
            'name'       : 'hrTimer',
            'description': 'Set the duration (in seconds) between consecutive health reports.',
            'request'    : [
                ['hrTimer',                 INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x1D,
            'name'       : 'routingMode',
            'description': 'This command allows the microprocessor to control whether the mote will become a router once joined the network. If disabled, the manager will keep the mote a leaf node.',
            'request'    : [
                ['mote',                    BOOL,     1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x1E,
            'name'       : 'appInfo',
            'description': '',
            'request'    : [
                ['vendorId',                INT,      2,   None],
                ['appId',                   INT,      1,   None],
                ['appMajorSwRev',           INT,      1,   None],
                ['appMinorSwRev',           INT,      1,   None],
                ['appPatchNum',             INT,      1,   None],
                ['appBuildNum',             INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x1F,
            'name'       : 'pwrSrcInfo',
            'description': 'This command allows the microprocessor to configure power source information on the device. This setting is persistent and is used at network join time.',
            'request'    : [
                ['MaxStCurrent',            INT,      2,   None],
                ['MinLifetime',             INT,      1,   None],
                ['currentLimit_0',          INT,      2,   None],
                ['dischargePeriod_0',       INT,      2,   None],
                ['rechargePeriod_0',        INT,      2,   None],
                ['currentLimit_1',          INT,      2,   None],
                ['dischargePeriod_1',       INT,      2,   None],
                ['rechargePeriod_1',        INT,      2,   None],
                ['currentLimit_2',          INT,      2,   None],
                ['dischargePeriod_2',       INT,      2,   None],
                ['rechargePeriod_2',        INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x21,
            'name'       : 'mobilityType',
            'description': '',
            'request'    : [
                ['mobilityType',            INT,      1,   True],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x22,
            'name'       : 'advKey',
            'description': 'Set the key used by the mote for advertisement packets',
            'request'    : [
                ['advKey',                  HEXDATA,  16,  None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x24,
            'name'       : 'autoJoin',
            'description': '',
            'request'    : [
                ['mode',                    INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
    ]
    
    subCommandsGet = [
        {
            'id'         : 0x01,
            'name'       : 'macAddress',
            'description': 'This command returns the MAC address of the device. By default, the MAC address returned is the EUI64 address of the device assigned by mote manufacturer, but it may be overwritten using the setParameter<macAddress> command.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['macAddress',          HEXDATA,  8,   None],
                ],
            },
        },
        {
            'id'         : 0x03,
            'name'       : 'networkId',
            'description': 'This command returns the network id stored in mote\'s persistent storage.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['networkId',           INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 0x04,
            'name'       : 'txPower',
            'description': 'Get the radio output power in dBm, excluding any antenna gain.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['txPower',             INTS,     1,   True],
                ],
            },
        },
        {
            'id'         : 0x06,
            'name'       : 'joinDutyCycle',
            'description': 'This command allows user to retrieve current value of joinDutyCycle parameter.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['joinDutyCycle',       INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 0x0B,
            'name'       : 'eventMask',
            'description': 'getParameter<eventMask> allows the microprocessor to read the currently subscribed-to event types.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['eventMask',           INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 0x0C,
            'name'       : 'moteInfo',
            'description': 'The getParameter<moteInfo> command returns static information about the mote\'s hardware and network stack software.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['apiVersion',          INT,      1,   None],
                    ['serialNumber',        HEXDATA,  8,   None],
                    ['hwModel',             INT,      1,   None],
                    ['hwRev',               INT,      1,   None],
                    ['swVerMajor',          INT,      1,   None],
                    ['swVerMinor',          INT,      1,   None],
                    ['swVerPatch',          INT,      1,   None],
                    ['swVerBuild',          INT,      2,   None],
                    ['bootSwVer',           INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 0x0D,
            'name'       : 'netInfo',
            'description': 'The getParameter<networkInfo> command may be used to retrieve the mote\'s network-related parameters.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['macAddress',          HEXDATA,  8,   None],
                    ['moteId',              INT,      2,   None],
                    ['networkId',           INT,      2,   None],
                    ['slotSize',            INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 0x0E,
            'name'       : 'moteStatus',
            'description': 'The getParameter<moteStatus> command is used to retrieve current mote state and other dynamic information.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['state',               INT,      1,   'moteState'],
                    ['reserved_0',          INT,      1,   None],
                    ['reserved_1',          INT,      2,   None],
                    ['numParents',          INT,      1,   None],
                    ['moteAlarms',          INT,      4,   None],
                    ['reserved_2',          INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 0x0F,
            'name'       : 'time',
            'description': 'The getParameter<time> command may be used to request the current time on the mote. The mote reports time at the moment it is processing the command, so the information includes variable delay. For more precise time information consider using TIMEn pin (see timeIndication).',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['upTime',              INT,      4,   None],
                    ['utcSecs',             INT,      8,   None],
                    ['utcUsecs',            INT,      4,   None],
                    ['asn',                 HEXDATA,  5,   None],
                    ['asnOffset',           INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 0x10,
            'name'       : 'charge',
            'description': 'The getParameter<charge> command retrieves the charge consumption of the mote since the last reset.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['qTotal',              INT,      4,   None],
                    ['upTime',              INT,      4,   None],
                    ['tempInt',             INTS,     1,   None],
                    ['tempFrac',            INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 0x11,
            'name'       : 'testRadioRxStats',
            'description': 'The getParameter<testRadioRxStats> command retrieves statistics for the latest radio test performed using the testRadioRx command. The statistics show the number of good and bad packets (CRC failures) received during the test',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['rxOk',                INT,      2,   None],
                    ['rxFailed',            INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 0x15,
            'name'       : 'otapLockout',
            'description': 'This command reads the current state of OTAP lockout, i.e. whether over-the-air upgrades of software are permitted on this mote.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['mode',                BOOL,     1,   None],
                ],
            },
        },
        {
            'id'         : 0x17,
            'name'       : 'moteId',
            'description': 'This command retrieves the short address of the mote. If the mote is not in the network, short address of 0 is returned.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['moteId',              INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 0x18,
            'name'       : 'ipv6Address',
            'description': 'This command allows the microprocessor to read IPV6 address assigned to the mote. Before the mote has an assigned address it will return all 0s.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['ipv6Address',         HEXDATA,  16,  None],
                ],
            },
        },
        {
            'id'         : 0x1D,
            'name'       : 'routingMode',
            'description': 'This command allows the microprocessor to retrieve the current routing mode of the mote.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['routingMode',         BOOL,     1,   None],
                ],
            },
        },
        {
            'id'         : 0x1E,
            'name'       : 'appInfo',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['vendorId',            INT,      2,   None],
                    ['appId',               INT,      2,   None],
                    ['appMajorSwRev',       INT,      1,   None],
                    ['appMinorSwRev',       INT,      1,   None],
                    ['appPatchNum',         INT,      1,   None],
                    ['appBuildNum',         INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 0x1F,
            'name'       : 'pwrSrcInfo',
            'description': 'This command allows the microprocessor to read mote\'s power source settings.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['MaxStCurrent',        INT,      2,   None],
                    ['MinLifetime',         INT,      1,   None],
                    ['currentLimit_0',      INT,      2,   None],
                    ['dischargePeriod_0',   INT,      2,   None],
                    ['rechargePeriod_0',    INT,      2,   None],
                    ['currrentLimit_1',     INT,      2,   None],
                    ['dischargePeriod_1',   INT,      2,   None],
                    ['rechargePeriod_1',    INT,      2,   None],
                    ['currentLimit_2',      INT,      2,   None],
                    ['dischargePeriod_2',   INT,      2,   None],
                    ['rechargePeriod_2',    INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 0x20,
            'name'       : 'powerCostInfo',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['maxTxCost',           INT,      1,   None],
                    ['maxRxCost',           INT,      1,   None],
                    ['minTxCost',           INT,      1,   None],
                    ['minRxCost',           INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 0x21,
            'name'       : 'mobilityType',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['mobilityType',        INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x22,
            'name'       : 'advKey',
            'description': 'Get the key used for advertisement packets.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['advKey',              HEXDATA,  16,  None],
                ],
            },
        },
        {
            'id'         : 0x23,
            'name'       : 'sizeInfo',
            'description': 'Get information about the mote\'s storage capacity.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['maxFrames',           INT,      1,   None],
                    ['maxLinks',            INT,      2,   None],
                    ['maxNeighbors',        INT,      1,   None],
                    ['maxRoutes',           INT,      1,   None],
                    ['maxGraphs',           INT,      1,   None],
                    ['maxMacQueue',         INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 0x24,
            'name'       : 'autoJoin',
            'description': 'This command allows the microprocessor to retrieve the current autoJoin setting.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['autoJoin',            BOOL,     1,   None],
                ],
            },
        },
    ]
    
    # We redefine this attribute inherited from ApiDefinition. See
    # ApiDefinition for a full description of the structure of this field.
    commands = [
        {
            'id'         : 0x01,
            'name'       : 'setParameter',
            'description': 'Set Parameter',
            'request'    : [
                [SUBID1,                    INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    [SUBID1,                INT,      1,   None],
                ]
            },
            'subCommands': subCommandsSet,
        },
        {
            'id'         : 0x02,
            'name'       : 'getParameter',
            'description': 'Get Parameter',
            'request'    : [
                [SUBID1,                    INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    [SUBID1,                INT,      1,   None],
                ]
            },
            'subCommands': subCommandsGet,
        },
        {
            'id'         : 0x06,
            'name'       : 'join',
            'description': 'The join command requests that mote start searching for the network and attempt to join.The mote must be in the IDLE state for this command to be valid. Note that the join time will be affected by the maximum current setting.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x07,
            'name'       : 'disconnect',
            'description': 'The disconnect command requests that the mote initiate disconnection from the network. After disconnection completes, the mote will generate a disconnected event, and proceed to reset. If the mote is not in the network, the disconnected event will be generated immediately. This command may be issued at any time.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x08,
            'name'       : 'reset',
            'description': 'The reset command initiates a soft-reset of the device. The device will initiate the reset sequence shortly after sending out the response to this command. Resetting a mote directly can adversely impact its descendants; to disconnect gracefully from the network, use the disconnect command.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x09,
            'name'       : 'lowPowerSleep',
            'description': 'The lowPowerSleep command shuts down all peripherals and places the mote into deep sleep mode. The command executes after the mote sends its response. The mote enters deep sleep within two seconds after the command executes. The command may be issued at any time and will cause the mote to interrupt all in-progress network operation. To achieve a graceful disconnect, use the disconnect command before using the lowPowerSleep command. A hardware reset is required to bring a mote out of deep sleep mode. ',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x0C,
            'name'       : 'testRadioRx',
            'description': 'The testRadioRx command clears all previously collected statistics and initiates a test of radio reception for the specified channel and duration. During the test, the mote keeps statistics about the number of packets received (with and without error). The test results may be retrieved using the getParameter<testRadioRxStats> command. The testRadioRx command may only be issued in IDLE mode. The mote must be reset (either hardware or software reset) after radio tests are complete and prior to joining.\n\nChannel numbering is 0-14, corresponding to IEEE 2.4 GHz channels 11-25.',
            'request'    : [
                ['channelMask',             HEXDATA,  2,   None],
                ['time',                    INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,  1,   True]
                ],
            },
        },
        {
            'id'         : 0x10,
            'name'       : 'clearNV',
            'description': 'The clearNV command resets the mote\'s non-volatile memory (NV) to its factory-default state. See User Guide for detailed information about the default values. Since many parameters are read by the mote only at power-up, this command should be followed up by mote reset.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x11,
            'name'       : 'requestService',
            'description': 'The requestService command may be used to request a new or changed service level to a destination device in the mesh. This command may only be used to update service to a device with an existing connection (session). A service is uniquely identified by <destination,type> pair.\n\nWhenever a change in bandwidth assignment occurs, the application receives a serviceChanged event that it can use as a trigger to read the new service allocation.',
            'request'    : [
                ['destAddr',                INT,      2,   None],
                ['serviceType',             INT,      1,   True],
                ['value',                   INT,      4,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x12,
            'name'       : 'getServiceInfo',
            'description': 'The getServiceInfo command returns information about the service currently allocated to the mote.',
            'request'    : [
                ['destAddr',                INT,      2,   None],
                ['type',                    INT,      1,   'serviceType'],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['destAddr',            HEXDATA,  2,   None],
                    ['type',                INT,      1,   'serviceType'],
                    ['state',               INT,      1,   'serviceState'],
                    ['value',               INT,      4,   None],
                ],
            },
        },
        {
            'id'         : 0x15,
            'name'       : 'openSocket',
            'description': 'The openSocket command creates an endpoint for IP communication and returns an id for the socket.',
            'request'    : [
                ['protocol',                INT,      1,   'protocolType'],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['socketId',            INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 0x16,
            'name'       : 'closeSocket',
            'description': 'Close the previously open socket.',
            'request'    : [
                ['socketId',                INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x17,
            'name'       : 'bindSocket',
            'description': 'Bind a previously opened socket to a port. When a socket is created, it is only given a protocol family, but not assigned a port. This association must be performed before the socket can accept connections from other hosts.',
            'request'    : [
                ['socketId',                INT,      1,   None],
                ['port',                    INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x18,
            'name'       : 'sendTo',
            'description': 'Send a packet into the network. If the command returns RC_OK, the mote has accepted the packet and has queued it up for transmission. A txDone notification will be issued when the packet has been sent, if and only if the packet ID passed in this command is different from 0xffff. You can set the packet ID to any value. The notification will contain the packet ID of the packet just sent, allowing association of the notification with a particular packet.  The destination port should be in the range 0xF0B8-F0BF (61624-61631) to maximize payload.',
            'request'    : [
                ['socketId',                INT,      1,   None],
                ['destIP',                  HEXDATA,  16,  None],
                ['destPort',                INT,      2,   None],
                ['serviceType',             INT,      1,   True],
                ['priority',                INT,      1,   'packetPriority'],
                ['packetId',                INT,      2,   None],
                ['payload',                 HEXDATA,  None,None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x24,
            'name'       : 'search',
            'description': 'The search command requests that mote start listening for advertisements and report those heard from any network without attempting to join.The mote must be in the IDLE state for this command to be valid.  The search state can be exiting by issuing the join command or the reset command.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x28,
            'name'       : 'testRadioTxExt',
            'description': 'The testRadioTxExt command allows the microprocessor to initiate a radio transmission test. This command may only be issued prior to the mote joining the network. Three types of transmission tests are supported:\n\n - Packet transmission\n - Continuous modulation\n - Continuous wave (unmodulated signal)\n\nIn a packet transmission test, the mote generates a repeatCnt number of packet sequences. Each sequence consists of up to 10 packets with configurable size and delays. Each packet starts with a phy preamble (5 bytes), followed by phy length field (1 byte), followed by data payload of up to 125 bytes, and finally a 2-byte 802.15.4 CRC at the end. Bytes 0 and 1 contain the packet number (in big-endian format) that increments with every packet transmitted. Bytes 2..N contain a counter (from 0..N-2) that increments with every byte inside payload. Transmissions occur on the set of channels defined by chanMask, selected in pseudo-random order.\n\nIn a continuous modulation test, the mote generates continuous pseudo-random modulated signal, centered at the specified channel. The test is stopped by resetting the mote.\n\nIn a continuous wave test, the mote generates an unmodulated tone, centered at the specified channel. The test tone is stopped by resetting the mote.\n\nThe testRadioTxExt command may only be issued when the mote is in IDLE mode, prior to its joining the network. The mote must be reset (either hardware or software reset) after radio tests are complete and prior to joining.\n\nNote: Channel numbering is 0-14, corresponding to IEEE 2.4 GHz channels 11-25.',
            'request'    : [
                ['testType',                INT,      1,   'radioTestTypes'],
                ['chanMask',                HEXDATA,  2,   None],
                ['repeatCnt',               INT,      2,   None],
                ['txPower',                 INTS,     1,   None],
                ['seqSize',                 INT,      1,   None],
                ['pkLen1',                  INT,      1,   None],
                ['delay1',                  INT,      2,   None],
                ['pkLen2',                  INT,      1,   None],
                ['delay2',                  INT,      2,   None],
                ['pkLen3',                  INT,      1,   None],
                ['delay3',                  INT,      2,   None],
                ['pkLen4',                  INT,      1,   None],
                ['delay4',                  INT,      2,   None],
                ['pkLen5',                  INT,      1,   None],
                ['delay5',                  INT,      2,   None],
                ['pkLen6',                  INT,      1,   None],
                ['delay6',                  INT,      2,   None],
                ['pkLen7',                  INT,      1,   None],
                ['delay7',                  INT,      2,   None],
                ['pkLen8',                  INT,      1,   None],
                ['delay8',                  INT,      2,   None],
                ['pkLen9',                  INT,      1,   None],
                ['delay9',                  INT,      2,   None],
                ['pkLen10',                 INT,      1,   None],
                ['delay10',                 INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
    ]
    
    # We redefine this attribute inherited from ApiDefinition. See
    # ApiDefinition for a full description of the structure of this field.
    notifications = [
        {
            'id'         : 0x0D,
            'name'       : 'timeIndication',
            'description': 'The timeIndication notification applies to mote products that support a time interrupt into the mote.  The time packet includes the network time and the current UTC time relative to the manager.\n\nFor LTC5800-IPM based products, driving the TIMEn pin low (assert) wakes the processor. The pin must asserted for a minimum of tstrobe micro-s.  De-asserting the pin latches the time, and a timeIndication will be generated within tresponse ms. Refer to the mote datasheet for product-specific details. The LTC5800-IPM datasheet also provides information about TIME pin usage.\n\nThe processor will remain awake and drawing current while the TIMEn pin is asserted. To avoid drawing excess current, take care to minimize the duration of the TIMEn pin being asserted past tstrobe minimums.',
            'response'   : {
                'FIELDS':  [
                    ['uptime',              INT,      4,   None],
                    ['utcSecs',             INT,      8,   None],
                    ['utcUsecs',            INT,      4,   None],
                    ['asn',                 HEXDATA,  5,   None],
                    ['asnOffset',           INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 0x0F,
            'name'       : 'eventsNotif',
            'description': 'Informs the application that some new events occurred since the last event notification. If the mote cannot send a packet (due to full queue or lack of buffers), it will retry once a minute until it succeeds.',
            'response'   : {
                'FIELDS':  [
                    ['events',              INT,      4,   'moteEvents'],
                    ['state',               INT,      1,   'moteState'],
                    ['alarmsList',          INT,      4,   None],
                ],
            },
        },
        {
            'id'         : 0x19,
            'name'       : 'receiveNotif',
            'description': 'Informs the application that a packet was received.',
            'response'   : {
                'FIELDS':  [
                    ['socketId',            INT,      1,   None],
                    ['srcAddr',             HEXDATA,  16,  None],
                    ['srcPort',             INT,      2,   None],
                    ['payload',             HEXDATA,  None,None],
                ],
            },
        },
        {
            'id'         : 0x24,
            'name'       : 'macRxNotif',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['payload',             HEXDATA,  None,None],
                ],
            },
        },
        {
            'id'         : 0x25,
            'name'       : 'txDoneNotif',
            'description': 'The txDone notification informs the application that the mote has finished sending a packet. This notification will only be generated if the user has provided a valid (0x0000-0xFFFE) packet id when calling the sendTo command.',
            'response'   : {
                'FIELDS':  [
                    ['packetId',            INT,      2,   None],
                    ['status',              INT,      1,   'packetTransmitStatus'],
                ],
            },
        },
        {
            'id'         : 0x26,
            'name'       : 'advReceived',
            'description': 'The \'advReceived\' notification is generated by the mote when it is in promiscuous listen state (see the Mote States table) and it receives an advertisement.',
            'response'   : {
                'FIELDS':  [
                    ['netId',             INT,      2,   None],
                    ['moteId',            INT,      2,   None],
                    ['rssi',              INTS,     1,   None],
                    ['joinPri',           INT,      1,   None],
                ],
            },
        },
    ]
