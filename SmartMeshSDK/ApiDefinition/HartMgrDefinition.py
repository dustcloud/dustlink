'''API Definition for HART Manager XML API'''

import ApiDefinition

import xmlutils
import re

# Add a log handler for the HART Manager

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

log = logging.getLogger('HartManager')
log.setLevel(logging.INFO)
log.addHandler(NullHandler())

##
# \ingroup ApiDefinition
#
class HartMgrDefinition(ApiDefinition.ApiDefinition):
    '''
    \brief API definition for the HART manager.
   
    \note This class inherits from ApiDefinition. It redefines the attributes of
          its parent class, but inherits the methods.
    '''

    FIELDS = 'unnamed'
    
    STRING    = ApiDefinition.FieldFormats.STRING
    BOOL      = ApiDefinition.FieldFormats.BOOL
    INT       = ApiDefinition.FieldFormats.INT
    INTS      = ApiDefinition.FieldFormats.INTS
    FLOAT     = 'float'
    HEXDATA   = ApiDefinition.FieldFormats.HEXDATA
    RC        = ApiDefinition.ApiDefinition.RC
    SUBID1    = ApiDefinition.ApiDefinition.SUBID1

    # Enumerations
    fieldOptions = {
        RC : [
            [0x0,                      'OK',                    ''],
            # ...
        ],
        'bool' : [
            ['true',                   'true',                  ''],
            ['false',                  'false',                 ''],
        ],
        'appDomain' : [
            ['maintenance',            'maintenance',           ''],
        ],
        'packetPriority' : [
            ['low',                    'low',                   ''],
            ['high',                   'high',                  ''],
        ],
        'pipeDirection' : [
            ['UniUp',                  'upstream',              ''],
            ['UniDown',                'downstream',            ''],
            ['Bi',                     'bidirectional',         ''],
        ],
        'moteState' : [
            ['Idle',                   'idle',                  ''],
            ['Lost',                   'lost',                  ''],
            ['Joining',                'joining',               ''],
            ['Operational',            'operational',           ''],
        ],
        'pathDirection' : [
            ['all',                    'all',                   ''],
            ['upstream',               'upstream',              ''],
            ['downstream',             'downstream',            ''],
            ['used',                   'used',                  ''],
            ['unused',                 'unused',                ''],
        ],
        'bandwidthProfile' : [
            ['Manual',                 'manual',                ''],
            ['P1',                     'p1',                    ''],
            ['P2',                     'p2',                    ''],
        ], 
        'securityMode' : [
            ['acceptACL',              'acceptacl',             ''],
            ['acceptCommonJoinKey',    'acceptcommonjoinkey',   '']
        ],
        'userPrivilege' : [
            ['viewer',                 'viewer',                ''],
            ['user',                   'user',                  ''],
            ['superuser',              'superuser',             ''],
        ],
        'onOff' : [
            ['on',                     'on',                    ''],
            ['off',                    'off',                   ''],
        ],
        'resetObject' : [
            ['network',                'network',               ''],
            ['system',                 'system',                ''],
            ['stat',                   'stat',                  ''],
            ['eventLog',               'eventLog',              ''],
        ],
        'resetMote' : [
            ['mote',                   'mote',                  ''],
        ],
        'statPeriod': [
            ['current',                'current',               ''],
            ['lifetime',               'lifetime',              ''],
            ['short',                  'short',                 ''],
            ['long',                   'long',                  ''],
        ]
        
        # TODO: SysConnectChannel: control, notif
    }


    # ----------------------------------------------------------------------
    # Notifications
    
    eventNotifications = [
        {
            'id'         : 'sysConnect',
            'name'       : 'UserConnect',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['channel',             STRING,   16,  None], # TODO: enum
                    ['ipAddr',              STRING,   16,  None],
                    ['userName',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'sysDisconnect',
            'name'       : 'UserDisconnect',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['channel',             STRING,   16,  None], # TODO: enum
                    ['ipAddr',              STRING,   16,  None],
                    ['userName',            STRING,   32,  None],
                ],
            },
        },
        # sysManualMoteDelete
        # sysManualMoteDecommission
        # sysManualNetReset
        # sysManualDccReset
        # sysManualStatReset
        # sysConfigChange
        {
            'id'         : 'sysManualMoteReset',
            'name'       : 'ManualMoteReset',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['userName',            STRING,   32,  None],
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'sysBootUp',
            'name'       : 'BootUp',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    # None
                ],
            },
        },
        {
            'id'         : 'netReset',
            'name'       : 'NetworkReset',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    # None
                ],
            },
        },
        {
            'id'         : 'sysCmdFinish',
            'name'       : 'CommandFinished',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['callbackId',          INT,      4,   None],
                    ['result',              INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 'netPacketSent',
            'name'       : 'PacketSent',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
        {
            'id'         : 'netMoteJoin',
            'name'       : 'MoteJoin',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                    ['reason',              STRING,   64,  None], # TODO: length
                    ['userData',            STRING,   64,  None], # TODO: length
                ],
            },
        },
        {
            'id'         : 'netMoteLive',
            'name'       : 'MoteLive',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                    ['reason',              STRING,   64,  None], # TODO: length
                ],
            },
        },
        {
            'id'         : 'netMoteUnknown',
            'name'       : 'MoteUnknown',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                    ['reason',              STRING,   64,  None], # TODO: length
                ],
            },
        },
        {
            'id'         : 'netMoteDisconnect',
            'name'       : 'MoteDisconnect',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                    ['reason',              STRING,   64,  None], # TODO: length
                ],
            },
        },
        {
            'id'         : 'netMoteJoinFailure',
            'name'       : 'MoteJoinFailure',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['macAddr',             STRING,   32,  None],
                    ['reason',              STRING,   64,  None], # TODO: length
                ],
            },
        },
        {
            'id'         : 'netMoteInvalidMIC',
            'name'       : 'InvalidMIC',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['macAddr',             STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'netPathCreate',
            'name'       : 'PathCreate',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['pathId',              INT,      4,   None],
                    ['moteAMac',            STRING,   32,  None],
                    ['moteBMac',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'netPathDelete',
            'name'       : 'PathDelete',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['pathId',              INT,      4,   None],
                    ['moteAMac',            STRING,   32,  None],
                    ['moteBMac',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'netPathActivate',
            'name'       : 'PathActivate',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['pathId',              INT,      4,   None],
                    ['moteAMac',            STRING,   32,  None],
                    ['moteBMac',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'netPathDeactivate',
            'name'       : 'PathDeactivate',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['pathId',              INT,      4,   None],
                    ['moteAMac',            STRING,   32,  None],
                    ['moteBMac',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'netPipeOn',
            'name'       : 'PipeOn',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['macAddr',             STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'netPipeOff',
            'name'       : 'PipeOff',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['macAddr',             STRING,   32,  None],
                ],
            },
        },
        # netServiceDenied
        {
            'id'         : 'netPingReply',
            'name'       : 'PingReply',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['macAddr',             STRING,   32,  None],
                    ['callbackId',          INT,      4,   None],
                    ['latency',             INT,      4,   None],
                    ['temperature',         FLOAT,    8,   None],
                    ['voltage',             FLOAT,    8,   None],
                    ['hopCount',            INT,      4,   None],
                ],
            },
        },

        # TODO: redundancy events: sysRdntModeChange, sysRdntPeerStatusChange
        # TODO: alarm open and close have sub-events
    ]

    measurementNotifications = [
        {
            'id'         : 'location',
            'name'       : 'Location',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['ver',                 INT,      1,   None],
                    ['asn',                 INT,      8,   None],
                    ['src',                 STRING,   32,  None],
                    ['dest',                STRING,   32,  None],
                    ['payload',             HEXDATA,  256, None],
                ],
            },
        },
    ]
    
    notifications = [
        {
            'id'         : 'event',
            'name'       : 'event',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['timeStamp',           INT,      8,   None],
                    ['eventId',             INT,      4,   None],
                    [SUBID1,                INT,      1,   None],
                ]
            },
            'subCommands': eventNotifications,
            'deserializer': 'parse_eventNotif',
        },
        {
            'id'         : 'data',
            'name'       : 'data',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                    ['time',                INT,      8,   None],
                    ['payload',             HEXDATA,  256, None],
                    ['payloadType',         INT,      1,   None],
                    ['isReliable',          BOOL,     1,   None],
                    ['isRequest',           BOOL,     1,   None],
                    ['isBroadcast',         BOOL,     1,   None],
                    ['callbackId',          INT,      4,   None],
                    # counter field added in 4.1.0.2
                    ['counter',             INT,      4,   None],
                ]
            },
            'deserializer': 'parse_dataNotif',
        },
        {
            'id'         : 'measurement',
            'name'       : 'measurement',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    [SUBID1,                INT,      1,   None],
                ]
            },
            'subCommands': measurementNotifications,
        },
        {
            'id'         : 'cli',
            'name'       : 'cli',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['time',                INT,      8,   None],
                    ['message',             STRING,   128, None],
                ]
            },
        },
        {
            'id'         : 'log',
            'name'       : 'log',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['time',                INT,      8,   None],
                    ['severity',            STRING,   16,  None],
                    ['message',             STRING,   128, None],
                ]
            },
        },
    ]

    # Notification parsing

    def parse_dataNotif(self, notif_str, notif_fields):
        data_dict = self._parse_xmlobj(notif_str, 'data', notif_fields)
        log.debug('DATA: %s' % str(data_dict))
        # reconvert payload type as a hex value
        data_dict['payloadType'] = int(str(data_dict['payloadType']), 16)
        # set default values for any fields that aren't present
        DEFAULTS = (('isRequest', False),
                    ('isReliable', False),
                    ('isBroadcast', False),
                    ('callbackId', 0))
        for f, v in DEFAULTS:
            if not data_dict[f]:
                data_dict[f] = v
        return (['data'], data_dict)

    def parse_eventNotif(self, notif_str, notif_fields):
        obj_dict = self._parse_xmlobj(notif_str, 'event', None)
        log.debug('EVENT: %s' % str(obj_dict))
        
        event_name = ['event']
        event_dict = {}
        for event_attr, val in obj_dict.items():
            if type(val) is dict:
                event_name += [self.subcommandIdToName(self.NOTIFICATION, event_name, event_attr)]
                subevent_fields = self.getResponseFields(self.NOTIFICATION, event_name)
                event_dict.update(self._xml_parse_fieldset(val, subevent_fields))
            else:
                # we assume that all event fields are defined
                field = [f for f in notif_fields if f.name == event_attr][0]
                event_dict[event_attr] = self._xml_parse_field(val, field)
        return (event_name, event_dict)

    def parse_notif(self, notif_name, notif_str):
        notif_metadata = self.getDefinition(self.NOTIFICATION, notif_name)
        notif_fields = self.getResponseFields(self.NOTIFICATION, notif_name)
        if notif_metadata.has_key('deserializer'):
            deserialize_func = getattr(self, notif_metadata['deserializer'])
            notif_name, notif_dict = deserialize_func(notif_str, notif_fields)
        else:
            notif_dict = self._parse_xmlobj(notif_str, notif_name[0], notif_fields)
        return (notif_name, notif_dict)
    
    # XML-RPC Serializer
    
    def _xmlrpc_format_field(self, field_value, field_metadata):
        if field_metadata[1] == self.HEXDATA:
            return ''.join(['%02X' % b for b in field_value])
        else:
            return field_value

    def default_serializer(self, commandArray, fields):
        cmd_metadata = self.getDefinition(self.COMMAND, commandArray)
        param_list = []
        # for each field in the input parameters, look up the value in cmd_params
        for p in cmd_metadata['request']:
            param_name = p[0]
            # format the parameter by type
            param_list.append(self._xmlrpc_format_field(fields[param_name], p))
        # param_list = [self.format_field(fields[f[0]], f) for f in cmd_metadata['request']]
        return param_list


    # XML-RPC Deserializer

    def _xml_parse_field(self, str_value, field_metadata):
        if field_metadata.format in [self.INT, self.INTS]:
            return int(str_value)
        elif field_metadata.format == self.FLOAT:
            return float(str_value)
        elif field_metadata.format == self.BOOL:
            if str_value.lower() == 'true':
                return True
            else:
                return False
        elif field_metadata.format == self.HEXDATA:
            returnVal = [int(str_value[i:i+2], 16) for i in range(0, len(str_value), 2)]
            return returnVal
        else: 
            return str_value

    def _xml_parse_fieldset(self, obj_dict, fields_metadata):
        'Filter and parse fields in obj_dict'
        filtered_dict = {}
        for field in fields_metadata:
            try:
                field_str = obj_dict[field.name]
                filtered_dict[field.name] = self._xml_parse_field(field_str, field)
            except KeyError:
                # some fields are not always present (especially in Statistics)
                filtered_dict[field.name] = ''
        return filtered_dict

    def _parse_xmlobj(self, xml_doc, base_element, fields_metadata, isArray = False):
        log.debug('Parsing XML: %s %s', base_element, xml_doc)
        aFull_resp = xmlutils.parse_xml_obj(xml_doc, base_element, fields_metadata)
        aRes = []
        for full_resp in aFull_resp : 
            if fields_metadata:
                # parse each field listed in the fields_metadata
                res = self._xml_parse_fieldset(full_resp, fields_metadata)
            else:
                res = full_resp
            if not isArray :
                return res
            aRes.append(res)
        return aRes
    
    def default_deserializer(self, cmd_metadata, xmlrpc_resp):
        resp = {}
        #resp = {'_raw_': xmlrpc_resp}
        resp_fields = self.getResponseFields(self.COMMAND, [cmd_metadata['name']])
        if cmd_metadata['response'].has_key(self.FIELDS):
            # unnamed fields are processed in order
            # note: special case the single return value
            if len(resp_fields) is 1:
                resp[resp_fields[0].name] = self._xml_parse_field(xmlrpc_resp, resp_fields[0])
            else:
                for i, field in enumerate(resp_fields):
                    resp[field.name] = self._xml_parse_field(xmlrpc_resp[i], field)

        elif cmd_metadata['id'] in ['getConfig', 'setConfig'] :
            # default getConfig parser
            # TODO: need an ApiDefinition method to get the response object name
            resp_obj = cmd_metadata['response'].keys()[0]
            isArray = False
            if ('isResponseArray' in cmd_metadata) :
                isArray = cmd_metadata['isResponseArray']
            resp = self._parse_xmlobj(xmlrpc_resp, resp_obj, resp_fields, isArray)
        
        return resp

    def deserialize(self, cmd_name, xmlrpc_resp):
        '''\brief Returns the XML-RPC response as a dict

        \returns A tuple of commandName and the response dictionary, 
                 which contains each of the fields of the response. 
        '''
        cmd_metadata = self.getDefinition(self.COMMAND, cmd_name)
        if cmd_metadata.has_key('deserializer'):
            deserializer = getattr(self, cmd_metadata['deserializer'])
        else:
            deserializer = self.default_deserializer
        resp = deserializer(cmd_metadata, xmlrpc_resp)
        return resp
    
    # ----------------------------------------------------------------------
    # Command-specific serialization methods
    # (must be defined ahead of commands)

    def serialize_getSystem(self, commandArray, cmd_params):
        return ['all', '<config><System/></config>']

    def serialize_getNetwork(self, commandArray, cmd_params):
        return ['all', '<config><Network/></config>']

    def serialize_getNetworkStats(self, commandArray, cmd_params):
        stat_query = self._build_stat_set(cmd_params['period'], cmd_params['index'])
        return ['all', '<config><Network><Statistics>%s</Statistics></Network></config>' % stat_query]

    def serialize_getMote(self, commandArray, cmd_params):
        config_doc = '<config><Motes><Mote><macAddr>%s</macAddr></Mote></Motes></config>' % (cmd_params['macAddr'])
        return ['all', config_doc]

    def serialize_getMotes(self, commandArray, cmd_params):
        config_doc = '<config><Motes></Motes></config>'
        return ['all', config_doc]
    
    def serialize_getMoteStats(self, commandArray, cmd_params):
        stat_query = self._build_stat_set(cmd_params['period'], cmd_params['index'])
        config_doc = '<config><Motes><Mote><macAddr>%s</macAddr><Statistics>%s</Statistics></Mote></Motes></config>' % (cmd_params['macAddr'], stat_query)
        return ['all', config_doc]

    def serialize_getPath(self, commandArray, cmd_params):
        config_doc = '<config><Paths><Path><moteMac>%s</moteMac></Path></Paths></config>' % (cmd_params['moteMac'])
        return ['all', config_doc]
    
    def serialize_getPathStats(self, commandArray, cmd_params):
        stat_query = self._build_stat_set(cmd_params['period'], cmd_params['index'])
        config_doc = '<config><Paths><Path><pathId>%s</pathId><Statistics>%s</Statistics></Path></Paths></config>' % (cmd_params['pathId'], stat_query)
        return ['all', config_doc]

    def serialize_getBlacklist(self, commandArray, cmd_params):
        config_doc = '<config><Network><ChannelBlackList/></Network></config>'
        return ['all', config_doc]      
      
    def serialize_getSla(self, commandArray, cmd_params):
        config_doc = '<config><Network><Sla/></Network></config>'
        return ['all', config_doc]      

    def serialize_getUsers(self, commandArray, cmd_params):
        config_doc = '<config><Users></Users></config>'
        return ['all', config_doc]      

    def serialize_getUser(self, commandArray, cmd_params):
        config_doc = '<config><Users><User><userName>%s</userName></User></Users></config>' % (cmd_params['userName'], )
        return ['all', config_doc]
          
    def serialize_setConfig(self, commandArray, fields) :
        cmd_metadata = self.getDefinition(self.COMMAND, commandArray)
        prefix = []
        if 'serializerParam' in cmd_metadata : 
            prefix = cmd_metadata['serializerParam']
        param_dict = {}
        # for each field in the input parameters, look up the value in cmd_params
        for p in cmd_metadata['request']:
            param_name = p[0]
            # format the parameter by type
            param_dict[param_name] = self._xmlrpc_format_field(fields[param_name], p)
        config_doc = xmlutils.dict_to_xml(param_dict, prefix)
        return [config_doc]

    def _build_stat_set(self, period, index = 0):
        STAT_PERIOD_QUERY_TMPL = '<{0}Set><{0}><index>{1}</index></{0}></{0}Set>'
        if period in ['current']:
            return '<statCur/>'
        elif period in ['lifetime']:
            return '<lifetime/>'
        elif period in ['short']:
            return STAT_PERIOD_QUERY_TMPL.format('stat15Min', index)
        elif period in ['long']:
            return STAT_PERIOD_QUERY_TMPL.format('stat1Day', index)
        else:
            raise RuntimeError('invalid stat period: %s', period)
    
    # ----------------------------------------------------------------------
    # Command-specific deserialization methods
    # (must be defined ahead of commands)

    def deserialize_getStats(self, cmd_metadata, xmlrpc_resp):
        net_stats = {}
        fields = self.getResponseFields(self.COMMAND, [cmd_metadata['name']])
        # parse the Statistics element
        resp_dict = self._parse_xmlobj(xmlrpc_resp, 'Statistics', None)
        # detect the statistics period
        stat_dict = {}
        if 'statCur' in resp_dict:
            stat_dict = resp_dict['statCur']
        elif 'lifetime' in resp_dict:
            stat_dict = resp_dict['lifetime']
        elif 'stat15MinSet' in resp_dict:
            stat_dict = resp_dict['stat15MinSet']['stat15Min']
        elif 'stat1DaySet' in resp_dict:
            stat_dict = resp_dict['stat1DaySet']['stat1Day']
        for field in fields:
            try:
                field_str = stat_dict[field.name]
                net_stats[field.name] = self._xml_parse_field(field_str, field)
            except KeyError:
                # some fields are not always present (especially in Statistics)
                net_stats[field.name] = ''
        return net_stats

    # Commands
    commands = [
        # Get Config commands
        {
            'id'         : 'getConfig', # TODO: is this required to be unique ?
            'name'       : 'getSystem',
            'description': 'Retrieves system-level information',
            'request'    : [
            ],
            'response'   : {
                'System':  [
                    ['systemName',          STRING,   32,  None],
                    ['location',            STRING,   32,  None],
                    ['swRev',               STRING,   32,  None],
                    ['hwModel',             STRING,   32,  None],
                    ['hwRev',               STRING,   32,  None],
                    ['serialNumber',        STRING,   32,  None],
                    ['time',                INT,      8,   None],
                    ['startTime',           INT,      8,   None],
                    ['cliTimeout',          INT,      4,   None],
                    ['controllerSwRev',     STRING,   32,  None],
                ],
            },
            'serializer' : 'serialize_getSystem',
        },
        {
            'id'         : 'getConfig',
            'name'       : 'getNetwork',
            'description': 'Retrieves network configuration parameters',
            'request'    : [
            ],
            'response'   : { 
                'Network':  [
                    ['netName',             STRING,   16,  None],
                    ['networkId',           INT,      4,   None],
                    ['maxMotes',            INT,      4,   None],
                    ['numMotes',            INT,      4,   None],
                    ['optimizationEnable',  BOOL,     1,   None],
                    ['accessPointPA',       BOOL,     1,   None],
                    ['ccaEnabled',          BOOL,     1,   None],
                    ['requestedBasePkPeriod', INT,    4,   None],
                    ['minServicesPkPeriod', INT,      4,   None],
                    ['minPipePkPeriod',     INT,      4,   None],
                    ['bandwidthProfile',    STRING,   16,  None], # TODO: enum
                    ['manualUSFrameSize',   INT,      4,   None],
                    ['manualDSFrameSize',   INT,      4,   None],
                    ['manualAdvFrameSize',  INT,      4,   None],
                    ['netQueueSize',        INT,      4,   None],
                    ['userQueueSize',       INT,      4,   None],
                    ['locationMode',        STRING,   16,  None], # TODO: enum
                ],
            },
            'serializer' : 'serialize_getNetwork',
        },
        {
            'id'         : 'getConfig',
            'name'       : 'getNetworkStatistics',
            'description': 'Get the Network Statistics',
            'request'    : [
                ['period',                  STRING,   32,  'statPeriod'],
                ['index',                   INT,      4,   None], # TODO: optional
            ],
            'response'   : { 
                'NetworkStatistics':  [
                    ['index',               INT,      4,   None],
                    ['startTime',           INT,      8,   None], # milliseconds
                    ['netLatency',          INT,      4,   None], # milliseconds
                    ['netReliability',      FLOAT,    0,   None], # percentage
                    ['netPathStability',    FLOAT,    0,   None], # percentage
                    ['lostUpstreamPackets', INT,      4,   None], # lifetime only ?
                ],
            },
            'serializer' : 'serialize_getNetworkStats',
            'deserializer' : 'deserialize_getStats',
        },
        
        {
            'id'         : 'getConfig',
            'name'       : 'getMote',
            'description': '',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : {
                'Mote':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   25,  None],
                    ['name',                STRING,   16,  None], # TODO: length
                    ['state',               STRING,   16,  'moteState'],
                    ['numJoins',            INT,      4,   None],
                    ['joinTime',            INT,      8,   None], # TODO: date time
                    ['reason',              STRING,   16,  None], # TODO: length
                    ['isAccessPoint',       BOOL,     1,   None],
                    ['powerSource',         STRING,   16,  None], # TODO: enum
                    ['dischargeCurrent',    INT,      4,   None],
                    ['dischargeTime',       INT,      4,   None],
                    ['recoveryTime',        INT,      4,   None],
                    ['enableRouting',       BOOL,     1,   None],
                    ['productName',         STRING,   16,  None], # TODO: length
                    ['hwModel',             INT,      4,   None], # TODO: type, length
                    ['hwRev',               INT,      4,   None], # TODO: type, length
                    ['swRev',               STRING,   16,  None], # TODO: length
                    ['voltage',             FLOAT,    8,   None],
                    ['numNeighbors',        INT,      4,   None],
                    ['needNeighbor',        BOOL,     1,   None],
                    ['goodNeighbors',       INT,      4,   None],
                    ['allocatedPkPeriod',   INT,      4,   None],
                    ['allocatedPipePkPeriod', INT,    4,   None],
                    ['pipeStatus',          STRING,   4,   'onOff'],
                    ['advertisingStatus',   STRING,   4,   'onOff'],
                    ['locationTag',         STRING,   16,  None], # TODO: enum                    
                ],
            },
            'serializer' : 'serialize_getMote',
        },
        {
            'id'         : 'getConfig',
            'name'       : 'getMoteStatistics',
            'description': 'Get the Mote Statistics',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['period',                  STRING,   32,  'statPeriod'],
                ['index',                   INT,      4,   None], # TODO: optional
            ],
            'response'   : { 
                'MoteStatistics':  [
                    ['index',               INT,      4,   None],
                    ['startTime',           INT,      8,   None], # milliseconds
                    ['avgLatency',          INT,      4,   None], # milliseconds
                    ['reliability',         FLOAT,    0,   None], # percentage
                    ['numJoins',            INT,      4,   None],
                    ['numLostPackets',      INT,      4,   None],
                ],
            },
            'serializer' : 'serialize_getMoteStats',
            'deserializer' : 'deserialize_getStats',
        },

        # getMotes -- return LIST of motess
        {
            'id'         : 'getConfig',
            'name'       : 'getMotes',
            'description': '''Get the list of Motes''',
            'request'    : [
            ],
            'response'   : {
                'Mote':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   25,  None],
                    ['name',                STRING,   16,  None], # TODO: length
                    ['state',               STRING,   16,  'moteState'],
                    ['numJoins',            INT,      4,   None],
                    ['joinTime',            INT,      8,   None], # TODO: date time
                    ['reason',              STRING,   16,  None], # TODO: length
                    ['isAccessPoint',       BOOL,     1,   None],
                    ['powerSource',         STRING,   16,  None], # TODO: enum
                    ['dischargeCurrent',    INT,      4,   None],
                    ['dischargeTime',       INT,      4,   None],
                    ['recoveryTime',        INT,      4,   None],
                    ['enableRouting',       BOOL,     1,   None],
                    ['productName',         STRING,   16,  None], # TODO: length
                    ['hwModel',             INT,      4,   None], # TODO: type, length
                    ['hwRev',               INT,      4,   None], # TODO: type, length
                    ['swRev',               STRING,   16,  None], # TODO: length
                    ['voltage',             FLOAT,    8,   None],
                    ['numNeighbors',        INT,      4,   None],
                    ['needNeighbor',        BOOL,     1,   None],
                    ['goodNeighbors',       INT,      4,   None],
                    ['allocatedPkPeriod',   INT,      4,   None],
                    ['allocatedPipePkPeriod', INT,    4,   None],
                    ['pipeStatus',          STRING,   4,   'onOff'],
                    ['advertisingStatus',   STRING,   4,   'onOff'],
                    ['locationTag',         STRING,   16,  None], # TODO: enum                    
                ],
            },
            'serializer' : 'serialize_getMotes',
            'isResponseArray': True,
        },
        # getPaths -- return LIST of paths
        {
            'id'         : 'getConfig',
            'name'       : 'getPaths',
            'description': '''Get the list of Paths to the mote\'s neighbors''',
            'request'    : [
                ['moteMac',                STRING,    25,  None],
            ],
            'response'   : {
                'Path':  [
                    ['pathId',              INT,      4,   None],
                    ['moteAMac',            STRING,   25,  None],
                    ['moteBMac',            STRING,   25,  None],
                    ['numLinks',            INT,      4,   None],
                    ['pathDirection',       STRING,   16,  'pathDirection'],
                    ['pathQuality',         FLOAT,    0,   None],
                ],
            },
            'serializer' : 'serialize_getPath',
            'isResponseArray': True,
        },
        {
            'id'         : 'getConfig',
            'name'       : 'getPathStatistics',
            'description': 'Get Statistics for a specific Path',
            'request'    : [
                ['pathId',                  INT,      4,   None],
                ['period',                  STRING,   16,  'statPeriod'],
                ['index',                   INT,      4,   None],
            ],
            'response'   : {
                'PathStatistics':  [
                    ['index',               INT,      4,   None],
                    ['startTime',           INT,      8,   None], # milliseconds
                    ['baPwr',               INT,      1,   None],
                    ['abPwr',               INT,      1,   None],
                    ['stability',           FLOAT,    0,   None],
                ],
            },
            'serializer' : 'serialize_getPathStats',
            'deserializer' : 'deserialize_getStats',
        },
        
        # getBlacklist -- return LIST of paths
        {
            'id'         : 'getConfig',
            'name'       : 'getBlacklist',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'ChannelBlackList':  [
                    ['frequency',           FLOAT,    0,   None],
                ],
            },
            'serializer' : 'serialize_getBlacklist',
            'isResponseArray': True,
        },
        
        # getSla
        {
            'id'         : 'getConfig',
            'name'       : 'getSla',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'Sla':  [
                    ['minNetReliability',   FLOAT,    0,   None],
                    ['maxNetLatency',       INT,      4,   None],
                    ['minNetPathStability', FLOAT,    0,   None],
                    ['apRdntCoverageThreshold', FLOAT,0,   None],
                ],
            },
            'serializer' : 'serialize_getSla',
        },
        
        # getUsers  -- return LIST of users 
        {
            'id'         : 'getConfig',
            'name'       : 'getUsers',
            'description': '',
            'request'    : [
            ],
            'response'   : {
                'User':  [
                    ['userName',            STRING,   16,  None],
                    ['privilege',           STRING,   16,  'userPrivilege'],
                ],
            },
            'serializer' : 'serialize_getUsers',
            'isResponseArray': True,
        },
                
        # getUser 
        {
            'id'         : 'getConfig',
            'name'       : 'getUser',
            'description': '',
            'request'    : [
                ['userName',                STRING,   16,  None],
            ],
            'response'   : {
                'User':  [
                    ['userName',            STRING,   16,  None],
                    ['privilege',           STRING,   16,  'userPrivilege'],
                ],
            },
            'serializer' : 'serialize_getUser',
        },
                
        # setSystem
        {
            'id'         : 'setConfig',
            'name'       : 'setSystem',
            'description': '',
            'request'    : [
                ['systemName',              STRING,   16,  None],
                ['location',                STRING,   16,  None],
                ['cliTimeout',              INT,      4,   None],
            ],
            'response'   : { 
                'System':  [
                    ['systemName',          STRING,   50,  None],
                    ['location',            STRING,   50,  None],
                    ['cliTimeout',          INT,      4,   None],
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'System'],
        },
           
        # setNetwork
        {
            'id'         : 'setConfig',
            'name'       : 'setNetwork',
            'description': '',
            'request'    : [
                ['netName',                 STRING,   16,  None],
                ['networkId',               INT,      4,   None],
                ['optimizationEnable',      STRING,   6,   'bool'],
                #['maintStartTime',          INT,      8,   None],
                #['maintEndTime',            INT,      8,   None],
                ['maxMotes',                INT,      4,   None],
                ['accessPointPA',           STRING,   6,   'bool'],
                ['ccaEnabled',              STRING,   6,   'bool'],
                ['requestedBasePkPeriod',   INT,      4,   None],
                ['minServicesPkPeriod',     INT,      4,   None],
                ['minPipePkPeriod',         INT,      4,   None],
                ['bandwidthProfile',        STRING,   16,  'bandwidthProfile'],
                ['manualUSFrameSize',       INT,      4,   None],
                ['manualDSFrameSize',       INT,      4,   None],
                ['manualAdvFrameSize',      INT,      4,   None],
                ['locationMode',            STRING,   8,   'onOff'],
            ],
            'response'   : { 
                'Network':  [
                    ['netName',             STRING,   16,  None],
                    ['networkId',           INT,      4,   None],
                    ['optimizationEnable',  STRING,   6,   'bool'],
                    #['maintStartTime',      INT,      8,   None],
                    #['maintEndTime',        INT,      8,   None],
                    ['maxMotes',            INT,      4,   None],
                    ['accessPointPA',       STRING,   6,   'bool'],
                    ['ccaEnabled',          STRING,   6,   'bool'],
                    ['requestedBasePkPeriod', INT,    4,   None],
                    ['minServicesPkPeriod', INT,      4,   None],
                    ['minPipePkPeriod',     INT,      4,   None],
                    ['bandwidthProfile',    STRING,   16,  'bandwidthProfile'],
                    ['manualUSFrameSize',   INT,      4,   None],
                    ['manualDSFrameSize',   INT,      4,   None],
                    ['manualAdvFrameSize',  INT,      4,   None],
                    ['locationMode',        STRING,   8,   'onOff'],
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Network'],
        },
        
        # setMote
        {
            'id'         : 'setConfig',
            'name'       : 'setMote',
            'description': '',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['name',                    STRING,   16,  None],
                ['enableRouting',           STRING,   6,   'bool'],
            ],
            'response'   : { 
                'Mote':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   25,  None],
                    ['name',                STRING,   16,  None], # TODO: length
                    ['state',               STRING,   16,  'moteState'],
                    ['numJoins',            INT,      4,   None],
                    ['joinTime',            INT,      8,   None], # TODO: date time
                    ['reason',              STRING,   16,  None], # TODO: length
                    ['isAccessPoint',       BOOL,     1,   None],
                    ['powerSource',         STRING,   16,  None], # TODO: enum
                    ['dischargeCurrent',    INT,      4,   None],
                    ['dischargeTime',       INT,      4,   None],
                    ['recoveryTime',        INT,      4,   None],
                    ['enableRouting',       BOOL,     1,   None],
                    ['productName',         STRING,   16,  None], # TODO: length
                    ['hwModel',             INT,      4,   None], # TODO: type, length
                    ['hwRev',               INT,      4,   None], # TODO: type, length
                    ['swRev',               STRING,   16,  None], # TODO: length
                    ['voltage',             FLOAT,    8,   None],
                    ['numNeighbors',        INT,      4,   None],
                    ['needNeighbor',        BOOL,     1,   None],
                    ['goodNeighbors',       INT,      4,   None],
                    ['allocatedPkPeriod',   INT,      4,   None],
                    ['allocatedPipePkPeriod', INT,    4,   None],
                    ['pipeStatus',          STRING,   4,   'onOff'],
                    ['advertisingStatus',   STRING,   4,   'onOff'],
                    ['locationTag',         STRING,   16,  None], # TODO: enum                    
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Motes', 'Mote'],
        },
        
        # setSla
        {
            'id'         : 'setConfig',
            'name'       : 'setSla',
            'description': '',
            'request'    : [
                ['minNetReliability',       FLOAT,    0,   None],
                ['maxNetLatency',           INT,      4,   None],
                ['minNetPathStability',     FLOAT,    0,   None],
                ['apRdntCoverageThreshold', FLOAT,    0,   None],
            ],
            'response'   : { 
                'Sla':  [
                    ['minNetReliability',   FLOAT,    0,   None],
                    ['maxNetLatency',       INT,      4,   None],
                    ['minNetPathStability', FLOAT,    0,   None],
                    ['apRdntCoverageThreshold', FLOAT, 0,  None],
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Network', 'Sla'],
        },

        # setSecurity
        {
            'id'         : 'setConfig',
            'name'       : 'setSecurity',
            'description': '',
            'request'    : [
                ['securityMode',            STRING,   25,  'securityMode'],
                ['commonJoinKey',           STRING,   33,  None],
                ['acceptHARTDevicesOnly',   STRING,   6,   'bool'],
            ],
            'response'   : { 
                'Security':  [
                    ['securityMode',        STRING,   16,  'securityMode'],
                    ['commonJoinKey',       STRING,   33,  None],
                    ['acceptHARTDevicesOnly', STRING, 6,   'bool'],
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Security'],
        },
           
        # setUser
        {
            'id'         : 'setConfig',
            'name'       : 'setUser',
            'description': '',
            'request'    : [
                ['userName',                STRING,   16,  None],
                ['password',                STRING,   16,  None],
                ['privilege',               STRING,   16,  'userPrivilege'],
            ],
            'response'   : { 
                'User':  [
                    ['userName',            STRING,   16,  None],
                    ['password',            STRING,   16,  None],
                    ['privilege',           STRING,   16,  'userPrivilege'],
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Users', 'User'],
        },
                
        # setAcl
        {
            'id'         : 'setConfig',
            'name'       : 'setAcl',
            'description': '',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['joinKey',                 STRING,   33,  None],
            ],
            'response'   : { 
                'Device':  [
                    ['macAddr',             STRING,   25,  None],
                    ['joinKey',             STRING,   33,  None],
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Security', 'Acl', 'Device'],
        },
                
        # setBlackList
        {
            'id'         : 'setConfig',
            'name'       : 'setBlackList',
            'description': '',
            'request'    : [
                ['frequency',               INT,      4,   None],
            ],
            'response'   : { 
                'ChannelBlackList':  [
                    ['frequency',           INT,      4,   None],
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Network', 'ChannelBlackList'],
        },
             
        # deleteAcl
        {
            'id'         : 'deleteConfig',
            'name'       : 'deleteAcl',
            'description': '',
            'request'    : [
                ['macAddr', STRING, 25, None],
            ],
            'response'   : { 
                FIELDS:  [
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Security', 'Acl', 'Device'],
        },
           
        # deleteUser
        {
            'id'         : 'deleteConfig',
            'name'       : 'deleteUser',
            'description': '',
            'request'    : [
                ['userName',                STRING,   16,  None],
            ],
            'response'   : { 
                FIELDS:  [
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Users', 'User'],
        },
                
        # deleteMote
        {
            'id'         : 'deleteConfig',
            'name'       : 'deleteMote',
            'description': '',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : { 
                FIELDS:  [
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Motes', 'Mote'],
        },
                
        # Send packet commands
        {
            'id'         : 'sendRequest',
            'name'       : 'sendRequest',
            'description': '',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['domain',                  STRING,   16,  'appDomain'],
                ['priority',                STRING,   16,  'packetPriority'],
                ['reliable',                BOOL,     0,   None],
                ['data',                    HEXDATA,  128, None],
            ],
            'response'   : { 
                FIELDS : [
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
        {
            'id'         : 'sendResponse',
            'name'       : 'sendResponse',
            'description': '',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['domain',                  STRING,   16,  'appDomain'],
                ['priority',                STRING,   16,  'packetPriority'],
                ['reliable',                BOOL,     0,   None],
                ['callbackId',              INT,      4,   None],
                ['data',                    HEXDATA,  128, None],
            ],
            'response'   : { 
                FIELDS : [
                    ['result',              STRING,   32,  None],
                ],
            },
        },

        # exchangeNetworkKey
        {
            'id'         : 'exchangeNetworkKey',
            'name'       : 'exchangeNetworkKey',
            'description': 'Exchange network key',
            'request'    : [
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },

        
        # exchangeJoinKey
        {
            'id'         : 'exchangeJoinKey',
            'name'       : 'exchangeJoinKey',
            'description': 'Exchange common join key',
            'request'    : [
                ['newKey',                  STRING,   33,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
                
        # exchangeMoteJoinKey
        {
            'id'         : 'exchangeMoteJoinKey',
            'name'       : 'exchangeMoteJoinKey',
            'description': 'Exchange mote join key',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['newKey',                  STRING,   33,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
                
        # exchangeNetworkId
        {
            'id'         : 'exchangeNetworkId',
            'name'       : 'exchangeNetworkId',
            'description': 'Exchange network ID',
            'request'    : [
                ['newId',                   INT,      4,   None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
                
        # exchangeMoteNetworkId
        {
            'id'         : 'exchangeMoteNetworkId',
            'name'       : 'exchangeMoteNetworkId',
            'description': 'Exchange network ID for mote',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['newId',                   INT,      4,   None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
                
        # exchangeSessionKey
        {
            'id'         : 'exchangeSessionKey',
            'name'       : 'exchangeSessionKey',
            'description': 'Exchange mote session key',
            'request'    : [
                ['macAddrA',                STRING,   25,  None],
                ['macAddrB',                STRING,   25,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
                

        # Miscellaneous commands
        {
            'id'         : 'activateFastPipe',
            'name'       : 'activateFastPipe',
            'description': 'Activate the fast network pipe to the specified mote.',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['pipeDirection',           STRING,   25,  'pipeDirection'],
            ],
            'response'   : {
                FIELDS : [
                    ['result',              STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'deactivateFastPipe',
            'name'       : 'deactivateFastPipe',
            'description': 'Deactivate the fast network pipe to the specified mote.',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : {
                FIELDS : [
                    ['result',              STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'getLatency',
            'name'       : 'getLatency',
            'description': 'Get estimated latency for a mote.',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['downstream',          INT,      4,   None],
                    ['upstream',            INT,      4,   None],
                ],
            },
        },
        {
            'id'         : 'getTime',
            'name'       : 'getTime',
            'description': 'Get the current time.',
            'request'    : [
            ],
            'response'   : {
                FIELDS : [ 
                    ['utc_time',            FLOAT,    0,   None], # TODO: return as a date-time format
                    ['asn_time',            INT,      8,   None],
                ],
            },
        },

        # activateAdvertising
        {
            'id'         : 'activateAdvertising',
            'name'       : 'advertising',
            'description': 'Activate advertisement frame',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['timeout',                 INT,      4,   None]
            ],
            'response'   : {
                FIELDS : [ 
                          ['result',        STRING,   32,  None],
                ],
            },
        },

        # decommissionDevice
        {
            'id'         : 'decommissionDevice',
            'name'       : 'decommission',
            'description': 'Device decommission',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : {
                FIELDS : [ 
                          ['result',        STRING,   32,  None],
                ],
            },
        },

        {
            'id'         : 'pingMote',
            'name'       : 'ping',
            'description': '''Ping the specified mote. A Net Ping Reply event notification will contain the mote's response.''',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },

        # getLicense
        {
            'id'         : 'getLicense',
            'name'       : 'getLicense',
            'description': 'Get license',
            'request'    : [
            ],
            'response'   : {
                FIELDS : [ 
                    ['license',             STRING,   40,  None],
                ],
            },
        },

        # setLicense
        {
            'id'         : 'setLicense',
            'name'       : 'setLicense',
            'description': 'Set license',
            'request'    : [
                ['license',                 STRING,   40,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['result',              STRING,   32,  None],
                ],
            },
        },
                
        # startLocation TODO
        
        # stopLocation
        {
            'id'         : 'stopLocation',
            'name'       : 'stopLocation',
            'description': 'Stop location',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
                
        # reset
        {
            'id'         : 'reset',
            'name'       : 'reset',
            'description': 'Reset',
            'request'    : [
                ['object',                  STRING,   25,  'resetObject'],
            ],
            'response'   : {
                FIELDS : [ 
                    ['result',              STRING,   32,  None],
                ],
            },
        },
                
        # resetWithId
        {
            'id'         : 'reset',
            'name'       : 'resetWithId',
            'description': 'Reset mote by ID',
            'request'    : [
                ['object',                  STRING,   25,  'resetMote'],
                ['moteId',                  INT,      4,   None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['result',              STRING,   32,  None],
                ],
            },
        },
                
        # resetWithMac
        {
            'id'         : 'reset',
            'name'       : 'resetWithMac',
            'description': 'Reset mote by MAC address',
            'request'    : [
                ['object',                  STRING,   25,  'resetMote'],
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['result',              STRING,   32,  None],
                ],
            },
        },
                
        # cli
        {
            'id'         : 'cli',
            'name'       : 'cli',
            'description': 'Run CLI command',
            'request'    : [
                ['command',                 STRING,   128, None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['result',              STRING,   32,  None],
                ],
            },
        },

        # subscribe, unsubscribe
        {
            'id'         : 'subscribe',
            'name'       : 'subscribe',
            'description': '''Subscribe to notifications. This function creates or updates the subscribed notifications to match 'filter'. The filter is a space-separated list of notification types. Valid types include 'data', 'events', 'alarms', 'log'.''',
            'request'    : [
                ['filter',                  STRING,   128, None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['notif_token',         STRING,   32,  None],
                ],
            },
            'command_override': 'subscribe_override',
        },
        {
            'id'         : 'unsubscribe',
            'name'       : 'unsubscribe',
            'description': 'Unsubscribe from notifications. This function clears any existing notification subscription and stops the notification thread. ',
            'request'    : [
            ],
            'response'   : {
                FIELDS : [ 
                    ['result',              STRING,   32,  None],
                ],
            },
            'command_override': 'unsubscribe_override',
        },
    ]
