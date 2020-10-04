# -*- encoding: utf-8

import requests

from . import utils
from .users import User
from .works import Work
from .works_io import AO3PublicHandler

class AO3(object):
    """A scraper for the Archive of Our Own (AO3)."""

    def __init__(self):
        self.user = None
        self.session = requests.Session()
        self.public_handler = AO3PublicHandler(self.session, self)

    def __repr__(self):
        return '%s()' % (type(self).__name__)

    def work(self, id):
        """Look up a work that's been posted to AO3.

        :param id: the work ID.  In the URL to a work, this is the number.
            e.g. the work ID of http://archiveofourown.org/works/1234 is 1234.
        """
        return Work(id=id, io_handler=self.public_handler)

    def login(self, username, password):
        """Log in to the archive.

        This allows you to access pages that are only available while
        logged in.  This doesn't do any checking that the password is correct.

        """
        self.user = User(username=username, password=password, public_handler=self.public_handler, sess=self.session)
