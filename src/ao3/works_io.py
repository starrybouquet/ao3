import requests

class AO3PublicHandler():
    '''Handler for pulling public AO3 data.'''

    def __init__(self, sess, first_client):

        if sess == None:
            self.sess = requests.Session()
        else:
            self.sess = sess

        self.clients = [first_client]

    def __eq__(self, other):
        return (self.sess == other.sess)

    def add_client(self, new_client):
        self.clients.append(new_client)

        return self.clients

    def get_work_soup(self, work_id):
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
            raise RestrictedWork('Looking at work ID %s requires login')

        return req.text

class AO3PrivateHandler(AO3PublicHandler):
    '''Handler for accessing AO3 data only available to users (primarily restricted works)'''
    pass

    # See below comment from AO3PublicHandler.__init__() about this

    # Check for restricted works, which require you to be logged in
    # first.  See https://archiveofourown.org/admin_posts/138
    # To make this work, we'd need to have a common Session object
    # across all the API classes.  Not impossible, but fiddlier than I
    # care to implement right now.
    # TODO: Fix this.
