'''
Created on Nov 15, 2012

@author: mhoffmann
'''


class DustWebDoc(object):
    '''
    Documentation provider for dustWeb.
    '''


    DOC_SHORT          = '''
<div class="doc-container">
    <span class="doc-intro">
        {INTRO}
    </span>
</div>
    '''

    DOC_FULL           = '''
<div class="doc-container" id="doc-container-{IDENTIFIER}">
    <span class="doc-intro">
        {INTRO}
        <a class="doc-show-more show" onClick="DUST_WEB.showVizHelp('#doc-container-{IDENTIFIER}', true);">More</a>
    </span>
    <div class="doc-more hide">
        <a class="doc-less" onClick="DUST_WEB.showVizHelp('#doc-container-{IDENTIFIER}', false);">&times;</a>
        {MORE}
    </div>
</div>
    '''



    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def getIntro(self, path):
        return None

    def getMore(self, path):
        return None
    
    def getClass(self, path):
        return ''
    
    def getDocHTML(self, path, identifier):
        intro = self.getIntro(path)
        more = self.getMore(path)
        
        if intro:
            if more:
                return self.DOC_FULL.format(INTRO=intro, MORE=more, IDENTIFIER=identifier)
            else:
                return self.DOC_SHORT.format(INTRO=intro)
        else:
            return ""