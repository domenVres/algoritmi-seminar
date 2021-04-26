from data_preparation import generate_data, create_graph


if __name__=="__main__":
    # Velikosti mnozic, ki jih bomo testirali
    VELIKOSTI_MNOZIC = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
    # Stevilo testnih primerov za vsako velikost mnozice
    STEVILO_PRIMEROV = 5

    # Ustvarimo mnozice
    generate_data(VELIKOSTI_MNOZIC, STEVILO_PRIMEROV, seed=42)