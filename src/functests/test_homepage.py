from selenium import webdriver
import unittest


class NewVisitorTests(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.PhantomJS()
        self.browser.implicitly_wait(10)

    def tearDown(self):
        self.browser.quit()

    def test_see_default_links(self):

        # Kevin connects to the site
        self.browser.get('http://localhost:8080')

        # The tab is called "Gator Life !"
        self.assertEquals('Gator Life !', self.browser.title)

        # The title of the page is 'Gator.Life, the best of the web just for you !'
        tab_title = self.browser.find_element_by_name('title').text
        self.assertEquals('Gator.Life, the best of the web just for you !', tab_title)

        # There is two links on the page : google.com, gator.life
        links = self.browser.find_elements_by_name('link')
        self.assertEqual(2, len(links))
        self.assertEqual('google.com', links[0].text)
        self.assertEqual('gator.life', links[1].text)

        # kevin clicks on google.com and wait to go there
        google_link = links[0]
        google_link.click()
        self.assertEqual("Google", self.browser.title)


if __name__ == '__main__':
    unittest.main()
