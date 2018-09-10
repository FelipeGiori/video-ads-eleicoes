#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
import pandas as pd
from time import sleep

# Conectar ao bando de dados e pegar o alinhamento da persona
channels = pd.read_csv("personas_politics_channels/rightwing.csv")

profile = webdriver.FirefoxProfile()
driver = webdriver.Firefox(firefox_profile = profile)

# Get credentials from database
name = ''
password = ''

def login_youtube(driver):
        driver.get('https://accounts.google.com/')
        driver.find_element_by_id('identifierId').send_keys(name)
        driver.find_element_by_id('identifierNext').click()
        driver.window_handles[0]
        sleep(10) # Espera a transição de formulário
        driver.find_element_by_name('password').send_keys(password)
        driver.find_element_by_id('passwordNext').click()
        sleep(5)
        logged_in_url = "https://myaccount.google.com/?pli=1"
        if(driver.current_url == logged_in_url):
            driver.get('https://youtube.com')
            return True
        else:
            print("Could not log in")
            return False
        
login_youtube(driver)

for _, row in channels.iterrows():
    driver.get(row['channel'])
    try:
        driver.find_element_by_id("subscribe-button").click()
    except:
        print("Couldn't find subscribe button")

driver.quit()