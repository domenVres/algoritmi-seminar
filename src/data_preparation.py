import numpy as np
import networkx as nx


def generate_data(set_sizes, n_sets, seed):
    """
    Funkcija, ki generira vhodne primere (delne urejenosti reda 2) in jih shrani v datoteke v mapi data. Datoteka
    vhod_n_k.txt predstavlja k-ti testni primer za mnozico velikosti n. Format vsake vhodne datoteke je sledec. Prva
    vrstica je oblike n m, kjer n predstavlja velikost mnozice X, na kateri imamo dano delno urejenost, m pa predstavlja
    stevilo primerjav znotraj delne urejenosti. Naslednjih m vrstic je oblike u v,  1 <= u, v <= n, ki predstavljajo
    urejene pare in sicer u < v.
    :param set_sizes: int list - seznam velikosti mnozic, ki jih bomo testirali
    :param n_sets: int - stevilo vhodnih primerov, ki jih generiramo za vsako mnozico
    :param seed: int - seme nakljucnega generatorja permutacij, uporabljenega za generiranje primerov
    """
    np.random.seed(seed)

    for n in set_sizes:
        for k in range(n_sets):
            # Generiramo nakljucni permutaciji
            p1 = np.random.permutation(n)
            p2 = np.random.permutation(n)
            # Potrebujemo razlicni permutaciji, sicer imamo delno urejenost reda 1
            while np.all(p1 == p2):
                p2 = np.random.permutation(n)
            # Slovarja, ki za vsako stevilo vrneta mesto v posamezni permutaciji
            inverse1 = {i: p1[i] for i in range(n)}
            inverse2 = {i: p2[i] for i in range(n)}

            # Gremo cez vse kombinacije, ce je eno stevilo manjse od drugega v obeh primerih, ju dodamo v delno urejenost
            partial_order = []
            for u in range(n):
                for v in range(n):
                    if inverse1[u] < inverse1[v] and inverse2[u] < inverse2[v]:
                        partial_order.append((u, v))

            # Izpisemo delno urejenost v datoteko
            f = open(f'../data/vhod_{n}_{k+1}.txt', 'w')
            # Prva vrstica
            f.write(f'{n} {len(partial_order)}\n')
            # Primerljivi elementi
            for u, v in partial_order:
                # Dodamo +1, da ni indeksiranja z 0
                f.write(f'{u+1} {v+1}\n')
            f.close()


def generate_with_antichain(set_sizes, n_sets, antichain_size, seed):
    """
    Funkcija, ki generira vhodne primere (delne urejenosti reda 2) in jih shrani v datoteke v mapi data. Datoteka
    vhod_n_k.txt predstavlja k-ti testni primer za mnozico velikosti n. Format vsake vhodne datoteke je sledec. Prva
    vrstica je oblike n m, kjer n predstavlja velikost mnozice X, na kateri imamo dano delno urejenost, m pa predstavlja
    stevilo primerjav znotraj delne urejenosti. Naslednjih m vrstic je oblike u v,  1 <= u, v <= n, ki predstavljajo
    urejene pare in sicer u < v.
    :param set_sizes: int list - seznam velikosti mnozic, ki jih bomo testirali
    :param n_sets: int - stevilo vhodnih primerov, ki jih generiramo za vsako mnozico
    :param seed: int - seme nakljucnega generatorja permutacij, uporabljenega za generiranje primerov
    """
    np.random.seed(seed)


def create_graph(path):
    """
    Funkcija, ki iz podane vhodne datoteke ustvari usmerjen graf, ki predstavlja delno urejenost, opisano v vhodni datoteki
    :param path: String - pot do vhodne datoteke
    :return: networkx.DiGraph - usmerjen graf, v katerem povezava u -> v pomeni, da je u < v
    """
    f = open(path, 'r')
    g = nx.DiGraph()

    # Velikost mnozice
    n = int(f.readline().split(" ")[0])

    # Dodamo vsa vozlisca v graf
    for i in range(n):
        g.add_node(i+1)

    # Gremo cez vse primerjave in dodamo povezave v graf
    for line in f:
        u, v = line.strip().split(" ")
        u, v = int(u), int(v)
        g.add_edge(u, v)

    return g
