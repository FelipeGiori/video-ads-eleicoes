# -*- coding: utf-8 -*-
from webdriver import Webdriver
import peewee
from model import Persona
import sys


def main():
    #ip = sys.argv[1]
    ip = '150.164.201.77'
    
    personas = Persona.select().where(Persona.source_ip is ip)
    bots = []

    for persona in Personas:
        bot = Webdriver(persona, machine_name)
        bot.start()
        bots.append(bot)

    # Wait all the threads to finish
    for bot in bots:
        bot.join()

    print('Program finished successfully')


if __name__ == '__main__':
    main()
