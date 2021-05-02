import numpy as np
import matplotlib.pyplot as plt
import time
from tqdm import trange
import os

from data_preparation import generate_data, create_graph
from algorithms import divide_and_conquer, paper_algorithm


def measure_execution(partial_order, algorithm, repeats=100):
    """
    Funkcija, ki izmeri cas izvajanja algoritma na delni urejenosti. Funkcija algoritem izvede veckrat in vrne seznam
    posameznih casov izvajanja.
    :param partial_order: networkx.DiGraph - delna urejenost predstavljena z grafom, kot jo vrne funkcija create_graph
    :param algorithm: function - ali divide_and_conquer ali pa paper_algorithm
    :param repeats: int - stevilo meritev
    :return: 1D numpy array - tabela, ki hrani cas izvajanja za vsako meritev
    """
    times = np.empty(repeats)
    for i in trange(repeats):
        # Zacnemo meriti cas
        start_time = time.time()
        # Izvedemo algoritem
        algorithm(partial_order)
        # Ustavimo merjenje
        end_time = time.time()

        # Pretecen cas je razlika med koncnim in zacetnim
        times[i] = end_time - start_time

    return times


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


def compare_algorithms(set_sizes, n_sets):
    """
    Funkcija, ki izmeri povprecen cas izvajanja obeh algoritmov na mnozicah razlicnih velikosti in izracuna interval
    zaupanja za posamezno povprecje. Funkcija na koncu izrise povprecni cas izvajanja v odvisnosti od velikosti mnozice
    za oba algoritma.
    :param set_sizes: int list - velikosti mnozic, na katerih preizkusamo delovanje algoritmov
    :param n_sets: int - stevilo razlicnih primerov za vsako velikost mnozice
    :return: None
    """
    # Povprecni casi izvajanja ter intervali zaupanja za oba algoritma
    time_divide = []
    time_paper = []
    lower_divide = []
    upper_divide = []
    lower_paper = []
    upper_paper = []

    print("Pricenjam evalvacijo algoritmov ...")

    for n in set_sizes:
        # Casi izvajanja pri tem n za oba algoritma
        results_divide = np.array([])
        results_paper = np.array([])

        for k in range(n_sets):
            # Pot do vhodne datoteke
            path = f'../data/vhod_{n}_{k+1}.txt'
            # Ustvarimo graf, ki predstavlja podano delno urejenost
            g = create_graph(path)

            # Izvedemo oba algoritma, razsirimo rezultate
            print(f"Evalvacija osnovnega deli in vladaj algoritma za n = {n} in k = {k+1} ...")
            results_divide = np.concatenate((results_divide, measure_execution(g, divide_and_conquer)))
            print(f"Evalvacija algoritma iz clanka za n = {n} in k = {k+1} ...")
            results_paper = np.concatenate((results_paper, measure_execution(g, paper_algorithm)))

        # Izracunamo povprecje in interval zaupanja za oba algoritma pri tem n in dodamo k rezultatom
        time_divide.append(np.mean(results_divide))
        lower, upper = bootstrap_ci(results_divide)
        lower_divide.append(lower)
        upper_divide.append(upper)
        time_paper.append(np.mean(results_paper))
        lower, upper = bootstrap_ci(results_paper)
        lower_paper.append(lower)
        upper_paper.append(upper)

    # Graficna primerjava casov izvajanja
    plt.figure(figsize=(16, 9))
    plt.plot(set_sizes, time_divide, color="red", marker="o", label="Povprečen čas deli in vladaj")
    plt.plot(set_sizes, lower_divide, color="red", marker="o", linestyle="--", label="Interval zaupanja deli in vladaj")
    plt.plot(set_sizes, upper_divide, color="red", marker="o", linestyle="--")
    plt.plot(set_sizes, time_paper, color="green", marker="o", label="Povprečen čas članek")
    plt.plot(set_sizes, lower_paper, color="green", marker="o", linestyle="--", label="Interval zaupanja članek")
    plt.plot(set_sizes, upper_paper, color="green", marker="o", linestyle="--")
    plt.xlabel("n")
    plt.ylabel("čas [s]")
    plt.legend(fontsize=14)
    plt.title("Primerjava povprečnega časa izvajanja v odvisnosti od velikosti vhoda za osnoven deli in vladaj algoritem in algoritem predlagan v članku")

    # Shranimo graf
    if not os.path.exists('../results'):
        os.makedirs('../results')
    plt.savefig('../results/time_comparison.png')


if __name__ == "__main__":
    # Velikosti mnozic, ki jih bomo testirali
    VELIKOSTI_MNOZIC = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    # Stevilo testnih primerov za vsako velikost mnozice
    STEVILO_PRIMEROV = 5

    # Ustvarimo mnozice
    generate_data(VELIKOSTI_MNOZIC, STEVILO_PRIMEROV, seed=42)

    # Izvedemo eksperiment
    compare_algorithms(VELIKOSTI_MNOZIC, STEVILO_PRIMEROV)
