#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import database_model as dbm
import subprocess
import sqlite3

columns = ['id', 'persona', 'time', 'content_id', 'ad_id', 'event_type',
       'content_data', 'ad_data']

data = pd.DataFrame(columns=columns)

docker_id = [("d6f18b0f8e45bebf19f2de53c469cebc429d2f013b896ba3b1f474e9bd43b271", "pb01"),
             ("3a7bb8ba7918c766debf1571924f8eb056938606dfb8cd63d05505b7a761772f", "pb02"),
             ("3ee141a9362caaaaf0ebaedc2ba3734e2f11fdf385ad8bea1da59aa8e5c59a67", "mg01"),
             ("825c4b38ff7c96db7686846cd172ec2a2b566960c7d3627e38ecd2330d0de2ce", "mg02")]

PATH = "/home/locus/Documentos/databases/"

for did, name in docker_id:
    cmd = "docker cp " + did + ":/database " + PATH + name + "/"
    subprocess.check_output(cmd, shell=True)
    cnx = sqlite3.connect(PATH + name + "/database/database.db")
    tmp = pd.read_sql_query("SELECT * FROM Event", cnx)
    data = data.append(tmp)
    
data.to_csv("merged_data.csv", index=False)