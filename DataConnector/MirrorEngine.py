#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('MirrorEngine')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import re
import threading
import copy

from   pydispatch import dispatcher

from DustLinkData import DustLinkData
from EventBus import EventBusClient

class MirrorEngine(EventBusClient.EventBusClient):

    def __init__(self):
        
        # store params
        
        # log
        log.info('creating instance')
        
        # initialize parent class
        EventBusClient.EventBusClient.__init__(self,
            signal='parsedAppData_OAPTemperature',
            cb=self._publish,
            teardown_cb=self._cleanup,
        )
        self.name  = 'DataConnector_MirrorEngine'
        
        # connect extra applications
        dispatcher.connect(
            self._addToQueue,
            signal = 'parsedAppData_SPIPressure',
            weak   = False,
        )
        dispatcher.connect(
            self._addToQueue,
            signal = 'parsedAppData_GPIONet',
            weak   = False,
        )
        dispatcher.connect(
            self._addToQueue,
            signal = 'parsedAppData_SPIAcceleration',
            weak   = False,
        )
        
        dispatcher.connect(
            self.getMirrorData,
            signal = 'getMirrorData',
            weak   = False,
        )
        dispatcher.connect(
            self.calibrateMirrorData,
            signal = 'calibrateMirrorData',
            weak   = False,
        )
        dispatcher.connect(
            self.clearMirrorData,
            signal = 'clearMirrorData',
            weak   = False,
        )
        
        # add stats
        
        # local variables
        self.dataLock             = threading.Lock()
        self.pressureOffsets      = {}
        self.mirrordata           = []
        
    #======================== public ==========================================
    
    def getMirrorData(self,sender,signal,data):
        try:
            self.dataLock.acquire()
            returnVal = copy.deepcopy(self.mirrordata)
            return returnVal
        finally:
            self.dataLock.release()
    
    def calibrateMirrorData(self,sender,signal,data):
        
        try:
            self.dataLock.acquire()
            
            pressures = {}
            for row in self.mirrordata:
                if row['type']=='pressure':
                    pressures[row['source']] = int(row['lastvalue'].split('_')[0])
            
            if len(pressures)==2:
                macs   = pressures.keys()
                offset = pressures[macs[0]]-pressures[macs[1]]
                self.pressureOffsets = {}
                self.pressureOffsets[macs[0]] = -offset
                self.pressureOffsets[macs[1]] = 0
        finally:
            self.dataLock.release()
    
    def clearMirrorData(self,sender,signal,data):
        try:
            self.dataLock.acquire()
            self.mirrordata            = []
        finally:
            self.dataLock.release()
    
    #======================== private =========================================
    
    def _cleanup(self):
        
        # disconnect extra applications
        dispatcher.disconnect(
            self._addToQueue,
            signal = 'parsedAppData_SPIPressure',
            weak   = False,
        )
        dispatcher.disconnect(
            self._addToQueue,
            signal = 'parsedAppData_GPIONet',
            weak   = False,
        )
        dispatcher.disconnect(
            self._addToQueue,
            signal = 'parsedAppData_SPIAcceleration',
            weak   = False,
        )
        
        dispatcher.disconnect(
            self.getMirrorData,
            signal = 'getMirrorData',
            weak   = False,
        )
        dispatcher.disconnect(
            self.calibrateMirrorData,
            signal = 'calibrateMirrorData',
            weak   = False,
        )
        dispatcher.disconnect(
            self.clearMirrorData,
            signal = 'clearMirrorData',
            weak   = False,
        )
    
    def _publish(self,sender,signal,data):
        
        # format the data to publish
        newData = None
        if   signal in ['parsedAppData_OAPTemperature']:
            
            newData = {
                'source':         DustLinkData.DustLinkData.macToString(data['mac']),
                'type':           'temperature',
                'min':            str(-40),
                'lastvalue':      str(data['fields']['temperature']),
                'max':            str(85),
                'lastupdated':    str(data['timestamp']),
            }
        
        elif signal in ['parsedAppData_SPIPressure']:
            sourceStr = DustLinkData.DustLinkData.macToString(data['mac'])
            try:
                self.dataLock.acquire()
            
                if sourceStr in self.pressureOffsets:
                    offset = self.pressureOffsets[DustLinkData.DustLinkData.macToString(data['mac'])]
                else:
                    offset = 0
            finally:
                self.dataLock.release()
            
            newData = {
                'source':         sourceStr,
                'type':           'pressure',
                'min':            None,
                'lastvalue':      str(data['fields']['adcPressure']) + "_" + str(offset),
                'max':            None,
                'lastupdated':    str(data['timestamp']),
            }
            
        elif signal in ['parsedAppData_GPIONet']:
            
            # convert 'pinVal' field to meaning
            if   data['fields']['pinVal']==1:
                energysource = 'solar'
            elif data['fields']['pinVal']==2:
                energysource = 'vibration'
            elif data['fields']['pinVal']==3:
                energysource = 'temperature'
            else:
                energysource = 'battery'
            
            # format newData entry
            newData = {
                'source':         DustLinkData.DustLinkData.macToString(data['mac']),
                'type':           'energysource',
                'min':            None,
                'lastvalue':      energysource,
                'max':            None,
                'lastupdated':    str(data['timestamp']),
            }
        
        elif signal in ['parsedAppData_SPIAcceleration']:
            
            newData = {
                'source':         DustLinkData.DustLinkData.macToString(data['mac']),
                'type':           'acceleration',
                'min':            None,
                'lastvalue':      '{0}_{1}_{2}'.format(data['fields']['x'],
                                                       data['fields']['y'],
                                                       data['fields']['z']),
                'max':            None,
                'lastupdated':    str(data['timestamp']),
            }
        
        else:
            
            raise SystemError('unexpected signal={0}'.format(signal))
        
        # store local mirror of data
        with self.dataLock:
            if newData:
                found = False
                newDataSource = newData['source']
                newDataType = newData['type']
                for i,e in enumerate(self.mirrordata):
                    if e['source']==newDataSource and e['type']==newDataType:
                        found = True
                        self.mirrordata[i] = newData
                        break
                if not found:
                    self.mirrordata.append(newData)
        
        # dispatch
        if newData:
            dispatcher.send(
                signal        = 'newDataMirrored',
                data          = None,
            )
    