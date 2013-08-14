import threading
import time

from web.session import Store

def synchronized(method):
    """ Work with instance method only !!! """

    def new_method(self, *arg, **kws):
        with self.lock:
            return method(self, *arg, **kws)
    return new_method

class _Item(object):
    def __init__(self, data):
        self.data = data
        self.time = time.time()


class MemSessionStore(Store):
    """Memory session store"""
    
    def __init__(self):
        self.sessions = {}
        self.lock = threading.Lock()

    @synchronized
    def __contains__(self, key):
        return self.sessions.has_key(key)

    @synchronized
    def __getitem__(self, key):
        value = self.sessions.get(key)
        if value:
            return value.data
        return value

    @synchronized
    def __setitem__(self, key, value):
        self.sessions[key] = _Item(value)

    @synchronized
    def __delitem__(self, key):
        if self.sessions.has_key(key):
            del self.sessions[key]

    @synchronized
    def cleanup(self, timeout):
        """removes all the expired sessions"""
        tRange = time.time() - timeout
        sessions = self.sessions
        for key in sessions.keys():
            if sessions[key].time <= tRange:
                del sessions[key]

    def getData(self):
        return [v.data for v in self.sessions.values()]
        

    def encode(self, session_dict):
        """encodes session dict as a string"""
        return session_dict

    def decode(self, session_data):
        """decodes the data to get back the session dict """
        return session_data
