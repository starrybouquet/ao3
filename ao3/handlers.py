import requests
import itertools
import time

from bs4 import BeautifulSoup

from . import RestrictedWork, WorkNotFound
from .utils import SoupList


class AO3Handler(object):
    """Handler for pulling AO3 data.

    Parameters
    ----------
    sess : Session
        requests Session to use
    first_client : Work or User
        Whichever Work or User initializes this handler.

    Attributes
    ----------
    page_urls : dict
        Class attribute. List of page url skeletons.
    clients : list
        list of Works and Users using this handler
    sess : Session
        requests Session used

    """

    page_urls = {'bookmarks': "https://archiveofourown.org/users/{0}/bookmarks?page={1}",
                'history': 'https://archiveofourown.org/users/{0}/readings?page={1}',
                'tags': 'https://archiveofourown.org/tags/{0}/works?page={1}'}


    def __init__(self, init_client, sess: requests.Session = None):
        """AO3Handler(Session sess, AO3 init_client) --> AO3PublicHandler

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

    def login(self, username: str, password: str) -> str:
        """AO3Handler.authenticate(str username, str password) --> str

        Parameters
        ----------
        username : str
            User username.
        password : str
            User password (does not check if it is correct).

        Returns
        -------
        str
            String describing outcome of authentication.

        """

        req = self.sess.get('https://archiveofourown.org')
        soup = BeautifulSoup(req.text, features='html.parser')

        authenticity_token = soup.find('input', {'name': 'authenticity_token'})['value']

        req = self.sess.post('https://archiveofourown.org/users/login', params={
            'authenticity_token': authenticity_token,
            'user[login]': username,
            'user[password]': password,
        })

        # Unfortunately AO3 doesn't use HTTP status codes to communicate
        # results -- it's a 200 even if the login fails.
        if 'Please try again' in req.text:
            raise RuntimeError(
                'Error logging in to AO3; is your password correct?')
        else:
            return "Authentication successful. You are logged in."

    def get_pages(self, username: str, type: str, tag: str = '', save_while_loading: bool = False, filename_template: str = "html/{0}_html_{1}.txt", pageRange: tuple =(None,None)) -> SoupList:
        """AO3Handler.get_pages(str username, str type) --> list
        Returns list of BeautifulSoups of specified type of user pages. User must be logged in to see private bookmarks.

        Parameters
        ----------
        username : str
            User username.
        type : str
            Type of page to get. Current types:
                'bookmarks'
                'history' (see class attribute page_urls)

        Returns
        -------
        type
            Description of returned object.

        """
        api_url = self.page_urls[type]

        soups = [] # list of html soups saved
        num_soups = 0

        if pageRange[0] and pageRange[1]:
            iterator = itertools.count(start=pageRange[0], end=pageRange[1])
        elif pageRange[0]:
            iterator = itertools.count(start=pageRange[0])
        else:
            iterator = itertools.count(start=1)

        for page_no in iterator:
            print("Finding page: \t" + str(page_no) + " of {}.".format(type))
            if page_no % 100 == 0:
                print('Have read 100 pages since last sleep; pausing 5 min')
                time.sleep(300)
                print('Continuing.')

            if type == 'tags':
                url = api_url.format(tag, page_no)
            else:
                url = api_url.format(username, page_no)

            req = self.sess.get(url)
            soup = BeautifulSoup(req.text, features='html.parser')
            if save_while_loading:
                filename = filename_template.format(type, page_no)
                with open(filename, "w") as f:
                    plain_html = str(soup)
                    f.write(plain_html)
            soups.append(soup) # append to all soups saved

            # The pagination button at the end of the page is of the form
            #
            #     <li class="next" title="next"> ... </li>
            #
            # If there's another page of results, this contains an <a> tag
            # pointing to the next page.  Otherwise, it contains a <span>
            # tag with the 'disabled' class.
            try:
                print('looking for next button')
                next_button = soup.find('li', attrs={'class': 'next'})
                if next_button.find('span', attrs={'class': 'disabled'}):
                    print('disabled; breaking')
                    break
            except Exception as e:
                # In case of absence of "next"
                print('no next button')
                print('Error: {}'.format(e))
                break

        return soups

    def get_work_soup(self, work_id: str, output_type: type=BeautifulSoup):
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
        req = self.sess.get('https://archiveofourown.org/works/%s?view_adult=true' % work_id)

        if req.status_code == 404:
            raise WorkNotFound('Unable to find a work with id %r' % work_id)
        elif req.status_code != 200:
            if req.text == 'Retry later':
                pause = str(input('Received error {}. Should I pause for 5 min and then try again? Enter y for yes: '.format(req.text)))
                if pause == 'y':
                    time.sleep(300)
                    self.get_work_soup(work_id)
                else:
                    raise RuntimeError('Unexpected error from AO3 API: %r (%r)' % (
                        req.text, req.status_code))

        # For some works, AO3 throws up an interstitial page asking you to
        # confirm that you really want to see the adult works.  Yes, we do.
        if 'This work could have adult content' in req.text:
            req = self.sess.get(
                'https://archiveofourown.org/works/%s?view_adult=true' %
                work_id)

        if 'This work is only available to registered users' in req.text:
            raise RestrictedWork('Looking at work ID {} requires login'.format(work_id))

        return output_type(req.text)
