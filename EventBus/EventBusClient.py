
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('EventBusClient')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

from pydispatch import dispatcher

import copy
import traceback
import threading
import Queue

class EventBusClient(threading.Thread):
    
    QUEUESIZE              = 20
    DISCONNECT_INSTRUCTION = 'disconnect'
    
    def __init__(self,signal=None,cb=None,teardown_cb=None,queuesize=QUEUESIZE):
        
        assert (cb and signal) or (not cb and not signal)
        assert callable(cb)
        
        # log
        log.info('creating instance ({0})'.format(self.__class__.__name__))
        
        # store params
        self._signal                   = signal
        self._cb                       = cb
        self._teardown_cb              = teardown_cb
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name                      = 'EventBusClient'
        
        # local variables
        self.eventQueue                = Queue.Queue(queuesize)
        self.goOn                      = True
        self.statsLock                 = threading.Lock()
        self.stats                     = {}
        self.stats['numQueuedOk']      = 0
        self.stats['numQueuedFail']    = 0
        self.stats['numIn']            = 0
        self.stats['numProcessOk']     = 0
        self.stats['numProcessFailed'] = 0
        self.stats['numOut']           = 0
        
        # connect to dispatcher
        if self._cb:
            dispatcher.connect(
                self._addToQueue,
                signal = self._signal,
                weak   = False,
            )
        dispatcher.connect(
            self.tearDown,
            signal = 'tearDown',
            weak   = False,
        )
        dispatcher.connect(
            self.getStats,
            signal = 'getStats',
            weak   = False,
        )
        
        # start myself
        self.start()
    
    def run(self):
        
        try:
        
            # log
            log.info('thread started ({0})'.format(self.__class__.__name__))
        
            while self.goOn:
            
                # get data from the queue
                newEvent = self.eventQueue.get()
                
                # stats
                self._incrementStats('numIn')
                
                if newEvent==self.DISCONNECT_INSTRUCTION:
                    
                    # log
                    log.info('disconnect received from dispatcher ({0})'.format(self.__class__.__name__))
                    
                    # disconnect from dispatcher
                    if self._cb:
                        dispatcher.disconnect(
                            self._addToQueue,
                            signal = self._signal,
                            weak   = False,
                        )
                    dispatcher.disconnect(
                        self.tearDown,
                        signal = 'tearDown',
                        weak   = False,
                    )
                    dispatcher.disconnect(
                        self.getStats,
                        signal = 'getStats',
                        weak   = False,
                    )
                    
                    # exit thread
                    return
                    
                    # kill this thread
                    return
                else:
                    # log
                    if log.isEnabledFor(logging.DEBUG):
                        log.debug(
                            "got event ({0}): {1}".format(
                                self.__class__.__name__,
                                newEvent,
                            )
                        )
                    
                    # call the callback
                    try:
                        self._cb(*newEvent)
                    except Exception as err:
                        log.error(
                            "({0}) Calling {1} failed. err={2}".format(
                                self.__class__.__name__,
                                self._cb,
                                err,
                            )
                        )
                        log.error(traceback.format_exc())
                        self._incrementStats('numProcessFailed')
                    else:
                        self._incrementStats('numProcessOk')
            
            if self._teardown_cb:
                self._teardown_cb()
            
            # log
            log.info('thread ended ({0})'.format(self.__class__.__name__))
            
        except Exception as err:
            output  = []
            output += ['===== crash in thread {0} ({1}) ====='.format(self.name,self.__class__.__name__)]
            output += ['\nerror:\n']
            output += [str(err)]
            output += ['\ncall stack:\n']
            output += [traceback.format_exc()]
            output  = '\n'.join(output)
            print output # critical error
            log.critical(output)
            raise
    
    #======================== public ==========================================
    
    def getStats(self):
        self.statsLock.acquire()
        returnVal = copy.deepcopy(self.stats)
        self.statsLock.release()
        returnVal['QueueFill'] = self.eventQueue.qsize()
        return returnVal
    
    def tearDown(self):
        # log
        log.warning('tearDown() called ({0})'.format(self.__class__.__name__))
        
        # put disconnect instruction in queue
        self.eventQueue.put(self.DISCONNECT_INSTRUCTION)
    
    #======================== private =========================================
    
    def _dispatch(self,signal=None,data=None):
    
        assert signal
        assert data
    
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug(
                '({0}) dispatching {1}: {2}'.format(
                    self.__class__.__name__,
                    signal,
                    data
                )
            )
        
        # dispatch
        dispatcher.send(
            signal        = signal,
            data          = data,
        )
        
        # stats
        self._incrementStats('numOut')
    
    def _addToQueue(self,sender,signal,data):
        try:
            self.eventQueue.put_nowait((sender,signal,data))
        except Queue.Full:
            log.error('Queue full ({0})'.format(self.__class__.__name__))
            self._incrementStats('numQueuedFail')
        else:
            if log.isEnabledFor(logging.DEBUG):
                log.debug(
                    '({0}) Queuing succesful, fill={1}'.format(
                        self.__class__.__name__,
                        self.eventQueue.qsize(),
                    )
                )
            self._incrementStats('numQueuedOk')
    
    def _incrementStats(self,statsName):
        assert(statsName in self.stats)
        self.statsLock.acquire()
        self.stats[statsName] += 1
        self.statsLock.release()