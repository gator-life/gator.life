from selenium import webdriver
import unittest


class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(10)


    def tearDown(self):
        self.browser.quit()

    def test_see_default_links_and_updates(self):

        #Kevin connects to the site
        self.browser.get('http://localhost:8080')

        #He notices the title and the tab is called "gator"
        self.assertEquals('Gator', self.browser.title)
        self.assertEquals('gator.life !', self.browser.find_element_by_name('title').text)
        #self.fail('TODO')

        #He sees a list a list of link : the ones of the site hckrnews

        #the links on hckrnews changes

        #he refreshes the page

        #he sees the page updated with the new links of hckrnews



if __name__ == '__main__':
    unittest.main()