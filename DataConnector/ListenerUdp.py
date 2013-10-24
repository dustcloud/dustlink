#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ListenerUdp')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import re
import time
import socket
import threading
import traceback

from pydispatch import dispatcher

class ListenerUdp(threading.Thread):
    
    UDP_RCVBUF_SIZE = 1024
    
    def __init__(self,port):
        
        # store params
        self.port                      = port
        
        # log
        log.info('creating instance, port={0}'.format(self.port))
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name                      = 'DataConnector_ListenerUdp_{0}'.format(self.port)
        
        # local variables
        self.goOn                                = True
        self.statsLock                           = threading.Lock()
        self.stats                               = {}
        self.stats['numIn']                      = 0
        self.stats['numOut']                     = 0
        
        # connect to dispatcher
        dispatcher.connect(
            self.tearDown,
            signal = 'tearDown',
            weak   = False,
        )
        
        # start itself
        self.start()
    
    def run(self):
        
        try:
            # log
            log.info('thread started')
            
            try:
                self.socket_handler  = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                self.socket_handler.bind(('',self.port))
            except socket.error as err:
                log.critical(err)
                raise
            
            # log
            log.debug('opened and bound socket to port {0}'.format(self.port))
            
            while True:
                try:
                    raw,conn = self.socket_handler.recvfrom(self.UDP_RCVBUF_SIZE)
                except socket.error as err:
                    log.critical("socket error: {0}".format(err))
                    self._closeSocket()
                    break
                else:
                    if not raw:
                        log.error("no data read from socket")
                        self._closeSocket()
                        break
                    if not self.goOn:
                        log.info("exiting thread")
                        self._closeSocket()
                        break
                    
                    self._incrementStats('numIn')
                    
                    try:
                        packet     = {
                            'timestamp' : time.time(),
                            'mac'       : self.ipv6ToMac(conn[0]),
                            'srcPort'   : conn[1],
                            'destPort'  : self.socket_handler.getsockname()[1],
                            'payload'   : [ord(i) for i in raw],
                        }
                    except Exception as err:
                        log.error(err)
                    
                    #log
                    if log.isEnabledFor(logging.DEBUG):
                        log.debug('received from [{0}]:{1}->:{2} {3}'.format(
                            packet['mac'],
                            packet['srcPort'],
                            packet['destPort'],
                            '[{0}]'.format(','.join(["0x%02x"%b for b in packet['payload']])),
                            )
                        )
                    
                    # dispatch
                    dispatcher.send(
                        signal        = 'notifData',
                        data          = packet,
                    )
                    
                    self._incrementStats('numOut')
            
            # disconnect from dispatcher
            dispatcher.disconnect(
                self.tearDown,
                signal = 'tearDown',
                weak   = False,
            )
            
            # log
            log.info('thread ended')
            
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
            raise
    
    #======================== public ==========================================
    
    def getStats(self):
        self.statsLock.acquire()
        returnVal = copy.deepcopy(self.stats)
        self.statsLock.release()
        return returnVal
    
    def tearDown(self):
        
        # log
        log.info('tearDown() called')
    
        # kill this thread
        self.goOn = False
        try:
            self.socket_handler.sendto( 'teardown', ('::1',self.port) )
        except AttributeError:
            # can happen if the UDP port couldn't be opened
            pass
        except socket.error:
            # can happen if socket already closed
            pass
    
    @classmethod
    def ipv6ToMac(self,ipv6String):
    
        if not re.match("^[0-9a-fA-F:]+$", ipv6String):
            raise ValueError('{0} contains invalid characters')
        
        if   ipv6String.count('::')==0:
            addressString = ipv6String.split(':')
            if len(addressString)!=8:
                raise ValueError('wrong length')
        elif ipv6String.count('::')==1:
            elems = ipv6String.split('::')
            prefix = elems[0].split(':')
            suffix = elems[1].split(':')
            while len(prefix)+len(suffix)<8:
                prefix.append('0')
            addressString = prefix+suffix
        else:
            raise ValueError('only one \"::\" accepted')
        
        for i in range(len(addressString)):
            if len(addressString[i])>4:
                raise ValueError('too many characters in {0}'.format(addressString[i]))
            while len(addressString[i])<4:
                addressString[i] = '0'+addressString[i]
        assert len(addressString)==8
        
        addressInt = []
        for b in addressString:
            addressInt.append(int(b[:2],16))
            addressInt.append(int(b[2:],16))
        assert len(addressInt)==16
        
        returnVal = addressInt[8:]
        assert len(returnVal)==8
        
        return tuple(returnVal)
    
    #======================== private =========================================
    
    def _incrementStats(self,statsName):
        assert(statsName in self.stats)
        self.statsLock.acquire()
        self.stats[statsName] += 1
        self.statsLock.release()
    
    def _closeSocket(self):
        log.info('closing socket')
        try:
            self.socket_handler.close()
        except Exception as err:
            log.warning('failed: {0}'.format(err))
    