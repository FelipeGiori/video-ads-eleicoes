# -*- coding: utf-8 -*-
from webdriver import Webdriver
from requests import get
from database_model import create_db, Persona
from log import parse_log

def check_database():
    create_db()

def get_public_ip():
    return get('https://ipapi.co/ip/').text

def main():
    ip = get_public_ip()
    
    check_database()
    
    personas = Persona.select().where(Persona.source_ip == ip)
    bots = []
    
    for persona in personas:
        print(persona.name)

    for persona in personas:
        print("Creating bot")
        bot = Webdriver(persona)
        bot.start()
        bots.append(bot)
        print("Created bot")

    # Wait all the threads to finish
    for bot in bots:
        bot.join()
        
    parse_log()

    print('Program finished successfully')


if __name__ == '__main__':
    main()
