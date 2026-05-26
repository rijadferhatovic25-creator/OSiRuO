import copy

def prikazi_rezultate(narudzbe, naziv):
    print(f"\n--- {naziv} ---")
    print("-" * 72)
    print("ID | Dolazak | Burst | Kompletiranje | TAT | Čekanje")
    print("-" * 72)

    ukupno_cekanje = 0
    ukupno_tat = 0

    narudzbe.sort(key=lambda x: x['id'])

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
    radne_narudzbe = copy.deepcopy(narudzbe)
    vrijeme = 0
    zavrsene = []

    while len(zavrsene) < len(radne_narudzbe):
        spremne = []
        
        for n in radne_narudzbe:
            if n not in zavrsene and n['dolazak'] <= vrijeme:
                spremne.append(n)

        if not spremne:
            sljedeci_dolazak = min([n['dolazak'] for n in radne_narudzbe if n not in zavrsene])
            vrijeme = sljedeci_dolazak
            continue

        spremne.sort(key=lambda x: x['burst'])
        trenutna = spremne[0]

        vrijeme += trenutna['burst']

        trenutna['kompletiranje'] = vrijeme
        trenutna['tat'] = trenutna['kompletiranje'] - trenutna['dolazak']
        trenutna['cekanje'] = trenutna['tat'] - trenutna['burst']

        zavrsene.append(trenutna)

    prikazi_rezultate(zavrsene, "SJF Non-Preemptive")


def izracunaj_srtf(narudzbe):
    radne_narudzbe = copy.deepcopy(narudzbe)
    for n in radne_narudzbe:
        n['preostalo'] = n['burst']

    vrijeme = 0
    zavrsene_brojac = 0
    ukupno_narudzbi = len(radne_narudzbe)
    zavrsene = []

    while zavrsene_brojac < ukupno_narudzbi:
        spremne = []
        
        for n in radne_narudzbe:
            if n['dolazak'] <= vrijeme and n['preostalo'] > 0:
                spremne.append(n)

        if not spremne:
            vrijeme += 1
            continue

        spremne.sort(key=lambda x: x['preostalo'])
        trenutna = spremne[0]

        vrijeme += 1
        trenutna['preostalo'] -= 1

        if trenutna['preostalo'] == 0:
            trenutna['kompletiranje'] = vrijeme
            trenutna['tat'] = trenutna['kompletiranje'] - trenutna['dolazak']
            trenutna['cekanje'] = trenutna['tat'] - trenutna['burst']
            zavrsene.append(trenutna)
            zavrsene_brojac += 1

    prikazi_rezultate(zavrsene, "Shortest Remaining Time First (SRTF)")


def izracunaj_priority(narudzbe):
    radne_narudzbe = copy.deepcopy(narudzbe)
    vrijeme = 0
    zavrsene = []

    while len(zavrsene) < len(radne_narudzbe):
        spremne = []
        
        for n in radne_narudzbe:
            if n not in zavrsene and n['dolazak'] <= vrijeme:
                spremne.append(n)

        if not spremne:
            sljedeci_dolazak = min([n['dolazak'] for n in radne_narudzbe if n not in zavrsene])
            vrijeme = sljedeci_dolazak
            continue

        spremne.sort(key=lambda x: (x['prioritet'], x['dolazak']))
        trenutna = spremne[0]

        vrijeme += trenutna['burst']

        trenutna['kompletiranje'] = vrijeme
        trenutna['tat'] = trenutna['kompletiranje'] - trenutna['dolazak']
        trenutna['cekanje'] = trenutna['tat'] - trenutna['burst']

        zavrsene.append(trenutna)

    prikazi_rezultate(radne_narudzbe, "Priority Scheduling")


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
            print("Pogrešan unos. Pokušajte ponovo.")
            continue

        broj = int(input("\nUnesite ukupan broj narudžbi: "))
        sve_narudzbe = []

        for i in range(broj):
            print(f"\nNarudžba #{i + 1}")

            dolazak = int(input("Vrijeme dolaska (minuta): "))
            burst = int(input("Vrijeme pripreme (burst): "))

            prioritet = 0
            if izbor == '3':
                prioritet = int(input("Prioritet (0 = najveći prioritet): "))

            narudzba = {
                'id': i + 1,
                'dolazak': dolazak,
                'burst': burst,
                'prioritet': prioritet,
                'kompletiranje': 0,
                'tat': 0,
                'cekanje': 0
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