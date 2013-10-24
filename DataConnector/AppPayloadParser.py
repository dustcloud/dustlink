#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('AppPayloadParser')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import struct

from DustLinkData import DustLinkData

from EventBus import EventBusClient

class AppPayloadParser(EventBusClient.EventBusClient):

    def __init__(self,appName):
        
        # store params
        self._appName = appName
        
        # log
        log.info('creating instance')
        
        # initialize parent class
        EventBusClient.EventBusClient.__init__(self,
            'rawAppData_{0}'.format(self._appName),
            self._parse,
        )
        self.name  = 'DataConnector_AppPayloadParser_{0}'.format(self._appName)
        
        # add stats
        
        # local variables
        self.fields = None
        
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _parse(self,sender,signal,data):
        
        # get the app's fields
        dld = DustLinkData.DustLinkData()
        with dld.dataLock:
            if (dld.getFastMode() and (not self.fields)) or (not dld.getFastMode()):
                # use caching in fast mode
                self.fields = dld.getAppFields(
                    self._appName,
                    DustLinkData.DustLinkData.APP_DIRECTION_FROMMOTE,
                )
        
        # make sure payload length is correct
        expectedNumBytes = struct.Struct(self.fields['fieldFormats']).size
        receivedNumBytes = len(data['payload'])
        if expectedNumBytes!=receivedNumBytes:
            raise ValueError('for {0} app, cannot parse payload {1} ({2} bytes) with format \"{3}\" ({4} bytes)'.format(
                    self._appName,
                    data['payload'],
                    receivedNumBytes,
                    self.fields['fieldFormats'],
                    expectedNumBytes,
                )
            )
        
        # unpack the payload
        try:
            fieldVals = struct.unpack(self.fields['fieldFormats'],''.join([chr(b) for b in data['payload']]))
        except struct.error:
            output = 'unpacking {0} as {1} impossible'
            log.error(output)
            raise ValueError(output)
        assert len(fieldVals)==len(self.fields['fieldNames'])
        
        # create output packet
        packetOut = {
            'timestamp': data['timestamp'],
            'mac':       data['mac'],
            'fields':    {},
        }
        for k,v in zip(self.fields['fieldNames'],fieldVals):
            packetOut['fields'][k] = v
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug('payload {0} unpacked as fields {1}'.format(
                    data['payload'],
                    packetOut['fields']
                )
            )
        
        # dispatch
        self._dispatch (
            signal        = 'parsedAppData_{0}'.format(self._appName),
            data          = packetOut,
        )
        