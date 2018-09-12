#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from pyvirtualdisplay import Display
import pandas as pd
from time import sleep
from requests import get
from database_model import Persona

def get_public_ip():
    return get('https://ipapi.co/ip/').text

def setup_driver():
    profile = webdriver.FirefoxProfile()
    driver = webdriver.Firefox(firefox_profile = profile)
    return driver


def driver_quit(driver):
    driver.quit()


def login_youtube(driver, name, password):
        driver.get('https://accounts.google.com/')
        driver.find_element_by_id('identifierId').send_keys(name)
        driver.find_element_by_id('identifierNext').click()
        driver.window_handles[0]
        sleep(5) # Espera a transição de formulário
        driver.find_element_by_name('password').send_keys(password)
        driver.find_element_by_id('passwordNext').click()
        sleep(5)
        logged_in_url = "https://myaccount.google.com/?pli=1"
        if(driver.current_url == logged_in_url):
            driver.get('https://youtube.com')
        else:
            print("Could not log in")
        

def subscribe(driver, name, password, channels):
    login_youtube(driver, name, password)
    
    for _, row in channels.iterrows():
        driver.get(row['channel'])
        try:
            driver.find_element_by_id("subscribe-button").click()
            print("Subscribed to {}".format(row['channel']))
        except:
            print("Couldn't find subscribe button of {}".format(row['channel']))


def main():
    display = Display(visible = False, size=(800, 600), backend='xvfb').start()
    
    ip = get_public_ip()
    personas = Persona.select().where(Persona.source_ip == ip)
    
    for persona in personas:
        if(persona.political_wing == 'right'):
            channels = pd.read_csv("personas_politics_channels/rightwing.csv")
        elif(persona.political_wing == 'left'):
            channels = pd.read_csv("personas_politics_channels/leftwing.csv")
        elif(persona.political_wing == 'center'):
            channels = pd.read_csv("personas_politics_channels/center.csv")
        else:
            print("Error! Cound not find persona alignment or channel file")
            
        driver = setup_driver()

        subscribe(driver, persona.email, persona.password, channels)
        
        driver_quit(driver)
    
    display.popen.terminate()

    
if __name__ == "__main__":
    main()