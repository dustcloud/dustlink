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
        self.goOn                 = True
        self.connectedToGoogle    = False
        self.spreadsheetKey       = None
        self.worksheetName        = None
        self.googleUsername       = None
        self.googlePassword       = None
        self.googleClient         = None
        self.syncLock             = threading.Lock()
        self.syncLock.acquire()
        
        # connect to dispatcher
        dispatcher.connect(
            self.indicateNewData,
            signal = 'newDataMirrored',
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
        
        dld = DustLinkData.DustLinkData()
        mirrorSettings = dld.get(['system','mirror'])
        
        #==== manage connection to Google Spreadsheet
        
        if     (not mirrorSettings['spreadsheetKey']):
            # disconnect from Google Spreadsheet
            
            if self.googleClient:
                log.info('disconnecting from Google Spreadsheet')
            
            self.spreadsheetKey       = None
            self.worksheetName        = None
            self.googleUsername       = None
            self.googlePassword       = None
            self.googleClient         = None
            
        elif  (
                mirrorSettings['spreadsheetKey']!=self.spreadsheetKey or
                mirrorSettings['worksheetName'] !=self.worksheetName  or
                mirrorSettings['googleUsername']!=self.googleUsername or
                mirrorSettings['googlePassword']!=self.googlePassword
            ):
            # (re)connect to Google Spreadsheet
            
            try:
                self.spreadsheetKey            = mirrorSettings['spreadsheetKey']
                self.worksheetName             = mirrorSettings['worksheetName']
                self.googleUsername            = mirrorSettings['googleUsername']
                self.googlePassword            = mirrorSettings['googlePassword']
                
                self.googleClient              = self._connectToGoogle(
                                                    self.googleUsername,
                                                    self.googlePassword
                                                 )
                
                self.worksheetId               = self._getWorksheetId(
                                                        self.googleClient,
                                                        self.spreadsheetKey,
                                                        self.worksheetName,
                                                   )
                log.info('(re)connected to Google Spreadsheet')
            except:
                self.spreadsheetKey       = None
                self.worksheetName        = None
                self.googleUsername       = None
                self.googlePassword       = None
                self.googleClient         = None
                log.error('unable to connect to Google spreadsheet')
        
        #==== get mirrorData
        
        if self.googleClient:
            # obtain a copy of the mirror data
            mirrorData = dispatcher.send(
                    signal        = 'getMirrorData',
                    data          = None,
                )
            assert len(mirrorData)==1
            mirrorData = mirrorData[0][1]
        
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
                log.warning('pushing data to Google failed, err={0}'.format(err))
                
                # force a reconnect next time
                self.spreadsheetKey       = None
                self.worksheetName        = None
                self.googleUsername       = None
                self.googlePassword       = None
                self.googleClient         = None
    
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
                    googleRow['source']==mirrorRow['source'] and
                    googleRow['type']==mirrorRow['type']
                ):
                    insertNewRow = False
                    if googleRow!=mirrorRow:
                        rowToUpdate = e
                    break
            
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
        thisLine['source'] = e.title.text
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
