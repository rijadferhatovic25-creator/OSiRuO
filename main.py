def prikazi_rezultate(narudzbe, naziv):
    print(f"\n--- {naziv} ---")
    print("-" * 72)
    print("ID | Dolazak | Burst | Kompletiranje | TAT | Čekanje")
    print("-" * 72)

    ukupno_cekanje = 0
    ukupno_tat = 0

    for n in narudzbe:
        ukupno_cekanje += n['cekanje']
        ukupno_tat += n['tat']

        print(
            f"{n['id']:2} | "
            f"{n['dolazak']:8} | "
            f"{n['burst']:5} | "
            f"{n['kompletiranje']:13} | "
            f"{n['tat']:3} | "
            f"{n['cekanje']:8}"
        )

    prosjek_cekanja = ukupno_cekanje / len(narudzbe)
    prosjek_tat = ukupno_tat / len(narudzbe)

    print("-" * 72)
    print(f"Prosječno vrijeme čekanja: {prosjek_cekanja:.2f} min")
    print(f"Prosječno turnaround vrijeme: {prosjek_tat:.2f} min")


def izracunaj_sjf_non_preemptive(narudzbe):
    narudzbe.sort(key=lambda x: (x['dolazak'], x['burst']))

    vrijeme = 0
    zavrsene = []
    spremne = []

    while len(zavrsene) < len(narudzbe):

        for n in narudzbe:
            if n not in spremne and n not in zavrsene and n['dolazak'] <= vrijeme:
                spremne.append(n)

        if not spremne:
            vrijeme += 1
            continue

        spremne.sort(key=lambda x: x['burst'])
        trenutna = spremne.pop(0)

        vrijeme += trenutna['burst']

        trenutna['kompletiranje'] = vrijeme
        trenutna['tat'] = trenutna['kompletiranje'] - trenutna['dolazak']
        trenutna['cekanje'] = trenutna['tat'] - trenutna['burst']

        zavrsene.append(trenutna)

    prikazi_rezultate(zavrsene, "SJF Non-Preemptive")


def izracunaj_srtf(narudzbe):
    print("\nSRTF algoritam trenutno nije potpuno implementiran.")
    print("Dodati logiku za prekid procesa sa većim burst vremenom.\n")


def izracunaj_priority(narudzbe):
    narudzbe.sort(key=lambda x: (x['prioritet'], x['dolazak']))

    vrijeme = 0

    for n in narudzbe:

        if vrijeme < n['dolazak']:
            vrijeme = n['dolazak']

        vrijeme += n['burst']

        n['kompletiranje'] = vrijeme
        n['tat'] = n['kompletiranje'] - n['dolazak']
        n['cekanje'] = n['tat'] - n['burst']

    prikazi_rezultate(narudzbe, "Priority Scheduling")


def glavni_program():

    while True:

        print("\n=== RESTORAN SISTEM ===")
        print("[1] Shortest Job First (SJF - Non-Preemptive)")
        print("[2] Shortest Remaining Time First (SRTF)")
        print("[3] Priority Scheduling")
        print("[4] Izlaz")

        izbor = input("Izaberite opciju: ")

        if izbor == '4':
            print("\nAplikacija zatvorena.")
            break

        if izbor not in ['1', '2', '3']:
            print("Pogrešan unos.")
            continue

        broj = int(input("\nUnesite ukupan broj narudžbi: "))
        sve_narudzbe = []

        for i in range(broj):

            print(f"\nNarudžba #{i + 1}")

            dolazak = int(input("Vrijeme dolaska: "))
            burst = int(input("Vrijeme pripreme: "))

            prioritet = 0

            if izbor == '3':
                prioritet = int(input("Prioritet (0 = najveći): "))

            narudzba = {
                'id': i + 1,
                'dolazak': dolazak,
                'burst': burst,
                'prioritet': prioritet
            }

            sve_narudzbe.append(narudzba)

        if izbor == '1':
            izracunaj_sjf_non_preemptive(sve_narudzbe)

        elif izbor == '2':
            izracunaj_srtf(sve_narudzbe)

        elif izbor == '3':
            izracunaj_priority(sve_narudzbe)

        input("\nPritisnite Enter za nastavak...")


if __name__ == "__main__":
    glavni_program()