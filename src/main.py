# -*- coding: utf-8 -*-
from webdriver import Webdriver
from connection_db import select_personas
from platform import node


def main():
    #machine_name = node()
    machine_name = "uk01"

    #  Returns a pandas table with the personas that will be executed #
    personas = select_personas(machine_name)
    bots = []

    for _, persona in personas.iterrows():
        bot = Webdriver(persona, machine_name)
        bot.start()
        bots.append(bot)

    # Wait all the threads to finish
    for bot in bots:
        bot.join()

    print('Program finished successfully')


if __name__ == '__main__':
    main()
