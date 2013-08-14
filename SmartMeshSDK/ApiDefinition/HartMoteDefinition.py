#!/usr/bin/python

import ApiDefinition
import ByteArraySerializer

class HartMoteDefinition(ApiDefinition.ApiDefinition):
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
    
    FLAG_SETNV_RAM      = 7
    FLAG_TRAN_ACKED     = 6
    FLAG_TRAN_DIR_RESP  = 7
    
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
    
    def serializeSend(self,commandArray,fieldsToFill):
        '''
        \brief Serializer specific for the send command
        
        This serializer:
        - toggles the 'tranType' and 'tranDir' flags
        '''
        
        # serialize the command using the default serializer
        cmdId,byteArray = self.serializer.serialize(commandArray,fieldsToFill)
        
        # byteArray now contains the following bytes:
        # [0]  is the paramId
        # [1]  is the tranType value
        # [2]  is the tranDir value
        # [3:] are the parameters
        
        # remove the tranType and tranDir from the packet
        tranType = byteArray.pop(0)
        tranDir  = byteArray.pop(0) # still index 0 since popped before
        
        # prepend the flagList, the list of flags to be set in the header
        flaglist = []
        if tranType:
            flaglist.append(self.FLAG_TRAN_ACKED)
        if tranDir:
            flaglist.append(self.FLAG_TRAN_DIR_RESP)
        
        # add the flagList as the first element of the byteArray
        byteArray = [flaglist]+byteArray
        
        return cmdId,byteArray
    
    def serializeSetNv(self,commandArray,fieldsToFill):
        '''
        \brief Serializer specific for the setNvParameter commands
        
        This serializer:
        - toggles the 'memory' flag
        - adds the 4B 'reserved' field to the serialized bytes
        '''
        
        # serialize the command using the default serializer
        cmdId,byteArray = self.serializer.serialize(commandArray,fieldsToFill)
        
        # byteArray now contains the following bytes:
        # [0]  is the paramId
        # [1]  is the targetMemory value
        # [2:] are the parameters
        
        # remove the targetFlag from the packet
        targetMemory = byteArray.pop(1)
        
        # prepend the flagList, the list of flags to be set in the header
        if targetMemory:
            flaglist = [self.FLAG_SETNV_RAM,]
        else:
            flaglist = []
        
        # add the 4B reserved field
        byteArray = [0,0,0,0]+byteArray
        
        # add the flagList as the first element of the byteArray
        byteArray = [flaglist]+byteArray
        
        return cmdId,byteArray
    
    def serializeGetNv(self,commandArray,fieldsToFill):
        '''
        \brief Serializer specific for the getNvParameter commands
        
        This serializer adds the 4B 'reserved' field to the serialized bytes
        '''
        
        # serialize the command using the default serializer
        cmdId,byteArray = self.serializer.serialize(commandArray,fieldsToFill)
        
        # add the 4B reserved field
        byteArray = [0,0,0,0]+byteArray
        
        return cmdId,byteArray
    
    # We redefine this attribute inherited from ApiDefinition. See
    # ApiDefinition for a full description of the structure of this field.
    fieldOptions = {
        RC: [
            [0,    'RC_OK',                 ''],
            [1,    'RC_RESERVED1',          ''],
            [2,    'RC_RESERVED2',          ''],
            [3,    'RC_BUSY',               ''],
            [4,    'RC_INVALID_LEN',        ''],
            [5,    'RC_INV_STATE',          ''],
            [6,    'RC_UNSUPPORTED',        ''],
            [7,    'RC_UNKNOWN_PARAM',      ''],
            [8,    'RC_UNKNOWN_CMD',        ''],
            [9,    'RC_WRITE_FAIL',         ''],
            [10,   'RC_READ_FAIL',          ''],
            [11,   'RC_LOW_VOLTAGE',        ''],
            [12,   'RC_NO_RESOURCES',       ''],
            [13,   'RC_INCOMPLETE_JOIN_INFO', ''],
            [14,   'RC_NOT_FOUND',          ''],
            [15,   'RC_INVALID_VALUE',      ''],
        ],
        'power_status_t' : [
            [0,    'nominal',               ''],
            [1,    'low',                   ''],
            [2,    'criticallyLow',         ''],
            [3,    'rechargingLow',         ''],
            [4,    'rechargingHigh',        ''],
        ],
        'app_domain_t' : [
            [0,    'publish',               ''],
            [1,    'event',                 ''],
            [2,    'maintenance',           ''],
            [3,    'blockTransfer',         ''],
        ],
        'service_state_t' : [
            [0,    'inactive',              ''],
            [1,    'active',                ''],
            [2,    'requested',             ''],
        ],
        'nstate_t' : [
            [0,    'init',                  ''],
            [1,    'idle',                  ''],
            [2,    'searching',             ''],
            [3,    'negotiating',           ''],
            [4,    'connected',             ''],
            [5,    'operational',           ''],
            [6,    'disconnected',          ''],
            [7,    'radioTest',             ''],
            [8,    'promiscuousListen',     ''],
        ],
        'pwr_src_t' : [
            [0,    'line',                  ''],
            [1,    'battery',               ''],
            [2,    'scavenging',            ''],
        ],
        'writeProtectMode_t' : [
            [0,    'writeAllowed',          ''],
            [1,    'writeNotAllowed',       ''],
        ],
        'otapLockout_t' : [
            [0,    'allowed',               ''],
            [1,    'disabled',              ''],
        ],
        'setNv_memory_t' : [
            [False,'NV_only',               ''],
            [True, 'NV_and_RAM',            ''],
        ],
        'tranType_t' : [
            [False,'bestEffort',            ''],
            [True, 'Acked',                 ''],
        ],
        'tranDir_t' : [
            [False,'request',               ''],
            [True, 'response',              ''],
        ],
        'radiotest_type_t' : [
            [0,    'packet',                ''],
            [1,    'CM',                    ''],
            [2,    'CW',                    ''],
        ],
        'txpower_t' : [
            [-2,   '-2dBm',                 ''],
            [8,    '+8dBm',                 ''],
        ],
    }
    
    subCommandsSet = [
        {
            'id'         : 0x4,
            'name'       : 'txPower',
            'description': '',
            'request'    : [
                ['txPower',                 INTS,     1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x6,
            'name'       : 'joinDutyCycle',
            'description': '',
            'request'    : [
                ['dutyCycle',               INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x7,
            'name'       : 'batteryLife',
            'description': '',
            'request'    : [
                ['batteryLife',             INT,      2,   None],
                ['powerStatus',             INT,      1,   'power_status_t'],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0x8,
            'name'       : 'service',
            'description': '',
            'request'    : [
                ['serviceId',               INT,      1,   None],
                ['serviceReqFlags',         INT,      1,   None],
                ['appDomain',               INT,      1,   'app_domain_t'],
                ['destAddr',                HEXDATA,  2,   None],
                ['time',                    INT,      4,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    ['numServices',         INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 0x9,
            'name'       : 'hartDeviceStatus',
            'description': '',
            'request'    : [
                ['hartDevStatus',           INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 0xa,
            'name'       : 'hartDeviceInfo',
            'description': '',
            'request'    : [
                ['hartCmd0',                HEXDATA,  22,  None],
                ['hartCmd20',               HEXDATA,  32,  None],
            ],
            'response'   : {
                'FIELDS':  [
                  
                ],
            },
        },
        {
            'id'         : 0xb,
            'name'       : 'eventMask',
            'description': '',
            'request'    : [
                ['eventMask',               INT,      4,   None],
            ],
            'response'   : {
                'FIELDS':  [
                  
                ],
            },
        },
        {
            'id'         : 0x12,
            'name'       : 'writeProtect',
            'description': '',
            'request'    : [
                ['writeProtect',            INT,      1,   'writeProtectMode_t'],
            ],
            'response'   : {
                'FIELDS':  [
                  
                ],
            },
        },
    ]
    
    subCommandsGet = [
        {
            'id'         : 0xc,
            'name'       : 'moteInfo',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['apiVersion',          INT,      1,   None],
                    ['serialNumber',        HEXDATA,  8,   None],
                    ['hwModel',             INT,      1,   None],
                    ['hwRev',               INT,      1,   None],
                    ['swMajor',             INT,      1,   None],
                    ['swMinor',             INT,      1,   None],
                    ['swPatch',             INT,      1,   None],
                    ['swBuild',             INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 0xd,
            'name'       : 'networkInfo',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['macAddress',          HEXDATA,  8,   None],
                    ['moteId',              INT,      2,   None],
                    ['netId',               INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 0xe,
            'name'       : 'moteStatus',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['state',               INT,      1,   'nstate_t'],
                    ['moteStateReason',     INT,      1,   None],
                    ['changeCounter',       INT,      2,   None],
                    ['numParents',          INT,      1,   None],
                    ['alarms',              INT,      4,   None],
                    ['statusFlags',         INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 0xf,
            'name'       : 'time',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['utcTimeSec',          INT,      4,   None],
                    ['utcTimeMsec',         INT,      4,   None],
                    ['asn',                 HEXDATA,  5,   None],
                    ['asnOffset',           INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 0x10,
            'name'       : 'charge',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['charge',              INT,      4,   None],
                    ['uptime',              INT,      4,   None],
                    ['temperature',         INTS,     1,   None],
                    ['fractionalTemp',      INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 0x11,
            'name'       : 'radioTestRxStats',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['rxOk',                INT,      2,   None],
                    ['rxFail',              INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 0x8,
            'name'       : 'service',
            'description': '',
            'request'    : [
                ['serviceId'    ,           INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    ['serviceId',           INT,      1,   None],
                    ['serviceState',        INT,      1,   'service_state_t'],
                    ['serviceFlags',        INT,      1,   None],
                    ['appDomain',           INT,      1,   'app_domain_t'],
                    ['destAddr',            HEXDATA,  2,   None],
                    ['time',                INT,      4,   None],
                ],
            },
        },
    ]

    subCommandsSetNv = [
        {
            'id'         : 0x1,
            'name'       : 'macAddress',
            'description': '',
            'request'    : [
                ['targetMemory',            BOOL,     1,   'setNv_memory_t'],
                ['macAddr',                 HEXDATA,  8,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x3,
            'name'       : 'networkId',
            'description': '',
            'request'    : [
                ['targetMemory',            BOOL,     1,   'setNv_memory_t'],
                ['networkId',               INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x4,
            'name'       : 'txPower',
            'description': '',
            'request'    : [
                ['targetMemory',            BOOL,     1,   'setNv_memory_t'],
                ['txPower',                 INTS,     1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x2,
            'name'       : 'joinKey',
            'description': '',
            'request'    : [
                ['targetMemory',            BOOL,     1,   'setNv_memory_t'],
                ['joinKey',                 HEXDATA,  16,  None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x5,
            'name'       : 'powerInfo',
            'description': '',
            'request'    : [
                ['targetMemory',            BOOL,     1,   'setNv_memory_t'],
                ['powerSource',             INT,      1,   'pwr_src_t'],
                ['dischargeCur',            INT,      2,   None],
                ['dischargeTime',           INT,      4,   None],
                ['recoverTime',             INT,      4,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x13,
            'name'       : 'ttl',
            'description': '',
            'request'    : [
                ['targetMemory',            BOOL,     1,   'setNv_memory_t'],
                ['timeToLive',              INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x14,
            'name'       : 'HARTantennaGain',
            'description': '',
            'request'    : [
                ['targetMemory',            BOOL,     1,   'setNv_memory_t'],
                ['antennaGain',             INTS,     1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x15,
            'name'       : 'OTAPlockout',
            'description': '',
            'request'    : [
                ['targetMemory',            BOOL,     1,   'setNv_memory_t'],
                ['otapLockout',             INT,      1,   'otapLockout_t'],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'serializer' : 'serializeSetNv',
        },
    ]

    subCommandsGetNv = [
        {
            'id'         : 0x1,
            'name'       : 'macAddress',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['macAddr',             HEXDATA,  8,   None],
                ],
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x3,
            'name'       : 'networkId',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['networkId',           INT,      2,   None],
                ],
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x4,
            'name'       : 'txPower',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['txpower',             INTS,     1,   None],
                ],
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x5,
            'name'       : 'powerInfo',
            'description': 'The getNVParameter<powerInfo> command returns power supply information stored in mote\'s persistent storage.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['powerSource',         INT,      1,   'pwr_src_t'],
                    ['dischargeCur',        INT,      2,   None],
                    ['dischargeTime',       INT,      4,   None],
                    ['recoverTime',         INT,      4,   None],
                ],
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x13,
            'name'       : 'ttl',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                     ['timeToLive',         INT,      1,   None],
                ],
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x14,
            'name'       : 'HARTantennaGain',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                     ['antennaGain',        INTS,     1,   None],
                ],
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x15,
            'name'       : 'OTAPlockout',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['otapLockout',         INT,      1,   'otapLockout_t'],
                ],
            },
            'serializer' : 'serializeGetNv',
        },
    ]
        
    # We redefine this attribute inherited from ApiDefinition. See
    # ApiDefinition for a full description of the structure of this field.
    commands = [
        {
            'id'         : 0x01,
            'name'       : 'setParameter',
            'description': 'Set the value of a parameter.',
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
            'description': 'Get the value of a parameter.',
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
            'id'         : 0x03,
            'name'       : 'setNvParameter',
            'description': 'Set the value of a NV-parameter.',
            'request'    : [
                # the 4B reserved field is added automatically
                [SUBID1,                    INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    [SUBID1,                INT,      1,   None],
                ]
            },
            'subCommands': subCommandsSetNv,
        },
        {
            'id'         : 0x04,
            'name'       : 'getNvParameter',
            'description': 'Get the value of a NV-parameter.',
            'request'    : [
                # the 4B reserved field is added automatically
                [SUBID1,                    INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    [SUBID1,                INT,      1,   None],
                ]
            },
            'subCommands': subCommandsGetNv,
        },
        {
            'id'         : 0x5,
            'name'       : 'send',
            'description': '',
            'request'    : [
                ['tranType',                BOOL,     1,   'tranType_t'],
                ['tranDir',                 BOOL,     1,   'tranDir_t'],
                ['destAddr',                HEXDATA,  2,   None],
                ['serviceId',               INT,      1,   None],
                ['appDomain',               INT,      1,   'app_domain_t'],
                ['priority',                INT,      1,   None],
                ['reserved',                HEXDATA,  2,   None],
                ['seqNum',                  INT,      1,   None],
                ['len',                     INT,      1,   None],
                ['payload',                 HEXDATA,  None,None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'serializer' : 'serializeSend',
        },
        {
            'id'         : 0x6,
            'name'       : 'join',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x7,
            'name'       : 'disconnect',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x8,
            'name'       : 'reset',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x9,
            'name'       : 'lowPowerSleep',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0xa,
            'name'       : 'hartPayload',
            'description': '',
            'request'    : [
                ['payloadLen',              INT,      1,   None],
                ['payload',                 HEXDATA,  None,None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['payloadLen',          INT,      1,   None],
                    ['payload',             HEXDATA,  None,None],
                ],
            },
        },
        {
            'id'         : 0xb,
            'name'       : 'testRadioTx',
            'description': '',
            'request'    : [
                ['channel',                 INT,      1,   None],
                ['numPackets',              INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0xc,
            'name'       : 'testRadioRx',
            'description': '',
            'request'    : [
                ['channel',                 INT,      1,   None],
                ['time',                    INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x10,
            'name'       : 'clearNV',
            'description': '',
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
            'name'       : 'search',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 0x13,
            'name'       : 'testRadioTxExt',
            'description': '',
            'request'    : [
                ['type',                    INT,      1,   'radiotest_type_t'],
                ['chanMask',                INT,      2,   None],
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
        {
            'id'         : 0x14,
            'name'       : 'testRadioRxExt',
            'description': '',
            'request'    : [
                ['channelMask',             INT,      2,   None],
                ['time',                    INT,      2,   None],
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
            'id'         : 0xd,
            'name'       : 'timeIndication',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['utcSec',              INT,      4,   None],
                    ['utcMicroSec',         INT,      4,   None],
                    ['asn',                 HEXDATA,  5,   None],
                    ['asnOffset',           INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 0xe,
            'name'       : 'serviceIndication',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['eventCode',           INT,      1,   None],
                    ['netMgrCode',          INT,      1,   None],
                    ['serviceId',           INT,      1,   None],
                    ['serviceState',        INT,      1,   'service_state_t'],
                    ['serviceFlags',        INT,      1,   None],
                    ['appDomain',           INT,      1,   'app_domain_t'],
                    ['destAddr',            HEXDATA,  2,   None],
                    ['time',                INT,      4,   None],
                ],
            },
        },
        {
            'id'         : 0xf,
            'name'       : 'events',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['events',              INT,      4,   None],
                    ['state',               INT,      1,   'nstate_t'],
                    ['moteAlarms',          INT,      4,   None],
                ],
            },
        },
        {
            'id'         : 0x81,
            'name'       : 'dataReceived',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['srcAddr',             HEXDATA,  2,   None],
                    ['seqNum',              INT,      1,   None],
                    ['pktLenth',            INT,      1,   None],
                    ['data',                HEXDATA,  None,None],
                ],
            },
        },
        {
            'id'         : 0x12,
            'name'       : 'advReceived',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['netId',               INT,      2,   None],
                    ['moteid',              HEXDATA,  2,   None],
                    ['rssi',                INT,      1,   None],
                    ['joinPri',             INT,      1,   None],
                ],
            },
        },
    ]
