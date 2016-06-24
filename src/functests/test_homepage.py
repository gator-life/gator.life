import time
import unittest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from server import frontendstructs as structs, passwordhelpers as passwordhelpers
from server.dal import Dal, REF_FEATURE_SET
from common.datehelper import utcnow
import daltesthelpers


class NewVisitorTests(unittest.TestCase):

    def get_webpage(self):
        for i in range(5):
            try:
                print "try " + str(i)
                self.browser.get('http://localhost:8080')
                break
            except:  # pylint: disable=bare-except
                pass
        else:
            raise TimeoutException

    @classmethod
    def setUpClass(cls):
        print "TRACE TEST setUpClass()"
        daltesthelpers.init_features_dummy(REF_FEATURE_SET)
        print "TRACE TEST setUpClass() end"

    def setUp(self):
        print "TRACE TEST setUp() start"
        self.browser = webdriver.PhantomJS()
        self.browser.implicitly_wait(3)
        self.browser.set_page_load_timeout(60)
        print "TRACE TEST setUp() start self.dal = Dal()"
        self.dal = Dal()
        print "TRACE TEST setUp() end self.dal = Dal()"

    def tearDown(self):
        print "TRACE TEST tearDown() start"
        self.browser.quit()
        print "TRACE TEST tearDown() end"

    def _login(self, email, password):
        print "TRACE TEST _login() start"
        login_input_elt = self.browser.find_element_by_name('email')
        login_input_elt.send_keys(email)
        password_input_elt = self.browser.find_element_by_name('password')
        password_input_elt.send_keys(password)
        login_button = self.browser.find_element_by_name('login-button')
        login_button.click()
        print "TRACE TEST _login() end"

    def _register(self, email, password, interests):
        print "TRACE TEST _register start"
        login_input_elt = self.browser.find_element_by_name('email')
        login_input_elt.send_keys(email)
        password_input_elt = self.browser.find_element_by_name('password')
        password_input_elt.send_keys(password)
        interests_input_elt = self.browser.find_element_by_name('interests')
        interests_input_elt.send_keys(interests)
        register_button = self.browser.find_element_by_name('register-button')
        register_button.click()
        print "TRACE TEST _register end"

    def test_login_with_unknown_email(self):
        print "TRACE TEST test_login_with_unknown_email start"
        self.get_webpage()
        print "TRACE TEST test_login_with_unknown_email browser.get"
        self._login('unknown@email.com', 'unknownpassword')
        print "TRACE TEST test_login_with_unknown_email _login"
        error_message = self.browser.find_element_by_name('error-message').text
        print "TRACE TEST test_login_with_unknown_email error_message"
        self.assertEquals('Unknown email or invalid password', error_message)

    def test_login_with_invalid_password(self):
        print "TRACE TEST test_login_with_invalid_password start"
        daltesthelpers.create_user_dummy('known_user@gator.com', '', [''])
        print "TRACE TEST test_login_with_invalid_password create_user"
        self.get_webpage()
        print "TRACE TEST test_login_with_invalid_password get"
        self._login('known_user@gator.com', 'invalid_password')
        print "TRACE TEST test_login_with_invalid_password _login"
        error_message = self.browser.find_element_by_name('error-message').text
        self.assertEquals('Unknown email or invalid password', error_message)

    def test_register(self):
        print "TRACE TEST test_register start"
        self.get_webpage()
        print "TRACE TEST test_register get"
        register_link = self.browser.find_element_by_link_text('Register')
        print "TRACE TEST test_register register_link"
        register_link.click()
        print "TRACE TEST test_register register_link click"

        # An unique email is generated at each run to avoid a failure of the test if it's launched twice on
        # the same instance of GAE (it's launching twice on Travis).
        email = 'register_' + str(int(time.time())) + '@gator.com'

        interests_str = 'finance\npython\ncomputer science'
        self._register(email, 'password', interests_str)

        user = self.dal.get_user(email)
        self.assertIsNotNone(user)
        self.assertItemsEqual(user.interests, interests_str.splitlines())
        self.assertItemsEqual(user.interests, interests_str.splitlines())

        # If the user as been successfully registered, it should be redirected to "Login" page
        self.assertEqual('http://localhost:8080/login', self.browser.current_url)

    def test_register_with_a_known_email(self):
        daltesthelpers.create_user_dummy('test_register_with_a_known_email@gator.com', '', [''])

        self.get_webpage()

        register_link = self.browser.find_element_by_link_text('Register')
        register_link.click()

        self._register('test_register_with_a_known_email@gator.com', 'password', 'interests')

        error_message = self.browser.find_element_by_name('error-message').text
        self.assertEquals('This account already exists', error_message)

    def test_login_and_do_actions(self):
        print "TRACE TEST test_login_and_do_actions 1"
        now = utcnow()
        print "TRACE TEST test_login_and_do_actions 2"
        email = 'kevin@gator.com'
        password = 'kevintheboss'

        user = daltesthelpers.create_user_dummy(email, passwordhelpers.hash_password(password),
                                                interests=['lol', 'xpdr', 'trop lol'])
        print "TRACE TEST test_login_and_do_actions 3"

        self.get_webpage()
        print "TRACE TEST test_login_and_do_actions 4"

        self._login(email, password)
        print "TRACE TEST test_login_and_do_actions 5"

        self.assertEquals('Gator Life !', self.browser.title)
        print "TRACE TEST test_login_and_do_actions 6"

        title = self.browser.find_element_by_name('title').text
        print "TRACE TEST test_login_and_do_actions 7"
        subtitle = self.browser.find_element_by_name('subtitle').text

        self.assertEquals('Gator.Life', title)
        self.assertEquals('The best of the web just for you ' + email + ' !', subtitle)

        disconnect_link = self.browser.find_elements_by_link_text('Disconnect')
        self.assertEquals(1, len(disconnect_link))

        # There is two links on the page and related up/down links : google.com, gator.life
        links = self.browser.find_elements_by_name('link')
        print "TRACE TEST test_login_and_do_actions 11"
        self.assertEqual(2, len(links))
        self.assertEqual('google.com', links[0].text)
        self.assertEqual('gator.life', links[1].text)

        # Click on up for first link & down for the second link
        up_vote_links = self.browser.find_elements_by_name('up-vote')
        print "TRACE TEST test_login_and_do_actions 12"
        self.assertEqual(2, len(up_vote_links))
        up_link = up_vote_links[0]
        up_link.click()

        down_vote_links = self.browser.find_elements_by_name('down-vote')

        self.assertEqual(2, len(down_vote_links))
        down_link = down_vote_links[1]
        down_link.click()

        # Click on google.com and wait to go there, if it worked, 'google' is the tab title
        # Note that an object referencing an element of the webpage (eg. a link) is not valid when a click is done,
        # T hus we need to retrieve links to click on google.
        links = self.browser.find_elements_by_name('link')

        google_link = links[0]
        google_link.click()
        self.assertEqual("Google", self.browser.title)

        actions_by_user = self.dal.get_user_actions_on_docs([user], now)

        actions = actions_by_user[0]
        self.assertEqual(3, len(actions))

        actions_as_tuples = [(action.document.url, action.action_type) for action in actions]

        self.assertTrue(('https://www.google.com', structs.UserActionTypeOnDoc.up_vote) in actions_as_tuples)
        self.assertTrue(('gator.life', structs.UserActionTypeOnDoc.down_vote) in actions_as_tuples)
        self.assertTrue(('https://www.google.com', structs.UserActionTypeOnDoc.click_link) in actions_as_tuples)


if __name__ == '__main__':
    unittest.main()
