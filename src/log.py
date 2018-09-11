# -*- coding: utf-8 -*-
import os
import re
import json
import urllib.request
import subprocess
from datetime import datetime
from time import mktime
from database_model import Event

def send2db(accounts_id, time, content_id, ad_id, event_type):
        # Get both jsons only when there's a pairing
        if(ad_id != ''):
            ad_data = return_json(ad_id)
            content_data = return_json(content_id)
        else:
            ad_data = '{"hello": null}'
            content_data = '{"hello": null}'
        
        print("{},{},{},{},{}".format(accounts_id, time, content_id, ad_id, event_type))
        
        # Insert new event 
        response = Event.insert({
                Event.persona: accounts_id,
                Event.time: time,
                Event.content_id: content_id,
                Event.ad_id: ad_id,
                Event.event_type: event_type,
                Event.content_data: content_data,
                Event.ad_data: ad_data}).execute()


def return_json(video_id):
        print('VIDEO ID = ' + video_id)
        json_url = 'https://www.googleapis.com/youtube/v3/videos?id='+ video_id
        json_url += '&key=AIzaSyBumLjL7RVMIu62kPlu9JU4fVppNRKzbxM&part=snippet,contentDetails,statistics,status'
        print(json_url)
        with urllib.request.urlopen(json_url) as url:
            data = json.loads(url.read().decode())
            return json.dumps(data)


def utc2local(utc_time):
    epoch = mktime(utc_time.timetuple())
    offset = datetime.fromtimestamp(epoch)-datetime.utcfromtimestamp(epoch)
    return utc_time + offset


def parse_log():
    cmd = "grep -E ptracking ../geckodriver.log | grep content_v > ../tmp.log"
    subprocess.check_output(cmd, shell=True)
    
    pairs = pd.DataFrame(columns=['time', 'content_id', 'ad_id'])
    request = open("../tmp.log", "r")
    
    # HTTPS request pair info parsing
    time_re = re.compile('(.+?)\.')
    ad_re = re.compile('&video_id=(.+?)&cpn')
    content_re = re.compile('&content_v=(...........)')
    
    # Search for flag content and append data to dataframe
    for line in request:
        req_time = time_re.search(line)
        ad_id = ad_re.search(line)
        content_id = content_re.search(line)
        pairs = pairs.append({'time': req_time.group(1), 
                              'content_id': content_id.group(1), 
                              'ad_id': ad_id.group(1)}, ignore_index=True)
        
    # Drop duplicate values because of many requests
    pairs = pairs.drop_duplicates()
    pairs.reset_index(inplace=True, drop=True)
    print(pairs)
    
    # Delete files
    os.remove("../tmp.log")
    os.remove("../geckodriver.log")