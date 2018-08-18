# -*- coding: utf-8 -*-
import os
import re
import json
import shutil
import fnmatch
import urllib.request
from datetime import datetime
from time import mktime
from connection_db import connect_db

def send2db(accounts_id, time, content_id, ad_id, is_train, event_type):
        cnx = connect_db()
        cursor = cnx.cursor()

        # Get both jsons only when there's a pairing
        if(ad_id != ''):
            ad_data = return_json(ad_id)
            content_data = return_json(content_id)
        else:
            ad_data = '{"hello": null}'
            content_data = '{"hello": null}'
            
        add_event = ("INSERT INTO event  "
                    "(id,accounts_id,time, content_id, ad_id, is_train, event_type, content_data, ad_data) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        
        data_event = ('NULL', accounts_id, time, content_id, ad_id, is_train, event_type, content_data, ad_data)

        # Insert new event
        cursor.execute(add_event, data_event)

        # Check if the data has been sent
        cnx.commit()
        cursor.close()
        cnx.close()


def return_json(video_id):
        print('VIDEO ID = ' + video_id)
        json_url = 'https://www.googleapis.com/youtube/v3/videos?id='+ video_id
        json_url += '&key=AIzaSyBumLjL7RVMIu62kPlu9JU4fVppNRKzbxM&part=snippet,contentDetails,statistics,status'
        print(json_url)
        with urllib.request.urlopen(json_url) as url:
            data = json.loads(url.read().decode())
            return json.dumps(data)


def find_log_file(pattern, path):
    result = []
    for root, _, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def utc2local(utc_time):
    epoch = mktime(utc_time.timetuple())
    offset = datetime.fromtimestamp(epoch)-datetime.utcfromtimestamp(epoch)
    return utc_time + offset

def start_log_capture(self, driver):
        driver.get('about:networking')
        driver.find_element_by_id('confpref').click()
        driver.find_element_by_css_selector('div.category:nth-child(7)').click()
        driver.find_element_by_id('log-file').clear()
        driver.find_element_by_id('log-file').send_keys('/dev/stdout')
        driver.find_element_by_id('log-modules').clear()
        driver.find_element_by_id('log-modules').send_keys('nsHttp:5')
        driver.find_element_by_id('start-logging-button').click()


def create_log(_id, name):
    # Constants
    AD_FLAG = 'video_id='
    CONTENT_FLAG = 'content_v='
    LOG_DIRECTORY = 'personas/' + name + "/"
        
    # log files created by firefox   
    logfile_child = find_log_file('firefox-log_' + name + '-child.*', LOG_DIRECTORY)
    logfile_full = find_log_file('firefox-log_' + name + '-main.*', LOG_DIRECTORY)
        
    # log file path used in grep
    parsed_log = LOG_DIRECTORY + name + '.txt'
    
    # Filters the requests containing 'ptracking' and 'content_v'
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
            log_time = utc2local(log_time) # convert to local date_time
            content_id = content_id.split('=', 1)[-1]
            ad_id = ad_id.split('=', 1)[-1]
                
            send2db(_id, log_time, content_id, ad_id, '', '')
            print("{},{},{},{},{},{}".format(name, log_time, content_id, ad_id,'',''))
                    
            line = myfile.readline()
            count += 1

    #print('Removing LOG FULL ...')
    os.remove(logfile_full[0])
        
    #print('Renaming LOG Files ...')
    DATESTRING = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S') #DATA E HORA
    shutil.move(logfile_child[0], 'personas/' + name + '/' + name + DATESTRING + '-CHILD'+ '.txt')
    shutil.move(parsed_log, 'personas/'+ name + '/' + name + DATESTRING + '-PARSED'+ '.txt')