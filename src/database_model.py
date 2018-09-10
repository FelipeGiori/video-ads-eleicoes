# -*- coding: utf-8 -*-
from peewee import *

db = SqliteDatabase('database.db')

class BaseModel(Model):
    class Meta:
        database = db

class Persona(BaseModel):
    name = CharField(unique=True)
    location = CharField()
    email = CharField()
    password = CharField()
    birthday = DateTimeField()
    gender = CharField()
    phone = CharField(null=True)
    political_wing = CharField()
    source_ip = CharField()
    session_time = IntegerField()


class Event(BaseModel):
    persona = IntegerField(null=True)
    time = DateTimeField()
    content_id = TextField()
    ad_id = TextField(null=True)
    event_type = TextField()
    content_data = CharField(null=True)
    ad_data = CharField(null=True)
    
    
def create_db():
    try:
        persona = Persona(BaseModel)
        persona.create_table()
    except:
        print ('Tabela Persona ja existe!')
        
    try:
        event = Event(BaseModel)
        event.create_table()
    except:
        print ('Tabela Event ja existe!')