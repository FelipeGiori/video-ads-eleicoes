# -*- coding: utf-8 -*-
import webdriver as wd
from connection_db import select_personas
from platform import node


def main():
    machine_name = node()
    #machine_name = "brazil00"

    #  Retorna uma tabela (pandas) com as personas que v�o rodar nesta m�quina #
    personas = select_personas(machine_name)
    bots = []

    for index, persona in personas.iterrows():
        bot = wd.Webdriver(persona, machine_name)
        bot.start()
        bots.append(bot)

    # Espera todas as threads terminarem
    for bot in bots:
        bot.join()

    print('Program finished successfully')


if __name__ == '__main__':
    main()
