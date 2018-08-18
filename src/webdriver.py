# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import re
import sys
import pickle
import pandas as pd
import threading
from datetime import datetime
from time import sleep, time
from selenium import webdriver
from random import uniform
from pyvirtualdisplay import Display
from connection_db import connect_db
from log import send2db, create_log


TRAIN = 1
TEST = 0


class Webdriver(threading.Thread):    
    def __init__ (self, persona, machine_name):
        threading.Thread.__init__(self)
        
        # Persona info setup
        self.id = persona['id']
        self.machine_id = persona['machine_id']
        self.name = persona['name']
        self.password = str(persona['password'])
        self.age = persona['age']
        self.gender = persona['gender']
        self.p_train = persona['p_train']
        self.skip_topic = persona['skip_topic']
        self.skip_offtopic = persona['skip_offtopic']
        self.use_proxy = persona['use_proxy']
        self.session_time = persona['session_time'] # em horas
        self.theme = persona['theme']
        self.machine_name = machine_name
        self.display = Display(visible = True, size=(800, 600),backend = 'xvfb').start()
        self.driver = self.setup_driver()
    
    
    def run(self):
        #topic_urls, offtopic_urls = self.get_playlist(self)
        topic_urls, offtopic_urls = self.get_playlist_random()
        self.login_youtube()
        self.browse(topic_urls, offtopic_urls)
        self.save_cookies()
        self.quit()
        #create_log(self.id, self.name)


    # Browser init
    def setup_driver(self):
        profile = webdriver.FirefoxProfile()
        
        if(self.use_proxy):
            proxy = ""
            ip, port = proxy.split(':')
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.http", ip)
            profile.set_preference("network.proxy.http_port", int(port))
            profile.update_preferences()
        
        try:
            driver = webdriver.Firefox(firefox_profile = profile)
        except:
            print('Erro ao inicializar o Firefox. Abortando Thread...')
            sys.exit()
        
        driver.get('https://www.youtube.com/')
        self.check_folder_exists()
        self.load_cookies(driver)
        return driver    
    
    # Check if the necessary folders exist
    def check_folder_exists(self):
        directory = "personas/"
        if not(os.path.isdir(directory)):
            os.makedirs(directory)

        directory = "personas/" + self.name
        if not(os.path.isdir(directory)):
            os.makedirs(directory)
    
    
    def load_cookies(self, driver):
        path_file = 'personas/' + self.name + '/' + self.name + '.pkl'
        if(os.path.isfile(path_file)):
            cookies = pickle.load(open(path_file, 'rb'))
            for cookie in cookies:
                driver.add_cookie(cookie)
    

    def login_youtube(self):
        self.driver.get('https://accounts.google.com/')
        self.driver.find_element_by_id('identifierId').send_keys(self.name)
        self.driver.find_element_by_id('identifierNext').click()
        self.driver.window_handles[0]
        sleep(10) # Espera a transição de formulário
        self.driver.find_element_by_name('password').send_keys(self.password)
        self.driver.find_element_by_id('passwordNext').click()
        sleep(5)
        logged_in_url = "https://myaccount.google.com/?pli=1"
        if(self.driver.current_url == logged_in_url):
            self.driver.get('https://youtube.com')
            return True
        else:
            print("Could not log in")
            return False
    
        
    def get_playlist(self):
        cnx = connect_db()
        country = ''.join(filter(str.isalpha, self.machine_name))
        
        try:
            playlist_topic = pd.read_sql("SELECT content_id "
                                         "FROM ad.playlist "
                                         "WHERE ad.playlist.country = '%s' AND ad.playlist.content_id NOT IN"
                                         "(SELECT content_id "
                                         "FROM ad.event "
                                         "WHERE ad.event.accounts_id = %d);" %(country, self.id), con = cnx)
            
            playlist_offtopic = pd.read_sql("SELECT content_id "
                                            "FROM ad.playlist "
                                            "WHERE ad.playlist.country = 'all' AND ad.playlist.content_id NOT IN"
                                            "(SELECT content_id "
                                            "FROM ad.event "
                                            "WHERE ad.event.accounts_id = %d);" %(self.id), con = cnx)
            cnx.close()
            return playlist_topic, playlist_offtopic
        except:
            print("Erro loading playlist: " + self.name)
            self.quit()
    

    def get_playlist_random(self):
        cnx = connect_db()
        country = ''.join(filter(str.isalpha, self.machine_name))

        try:
            playlist_topic = pd.read_sql(
                "SELECT content_id "
                "FROM ad.playlist "
                "WHERE ad.playlist.country = '%s';" %(country), con = cnx)

            playlist_offtopic = pd.read_sql(
                "SELECT content_id "
                "FROM ad.playlist "
                "WHERE ad.playlist.country = 'all';", con = cnx)
            
            cnx.close()

            # Shuffles the playlists
            playlist_topic = playlist_topic.sample(frac = 1).reset_index(drop = True)
            playlist_offtopic = playlist_offtopic.sample(frac = 1).reset_index(drop = True)
            return playlist_topic, playlist_offtopic
        except:
            print("Erro loading playlist: " + self.name)
            self.quit()


    # Only works if the user is logged in
    def get_subscribed_playlist(self):
        self.driver.get('https://www.youtube.com/feed/subscriptions')
        html_source = self.driver.page_source
        
        # TODO: It is possible that the page can be loaded in portuguese. Check language before parsing
        try:
            a = re.compile('{"simpleText":"Today"}(.*){"simpleText":"Yesterday"}')
            today_html = a.search(html_source)

            b = re.compile('{"videoId":"(.+?)"')
            playlist = b.findall(today_html.group(1))

            playlist = list(set(playlist))
        except:
            print("Could not build playlist")
            self.quit()

        return playlist


    # Start youtube browsing
    def browse(self, topic_urls, offtopic_urls):

        # seconds * minutes * hours
        timeout = time() + 60 * 60 * self.session_time
        i, j = 0, 0

        while(time() < timeout):
            if(i == len(topic_urls) or j == len(offtopic_urls)):
                print(self.name + ' does not have more videos to watch')
                break
                
            # Dada a probabilidade da persona, um número real entre 0 e 1 é gerado.
            # Se o número gerado for menor ou igual a probabilidade de treino da persona,
            # um vídeo da lista de treino será visto. Caso contrário, um vídeo da lista
            # de teste será visto.
            if(uniform(0, 1) <= self.p_train and i < len(topic_urls)):
                self.watch(topic_urls.content_id[i], self.skip_topic, TRAIN)
                i += 1
                    
            elif(j < len(offtopic_urls)):
                self.watch(offtopic_urls.content_id[j], self.skip_offtopic, TEST)
                j += 1
        
    
    def watch(self, video_id, skip, is_train):
        start_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
        #send2db(self.id, start_time, video_id, '', is_train, 'STARTED WATCHING VCONTENT')
        print("{},{},{},{},{},{}".format(self.name, start_time, video_id, '', is_train, 'STARTED WATCHING VCONTENT'))
        
        video_url = "https://www.youtube.com/watch?v=" + video_id
        self.driver.get(video_url)
        
        while(self.player_status() is None): sleep(1) # Waiting for the video player...
        
        # If skip is True, Skips the video-ad
        # If skip is False, watch the whole video-ad
        if(self.player_status() == -1):
            time_start = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
            #send2db(self.id, time_start, video_id, '', is_train, 'STARTED WATCHING AD')            
            print("{},{},{},{},{},{}".format(self.name, time_start, video_id, '', is_train, 'STARTED WATCHING AD'))
            self.watching_ad(skip, video_id)

        # Check if the video streaming has finished
        if(self.player_status() != 0 and self.player_status() != 5): 
            while(self.player_status() != 0 and self.driver.current_url.find('watch?v=') != -1):
                sleep(1)
                try:
                    self.driver.find_element_by_css_selector('.videoAdUiSkipButton').click()
                    time_now = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    #send2db(self.id, time_start, video_id, '', is_train, 'AD SKIPPED MID VCONTENT')
                    print("{},{},{},{},{},{}".format(self.name, time_now, video_id, '', is_train, 'AD SKIPPED MID VCONTENT'))
                except:
                    pass
        
        end_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
        #send2db(self.id, end_time, video_id, '', is_train, 'FINISHED WATCHING VCONTENT')
        print("{},{},{},{},{},{}".format(self.name, end_time, video_id, '', is_train, 'FINISHED WATCHING VCONTENT'))
                
    
    # Returns the video player current state
    def player_status(self):

        # Video player state code
        #  1: Video-Content being streamed
        #  2: Video paused
        #  5: Video has been removed
        #  0: Video streaming finished
        # -1: Video-Ad being streamed

        try:
            status = self.driver.execute_script("return document.getElementById('movie_player').getPlayerState()")
        except :
            status = None
        
        return status
        
    
    def watching_ad(self, skip, video_id):
        if(skip): 
            self.skip_ad(video_id)
        else: 
            while(self.player_status() == -1 and self.driver.current_url.find('watch?v=')):
                sleep(1)   
            time_now = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            #send2db(self.id, time_now, video_id, '', '', 'FINISHED WATCHING AD')
            print("{},{},{},{},{},{}".format(self.name, time_now, video_id, '', '', 'FINISHED WATCHING AD'))


    def skip_ad(self, video_id):
        while(self.player_status() == -1):
            try:
                self.driver.find_element_by_css_selector('.videoAdUiSkipButton').click()
                time_now = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                #send2db(self.id, time_now, video_id, '', '', 'AD SKIPPED')
                return print("{},{},{},{},{},{}".format(self.name, time_now, video_id, '', '', 'AD SKIPPED'))
            except Exception as _:
                sleep(1)
    
            
    def save_cookies(self):
        pickle.dump(self.driver.get_cookies(), open('personas/' + self.name + '/' + self.name + '.pkl', 'wb'))
        
    
    def quit(self):
        self.driver.close()
        self.display.popen.terminate()