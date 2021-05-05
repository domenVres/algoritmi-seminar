import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from tqdm.auto import trange
import os

from data_preparation import generate_data, generate_with_antichain, create_graph
from algorithms import divide_and_conquer, paper_algorithm


def measure_execution(partial_order, algorithm, repeats=100):
    """
    Funkcija, ki izmeri cas izvajanja algoritma na delni urejenosti. Funkcija algoritem izvede veckrat in vrne seznam
    posameznih casov izvajanja.
    :param partial_order: networkx.DiGraph - delna urejenost predstavljena z grafom, kot jo vrne funkcija create_graph
    :param algorithm: function - ali divide_and_conquer ali pa paper_algorithm
    :param repeats: int - stevilo meritev
    :return: (1D numpy array, result) - tabela, ki hrani cas izvajanja za vsako meritev in rezultat klica algoritma
    """
    times = np.empty(repeats)
    result = None
    for i in trange(repeats):
        # Zacnemo meriti cas
        start_time = time.time()
        # Izvedemo algoritem
        result = algorithm(partial_order)
        # Ustavimo merjenje
        end_time = time.time()

        # Pretecen cas je razlika med koncnim in zacetnim
        times[i] = end_time - start_time

    return times, result


def bootstrap_ci(x, alpha=0.95, nsamples=1000):
    """
    Funkcija, ki izracuna alpha-interval zaupanja za povprecje vektorja x s pomocjo bootstrap vzorcenja.
    :param x: 1D numpy array - podatki, katerih povprecje nas zanima
    :param alpha: float - nivo zaupanja
    :param nsamples: int - stevilo bootstrap vzorcev
    :return: (c_min, c_max) - spodnja in zgornja meja za interval zaupanja
    """
    # Velikost vzorcev
    n = len(x)

    samples = np.empty(nsamples)
    for i in range(nsamples):
        samples[i] = np.mean(np.random.choice(x, size=n))

    # Uredimo vzorce, in izracunamo indeks kvantila
    samples = np.sort(samples)
    quantile = int(np.ceil((1-alpha)*n/2))

    return samples[quantile-1], samples[-quantile]


