# -*- coding: utf-8 -*-
from webdriver import Webdriver
from requests import get
from database_model import Persona
from log import parse_log


def get_public_ip():
    return get('https://ipapi.co/ip/').text

def main():
    ip = get_public_ip()
    
    personas = Persona.select().where(Persona.source_ip == ip)
    bots = []
    
    for persona in personas:
        print(persona.name)

    for persona in personas:
        bot = Webdriver(persona)
        bot.start()
        bots.append(bot)

    # Wait all the threads to finish
    for bot in bots:
        bot.join()
        
    parse_log(personas)

    print('Program finished successfully')


if __name__ == '__main__':
    main()
