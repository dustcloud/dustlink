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

from pydispatch                                  import dispatcher

from SmartMeshSDK.protocols.DC2126AConverters    import DC2126AConverters
from EventBus                                    import EventBusClient

class MirrorEngine(EventBusClient.EventBusClient):
    
    def __init__(self):
        
        # store params
        
        # log
        log.info('creating instance')
        
        # initialize parent class
        EventBusClient.EventBusClient.__init__(self,
            signal      = 'parsedAppData_OAPTemperature',
            cb          = self._publish,
            teardown_cb = self._cleanup,
        )
        self.name       = 'DataConnector_MirrorEngine'
        
        # connect extra applications
        dispatcher.connect(
            self._addToQueue,
            signal      = 'parsedAppData_DC2126A',
            weak        = False,
        )
        dispatcher.connect(
            self._addToQueue,
            signal      = 'parsedAppData_SPIPressure',
            weak        = False,
        )
        dispatcher.connect(
            self._addToQueue,
            signal      = 'parsedAppData_GPIONet',
            weak        = False,
        )
        dispatcher.connect(
            self._addToQueue,
            signal      = 'parsedAppData_LIS331',
            weak        = False,
        )
        
        dispatcher.connect(
            self.getMirrorData,
            signal      = 'getMirrorData',
            weak        = False,
        )
        dispatcher.connect(
            self.calibrateMirrorData,
            signal      = 'calibrateMirrorData',
            weak        = False,
        )
        dispatcher.connect(
            self.clearMirrorData,
            signal      = 'clearMirrorData',
            weak        = False,
        )
        
        # add stats
        
        # local variables
        self.dataLock             = threading.Lock()
        self.pressureOffsets      = {}
        self.mirrordata           = []
        self.dc2126Aconverters    = DC2126AConverters.DC2126AConverters()
        
    #======================== public ==========================================
    
    def getMirrorData(self,sender,signal,data):
        with self.dataLock:
            return copy.deepcopy(self.mirrordata)
    
    def calibrateMirrorData(self,sender,signal,data):
        with self.dataLock:
            pressures = {}
            for row in self.mirrordata:
                if row['type']=='pressure':
                    pressures[row['mac']] = int(row['lastvalue'].split('_')[0])
            
            if len(pressures)==2:
                macs   = pressures.keys()
                offset = pressures[macs[0]]-pressures[macs[1]]
                self.pressureOffsets = {}
                self.pressureOffsets[macs[0]] = -offset
                self.pressureOffsets[macs[1]] = 0
    
    def clearMirrorData(self,sender,signal,data):
        with self.dataLock:
            self.mirrordata            = []
    
    #======================== private =========================================
    
    def _cleanup(self):
        
        # disconnect extra applications
        dispatcher.disconnect(
            self._addToQueue,
            signal      = 'parsedAppData_DC2126A',
            weak        = False,
        )
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
            signal = 'parsedAppData_LIS331',
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
        newData    = []
        
        mac        = data['mac']
        
        if   signal in ['parsedAppData_OAPTemperature']:
            
            # temperature reported in 1/100th C, displayed in C
            temperature_C = float(data['fields']['temperature'])/100.0
            
            # format newData entry
            newData += [
                {
                    'mac':             mac,
                    'type':            'temperature',
                    'lastvalue':       str(temperature_C),
                    'lastupdated':     str(data['timestamp']),
                    'subscribeToLed':  True,
                }
            ]
        
        elif signal in ['parsedAppData_DC2126A']:
            
            # publish temperature
            temperature   = self.dc2126Aconverters.convertTemperature(
                data['fields']['temperature'],
            )
            if temperature!=None:
                newData += [
                    {
                        'mac':         mac,
                        'type':        'temperature',
                        'lastvalue':   str(temperature),
                        'lastupdated': str(data['timestamp']),
                    }
                ]
            
            # publish adcValue
            adcValue      = self.dc2126Aconverters.convertAdcValue(
                data['fields']['adcValue'],
            )
            newData += [
                {
                    'mac':             mac,
                    'type':            'voltage',
                    'lastvalue':       adcValue,
                    'lastupdated':     str(data['timestamp']),
                }
            ]
            
            # publish energysource
            energysource  = self.dc2126Aconverters.convertEnergySource(
                mac,adcValue,
            )
            newData += [
                {
                    'mac':             mac,
                    'type':            'energysource',
                    'lastvalue':       energysource,
                    'lastupdated':     str(data['timestamp']),
                }
            ]
        
        elif signal in ['parsedAppData_SPIPressure']:
            
            with self.dataLock:
                if mac in self.pressureOffsets:
                    offset = self.pressureOffsets[mac]
                else:
                    offset = 0
            
            # format newData entry
            newData += [
                {
                    'mac':             mac,
                    'type':            'pressure',
                    'lastvalue':       str(data['fields']['adcPressure']) + "_" + str(offset),
                    'lastupdated':     str(data['timestamp']),
                }
            ]
        
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
            newData += [
                {
                    'mac':             mac,
                    'type':            'energysource',
                    'lastvalue':       energysource,
                    'lastupdated':     str(data['timestamp']),
                }
            ]
        
        elif signal in ['parsedAppData_LIS331']:
            
            # format newData entry
            newData += [
                {
                    'mac':             mac,
                    'type':            'acceleration',
                    'lastvalue':       '{0}_{1}_{2}'.format(
                                           data['fields']['x'],
                                           data['fields']['y'],
                                           data['fields']['z'],
                                       ),
                    'lastupdated':     str(data['timestamp']),
                }
            ]
        
        else:
            
            raise SystemError('unexpected signal={0}'.format(signal))
        
        # store local mirror of data
        with self.dataLock:
            for nd in newData:
                found             = False
                newDataSource     = nd['mac']
                newDataType       = nd['type']
                for i,e in enumerate(self.mirrordata):
                    if e['mac']==newDataSource and e['type']==newDataType:
                        found     = True
                        self.mirrordata[i] = nd
                        break
                if not found:
                    self.mirrordata.append(nd)
        
        # dispatch (once even if multiple data points)
        with self.dataLock:
            for nd in newData:
                dispatcher.send(
                    signal        = 'newDataMirrored',
                    data          = copy.deepcopy(nd),
                )
    