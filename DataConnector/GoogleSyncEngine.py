#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('GoogleSyncEngine')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import re
import time
import copy
import threading
import traceback

from   pydispatch import dispatcher
import gdata.spreadsheet.service

from DustLinkData import DustLinkData

class GoogleSyncEngine(threading.Thread):
    
    def __init__(self):
        
        # store params
        
        # log
        log.info('creating instance')
        
        # initialize parent class
        threading.Thread.__init__(self)
        self.name                 = 'DataConnector_GoogleSyncEngine'
        
        # local variables
        self.goOn                           = True
        self.spreadsheetKey                 = None
        self.worksheetName                  = None
        self.googleUsername                 = None
        self.googlePassword                 = None
        self.googleClient                   = None
        self.syncLock                       = threading.Lock()
        self.syncLock.acquire()
        self.statusLock                     = threading.Lock()
        self.status                         = {}
        self.status['usernameSet']          = 'WAIT...'
        self.status['passwordSet']          = 'WAIT...'
        self.status['status']               = 'DISCONNECTED'
        self.status['numConnectionsOK']     = 0
        self.status['numConnectionsFailed'] = 0
        self.status['lastConnected']        = None
        self.status['lastDisconnected']     = None
        self.status['numPublishedOK']       = 0
        self.status['numPublishedFail']     = 0
        
        # connect to dispatcher
        dispatcher.connect(
            self.indicateNewData,
            signal = 'newDataMirrored',
            weak   = False,
        )
        dispatcher.connect(
            self.getStatus,
            signal = "googlestatus",
            weak   = False,
        )
        
        # start myself
        self.start()
    
    def run(self):
        
        try:
        
            # log
            log.info('thread started')
        
            while True:
                
                # kill thread
                if not self.goOn:
                    break
                
                # wait for syncLock to be released
                self.syncLock.acquire()
                
                # kill thread
                if not self.goOn:
                    break
                
                # sync mirror data to Google, if necessary
                self._syncToGoogle()
            
            # disconnect from dispatcher
            dispatcher.disconnect(
                self.indicateNewData,
                signal = 'newDataMirrored',
                weak   = False,
            )
            dispatcher.disconnect(
                self.getStatus,
                signal = "googlestatus",
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
    
    def getStatus(self):
        with self.statusLock:
           return copy.deepcopy(self.status)
    
    def indicateNewData(self):
        try:
            self.syncLock.release()
        except:
            pass # happens when lock already released because thread is busy
    
    def tearDown(self):
        
        # log
        log.info('tearDown() called')
        
        self.goOn = False
        try:
            self.syncLock.release()
        except:
            pass # happens when lock already released because thread is busy
    
    #======================== private =========================================
    
    def _syncToGoogle(self):
        
        now = time.time()
        dld = DustLinkData.DustLinkData()
        
        # we need to use "raw" access because dld.getPublisherSettings()
        # does not return all settings
        googleSettings = dld.get(['system','publishers','google'])
        
        # update status
        with self.statusLock:
            if googleSettings['googleUsername']:
                self.status['usernameSet']            = 'YES'
            else:
                self.status['usernameSet']            = 'NO'
            if googleSettings['googlePassword']:
                self.status['passwordSet']            = 'YES'
            else:
                self.status['passwordSet']            = 'NO'
        
        #==== manage connection to Google Spreadsheet
        
        if     (not googleSettings['spreadsheetKey']):
            # disconnect from Google Spreadsheet
            
            if self.googleClient:
                # log
                log.info('disconnecting from Google Spreadsheet')
            
                # update status
                with self.statusLock:
                    self.status['status']             = 'DISCONNECTED'
                    self.status['lastDisconnected']   = dld.timestampToStringShort(now)
            
            self.spreadsheetKey        = None
            self.worksheetName         = None
            self.googleUsername        = None
            self.googlePassword        = None
            self.googleClient          = None
            
        elif  (
                googleSettings['spreadsheetKey']!=self.spreadsheetKey or
                googleSettings['worksheetName'] !=self.worksheetName  or
                googleSettings['googleUsername']!=self.googleUsername or
                googleSettings['googlePassword']!=self.googlePassword
            ):
            # (re)connect to Google Spreadsheet
            
            try:
                self.spreadsheetKey         = googleSettings['spreadsheetKey']
                self.worksheetName          = googleSettings['worksheetName']
                self.googleUsername         = googleSettings['googleUsername']
                self.googlePassword         = googleSettings['googlePassword']
                
                self.googleClient           = self._connectToGoogle(
                    self.googleUsername,
                    self.googlePassword
                )
                
                self.worksheetId            = self._getWorksheetId(
                    self.googleClient,
                    self.spreadsheetKey,
                    self.worksheetName,
                )
                
                # log
                log.info('(re)connected to Google Spreadsheet')
                
                # update status
                with self.statusLock:
                    self.status['status']             = 'CONNECTED'
                    self.status['numConnectionsOK']  += 1
                    self.status['lastConnected']      = dld.timestampToStringShort(now)
                
            except:
                self.spreadsheetKey         = None
                self.worksheetName          = None
                self.googleUsername         = None
                self.googlePassword         = None
                self.googleClient           = None
                
                # log
                log.error('unable to connect to Google spreadsheet')
                
                # update status
                with self.statusLock:
                    self.status['status']                  = 'CONNECTION FAILED'
                    self.status['numConnectionsFailed']   += 1
        
        #==== get mirrorData
        
        if self.googleClient:
            # obtain a copy of the mirror data
            mirrorData = dispatcher.send(
                signal        = 'getMirrorData',
                data          = None,
            )
            assert len(mirrorData)==1
            mirrorData = mirrorData[0][1]
        
            # convert MAC addresses to string
            for d in mirrorData:
                d['mac'] = DustLinkData.DustLinkData.macToString(d['mac'])
        
        #==== push mirrorData to Google Spreadsheet
        
        if self.googleClient:
            try:
                self._pushData(
                    self.googleClient,
                    self.spreadsheetKey,
                    self.worksheetId,
                    mirrorData
                )
            except Exception as err:
                
                # log
                log.warning('pushing data to Google failed: (0) {1}'.format(
                       type(err),
                       err,
                    )
                )
                
                # update status
                with self.statusLock:
                    self.status['numPublishedFail']  += 1
                
                # force a reconnect next time
                self.spreadsheetKey       = None
                self.worksheetName        = None
                self.googleUsername       = None
                self.googlePassword       = None
                self.googleClient         = None
            
            else:
                # update status
                with self.statusLock:
                    self.status['numPublishedOK']    += 1
    
    def _pushData(self,googleClient,spreadsheetKey,worksheetId,mirrorData):
        
        # get data from Google Spreadsheet
        googleData = googleClient.GetListFeed(spreadsheetKey,worksheetId)
        
        # loop through the mirrorData
        for mirrorRow in mirrorData:
            
            # find row to update (if any)
            insertNewRow = True
            rowToUpdate  = None
            for e in googleData.entry:
                googleRow = self._rowToDict(e)
                
                if  (
                    googleRow['mac']==mirrorRow['mac'] and
                    googleRow['type']==mirrorRow['type']
                ):
                    insertNewRow = False
                    if googleRow!=mirrorRow:
                        rowToUpdate = e
                    break
            
            # copy 'mac' to 'source'
            mirrorRow['source'] = mirrorRow['mac']
            
            # delete all keys not in standard headers
            SPREADSHEET_ROWS = ['source','type','min','lastvalue','max','lastupdated']
            for k in mirrorRow.keys():
                if k in SPREADSHEET_ROWS:
                    mirrorRow[k] = str(mirrorRow[k])
                else:
                    del mirrorRow[k]
            
            # update or add row
            if insertNewRow:
                googleClient.InsertRow(mirrorRow, spreadsheetKey, worksheetId)
            else:
                if rowToUpdate:
                    googleClient.UpdateRow(rowToUpdate, mirrorRow)
    
    #======================== helpers =========================================
    
    @classmethod
    def _connectToGoogle(self,googleUsername,googlePassword):
        googleClient              = gdata.spreadsheet.service.SpreadsheetsService()
        googleClient.email        = googleUsername
        googleClient.password     = googlePassword
        googleClient.source       = 'MirrorEngine'
        googleClient.ProgrammaticLogin()
        
        return googleClient
    
    @classmethod
    def _getWorksheetId(self,googleClient,spreadsheetKey,worksheetName):
        worksheetId = None
        
        feed = googleClient.GetWorksheetsFeed(spreadsheetKey)
        
        for e in feed.entry:
            thisTitle = e.title.text
            thisId    = e.id.text.split('/')[-1]
            if thisTitle==worksheetName:
                worksheetId = thisId
                break
        
        return worksheetId
    
    @classmethod
    def _getWorksheetData(self,googleClient,spreadsheetKey,worksheetId):
        return [self._rowToDict(e) for e in googleClient.GetListFeed(spreadsheetKey,worksheetId).entry]
    
    @classmethod
    def _deleteAllRows(self,googleClient,spreadsheetKey,worksheetId,newData):
        
        # get data from Google Spreadsheet
        data = googleClient.GetListFeed(spreadsheetKey,worksheetId)
        
        # delete all rows
        for i in range(len(data.entry)):
            googleClient.DeleteRow(data.entry[i])
    
    #======================== helpers' helpers ================================
    
    @classmethod
    def _rowToDict(self,e):
        thisLine = {}
        thisLine['mac'] = e.title.text
        m = re.match('type: (\S+), min: (\S+), lastvalue: (\S+), max: (\S+), lastupdated: (\S+)', e.content.text)
        if m:
            thisLine['type']          = m.group(1)
            thisLine['min']           = m.group(2)
            thisLine['lastvalue']     = m.group(3)
            thisLine['max']           = m.group(4)
            thisLine['lastupdated']   = m.group(5)
        else:
            m = re.match('type: (\S+), lastvalue: (\S+), lastupdated: (\S+)', e.content.text)
            if m:
                thisLine['type']          = m.group(1)
                thisLine['min']           = None
                thisLine['lastvalue']     = m.group(2)
                thisLine['max']           = None
                thisLine['lastupdated']   = m.group(3)
            else:
                raise SystemError('misformed spreadsheet data')
        return thisLine
