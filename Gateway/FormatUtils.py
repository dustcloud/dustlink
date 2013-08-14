import datetime
import time
import urllib

LOG_FORMAT_TIMESTAMP = '%Y/%m/%d %H:%M:%S'

def formatMacString(mac):
    return '-'.join(["%.2x"%i for i in mac])

def formatShortMac(mac):
    return '-'.join(["%.2x"%i for i in mac[6:]])

def quote(string):
    return urllib.quote(urllib.quote(string, ''))

def unquote(string):
    return urllib.unquote(urllib.unquote(string))

def formatConnectionParams(connectionParams):
    if   isinstance(connectionParams,str):
        return quote(connectionParams)
    elif isinstance(connectionParams,tuple):
        return quote('{0}:{1}'.format(*connectionParams))

def formatTimestamp(timestamp=None):
    if timestamp==None:
        timestamp = time.time()
    return '{0}.{1}'.format(
        time.strftime(LOG_FORMAT_TIMESTAMP,time.localtime(timestamp)),
        int((timestamp*1000)%1000)
    )
