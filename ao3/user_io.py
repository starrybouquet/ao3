import requests
import itertools

from bs4 import BeautifulSoup

class AO3UserHandler():
    """Handler for User class I/O needs.

    Parameters
    ----------
    user : User() object
        User of handler.
    sess : requests.Session() object
        requests Session to use

    Attributes
    ----------
    user : User() object
        User of handler.
    page_urls : dict
        Class attribute. List of page url skeletons.
    sess : requests.Session() object
        requests Session to use for all queries

    """
    '''connects to User class; handles I/O'''

    page_urls = {'bookmarks': 'https://archiveofourown.org/users/%s/bookmarks?page=%%d',
                      'history': 'https://archiveofourown.org/users/%s/readings?page=%%d'}

    def __init__(self, user, sess=None):
        """AO3UserHandler(User user, [Session sess]) --> AO3UserHandler

        Parameters
        ----------
        user : User() object
            User of handler.
        sess : requests.Session() object
            requests Session to use.

        Returns
        -------
        AO3UserHandler
            Handler for User I/O needs.

        """

        if sess == None:
            self.sess = requests.Session()
        else:
            self.sess = sess
        self.user = user

    def authenticate(self, username, password):
        """AO3UserHandler.authenticate(str username, str password) --> str

        Parameters
        ----------
        username : str
            User username.
        password : type
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

    def get_pages(self, username, type):
        """AO3UserHandler.get_pages(str username, str type) --> list
        Returns list of BeautifulSoups of specified type of user pages. User must be logged in to see private bookmarks.

        Parameters
        ----------
        username : str
            User username.
        type : str
            Type of page to get. Current types: 'bookmarks', 'history' (see class attribute page_urls)

        Returns
        -------
        type
            Description of returned object.

        """

        api_url = (
            self.page_urls[type]
            % username)

        soups = [] # list of html soups saved
        num_soups = 0

        for page_no in itertools.count(start=1):
            print("Finding page: \t" + str(page_no) + " of bookmarks.")

            req = self.sess.get(api_url % page_no)
            soup = BeautifulSoup(req.text, features='html.parser')
            soups.append(soup) # append to all soups saved

            # The pagination button at the end of the page is of the form
            #
            #     <li class="next" title="next"> ... </li>
            #
            # If there's another page of results, this contains an <a> tag
            # pointing to the next page.  Otherwise, it contains a <span>
            # tag with the 'disabled' class.
            try:
                print("found next button")
                next_button = soup.find('li', attrs={'class': 'next'})
                if next_button.find('span', attrs={'class': 'disabled'}):
                    print("next button was disabled")
                    break
            except:
                # In case of absence of "next"
                print("no next button")
                break

        return soups
