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


def get_matching_nodes(M):
    """
    Funkcija, ki vrne vozlišča maksimalne ujemanosti
    :param M: set - maksimalna ujemanost
    :return: set - vozlišča maksimalne ujemanosti
    """
    W = set()
    for (n1, n2) in M:
        W.add(n1)
        W.add(n2)
    return W


def get_separated(edge, A, all_edges):
    """
    Funkcija, ki preveri če je povezava razdvojena in poišče element antivirige, ki povzroči razdvojenost povezave
    :param edge: edge - povezava
    :param A: set - antiveriga
    :param all_edges: set povezav - povezava u -> v pomeni, da je u < v
    :return: bool - ali je povezava razdvojena; int - vozlišče antiverige
    """
    for a in A:
        if (edge[0], a) in all_edges and (a, edge[1]) in all_edges:
            return True, a
    return False, -1


def get_canonical_matching(M, A, all_edges):
    """
    Funkcija, ki vrne kanonično maksimalno ujemanje
    :param M: set - maksimalno ujemanje
    :param A: set - antiveriga
    :param all_edges: set povezav - povezava u -> v pomeni, da je u < v
    :return: set - kanonično maksimalno ujemanje
    """
    for edge in M:
        is_separated, replacement = get_separated(edge, A, all_edges)
        if is_separated:
            M.remove(edge)
            M.add(replacement, edge[1])
            A.remove(replacement)
            A.add(edge[0])
            get_canonical_matching(M, A, all_edges)
            break
    return M


def make_bipartite_triplets(M, A, all_edges):
    """
    Funkcija, ki vrne bipartitni graf za trojčke, kot je opisano v članku
    :param M: set - kanonično maskimalno ujemanje
    :param A: set - antiveriga
    :param all_edges: set povezav - povezava u -> v pomeni, da je u < v
    :return: nx.Graph() - bipartitni graf za trojčke
    """
    B = nx.Graph()
    B.add_nodes_from(A, bipartite=0)
    B.add_nodes_from(M, bipartite=1)
    for a in A:
        for m in M:
            if (a, m[0]) in all_edges or (m[0], a) in all_edges or (a, m[1]) in all_edges or (m[1], a) in all_edges:
                B.add_edge(a, m)
    return B


def get_bipartite_quartets(T, A, all_edges):
    """
    Funkcija, ki vrne bipartitni graf za četvorčke opisan v članku
    :param T: set - trojčki
    :param A: set - antiveriga
    :param all_edges: set povezav, povezava u -> v pomeni, da je u < v
    :return: nx.Graph() - bipartitni graf za četvorčke
    """
    B = nx.Graph()
    B.add_nodes_from(A, bipartite=0)
    B.add_nodes_from(T, bipartite=1)
    for a in A:
        for t in T:
            if (a, t[0]) in all_edges or (t[0], a) in all_edges:
                B.add_edge(a, t)
            else:
                if (a, t[1][0]) in all_edges or (t[1][0], a) in all_edges or (a, t[1][1]) in all_edges or (t[1][1], a) in all_edges:
                    B.add_edge(a, t)
    return B


def paper_algorithm(partial_order, triplets=True):
    """
    Algoritem z boljso casovno zahtevnostjo, predstavljen v clanku
    :param partial_order: networkx.DiGraph - vozlisca so mnozice tock, povezava u -> v pomeni, da je u < v
    :param triplets: boolean - ali algoritem ujemanje se dodatno deli na trojcke in cetvorcke
    :return: Stevilo linearnih razsiritev
    """

    linear_extensions = 1
    all_edges = set(partial_order.edges())
    n = partial_order.number_of_nodes()

    M = nx.maximal_matching(partial_order)
    # large matching or small matching
    if len(M)/n >= 1/3:
        return divide_and_conquer(partial_order)
    W = get_matching_nodes(M)
    A = set(partial_order.nodes()) - W

    # canonical maximum matching
    if triplets:
        canonical_maximum_matching = get_canonical_matching(M, A, all_edges)
        W = get_matching_nodes(canonical_maximum_matching)
        A = set(partial_order.nodes()) - W

        # triplets and quartets
        triplets_bipartite = make_bipartite_triplets(canonical_maximum_matching, A, all_edges)
        M_triplets = nx.maximal_matching(triplets_bipartite)
        for edge in M_triplets:
            A.remove(edge[0])

        quartets_bipartite = get_bipartite_quartets(M_triplets, A, all_edges)
        M_quartets = nx.maximal_matching(quartets_bipartite)
        for edge in M_quartets:
            A.remove(edge[0])

    # partition A into  A'
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
