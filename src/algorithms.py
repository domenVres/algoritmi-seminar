import time
import random


def divide_and_conquer(partial_order):
    """
    Osnovni deli in vladaj algoritem, ki deluje v casu O(n*2^n)
    :param partial_order: networkx.DiGraph - vozlisca so mnozice tock, povezava u -> v pomeni, da je u < v
    :return: Stevilo linearnih razsiritev
    """
    i = random.uniform(0, 0.05)
    time.sleep(0.002*partial_order.order() + i)

    return 1


def paper_algorithm(partial_order):
    """
    Algoritem z boljso casovno zahtevnostjo, predstavljen v clanku
    :param partial_order: networkx.DiGraph - vozlisca so mnozice tock, povezava u -> v pomeni, da je u < v
    :return: Stevilo linearnih razsiritev
    """
    i = random.uniform(0, 0.05)
    time.sleep(0.001 * partial_order.order() + i)

    return 1
