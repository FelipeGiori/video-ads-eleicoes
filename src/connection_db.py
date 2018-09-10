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
    phone = CharField()
    source_ip = CharField()
    session_time = IntField()


def event_defaults():
    return {"hello": None}

class Event(BaseModel):
    persona = ForeignKeyField(Persona)
    time = DateTimeField()
    content_id = TextField()
    ad_id = TextField()
    event_type = TextField()
    content_data = CharField(default=event_defaults)
    ad_data = CharField(default=house_defaults)
    
    
def create_db():
    try:
        Persona.create_table()
    except peewee.OperationalError:
        print ('Tabela Persona ja existe!')
        
    try:
        Event.create_table()
    except peewee.OperationalError:
        print ('Tabela Event ja existe!')