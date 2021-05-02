import time
import random
import math

import networkx as nx

from data_preparation import generate_data, create_graph


def divide_and_conquer(partial_order, memo=None):
    """
    Osnovni deli in vladaj algoritem, ki deluje v casu O(n*2^n)
    :param partial_order: networkx.DiGraph - vozlisca so mnozice tock, povezava u -> v pomeni, da je u < v
    :param memo: dictionary - memoizacija, kljuci so urejene terke, ki predstavljajo mnozico vozlisc, ki je v grafu, vrednosti so stevila linearnih razsiritev
    :return: Stevilo linearnih razsiritev
    """
    if memo is None:
        memo = {}

    # Zaustavitveni pogoj rekurzije
    if partial_order.order() == 1:
        return 1

    # Urejena terka za memoizacijo
    nodes = tuple(sorted(partial_order.nodes()))
    # Preverimo, ce imamo stevilo ze naracunano
    linear_extensions = memo.get(nodes, None)
    if linear_extensions is not None:
        return linear_extensions

    # Gremo rekurzivno po maksimalnih elementih (tistih brez izhodnih povezav)
    linear_extensions = 0
    out_degrees = list(partial_order.out_degree())
    for node, degree in out_degrees:
        if degree == 0:
            # Seznam povezav, ki jih odstranimo
            removed = [(pred, node) for pred in partial_order.predecessors(node)]
            partial_order.remove_node(node)
            # Rekurziven klic
            linear_extensions += divide_and_conquer(partial_order, memo)
            # Vrnemo odstranjeno vozlisce in povezave
            partial_order.add_node(node)
            for u, v in removed:
                partial_order.add_edge(u, v)

    # Shranimo v memoizacijo
    memo[nodes] = linear_extensions
    return linear_extensions


# def get_maximum_matching(partial_order):
#     W = set()
#     for edge in partial_order.edges():
#         W.add(edge[0])
#         W.add(edge[1])
#     return W
#
#
# def get_A(partial_order):
#     A = []
#     for (node, deg) in partial_order.degree():
#         if deg == 0:
#             A.append(node)
#     return A


def get_matching_nodes(M):
    W = set()
    for (n1, n2) in M:
        W.add(n1)
        W.add(n2)
    return W


def paper_algorithm(partial_order):
    """
    Algoritem z boljso casovno zahtevnostjo, predstavljen v clanku
    :param partial_order: networkx.DiGraph - vozlisca so mnozice tock, povezava u -> v pomeni, da je u < v
    :return: Stevilo linearnih razsiritev
    """

    linear_extensions = 1

    M = nx.maximal_matching(partial_order)
    W = get_matching_nodes(M)
    A = list(set(partial_order.nodes()) - W)

    # todo improvements

    # partition A  A'
    A_line = dict()
    for node in A:
        neighborhood = tuple(sorted(list(partial_order.predecessors(node)) + list(partial_order.successors(node))))
        if neighborhood in A_line:
            A_line[neighborhood].append(node)
        else:
            A_line[neighborhood] = [node]

    # konstrukcija P' in kalkulacija produkta |Ai|!
    for a in A_line.values():
        nx.add_path(partial_order, a)
        linear_extensions *= math.factorial(len(a))

    linear_extensions *= divide_and_conquer(partial_order)

    return linear_extensions


if __name__ == "__main__":
    velikosti = [5, 10, 15, 20, 25, 30, 35, 40]
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
            l1 = divide_and_conquer(g)
            l2 = paper_algorithm(g)
            print(f"Rezultat deli in vladaj algoritma na vhodu {path}:", l1)
            print(f"Rezultat algoritma iz clanka na vhodu {path}:", l2)
            assert (l1 == l2)
