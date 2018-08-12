# -*- coding: utf-8 -*-
from __future__ import print_function
import shutil
import os, fnmatch
import pickle
import re
import pandas as pd
import threading
import connection_db as conn
import sys
import urllib.request, json
from datetime import datetime
from time import sleep, time,mktime
from selenium import webdriver
from random import uniform
from pyvirtualdisplay import Display


class Webdriver(threading.Thread):    
    def __init__ (self, persona, machine_name):
        threading.Thread.__init__(self)
        
        # Informações referentes à persona
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
        self.display = Display(visible = False, size=(800, 600)).start()
        self.driver = Webdriver.setup_driver(self)
    
    
    def run(self):
        #topic_urls, offtopic_urls = Webdriver.get_playlist(self)
        topic_urls, offtopic_urls = Webdriver.get_playlist_random(self)
        if(Webdriver.login_youtube(self)):
            Webdriver.browse(self, topic_urls, offtopic_urls)
            Webdriver.save_cookies(self)
        Webdriver.quit(self)
        Webdriver.create_log(self)
        
        
    def utc2local(utc_time):
        epoch = mktime(utc_time.timetuple())
        offset = datetime.fromtimestamp(epoch)-datetime.utcfromtimestamp(epoch)
        return utc_time+offset


    def return_json(video_id):
        print('VIDEO ID = ' + video_id)
        json_url = 'https://www.googleapis.com/youtube/v3/videos?id='+ video_id
        json_url += '&key=AIzaSyBumLjL7RVMIu62kPlu9JU4fVppNRKzbxM&part=snippet,contentDetails,statistics,status'
        print(json_url)
        with urllib.request.urlopen(json_url) as url:
            data = json.loads(url.read().decode())
            return json.dumps(data)
    
    
    def send2db(accounts_id, time, content_id, ad_id, is_train, event_type):
        cnx = conn.connect_db()
        cursor = cnx.cursor()
        content_data = Webdriver.return_json(content_id)
        if(ad_id != ''):
            ad_data = Webdriver.return_json(ad_id)
        else:
            ad_data = '{"hello": null}'
            
        add_event = ("INSERT INTO event  "
               "(id,accounts_id,time, content_id, ad_id, is_train, event_type, content_data, ad_data) "
               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        
        data_event = ('NULL', accounts_id, time, content_id, ad_id, is_train, event_type, content_data, ad_data)
        # Inserir novo evento
        cursor.execute(add_event, data_event)
        # Ter certeza que o dado foi enviado ao banco.
        cnx.commit()
        cursor.close()
        cnx.close()


    # Inicializa o browser
    def setup_driver(self):
        profile = webdriver.FirefoxProfile()
        
        if(self.use_proxy):
            ip, port = self.proxy.split(':')
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.http", ip)
            profile.set_preference("network.proxy.http_port", int(port))
            profile.update_preferences()
        
        try:
            driver = webdriver.Firefox(firefox_profile = profile)
        except:
            print('Erro ao inicializar o Firefox. Abortando Thread...')
            sys.exit()
        
        Webdriver.start_log_capture(self, driver)
        driver.get('https://www.youtube.com/')
        Webdriver.check_folder_exists(self)
        Webdriver.load_cookies(self, driver)
        return driver
    
    
    # Inicia a captura das requisições HTTPS geradas pelo Firefox
    def start_log_capture(self, driver):
        driver.get('about:networking')
        driver.find_element_by_id('confpref').click()
        driver.find_element_by_css_selector('div.category:nth-child(7)').click()
        driver.find_element_by_id('log-file').clear()
        driver.find_element_by_id('log-file').send_keys('personas/' + self.name + '/' + 'firefox-log_' + self.name)
        driver.find_element_by_id('log-modules').clear()
        driver.find_element_by_id('log-modules').send_keys('timestamp,nsHttp:5')
        driver.find_element_by_id('start-logging-button').click()
    
    
    # Verifica se o diretório da persona existe. Se não existe, cria
    def check_folder_exists(self):
        directory = 'personas/' + self.name
        if not(os.path.isdir(directory)):
            os.makedirs(directory)
    
    
    # Verifica se existem cookies. Se existir, faz o load
    def load_cookies(self, driver):
        path_file = 'personas/' + self.name + '/' + self.name + '.pkl'
        if(os.path.isfile(path_file)):
            cookies = pickle.load(open(path_file, 'rb'))
            for cookie in cookies:
                driver.add_cookie(cookie)
    
    # Login no Google e redirecionamento para o Youtube
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
        cnx = conn.connect_db()
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
            print("Erro ao carregar lista de vídeos de " + self.name)
            Webdriver.quit(self)
    

    def get_playlist_random(self):
        cnx = conn.connect_db()
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
            playlist_topic = playlist_topic.sample(frac = 1).reset_index(drop = True)
            playlist_offtopic = playlist_offtopic.sample(frac = 1).reset_index(drop = True)
            return playlist_topic, playlist_offtopic
        except:
            print("Erro ao carregar lista de videos de " + self.name)
            Webdriver.quit(self)


    # Inicia navegação nas urls listadas
    def browse(self, topic_urls, offtopic_urls):
        # segundos * minutos * horas
        timeout = time() + 60 * 60 * self.session_time
        run = True
        i, j = 0, 0
        if(run):
            while(time() < timeout):
                if(i == len(topic_urls) or j == len(offtopic_urls)):
                    print(self.name + ' does not have more videos to watch')
                    break
                
                # Dada a probabilidade da persona, um número real entre 0 e 1 é gerado.
                # Se o número gerado for menor ou igual a probabilidade de treino da persona,
                # um vídeo da lista de treino será visto. Caso contrário, um vídeo da lista
                # de teste será visto.
                if(uniform(0, 1) <= self.p_train and i < len(topic_urls)):
                    Webdriver.watch(self, topic_urls.content_id[i], self.skip_topic, '1')
                    i += 1
                    
                elif(j < len(offtopic_urls)):
                    Webdriver.watch(self, offtopic_urls.content_id[j], self.skip_offtopic, '0')
                    j += 1
        
    
    def watch(self, video_id, skip, is_train):
        start_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
        Webdriver.send2db(self.id, start_time, video_id, '', is_train, 'STARTED WATCHING VCONTENT')
        print("{},{},{},{},{},{}".format(self.name, start_time, video_id, '', is_train, 'STARTED WATCHING VCONTENT'))
        
        video_url = "https://www.youtube.com/watch?v=" + video_id
        self.driver.get(video_url)
        
        while(Webdriver.player_status(self) is None): sleep(1) # Espera o player ...
        
        # Se houver propaganda ele pula ou a assiste até o fim dependendo do argumento
        if(Webdriver.player_status(self) == -1):
            time_start = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
            Webdriver.send2db(self.id, time_start, video_id, '', is_train, 'STARTED WATCHING AD')            
            print("{},{},{},{},{},{}".format(self.name, time_start, video_id, '', is_train, 'STARTED WATCHING AD'))
            Webdriver.watching_ad(self, skip, video_id)

        # Enquanto o streaming ainda não terminou
        if(Webdriver.player_status(self) != 0 and Webdriver.player_status(self) != 5): 
            while(Webdriver.player_status(self) != 0 and self.driver.current_url.find('watch?v=') != -1):
                sleep(1)
                try:
                    self.driver.find_element_by_css_selector('.videoAdUiSkipButton').click()
                    time_now = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    Webdriver.send2db(self.id, time_start, video_id, '', is_train, 'AD SKIPPED MID VCONTENT')
                    print("{},{},{},{},{},{}".format(self.name, time_now, video_id, '', is_train, 'AD SKIPPED MID VCONTENT'))
                except:
                    pass
        
        end_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
        Webdriver.send2db(self.id, end_time, video_id, '', is_train, 'FINISHED WATCHING VCONTENT')
        print("{},{},{},{},{},{}".format(self.name, end_time, video_id, '', is_train, 'FINISHED WATCHING VCONTENT'))
                
    
    # Retorna o estado atual do player
    def player_status(self):
        # Valores para Player Status
        #  1: Video-Content sendo executado
        #  2: Video pausado
        #  5: O vídeo não existe mais
        #  0: Video terminou de ser executado
        # -1: Video-Ad sendo executado
        try:
            status = self.driver.execute_script("return document.getElementById('movie_player').getPlayerState()")
        except :
            status = None
        
        return status
        
    
    def watching_ad(self, skip, video_id):
        if(skip): 
            Webdriver.skip_ad(self, video_id)
        else: 
            while(Webdriver.player_status(self) == -1 and self.driver.current_url.find('watch?v=')):
                sleep(1)   
            time_now = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print("{},{},{},{},{},{}".format(self.name, time_now, video_id, '', '', 'FINISHED WATCHING AD'))
            Webdriver.send2db(self.id, time_now, video_id, '', '', 'FINISHED WATCHING AD')


    def skip_ad(self, video_id):
        while(Webdriver.player_status(self) == -1):
            try:
                self.driver.find_element_by_css_selector('.videoAdUiSkipButton').click()
                time_now = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                Webdriver.send2db(self.id, time_now, video_id, '', '', 'AD SKIPPED')
                return print("{},{},{},{},{},{}".format(self.name, time_now, video_id, '', '', 'AD SKIPPED'))
            except Exception as inst:
                sleep(1)
    
            
    def save_cookies(self):
        pickle.dump(self.driver.get_cookies(), open('personas/' + self.name + '/' + self.name + '.pkl', 'wb'))
        
    
    def quit(self):
        self.driver.close()
        self.display.popen.terminate()

        
    def find_log_file(pattern, path):
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return result   
    
    
    def create_log(self):
        # Constantes
        AD_FLAG = 'video_id='
        CONTENT_FLAG = 'content_v='
        LOG_DIRECTORY = 'personas/' + self.name + "/"
        
        # Arquivos de log gerados pelo Firefox    
        logfile_child = Webdriver.find_log_file('firefox-log_' + self.name + '-child.*', LOG_DIRECTORY)
        logfile_full = Webdriver.find_log_file('firefox-log_' + self.name + '-main.*', LOG_DIRECTORY)
        
        # Caminho do arquivo de LOG usado no GREP 
        parsed_log = LOG_DIRECTORY + self.name + '.txt'
    
        # Filtra as requisicoes que contenham "ptracking e content_v"
        os.system(" grep -E ptracking " + logfile_child[0] + ' > ' + parsed_log)


        with open(parsed_log, "r") as myfile:
            line = myfile.readline()
            count = 1 
            while line:
                content_id = re.findall(CONTENT_FLAG + '[^]\n]*', line)
                content_id = next(iter(content_id or []),'')
                ad_id = re.findall(AD_FLAG + '[^&\n]*', line)
                ad_id = next(iter(ad_id or []),'')
                log_time = datetime.strptime(line[:26], '%Y-%m-%d %H:%M:%S.%f')
                log_time = Webdriver.utc2local(log_time) # convert to local date_time
                content_id = content_id.split('=', 1)[-1]
                ad_id = ad_id.split('=', 1)[-1]
                
                Webdriver.send2db(self.id, log_time, content_id, ad_id, '', '')
                print("{},{},{},{},{},{}".format(self.name, log_time, content_id, ad_id,'',''))
                    
                line = myfile.readline()
                count += 1

        #print('Removing LOG FULL ...')
        os.remove(logfile_full[0])
        
        #print('Renaming LOG Files ...')
        DATESTRING = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S') #DATA E HORA
        shutil.move(logfile_child[0], 'personas/' + self.name + '/' + self.name + DATESTRING + '-CHILD'+ '.txt')
        shutil.move(parsed_log, 'personas/'+ self.name + '/' + self.name + DATESTRING + '-PARSED'+ '.txt')