#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('PersistenceEngine')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import time
import threading
import traceback

class PersistenceEngine(threading.Thread):
    
    DEFAULT_SAVEDDATALOCATION     = None
    DEFAULT_SAVE_PERIOD           = 60 # in seconds
    PERIOD_WAKEUP                 =  1 # in seconds
    
    def __init__(self,getDataCb):
        
        # store params
        self.getDataCb            = getDataCb
        
        # local variables
        self.varLock              = threading.RLock()
        self.savePeriod           = self.DEFAULT_SAVE_PERIOD
        self.savedDataLocation    = self.DEFAULT_SAVEDDATALOCATION
        self.runningPeriod        = 0
        self.goOn                 = True
        self.closingSem           = threading.Lock()
        self.closingSem.acquire()
        
        # intialize parent class
        threading.Thread.__init__(self)
        self.name                 = "PersistenceEngine"
        
    def run(self):
        
        # log
        log.info('thread started')
        
        try:
            
            # run in loop until time to stop
            while self._getGoOn():
                
                time.sleep(self.PERIOD_WAKEUP)
                with self.varLock:
                    self.runningPeriod += self.PERIOD_WAKEUP
                    
                    if self.runningPeriod >= self.getSavePeriod():
                        self._performSaveRoutine()
                        self.runningPeriod = 0
            
            # time to stop, save one last time
            self._performSaveRoutine()
            
            # release closingSem
            self.closingSem.release()
            
        except Exception as err:
            output  = []
            output += ['===== crash in thread {0} ====='.format(self.name)]
            output += ['\nerror:\n']
            output += [str(err)]
            output += ['\ncall stack:\n']
            output += [traceback.format_exc()]
            output  = '\n'.join(output)
            print output # critical error
            log.critical(output)
            
            # release closingSem
            self.closingSem.release()
            
            raise
        
        finally:        
            # log
            log.info('thread ended')
    
    #======================== public ==========================================
    
    def setSavePeriod(self,newSavePeriod):
        assert type(newSavePeriod)==int
        self.varLock.acquire()
        self.savePeriod = newSavePeriod
        self.varLock.release()
    
    def getSavePeriod(self):
        self.varLock.acquire()
        returnVal = self.savePeriod
        self.varLock.release()
        return returnVal
    
    def setSavedDataLocation(self,newSavedDataLocation):
        self.varLock.acquire()
        self.savedDataLocation = newSavedDataLocation
        self.varLock.release()
    
    def getSavedDataLocation(self):
        self.varLock.acquire()
        returnVal = self.savedDataLocation
        self.varLock.release()
        return returnVal
    
    def stop(self):
        log.info("stop called")
        self._setGoOn(False)
        self.closingSem.acquire()
        log.info("stopped")
        
    def indicateChange(self):
        '''
        Some important data has been changed and data should be saved soon.
        '''
        
        with self.varLock:
            self.runningPeriod = self.getSavePeriod()
        
    #======================== virtual methods =================================
    
    def retrieveData(self):
        raise NotImplementedError()    # to be implemented by child class
    
    def saveData(self,dataToSave):
        raise NotImplementedError()    # to be implemented by child class
    
    def quarantineData(self):
        raise NotImplementedError()    # to be implemented by child class
    
    #======================== private =========================================
    
    def _performSaveRoutine(self):
    
        # get a copy of the data to save
        dataToSave = self.getDataCb()
        
        # save the data
        self.saveData(dataToSave)
        
    def _getGoOn(self):
        self.varLock.acquire()
        returnVal = self.goOn
        self.varLock.release()
        return returnVal
    
    def _setGoOn(self,newGoOn):
        assert newGoOn in [True,False]
        self.varLock.acquire()
        self.goOn = newGoOn
        self.varLock.release()