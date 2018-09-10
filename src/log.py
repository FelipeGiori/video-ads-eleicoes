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
import peewee
from model import Event

def send2db(accounts_id, time, content_id, ad_id, event_type):
        # Get both jsons only when there's a pairing
        if(ad_id != ''):
            ad_data = return_json(ad_id)
            content_data = return_json(content_id)
        else:
            ad_data = '{"hello": null}'
            content_data = '{"hello": null}'
         
        event = {'user_id': accounts_id,
                 'time': time,
                 'content_id': content_id,
                 'ad_id': ad_id, 
                 'event_type': event_type,
                 'content_data': content_data,
                 'ad_data': ad_data}
        
        # Insert new event
        return Event.create(event)


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