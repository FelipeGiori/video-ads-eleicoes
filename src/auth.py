from selenium import webdriver
from time import sleep
from pyvirtualdisplay import Display

def authenticate(driver, LOCATION):
    driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/form/div[2]/div/div/div/ul/li[1]/div/div[2]').click()
    sleep(5)
    driver.find_element_by_id('knowledgeLoginLocationInput').send_keys(LOCATION)
    driver.find_element_by_id('next').click()
    driver.find_element_by_xpath('/html/body/c-wiz[2]/c-wiz/div/div[1]/div/div/div/div[2]/div[3]/div/div[2]/div/content/span').click()


# Closes Firefox and virtual window
def quit(driver, display):
    driver.close()
    display.popen.terminate()


def main():
    # auth data
    LOCATION = 'Sao Paulo'
    ACCOUNT = 'juliofagundes324'
    PASSWORD = 'juliofagundes334'
    
    # webdriver setup
    display = Display(visible = False, size=(800, 600)).start()
    profile = webdriver.FirefoxProfile()
    driver = webdriver.Firefox(firefox_profile = profile)
    
    # Google login
    driver.get('https://accounts.google.com/')
    driver.find_element_by_id('identifierId').send_keys(ACCOUNT)
    driver.find_element_by_id('identifierNext').click()
    driver.window_handles[0]
    sleep(5)
    driver.find_element_by_name('password').send_keys(PASSWORD)
    driver.find_element_by_id('passwordNext').click()
    sleep(5)

    # Device auth via location
    logged_in_url = "https://myaccount.google.com/?pli=1"
    if(driver.current_url == logged_in_url):
        print("Logged in")
    else:
        try:
            print("Could not log in. Authenticating")
            driver.save_screenshot(ACCOUNT + ".png")
            authenticate(driver, LOCATION)
        except:
            print("Authentication failed")
            quit(driver, display)
    
    quit(driver, display)
    
if __name__ == '__main__':
    main()