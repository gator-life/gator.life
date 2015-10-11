from selenium import webdriver
import unittest


class NewVisitorTests(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.PhantomJS()
        self.browser.implicitly_wait(5)

    def tearDown(self):
        self.browser.quit()

    def test_in_homepage_should_see_default_links(self):

        self.test_login_kevin_should_go_to_homepage()

        # There is two links on the page : google.com, gator.life
        links = self.browser.find_elements_by_name('link')
        self.assertEqual(2, len(links))
        self.assertEqual('google.com', links[0].text)
        self.assertEqual('gator.life', links[1].text)

        # kevin clicks on google.com and wait to go there
        google_link = links[0]
        google_link.click()
        self.assertEqual("Google", self.browser.title)


    def test_save_features(self):

        self.test_login_kevin_should_go_to_homepage()

        # we want to become a Forex trader, he set 0.99 in trading category and save
        trading_input_elt = self.browser.find_element_by_name('trading')
        trading_input_elt.clear()
        trading_input_elt.send_keys('0.99')
        save_features_button = self.browser.find_element_by_name('save_features_button')
        save_features_button.click()

        trading_input_elt_after_save = self.browser.find_element_by_name('trading')
        result_trading_feature_value = trading_input_elt_after_save.get_attribute('value')
        self.assertEquals('0.99', result_trading_feature_value)


    def test_login_kevin_should_go_to_homepage(self):
        # Kevin connects to the site
        self.browser.get('http://localhost:8080')
        # The tab is called "Gator Life !"
        self.assertEquals('Gator Life !', self.browser.title)
        # he see a textbox to enter its email, then click
        login_input_elt = self.browser.find_element_by_name('email')
        login_input_elt.send_keys('kevin@gator.com')
        login_button = self.browser.find_element_by_name('login_button')
        login_button.click()

        # The title of the page is 'Gator.Life, the best of the web just for you !'
        tab_title = self.browser.find_element_by_name('title').text
        self.assertEquals('Gator.Life, the best of the web just for you kevin@gator.com!', tab_title)


if __name__ == '__main__':
    unittest.main()
