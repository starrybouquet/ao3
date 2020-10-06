import requests
from bs4 import BeautifulSoup

class WorkNotFound(Exception):
    pass


class RestrictedWork(Exception):
    pass

class AO3PublicHandler():
    """Handler for pulling public AO3 data.

    Parameters
    ----------
    sess : Session
        requests Session to use
    first_client : Work or User
        Whichever Work or User initializes this handler.

    Attributes
    ----------
    clients : list
        list of Works and Users using this handler
    sess : Session
        requests Session used

    """

    def __init__(self, sess, init_client):
        """AO3PublicHandler(Session sess, AO3 init_client) --> AO3PublicHandler

        Parameters
        ----------
        sess : Session
            Session to use.
        init_client : AO3 object
            Parent AO3 instance.
        """

        if sess == None:
            self.sess = requests.Session()
        else:
            self.sess = sess

        self.init_client = init_client

    def get_work_soup(self, work_id):
        """Get the BeautifulSoup of a given work.

        Parameters
        ----------
        work_id : str or int
            AO3 ID of work.

        Returns
        -------
        BeautifulSoup object
            Soup of work.

        """
        req = self.sess.get('https://archiveofourown.org/works/%s' % work_id)

        if req.status_code == 404:
            raise WorkNotFound('Unable to find a work with id %r' % work_id)
        elif req.status_code != 200:
            raise RuntimeError('Unexpected error from AO3 API: %r (%r)' % (
                req.text, req.status_code))

        # For some works, AO3 throws up an interstitial page asking you to
        # confirm that you really want to see the adult works.  Yes, we do.
        if 'This work could have adult content' in req.text:
            req = self.sess.get(
                'https://archiveofourown.org/works/%s?view_adult=true' %
                work_id)

        # Check for restricted works, which require you to be logged in
        # first.  See https://archiveofourown.org/admin_posts/138
        # To make this work, we'd need to have a common Session object
        # across all the API classes.  Not impossible, but fiddlier than I
        # care to implement right now.
        # TODO: Fix this.
        if 'This work is only available to registered users' in req.text:
            raise RestrictedWork('Looking at work ID {} requires login'.format(work_id))

        return req.text