def compare_algorithms(set_sizes, n_sets, n_antichains):
    """
    Funkcija, ki izmeri povprecen cas izvajanja obeh algoritmov na mnozicah razlicnih velikosti in izracuna interval
    zaupanja za posamezno povprecje. Funkcija na koncu izrise povprecni cas izvajanja v odvisnosti od velikosti mnozice
    za oba algoritma.
    :param set_sizes: int list - velikosti mnozic, na katerih preizkusamo delovanje algoritmov
    :param n_sets: int - stevilo razlicnih nakljucnih primerov za vsako velikost mnozice
    :param n_antichains: int - stevilo razlicnih primerov z vsiljenimi verigami za vsako velikost mnozice
    :return: None
    """
    # Povprecni casi izvajanja ter intervali zaupanja za oba algoritma
    time_divide = []
    time_paper = []
    time_paper_triplets = []
    lower_divide = []
    upper_divide = []
    lower_paper = []
    upper_paper = []
    lower_paper_triplets = []
    upper_paper_triplets = []

    # Intervali zaupanja za stevilo primerov, ko imamo large matching case
    large_matching_upper = []
    large_matching_lower = []

    # Velikosti mnozice A, ce imamo large matching case shranimo kar 0
    A_size = []
    A_size_triplets = []
    A_size_upper = []
    A_size_lower = []
    A_size_upper_triplets = []
    A_size_lower_triplets = []

    print("Pricenjam evalvacijo algoritmov ...")

    for n in set_sizes:
        # Casi izvajanja pri tem n za vse tri algoritme
        results_divide = np.array([])
        results_paper = np.array([])
        results_paper_triplets = np.array([])

        # Ali smo sli v large matching case
        large_matching = []

        # Velikost mnozice A
        A_sizes = []
        A_sizes_triplets = []

        # wrapper za poganjanje algoritma iz clanka brez trojckov in cetvorckov
        def without_triplets(graph):
            return paper_algorithm(graph, triplets=False)

        # Evalviramo na nakljucnih primerih
        for k in range(n_sets):
            # Pot do vhodne datoteke
            path = f'../data/vhod_{n}_{k+1}.txt'
            # Ustvarimo graf, ki predstavlja podano delno urejenost
            g = create_graph(path)

            # Izvedemo vse tri algoritme, razsirimo rezultate
            print(f"Evalvacija osnovnega deli in vladaj algoritma za n = {n} in k = {k+1} ...")
            results_divide = np.concatenate((results_divide, measure_execution(g, divide_and_conquer)[0]))
            print(f"Evalvacija algoritma iz clanka za n = {n} in k = {k+1} ...")
            times, results = measure_execution(g, without_triplets)
            results_paper = np.concatenate((results_paper, times))
            large_matching.append(results[1])
            A_sizes.append(results[2])
            print(f"Evalvacija algoritma iz clanka s trojcki in cetvorcki za n = {n} in k = {k+1} ...")
            times, results = measure_execution(g, paper_algorithm)
            results_paper_triplets = np.concatenate((results_paper_triplets, times))
            A_sizes_triplets.append(results[2])

        # Evalviramo na primerih z vsiljenimi antiverigami
        for k in range(n_antichains):
            # Pot do vhodne datoteke
            path = f'../data/vhod_antichain_{n}_{k + 1}.txt'
            # Ustvarimo graf, ki predstavlja podano delno urejenost
            g = create_graph(path)

            # Izvedemo vse tri algoritme, razsirimo rezultate
            print(f"Evalvacija osnovnega deli in vladaj algoritma na vsiljenih antiverigah za n = {n} in k = {k + 1} ...")
            results_divide = np.concatenate((results_divide, measure_execution(g, divide_and_conquer)[0]))
            print(f"Evalvacija algoritma iz clanka na vsiljenih antiverigah za n = {n} in k = {k + 1} ...")
            times, results = measure_execution(g, without_triplets)
            results_paper = np.concatenate((results_paper, times))
            large_matching.append(results[1])
            A_sizes.append(results[2])
            print(f"Evalvacija algoritma iz clanka s trojcki in cetvorcki na vsiljenih antiverigah za n = {n} in k = {k + 1} ...")
            times, results = measure_execution(g, paper_algorithm)
            results_paper_triplets = np.concatenate((results_paper_triplets, times))
            A_sizes_triplets.append(results[2])

        # Spremenimo v arraye za lazje racunanje
        large_matching = np.array(large_matching)
        A_sizes = np.array(A_sizes)
        A_sizes_triplets = np.array(A_sizes_triplets)

        # Izracunamo povprecje in interval zaupanja za vse tri algoritme pri tem n in dodamo k rezultatom
        time_divide.append(np.mean(results_divide))
        lower, upper = bootstrap_ci(results_divide)
        lower_divide.append(lower)
        upper_divide.append(upper)
        time_paper.append(np.mean(results_paper))
        lower, upper = bootstrap_ci(results_paper)
        lower_paper.append(lower)
        upper_paper.append(upper)
        time_paper_triplets.append(np.mean(results_paper_triplets))
        lower, upper = bootstrap_ci(results_paper_triplets)
        lower_paper_triplets.append(lower)
        upper_paper_triplets.append(upper)

        # Izracunamo intervale zaupanja za odstotek primerov, ko gremo v large matching case
        lower, upper = bootstrap_ci(large_matching, nsamples=100)
        large_matching_lower.append(100*np.round(lower, 4))
        large_matching_upper.append(100*np.round(upper, 4))

        # Povprecna velikost A in interval zaupanja
        A_size.append(np.mean(A_sizes))
        lower, upper = bootstrap_ci(A_sizes, nsamples=100)
        A_size_lower.append(lower)
        A_size_upper.append(upper)
        A_size_triplets.append(np.mean(A_sizes_triplets))
        lower, upper = bootstrap_ci(A_sizes_triplets, nsamples=100)
        A_size_lower_triplets.append(lower)
        A_size_upper_triplets.append(upper)

    # Graficna primerjava casov izvajanja
    plt.figure(figsize=(16, 9))
    plt.plot(set_sizes, time_divide, color="red", marker="o", label="Povprečen čas deli in vladaj")
    plt.plot(set_sizes, lower_divide, color="red", linestyle="--", linewidth=0.5, label="Interval zaupanja deli in vladaj")
    plt.plot(set_sizes, upper_divide, color="red", linestyle="--", linewidth=0.5)
    plt.plot(set_sizes, time_paper, color="blue", marker="o", label="Povprečen čas članek brez trojčkov")
    plt.plot(set_sizes, lower_paper, color="blue", linestyle="--", linewidth=0.5, label="Interval zaupanja članek brez trojčkov")
    plt.plot(set_sizes, upper_paper, color="blue", linestyle="--", linewidth=0.5)
    plt.plot(set_sizes, time_paper_triplets, color="green", marker="o", label="Povprečen čas članek s trojčki")
    plt.plot(set_sizes, lower_paper_triplets, color="green", linestyle="--", linewidth=0.5, label="Interval zaupanja članek s trojčki")
    plt.plot(set_sizes, upper_paper_triplets, color="green", linestyle="--", linewidth=0.5)
    plt.xlabel("n")
    plt.ylabel("čas [s]")
    plt.legend(fontsize=14)
    plt.title("Primerjava povprečnega časa izvajanja v odvisnosti od velikosti vhoda za osnoven deli in vladaj algoritem in algoritem predlagan v članku")

    # Shranimo graf
    if not os.path.exists('../results'):
        os.makedirs('../results')
    # Shranimo v razlicne datoteke, ce imamo vsiljene antiverige ali pa ce jih nimamo
    if n_antichains == 0:
        plt.savefig('../results/time_comparison.png')
    else:
        plt.savefig('../results/time_comparison_antichains.png')

    # Shranimo intervale zaupanja za odstotek primerov, ko gremo v large matching v .csv datoteko
    df = pd.DataFrame(data={"n": set_sizes, "ci_min": large_matching_lower, "ci_max": large_matching_upper})
    if n_antichains == 0:
        df.to_csv('../results/large_matching.csv', index=False)
    else:
        df.to_csv('../results/large_matching_antichains.csv', index=False)

    # Graficna primerjava velikosti mnozice A
    plt.figure(figsize=(16, 9))
    plt.plot(set_sizes, A_size, color="blue", marker="o", label="Povprečna velikost brez trojčkov")
    plt.plot(set_sizes, A_size_lower, color="blue", linestyle="--", linewidth=0.5,
             label="Interval zaupanja brez trojčkov")
    plt.plot(set_sizes, A_size_upper, color="blue", linestyle="--", linewidth=0.5)
    plt.plot(set_sizes, A_size_triplets, color="green", marker="o", label="Povprečna velikost s trojčki")
    plt.plot(set_sizes, A_size_lower_triplets, color="green", linestyle="--", linewidth=0.5,
             label="Interval zaupanja s trojčki")
    plt.plot(set_sizes, A_size_upper_triplets, color="green", linestyle="--", linewidth=0.5)
    plt.xlabel("n")
    plt.ylabel("Velikost A")
    plt.legend(fontsize=14)
    plt.title(
        "Primerjava povprečne velikosti množice A v odvisnosti od velikosti vhoda za algoritem predlagan v članku brez in z delitvijo točk v trojčke in četvorčke")

    # Shranimo v razlicne datoteke, ce imamo vsiljene antiverige ali pa ce jih nimamo
    if n_antichains == 0:
        plt.savefig('../results/A_size_comparison.png')
    else:
        plt.savefig('../results/A_size_comparison_antichains.png')


