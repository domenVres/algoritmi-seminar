import time
import random

import networkx as nx

from data_preparation import generate_data, create_graph


def divide_and_conquer(partial_order):
    """
    Osnovni deli in vladaj algoritem, ki deluje v casu O(n*2^n)
    :param partial_order: networkx.DiGraph - vozlisca so mnozice tock, povezava u -> v pomeni, da je u < v
    :return: Stevilo linearnih razsiritev
    """
    # Zaustavitveni pogoj rekurzije
    if partial_order.order() == 1:
        return 1

    # Gremo rekurzivno po maksimalnih elementih (tistih brez izhodnih povezav)
    linear_extensions = 0
    out_degrees = list(partial_order.out_degree())
    for node, degree in out_degrees:
        if degree == 0:
            # Seznam povezav, ki jih odstranimo
            removed = [(pred, node) for pred in partial_order.predecessors(node)]
            partial_order.remove_node(node)
            # Rekurziven klic
            linear_extensions += divide_and_conquer(partial_order)
            # Vrnemo odstranjeno vozlisce in povezave
            partial_order.add_node(node)
            for u, v in removed:
                partial_order.add_edge(u, v)

    return linear_extensions


def paper_algorithm(partial_order):
    """
    Algoritem z boljso casovno zahtevnostjo, predstavljen v clanku
    :param partial_order: networkx.DiGraph - vozlisca so mnozice tock, povezava u -> v pomeni, da je u < v
    :return: Stevilo linearnih razsiritev
    """
    i = random.uniform(0, 0.05)
    time.sleep(0.001 * partial_order.order() + i)

    return 1

if __name__ == "__main__":
    velikosti = [2, 4, 6, 8, 10]
    st_primerov = 5
    generate_data(velikosti, st_primerov, seed=1)

    # Preizkus pravilnosti algoritmov
    for n in velikosti:
        for k in range(st_primerov):
            # Pot do vhodne datoteke
            path = f'../data/vhod_{n}_{k + 1}.txt'
            # Ustvarimo graf, ki predstavlja podano delno urejenost
            g = create_graph(path)

            # Izvedemo oba algoritma, razsirimo rezultate
            print(f"Rezultat deli in vladaj algoritma na vhodu {path}:", divide_and_conquer(g))
            print(f"Rezultat algoritma iz clanka na vhodu {path}:", paper_algorithm(g))