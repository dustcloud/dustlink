#!/usr/bin/python

from pydispatch import dispatcher

from dustCli import DustCli

class DustLinkCli(DustCli.DustCli):
    
    def __init__(self,appName='Dust Link',**kwargs):
        
        # record parameters
        
        # instanciate parent class
        DustCli.DustCli.__init__(self,appName,**kwargs)
        self.name     = 'DustLinkCli'
        
        # register commands
        self.registerCommand('stats',
                             'st',
                             'display statistics from a subset of connected managers',
                             [],
                             self._handleStats)
    
    #======================== private =========================================
    
    #=== command handlers
    
    def _handleStats(self,params):
        
        allStats = dispatcher.send(
            signal       = 'getStats',
            data         = None,
        )
        
        output  = []
        for moduleStats in allStats:
            module = moduleStats[0].im_self.name
            stats  = moduleStats[1]
            
            output += [" - {0}:".format(module)]
            keys = stats.keys()
            keys.sort()
            for k in keys:
                output += ["       - {0:>20}: {1}".format(k,stats[k])]
        
        print '\n'.join(output)
        
    #======================== helpers =========================================
    