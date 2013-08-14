'''
This module was generated automatically. Do not edit directly.
'''

import collections
import ApiException
from   HartMoteConnectorInternal import HartMoteConnectorInternal

class HartMoteConnector(HartMoteConnectorInternal):
    '''
    \ingroup ApiConnector
    \brief Public class for the HART Mote connector, over Serial.
    '''

    #======================== commands ========================================

    ##
    # The named tuple returned by the dn_setParameter_txPower() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setParameter_txPower = collections.namedtuple("Tuple_dn_setParameter_txPower", ['RC'])

    ##
    # 
    # 
    # \param txPower 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_txPower named tuple.
    # 
    def dn_setParameter_txPower(self, txPower) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'txPower'], {"txPower" : txPower})
        return HartMoteConnector.Tuple_dn_setParameter_txPower(**res)

    ##
    # The named tuple returned by the dn_setParameter_joinDutyCycle() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setParameter_joinDutyCycle = collections.namedtuple("Tuple_dn_setParameter_joinDutyCycle", ['RC'])

    ##
    # 
    # 
    # \param dutyCycle 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_joinDutyCycle named tuple.
    # 
    def dn_setParameter_joinDutyCycle(self, dutyCycle) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'joinDutyCycle'], {"dutyCycle" : dutyCycle})
        return HartMoteConnector.Tuple_dn_setParameter_joinDutyCycle(**res)

    ##
    # The named tuple returned by the dn_setParameter_batteryLife() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setParameter_batteryLife = collections.namedtuple("Tuple_dn_setParameter_batteryLife", ['RC'])

    ##
    # 
    # 
    # \param batteryLife 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param powerStatus 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: nominal
    #      - 1: low
    #      - 2: criticallyLow
    #      - 3: rechargingLow
    #      - 4: rechargingHigh
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_batteryLife named tuple.
    # 
    def dn_setParameter_batteryLife(self, batteryLife, powerStatus) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'batteryLife'], {"batteryLife" : batteryLife, "powerStatus" : powerStatus})
        return HartMoteConnector.Tuple_dn_setParameter_batteryLife(**res)

    ##
    # The named tuple returned by the dn_setParameter_service() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>numServices</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_setParameter_service = collections.namedtuple("Tuple_dn_setParameter_service", ['RC', 'numServices'])

    ##
    # 
    # 
    # \param serviceId 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param serviceReqFlags 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param appDomain 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: publish
    #      - 1: event
    #      - 2: maintenance
    #      - 3: blockTransfer
    # \param destAddr 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # \param time 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_service named tuple.
    # 
    def dn_setParameter_service(self, serviceId, serviceReqFlags, appDomain, destAddr, time) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'service'], {"serviceId" : serviceId, "serviceReqFlags" : serviceReqFlags, "appDomain" : appDomain, "destAddr" : destAddr, "time" : time})
        return HartMoteConnector.Tuple_dn_setParameter_service(**res)

    ##
    # The named tuple returned by the dn_setParameter_hartDeviceStatus() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setParameter_hartDeviceStatus = collections.namedtuple("Tuple_dn_setParameter_hartDeviceStatus", ['RC'])

    ##
    # 
    # 
    # \param hartDevStatus 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_hartDeviceStatus named tuple.
    # 
    def dn_setParameter_hartDeviceStatus(self, hartDevStatus) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'hartDeviceStatus'], {"hartDevStatus" : hartDevStatus})
        return HartMoteConnector.Tuple_dn_setParameter_hartDeviceStatus(**res)

    ##
    # The named tuple returned by the dn_setParameter_hartDeviceInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setParameter_hartDeviceInfo = collections.namedtuple("Tuple_dn_setParameter_hartDeviceInfo", ['RC'])

    ##
    # 
    # 
    # \param hartCmd0 22-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # \param hartCmd20 32-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_hartDeviceInfo named tuple.
    # 
    def dn_setParameter_hartDeviceInfo(self, hartCmd0, hartCmd20) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'hartDeviceInfo'], {"hartCmd0" : hartCmd0, "hartCmd20" : hartCmd20})
        return HartMoteConnector.Tuple_dn_setParameter_hartDeviceInfo(**res)

    ##
    # The named tuple returned by the dn_setParameter_eventMask() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setParameter_eventMask = collections.namedtuple("Tuple_dn_setParameter_eventMask", ['RC'])

    ##
    # 
    # 
    # \param eventMask 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_eventMask named tuple.
    # 
    def dn_setParameter_eventMask(self, eventMask) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'eventMask'], {"eventMask" : eventMask})
        return HartMoteConnector.Tuple_dn_setParameter_eventMask(**res)

    ##
    # The named tuple returned by the dn_setParameter_writeProtect() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setParameter_writeProtect = collections.namedtuple("Tuple_dn_setParameter_writeProtect", ['RC'])

    ##
    # 
    # 
    # \param writeProtect 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: writeAllowed
    #      - 1: writeNotAllowed
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_writeProtect named tuple.
    # 
    def dn_setParameter_writeProtect(self, writeProtect) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'writeProtect'], {"writeProtect" : writeProtect})
        return HartMoteConnector.Tuple_dn_setParameter_writeProtect(**res)

    ##
    # The named tuple returned by the dn_getParameter_moteInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>apiVersion</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>serialNumber</tt>: 8-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>hwModel</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>hwRev</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swMajor</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swMinor</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swPatch</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swBuild</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_moteInfo = collections.namedtuple("Tuple_dn_getParameter_moteInfo", ['RC', 'apiVersion', 'serialNumber', 'hwModel', 'hwRev', 'swMajor', 'swMinor', 'swPatch', 'swBuild'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_moteInfo named tuple.
    # 
    def dn_getParameter_moteInfo(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'moteInfo'], {})
        return HartMoteConnector.Tuple_dn_getParameter_moteInfo(**res)

    ##
    # The named tuple returned by the dn_getParameter_networkInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>macAddress</tt>: 8-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>moteId</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>netId</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_networkInfo = collections.namedtuple("Tuple_dn_getParameter_networkInfo", ['RC', 'macAddress', 'moteId', 'netId'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_networkInfo named tuple.
    # 
    def dn_getParameter_networkInfo(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'networkInfo'], {})
        return HartMoteConnector.Tuple_dn_getParameter_networkInfo(**res)

    ##
    # The named tuple returned by the dn_getParameter_moteStatus() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>state</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: init
    #      - 1: idle
    #      - 2: searching
    #      - 3: negotiating
    #      - 4: connected
    #      - 5: operational
    #      - 6: disconnected
    #      - 7: radioTest
    #      - 8: promiscuousListen
    # - <tt>moteStateReason</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>changeCounter</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>numParents</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>alarms</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>statusFlags</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_moteStatus = collections.namedtuple("Tuple_dn_getParameter_moteStatus", ['RC', 'state', 'moteStateReason', 'changeCounter', 'numParents', 'alarms', 'statusFlags'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_moteStatus named tuple.
    # 
    def dn_getParameter_moteStatus(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'moteStatus'], {})
        return HartMoteConnector.Tuple_dn_getParameter_moteStatus(**res)

    ##
    # The named tuple returned by the dn_getParameter_time() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>utcTimeSec</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>utcTimeMsec</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>asn</tt>: 5-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>asnOffset</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_time = collections.namedtuple("Tuple_dn_getParameter_time", ['RC', 'utcTimeSec', 'utcTimeMsec', 'asn', 'asnOffset'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_time named tuple.
    # 
    def dn_getParameter_time(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'time'], {})
        return HartMoteConnector.Tuple_dn_getParameter_time(**res)

    ##
    # The named tuple returned by the dn_getParameter_charge() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>charge</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>uptime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>temperature</tt>: 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>fractionalTemp</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_charge = collections.namedtuple("Tuple_dn_getParameter_charge", ['RC', 'charge', 'uptime', 'temperature', 'fractionalTemp'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_charge named tuple.
    # 
    def dn_getParameter_charge(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'charge'], {})
        return HartMoteConnector.Tuple_dn_getParameter_charge(**res)

    ##
    # The named tuple returned by the dn_getParameter_radioTestRxStats() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>rxOk</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>rxFail</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_radioTestRxStats = collections.namedtuple("Tuple_dn_getParameter_radioTestRxStats", ['RC', 'rxOk', 'rxFail'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_radioTestRxStats named tuple.
    # 
    def dn_getParameter_radioTestRxStats(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'radioTestRxStats'], {})
        return HartMoteConnector.Tuple_dn_getParameter_radioTestRxStats(**res)

    ##
    # The named tuple returned by the dn_getParameter_service() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>serviceId</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>serviceState</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: inactive
    #      - 1: active
    #      - 2: requested
    # - <tt>serviceFlags</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>appDomain</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: publish
    #      - 1: event
    #      - 2: maintenance
    #      - 3: blockTransfer
    # - <tt>destAddr</tt>: 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>time</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_service = collections.namedtuple("Tuple_dn_getParameter_service", ['RC', 'serviceId', 'serviceState', 'serviceFlags', 'appDomain', 'destAddr', 'time'])

    ##
    # 
    # 
    # \param serviceId 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_service named tuple.
    # 
    def dn_getParameter_service(self, serviceId) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'service'], {"serviceId" : serviceId})
        return HartMoteConnector.Tuple_dn_getParameter_service(**res)

    ##
    # The named tuple returned by the dn_setNvParameter_macAddress() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setNvParameter_macAddress = collections.namedtuple("Tuple_dn_setNvParameter_macAddress", ['RC'])

    ##
    # 
    # 
    # \param targetMemory 1-byte field formatted as a bool.<br/>
    #     This field can only take one of the following values:
    #      - False: NV_only
    #      - True: NV_and_RAM
    # \param macAddr 8-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNvParameter_macAddress named tuple.
    # 
    def dn_setNvParameter_macAddress(self, targetMemory, macAddr) :
        res = HartMoteConnectorInternal.send(self, ['setNvParameter', 'macAddress'], {"targetMemory" : targetMemory, "macAddr" : macAddr})
        return HartMoteConnector.Tuple_dn_setNvParameter_macAddress(**res)

    ##
    # The named tuple returned by the dn_setNvParameter_networkId() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setNvParameter_networkId = collections.namedtuple("Tuple_dn_setNvParameter_networkId", ['RC'])

    ##
    # 
    # 
    # \param targetMemory 1-byte field formatted as a bool.<br/>
    #     This field can only take one of the following values:
    #      - False: NV_only
    #      - True: NV_and_RAM
    # \param networkId 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNvParameter_networkId named tuple.
    # 
    def dn_setNvParameter_networkId(self, targetMemory, networkId) :
        res = HartMoteConnectorInternal.send(self, ['setNvParameter', 'networkId'], {"targetMemory" : targetMemory, "networkId" : networkId})
        return HartMoteConnector.Tuple_dn_setNvParameter_networkId(**res)

    ##
    # The named tuple returned by the dn_setNvParameter_txPower() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setNvParameter_txPower = collections.namedtuple("Tuple_dn_setNvParameter_txPower", ['RC'])

    ##
    # 
    # 
    # \param targetMemory 1-byte field formatted as a bool.<br/>
    #     This field can only take one of the following values:
    #      - False: NV_only
    #      - True: NV_and_RAM
    # \param txPower 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNvParameter_txPower named tuple.
    # 
    def dn_setNvParameter_txPower(self, targetMemory, txPower) :
        res = HartMoteConnectorInternal.send(self, ['setNvParameter', 'txPower'], {"targetMemory" : targetMemory, "txPower" : txPower})
        return HartMoteConnector.Tuple_dn_setNvParameter_txPower(**res)

    ##
    # The named tuple returned by the dn_setNvParameter_joinKey() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setNvParameter_joinKey = collections.namedtuple("Tuple_dn_setNvParameter_joinKey", ['RC'])

    ##
    # 
    # 
    # \param targetMemory 1-byte field formatted as a bool.<br/>
    #     This field can only take one of the following values:
    #      - False: NV_only
    #      - True: NV_and_RAM
    # \param joinKey 16-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNvParameter_joinKey named tuple.
    # 
    def dn_setNvParameter_joinKey(self, targetMemory, joinKey) :
        res = HartMoteConnectorInternal.send(self, ['setNvParameter', 'joinKey'], {"targetMemory" : targetMemory, "joinKey" : joinKey})
        return HartMoteConnector.Tuple_dn_setNvParameter_joinKey(**res)

    ##
    # The named tuple returned by the dn_setNvParameter_powerInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setNvParameter_powerInfo = collections.namedtuple("Tuple_dn_setNvParameter_powerInfo", ['RC'])

    ##
    # 
    # 
    # \param targetMemory 1-byte field formatted as a bool.<br/>
    #     This field can only take one of the following values:
    #      - False: NV_only
    #      - True: NV_and_RAM
    # \param powerSource 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: line
    #      - 1: battery
    #      - 2: scavenging
    # \param dischargeCur 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param dischargeTime 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param recoverTime 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNvParameter_powerInfo named tuple.
    # 
    def dn_setNvParameter_powerInfo(self, targetMemory, powerSource, dischargeCur, dischargeTime, recoverTime) :
        res = HartMoteConnectorInternal.send(self, ['setNvParameter', 'powerInfo'], {"targetMemory" : targetMemory, "powerSource" : powerSource, "dischargeCur" : dischargeCur, "dischargeTime" : dischargeTime, "recoverTime" : recoverTime})
        return HartMoteConnector.Tuple_dn_setNvParameter_powerInfo(**res)

    ##
    # The named tuple returned by the dn_setNvParameter_ttl() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setNvParameter_ttl = collections.namedtuple("Tuple_dn_setNvParameter_ttl", ['RC'])

    ##
    # 
    # 
    # \param targetMemory 1-byte field formatted as a bool.<br/>
    #     This field can only take one of the following values:
    #      - False: NV_only
    #      - True: NV_and_RAM
    # \param timeToLive 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNvParameter_ttl named tuple.
    # 
    def dn_setNvParameter_ttl(self, targetMemory, timeToLive) :
        res = HartMoteConnectorInternal.send(self, ['setNvParameter', 'ttl'], {"targetMemory" : targetMemory, "timeToLive" : timeToLive})
        return HartMoteConnector.Tuple_dn_setNvParameter_ttl(**res)

    ##
    # The named tuple returned by the dn_setNvParameter_HARTantennaGain() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setNvParameter_HARTantennaGain = collections.namedtuple("Tuple_dn_setNvParameter_HARTantennaGain", ['RC'])

    ##
    # 
    # 
    # \param targetMemory 1-byte field formatted as a bool.<br/>
    #     This field can only take one of the following values:
    #      - False: NV_only
    #      - True: NV_and_RAM
    # \param antennaGain 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNvParameter_HARTantennaGain named tuple.
    # 
    def dn_setNvParameter_HARTantennaGain(self, targetMemory, antennaGain) :
        res = HartMoteConnectorInternal.send(self, ['setNvParameter', 'HARTantennaGain'], {"targetMemory" : targetMemory, "antennaGain" : antennaGain})
        return HartMoteConnector.Tuple_dn_setNvParameter_HARTantennaGain(**res)

    ##
    # The named tuple returned by the dn_setNvParameter_OTAPlockout() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_setNvParameter_OTAPlockout = collections.namedtuple("Tuple_dn_setNvParameter_OTAPlockout", ['RC'])

    ##
    # 
    # 
    # \param targetMemory 1-byte field formatted as a bool.<br/>
    #     This field can only take one of the following values:
    #      - False: NV_only
    #      - True: NV_and_RAM
    # \param otapLockout 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: allowed
    #      - 1: disabled
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNvParameter_OTAPlockout named tuple.
    # 
    def dn_setNvParameter_OTAPlockout(self, targetMemory, otapLockout) :
        res = HartMoteConnectorInternal.send(self, ['setNvParameter', 'OTAPlockout'], {"targetMemory" : targetMemory, "otapLockout" : otapLockout})
        return HartMoteConnector.Tuple_dn_setNvParameter_OTAPlockout(**res)

    ##
    # The named tuple returned by the dn_getNvParameter_macAddress() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>macAddr</tt>: 8-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNvParameter_macAddress = collections.namedtuple("Tuple_dn_getNvParameter_macAddress", ['RC', 'macAddr'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNvParameter_macAddress named tuple.
    # 
    def dn_getNvParameter_macAddress(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNvParameter', 'macAddress'], {})
        return HartMoteConnector.Tuple_dn_getNvParameter_macAddress(**res)

    ##
    # The named tuple returned by the dn_getNvParameter_networkId() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>networkId</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNvParameter_networkId = collections.namedtuple("Tuple_dn_getNvParameter_networkId", ['RC', 'networkId'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNvParameter_networkId named tuple.
    # 
    def dn_getNvParameter_networkId(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNvParameter', 'networkId'], {})
        return HartMoteConnector.Tuple_dn_getNvParameter_networkId(**res)

    ##
    # The named tuple returned by the dn_getNvParameter_txPower() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>txpower</tt>: 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNvParameter_txPower = collections.namedtuple("Tuple_dn_getNvParameter_txPower", ['RC', 'txpower'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNvParameter_txPower named tuple.
    # 
    def dn_getNvParameter_txPower(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNvParameter', 'txPower'], {})
        return HartMoteConnector.Tuple_dn_getNvParameter_txPower(**res)

    ##
    # The named tuple returned by the dn_getNvParameter_powerInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>powerSource</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: line
    #      - 1: battery
    #      - 2: scavenging
    # - <tt>dischargeCur</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>dischargeTime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>recoverTime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNvParameter_powerInfo = collections.namedtuple("Tuple_dn_getNvParameter_powerInfo", ['RC', 'powerSource', 'dischargeCur', 'dischargeTime', 'recoverTime'])

    ##
    # The getNVParameter<powerInfo> command returns power supply information stored in mote's persistent storage.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNvParameter_powerInfo named tuple.
    # 
    def dn_getNvParameter_powerInfo(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNvParameter', 'powerInfo'], {})
        return HartMoteConnector.Tuple_dn_getNvParameter_powerInfo(**res)

    ##
    # The named tuple returned by the dn_getNvParameter_ttl() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>timeToLive</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNvParameter_ttl = collections.namedtuple("Tuple_dn_getNvParameter_ttl", ['RC', 'timeToLive'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNvParameter_ttl named tuple.
    # 
    def dn_getNvParameter_ttl(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNvParameter', 'ttl'], {})
        return HartMoteConnector.Tuple_dn_getNvParameter_ttl(**res)

    ##
    # The named tuple returned by the dn_getNvParameter_HARTantennaGain() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>antennaGain</tt>: 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNvParameter_HARTantennaGain = collections.namedtuple("Tuple_dn_getNvParameter_HARTantennaGain", ['RC', 'antennaGain'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNvParameter_HARTantennaGain named tuple.
    # 
    def dn_getNvParameter_HARTantennaGain(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNvParameter', 'HARTantennaGain'], {})
        return HartMoteConnector.Tuple_dn_getNvParameter_HARTantennaGain(**res)

    ##
    # The named tuple returned by the dn_getNvParameter_OTAPlockout() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>otapLockout</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: allowed
    #      - 1: disabled
    # 
    Tuple_dn_getNvParameter_OTAPlockout = collections.namedtuple("Tuple_dn_getNvParameter_OTAPlockout", ['RC', 'otapLockout'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNvParameter_OTAPlockout named tuple.
    # 
    def dn_getNvParameter_OTAPlockout(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNvParameter', 'OTAPlockout'], {})
        return HartMoteConnector.Tuple_dn_getNvParameter_OTAPlockout(**res)

    ##
    # The named tuple returned by the dn_send() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_send = collections.namedtuple("Tuple_dn_send", ['RC'])

    ##
    # 
    # 
    # \param tranType 1-byte field formatted as a bool.<br/>
    #     This field can only take one of the following values:
    #      - False: bestEffort
    #      - True: Acked
    # \param tranDir 1-byte field formatted as a bool.<br/>
    #     This field can only take one of the following values:
    #      - False: request
    #      - True: response
    # \param destAddr 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # \param serviceId 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param appDomain 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: publish
    #      - 1: event
    #      - 2: maintenance
    #      - 3: blockTransfer
    # \param priority 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param reserved 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # \param seqNum 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param len 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param payload None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_send named tuple.
    # 
    def dn_send(self, tranType, tranDir, destAddr, serviceId, appDomain, priority, reserved, seqNum, len, payload) :
        res = HartMoteConnectorInternal.send(self, ['send'], {"tranType" : tranType, "tranDir" : tranDir, "destAddr" : destAddr, "serviceId" : serviceId, "appDomain" : appDomain, "priority" : priority, "reserved" : reserved, "seqNum" : seqNum, "len" : len, "payload" : payload})
        return HartMoteConnector.Tuple_dn_send(**res)

    ##
    # The named tuple returned by the dn_join() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_join = collections.namedtuple("Tuple_dn_join", ['RC'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_join named tuple.
    # 
    def dn_join(self, ) :
        res = HartMoteConnectorInternal.send(self, ['join'], {})
        return HartMoteConnector.Tuple_dn_join(**res)

    ##
    # The named tuple returned by the dn_disconnect() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_disconnect = collections.namedtuple("Tuple_dn_disconnect", ['RC'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_disconnect named tuple.
    # 
    def dn_disconnect(self, ) :
        res = HartMoteConnectorInternal.send(self, ['disconnect'], {})
        return HartMoteConnector.Tuple_dn_disconnect(**res)

    ##
    # The named tuple returned by the dn_reset() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_reset = collections.namedtuple("Tuple_dn_reset", ['RC'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_reset named tuple.
    # 
    def dn_reset(self, ) :
        res = HartMoteConnectorInternal.send(self, ['reset'], {})
        return HartMoteConnector.Tuple_dn_reset(**res)

    ##
    # The named tuple returned by the dn_lowPowerSleep() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_lowPowerSleep = collections.namedtuple("Tuple_dn_lowPowerSleep", ['RC'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_lowPowerSleep named tuple.
    # 
    def dn_lowPowerSleep(self, ) :
        res = HartMoteConnectorInternal.send(self, ['lowPowerSleep'], {})
        return HartMoteConnector.Tuple_dn_lowPowerSleep(**res)

    ##
    # The named tuple returned by the dn_hartPayload() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # - <tt>payloadLen</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>payload</tt>: None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_hartPayload = collections.namedtuple("Tuple_dn_hartPayload", ['RC', 'payloadLen', 'payload'])

    ##
    # 
    # 
    # \param payloadLen 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param payload None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_hartPayload named tuple.
    # 
    def dn_hartPayload(self, payloadLen, payload) :
        res = HartMoteConnectorInternal.send(self, ['hartPayload'], {"payloadLen" : payloadLen, "payload" : payload})
        return HartMoteConnector.Tuple_dn_hartPayload(**res)

    ##
    # The named tuple returned by the dn_testRadioTx() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_testRadioTx = collections.namedtuple("Tuple_dn_testRadioTx", ['RC'])

    ##
    # 
    # 
    # \param channel 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param numPackets 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_testRadioTx named tuple.
    # 
    def dn_testRadioTx(self, channel, numPackets) :
        res = HartMoteConnectorInternal.send(self, ['testRadioTx'], {"channel" : channel, "numPackets" : numPackets})
        return HartMoteConnector.Tuple_dn_testRadioTx(**res)

    ##
    # The named tuple returned by the dn_testRadioRx() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_testRadioRx = collections.namedtuple("Tuple_dn_testRadioRx", ['RC'])

    ##
    # 
    # 
    # \param channel 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param time 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_testRadioRx named tuple.
    # 
    def dn_testRadioRx(self, channel, time) :
        res = HartMoteConnectorInternal.send(self, ['testRadioRx'], {"channel" : channel, "time" : time})
        return HartMoteConnector.Tuple_dn_testRadioRx(**res)

    ##
    # The named tuple returned by the dn_clearNV() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_clearNV = collections.namedtuple("Tuple_dn_clearNV", ['RC'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_clearNV named tuple.
    # 
    def dn_clearNV(self, ) :
        res = HartMoteConnectorInternal.send(self, ['clearNV'], {})
        return HartMoteConnector.Tuple_dn_clearNV(**res)

    ##
    # The named tuple returned by the dn_search() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_search = collections.namedtuple("Tuple_dn_search", ['RC'])

    ##
    # 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_search named tuple.
    # 
    def dn_search(self, ) :
        res = HartMoteConnectorInternal.send(self, ['search'], {})
        return HartMoteConnector.Tuple_dn_search(**res)

    ##
    # The named tuple returned by the dn_testRadioTxExt() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_testRadioTxExt = collections.namedtuple("Tuple_dn_testRadioTxExt", ['RC'])

    ##
    # 
    # 
    # \param type 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: packet
    #      - 1: CM
    #      - 2: CW
    # \param chanMask 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param repeatCnt 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param txPower 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # \param seqSize 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen1 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay1 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen2 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay2 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen3 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay3 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen4 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay4 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen5 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay5 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen6 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay6 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen7 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay7 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen8 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay8 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen9 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay9 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen10 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay10 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_testRadioTxExt named tuple.
    # 
    def dn_testRadioTxExt(self, type, chanMask, repeatCnt, txPower, seqSize, pkLen1, delay1, pkLen2, delay2, pkLen3, delay3, pkLen4, delay4, pkLen5, delay5, pkLen6, delay6, pkLen7, delay7, pkLen8, delay8, pkLen9, delay9, pkLen10, delay10) :
        res = HartMoteConnectorInternal.send(self, ['testRadioTxExt'], {"type" : type, "chanMask" : chanMask, "repeatCnt" : repeatCnt, "txPower" : txPower, "seqSize" : seqSize, "pkLen1" : pkLen1, "delay1" : delay1, "pkLen2" : pkLen2, "delay2" : delay2, "pkLen3" : pkLen3, "delay3" : delay3, "pkLen4" : pkLen4, "delay4" : delay4, "pkLen5" : pkLen5, "delay5" : delay5, "pkLen6" : pkLen6, "delay6" : delay6, "pkLen7" : pkLen7, "delay7" : delay7, "pkLen8" : pkLen8, "delay8" : delay8, "pkLen9" : pkLen9, "delay9" : delay9, "pkLen10" : pkLen10, "delay10" : delay10})
        return HartMoteConnector.Tuple_dn_testRadioTxExt(**res)

    ##
    # The named tuple returned by the dn_testRadioRxExt() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_RESERVED1
    #      - 2: RC_RESERVED2
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INV_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    # 
    Tuple_dn_testRadioRxExt = collections.namedtuple("Tuple_dn_testRadioRxExt", ['RC'])

    ##
    # 
    # 
    # \param channelMask 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param time 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_testRadioRxExt named tuple.
    # 
    def dn_testRadioRxExt(self, channelMask, time) :
        res = HartMoteConnectorInternal.send(self, ['testRadioRxExt'], {"channelMask" : channelMask, "time" : time})
        return HartMoteConnector.Tuple_dn_testRadioRxExt(**res)

    #======================== notifications ===================================
    
    ##
    # Dictionary of all notification tuples.
    #
    notifTupleTable = {}
    
    ##
    # \brief TIMEINDICATION notification.
    # 
    # 
    #
    # Formatted as a Tuple_timeIndication named tuple. It contains the following fields:
    #   - <tt>utcSec</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>utcMicroSec</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>asn</tt> 5-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>asnOffset</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    TIMEINDICATION = "timeIndication"
    notifTupleTable[TIMEINDICATION] = Tuple_timeIndication = collections.namedtuple("Tuple_timeIndication", ['utcSec', 'utcMicroSec', 'asn', 'asnOffset'])

    ##
    # \brief SERVICEINDICATION notification.
    # 
    # 
    #
    # Formatted as a Tuple_serviceIndication named tuple. It contains the following fields:
    #   - <tt>eventCode</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>netMgrCode</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>serviceId</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>serviceState</tt> 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: inactive
    #      - 1: active
    #      - 2: requested
    #   - <tt>serviceFlags</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>appDomain</tt> 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: publish
    #      - 1: event
    #      - 2: maintenance
    #      - 3: blockTransfer
    #   - <tt>destAddr</tt> 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>time</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    SERVICEINDICATION = "serviceIndication"
    notifTupleTable[SERVICEINDICATION] = Tuple_serviceIndication = collections.namedtuple("Tuple_serviceIndication", ['eventCode', 'netMgrCode', 'serviceId', 'serviceState', 'serviceFlags', 'appDomain', 'destAddr', 'time'])

    ##
    # \brief EVENTS notification.
    # 
    # 
    #
    # Formatted as a Tuple_events named tuple. It contains the following fields:
    #   - <tt>events</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>state</tt> 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: init
    #      - 1: idle
    #      - 2: searching
    #      - 3: negotiating
    #      - 4: connected
    #      - 5: operational
    #      - 6: disconnected
    #      - 7: radioTest
    #      - 8: promiscuousListen
    #   - <tt>moteAlarms</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    EVENTS = "events"
    notifTupleTable[EVENTS] = Tuple_events = collections.namedtuple("Tuple_events", ['events', 'state', 'moteAlarms'])

    ##
    # \brief DATARECEIVED notification.
    # 
    # 
    #
    # Formatted as a Tuple_dataReceived named tuple. It contains the following fields:
    #   - <tt>srcAddr</tt> 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>seqNum</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>pktLenth</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>data</tt> None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.    
    # 
    DATARECEIVED = "dataReceived"
    notifTupleTable[DATARECEIVED] = Tuple_dataReceived = collections.namedtuple("Tuple_dataReceived", ['srcAddr', 'seqNum', 'pktLenth', 'data'])

    ##
    # \brief ADVRECEIVED notification.
    # 
    # 
    #
    # Formatted as a Tuple_advReceived named tuple. It contains the following fields:
    #   - <tt>netId</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteid</tt> 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>rssi</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>joinPri</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    ADVRECEIVED = "advReceived"
    notifTupleTable[ADVRECEIVED] = Tuple_advReceived = collections.namedtuple("Tuple_advReceived", ['netId', 'moteid', 'rssi', 'joinPri'])

    ##
    # \brief Get a notification from the notification queue, and returns
    #        it properly formatted.
    #
    # \exception NotificationError if unknown notification.
    # 
    def getNotification(self, timeoutSec=-1) :
        temp = self.getNotificationInternal(timeoutSec)
        if not temp:
            return temp
        (ids, param) = temp
        try :
            if  HartMoteConnector.notifTupleTable[ids[-1]] :
                return (ids[-1], HartMoteConnector.notifTupleTable[ids[-1]](**param))
            else :
                return (ids[-1], None)
        except KeyError :
            raise ApiException.NotificationError(ids, param)
