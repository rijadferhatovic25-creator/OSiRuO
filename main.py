def izracunaj_sjf_non_preemptive(narudzbe):
    # TODO: Implementirati logiku za Shortest Job First (ne-preemptivni)
    # Trenutno samo ispisuje podatke bez kalkulacije
    print("\nRezultati za SJF (Non-Preemptive):")
    for n in narudzbe:
        print(f"ID: {n['id']}, Dolazak: {n['dolazak']}, Burst: {n['burst']}")

def izracunaj_srtf(narudzbe):
    # TODO: Implementirati SRTF (preemptivni SJF)
    pass

def izracunaj_priority(narudzbe):
    # TODO: Implementirati Priority Scheduling
    pass

def glavni_program():
    while True:
        print("\n--- RESTORAN SISTEM ---")
        print("[1] Shortest Job First (SJF - Non-Preemptive)")
        print("[2] Shortest Job First Preemptive (SRTF)")
        print("[3] Priority Scheduling")
        print("[4] Izlaz iz aplikacije")
        
        izbor = input("Izaberite opciju: ")
        
        if izbor == '4':
            break
            
        n_count = int(input("Unesite ukupan broj narudžbi: "))
        sve_narudzbe = []
        
        for i in range(n_count):
            print(f"\nPodaci za narudžbu #{i+1}:")
            dolazak = int(input("Vrijeme dolaska: "))
            burst = int(input("Vrijeme pripreme (burst): "))
            
            narudzba = {
                'id': i + 1,
                'dolazak': dolazak,
                'burst': burst,
                'prioritet': 0 # Dodati input ako se bira opcija 3
            }
            sve_narudzbe.append(narudzba)

        if izbor == '1':
            izracunaj_sjf_non_preemptive(sve_narudzbe)
        elif izbor == '2':
            izracunaj_srtf(sve_narudzbe)
        elif izbor == '3':
            # Ovdje bi trebao dodati unos prioriteta prije poziva funkcije
            izracunaj_priority(sve_narudzbe)

if __name__ == "__main__":
    glavni_program()