if __name__ == "__main__":
    # Velikosti mnozic, ki jih bomo testirali
    VELIKOSTI_MNOZIC = [5, 10, 15, 20, 25, 30, 35, 40, 45]
    # Stevilo testnih primerov za vsako velikost mnozice
    STEVILO_PRIMEROV = 5
    # Velikosti mnozic, ki jih bomo testirali pri dodanih primerih z vsiljenimi antiverigami
    VELIKOSTI_MNOZIC_ANTIVERIGE = [5, 10, 15, 20, 25]
    # Stevilo testnih primerov z vsiljenimi antiverigami za vsako velikost mnozice
    STEVILO_ANTIVERIG = 10
    # Velikosti vsiljenih antiverig
    VELIKOSTI_ANTIVERIG = 5*[1/3] + 5*[1/2]

    # Ustvarimo mnozice
    generate_data(VELIKOSTI_MNOZIC, STEVILO_PRIMEROV, seed=42)

    # Izvedemo eksperiment brez vsiljenih antiverig
    compare_algorithms(VELIKOSTI_MNOZIC, STEVILO_PRIMEROV, 0)

    # Ustvarimo mnozice z antiverigami
    generate_with_antichain(VELIKOSTI_MNOZIC_ANTIVERIGE, STEVILO_ANTIVERIG, VELIKOSTI_ANTIVERIG, seed=7)

    # Izvedemo eksperiment z vsiljenimi antiverigami
    compare_algorithms(VELIKOSTI_MNOZIC_ANTIVERIGE, STEVILO_PRIMEROV, STEVILO_ANTIVERIG)
