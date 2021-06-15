from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
from bs4 import BeautifulSoup

league_name = "Championship"#"Serie A"#"Bundesliga"#"Premier League"

with open(league_name + "/season_links.txt", "r") as f:
    season_links = [l.replace("\r","").replace("\n","") for l in f.readlines() if l.startswith("http")]
    print season_links
    

br = webdriver.Chrome()
br.set_page_load_timeout(60)
br.set_script_timeout(60)

#for url in season_links:

match_ids = []
for url in season_links:   
    loaded = False
    while(loaded == False):
        try:
            br.get(url)
        except Exception as e:
            #print "ERROR: Couldn't load page, trying again..."
            time.sleep(2)
            br.quit()
            br = webdriver.Chrome()
            with open(league_name + "/debug.txt", "a+")as f:
                f.write(str(e) + "\n\n" + url + "\n\n\n")
        else:
            loaded = True
    
    time.sleep(5)
    allfound = False
    while(not allfound):
        time.sleep(2)
        htmltext = br.page_source
        try:
            prev_button = br.find_element_by_css_selector("#date-controller > a.previous.button.ui-state-default.rc-l.is-default") #('//*[@title="View previous month"]')#//*[@id="date-controller"]/a[1]
        except:
            allfound = True
        else:            
            prev_button.click()
        finally:
            for m_id in reversed(re.findall(re.compile('<a\sclass="result-1\src"\shref="/Matches/(\d+?)/Live'),htmltext)):
                match_ids.append(m_id)

for m in match_ids:
    print 'https://www.whoscored.com/Matches/' + m + '/live'

br.quit()




'''

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import unittest

class LoginTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.get('https://www.facebook.com')

    def test_Login(self):
        driver = self.driver
        facebookUsername = 'boro5@vp.pl'
        facebookPassword = ''
        emailFieldID = 'email'
        passFieldID = 'pass'
        loginButtonXpath = 'input[@value="Log In"]'
        fbLogoXpath = '(//a[contains(@href, "logo")])[1]'
        loginFieldID = 'u_0_n'

        emailFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id(emailFieldID))
        print '1'

        passFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id(passFieldID))
        print '2'
        loginButtonElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id(loginFieldID))
        print '3'
        
        emailFieldElement.clear()
        emailFieldElement.send_keys(facebookUsername)
        passFieldElement.clear()
        passFieldElement.send_keys(facebookPassword)

        loginButtonElement.click()
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(fbLogoXpath))

        def tearDown(self):
            self.driver.quit()

if __name__ == '__main__':
    unittest.main()
'''

    
