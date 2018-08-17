# -*- coding: utf-8 -*-
import pandas as pd
import mysql.connector
import sys

def connect_db():
    config = {
        'user': 'locus@video-ads',
        'password': 'JS~K=8V^y9S=3aG4',
        'host': 'video-ads.mysql.database.azure.com',
        'database': 'ad',
    }
    
    try:
        cnx = mysql.connector.connect(**config)
        return cnx
    except:
        print("Could not connect to database.")
        sys.exit()

    
def select_personas(machine_name):
    cnx = connect_db()
    try:
        machine_id = pd.read_sql("SELECT id FROM ad.machine WHERE ad.machine.machine_name = '%s'" %(machine_name), con = cnx)
        machine_id = int(machine_id.id)
        personas = pd.read_sql("SELECT * FROM ad.persona WHERE ad.persona.machine_id = '%d'" %(machine_id), con = cnx)
        cnx.close()
        return personas
    except:
        print("Machine name invalid")
        sys.exit()