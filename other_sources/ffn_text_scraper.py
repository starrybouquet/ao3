import requests

from bs4 import BeautifulSoup

class FFN_Handler(object):
    pass

class FFN_Story(object):
    """story from fanfiction.net"""

    def __init__(self, story_id, handler, load=True, soup=None):
        """FFN_Story(int id, FFN_Handler handler, [bool load], [BeautifulSoup soup]) --> FFN_Story"""

        self.id = story_id
        self.handler = handler
        self._loaded = False
        if soup:
            self._soup = soup 
            self._loaded = True
        else:
            if load:
                self.load_metadata()
                self.load_text()
                self._loaded = True
            

    def load_metadata(self):
        pass 

    def load_text(self):
        pass 


        