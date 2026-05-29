import copy

def prikazi_rezultate(narudzbe, naziv):
    """
    Funkcija za tabelarni prikaz rezultata izvršavanja algoritma.
    Izračunava i prikazuje prosječna vremena, kao i uspješnost isporuke unutar SLA (20 min).
    """
    print(f"\n" + "="*80)
    print(f" REZULTATI ZA ALGORITAM: {naziv} ".center(80, '#'))
    print(f"="*80)
    print(f"{'ID':<4} | {'Dolazak':<8} | {'Burst':<6} | {'Prioritet':<9} | {'Komplet':<8} | {'TAT':<5} | {'Čekanje':<8} | {'Status (<20m)'}")
    print("-" * 80)

    ukupno_cekanje = 0
    ukupno_tat = 0
    usluzeno_na_vrijeme = 0

    # Sortiranje po ID-u radi konzistentnosti prikaza
    narudzbe.sort(key=lambda x: x['id'])

    for n in narudzbe:
        ukupno_cekanje += n['cekanje']
        ukupno_tat += n['tat']
        
        # Provjera da li je narudžba izvršena unutar kritičnih 20 minuta od dolaska
        status_sla = "OK" if n['tat'] <= 20 else "PROBIJEN ROK"
        if n['tat'] <= 20:
            usluzeno_na_vrijeme += 1

        print(
            f"{n['id']:<4} | "
            f"{n['dolazak']:<8} | "
            f"{n['burst']:<6} | "
            f"{n['prioritet']:<9} | "
            f"{n['kompletiranje']:<8} | "
            f"{n['tat']:<5} | "
            f"{n['cekanje']:<8} | "
            f"{status_sla}"
        )

    prosjek_cekanja = ukupno_cekanje / len(narudzbe) if narudzbe else 0
    prosjek_tat = ukupno_tat / len(narudzbe) if narudzbe else 0
    procenat_uspjesnosti = (usluzeno_na_vrijeme / len(narudzbe)) * 100 if narudzbe else 0

    print("-" * 80)
    print(f"📊 Prosječno vrijeme čekanja: {prosjek_cekanja:.2f} min")
    print(f"📊 Prosječno ukupno vrijeme izvršavanja (TAT): {prosjek_tat:.2f} min")
    print(f"🎯 Procenat zadovoljstva kupaca (SLA <= 20min): {procenat_uspjesnosti:.2f}%")
    print("=" * 80)
    
    # Vraćamo vrijednosti za potrebe komparativne analize
    return prosjek_cekanja, prosjek_tat, procenat_uspjesnosti


def izracunaj_sjf_non_preemptive(narudzbe, tihi_mod=False):
    """
    Implementacija Shortest Job First (SJF - Non-Preemptive) algoritma.
    Procesi se ne prekidaju jednom kada započne njihova priprema.
    """
    radne_narudzbe = copy.deepcopy(narudzbe)
    vrijeme = 0
    zavrsene = []

    while len(zavrsene) < len(radne_narudzbe):
        # Filtriranje narudžbi koje su stigle do trenutnog vremena, a nisu završene
        spremne = [n for n in radne_narudzbe if n not in zavrsene and n['dolazak'] <= vrijeme]

        if not spremne:
            # Ako nema spremnih narudžbi, pomjeri vrijeme na dolazak sljedeće najranije
            sljedeci_dolazak = min([n['dolazak'] for n in radne_narudzbe if n not in zavrsene])
            vrijeme = sljedeci_dolazak
            continue

        # Sortiranje po dužini trajanja pripreme (Burst Time)
        spremne.sort(key=lambda x: x['burst'])
        trenutna = spremne[0]

        # Budući da je Non-Preemptive, radimo obradu do kraja
        vrijeme += trenutna['burst']
        trenutna['kompletiranje'] = vrijeme
        trenutna['tat'] = trenutna['kompletiranje'] - trenutna['dolazak']
        trenutna['cekanje'] = trenutna['tat'] - trenutna['burst']

        zavrsene.append(trenutna)

    if tihi_mod:
        return zavrsene
    return prikazi_rezultate(zavrsene, "Shortest Job First (SJF - Non-Preemptive)")


def izracunaj_srtf(narudzbe, tihi_mod=False):
    """
    Implementacija Shortest Remaining Time First (SRTF) - Preemptive SJF algoritma.
    Ako stigne narudžba sa kraćim preostalim vremenom, trenutna priprema se prekida.
    """
    radne_narudzbe = copy.deepcopy(narudzbe)
    for n in radne_narudzbe:
        n['preostalo'] = n['burst']

    vrijeme = 0
    zavrsene_brojac = 0
    ukupno_narudzbi = len(radne_narudzbe)
    zavrsene = []

    while zavrsene_brojac < ukupno_narudzbi:
        # Traženje narudžbi koje su stigle i još uvijek imaju posla za pripremu
        spremne = [n for n in radne_narudzbe if n['dolazak'] <= vrijeme and n['preostalo'] > 0]

        if not spremne:
            vrijeme += 1
            continue

        # Sortiranje prema PREOSTALOM vremenu pripreme
        spremne.sort(key=lambda x: x['preostalo'])
        trenutna = spremne[0]

        # Izvršavanje za 1 vremensku jedinicu (minutu)
        vrijeme += 1
        trenutna['preostalo'] -= 1

        # Ako je priprema završena, izračunaj metrike
        if trenutna['preostalo'] == 0:
            trenutna['kompletiranje'] = vrijeme
            trenutna['tat'] = trenutna['kompletiranje'] - trenutna['dolazak']
            trenutna['cekanje'] = trenutna['tat'] - trenutna['burst']
            zavrsene.append(trenutna)
            zavrsene_brojac += 1

    if tihi_mod:
        return zavrsene
    return prikazi_rezultate(zavrsene, "Shortest Remaining Time First (SRTF)")


def izracunaj_priority(narudzbe, tihi_mod=False):
    """
    Implementacija Priority Scheduling algoritma (Non-preemptive).
    Narudžbe sa manjim brojem prioriteta (npr. 0) imaju prednost.
    """
    radne_narudzbe = copy.deepcopy(narudzbe)
    vrijeme = 0
    zavrsene = []

    while len(zavrsene) < len(radne_narudzbe):
        spremne = [n for n in radne_narudzbe if n not in zavrsene and n['dolazak'] <= vrijeme]

        if not spremne:
            sljedeci_dolazak = min([n['dolazak'] for n in radne_narudzbe if n not in zavrsene])
            vrijeme = sljedeci_dolazak
            continue

        # Sortiranje primarno po prioritetu, a sekundarno po vremenu dolaska (FCFS)
        spremne.sort(key=lambda x: (x['prioritet'], x['dolazak']))
        trenutna = spremne[0]

        vrijeme += trenutna['burst']
        trenutna['kompletiranje'] = vrijeme
        trenutna['tat'] = trenutna['kompletiranje'] - trenutna['dolazak']
        trenutna['cekanje'] = trenutna['tat'] - trenutna['burst']

        zavrsene.append(trenutna)

    if tihi_mod:
        return zavrsene
    return prikazi_rezultate(zavrsene, "Priority Scheduling")


def pokreni_komparativnu_analizu(narudzbe):
    """
    Nova funkcionalnost: Pokreće sva tri algoritma nad istim podacima
    i prikazuje uporedni izvještaj za menadžment restorana.
    """
    if not narudzbe:
        print("\nNema unesenih narudžbi za analizu.")
        return

    print("\n" + "="*80)
    print(" REZIME KOMPARATIVNE ANALIZE ".center(80, '*'))
    print("="*80)

    # Pokretanje u "tihom" modu kako se ne bi ispisivale pojedinačne tabele ponovo
    sjf_zavrsene = izracunaj_sjf_non_preemptive(narudzbe, tihi_mod=True)
    srtf_zavrsene = izracunaj_srtf(narudzbe, tihi_mod=True)
    prio_zavrsene = izracunaj_priority(narudzbe, tihi_mod=True)

    def kalkulisi_prosjeke(liste_narudzbi):
        wc = sum(n['cekanje'] for n in liste_narudzbi) / len(liste_narudzbi)
        wtat = sum(n['tat'] for n in liste_narudzbi) / len(liste_narudzbi)
        wsla = (sum(1 for n in liste_narudzbi if n['tat'] <= 20) / len(liste_narudzbi)) * 100
        return wc, wtat, wsla

    sjf_c, sjf_t, sjf_s = kalkulisi_prosjeke(sjf_zavrsene)
    srtf_c, srtf_t, srtf_s = kalkulisi_prosjeke(srtf_zavrsene)
    prio_c, prio_t, prio_s = kalkulisi_prosjeke(prio_zavrsene)

    print(f"{'Algoritam':<30} | {'Prosječno Čekanje':<18} | {'Prosječni TAT':<15} | {'Zadovoljstvo (SLA)'}")
    print("-" * 80)
    print(f"{'[1] SJF (Non-Preemptive)':<30} | {sjf_c:<18.2f} | {sjf_t:<15.2f} | {sjf_s:.2f}%")
    print(f"{'[2] SRTF (Preemptive)':<30} | {srtf_c:<18.2f} | {srtf_t:<15.2f} | {srtf_s:.2f}%")
    print(f"{'[3] Priority Scheduling':<30} | {prio_c:<18.2f} | {prio_t:<15.2f} | {prio_s:.2f}%")
    print("=" * 80)
    
    # Preporuka sistema na osnovu minimalnog vremena čekanja
    najbolji = min(
        [("[1] SJF", sjf_c), ("[2] SRTF", srtf_c), ("[3] Priority", prio_c)],
        key=lambda x: x[1]
    )
    print(f"💡 PREPORUKA SISTEMA: Za unesene podatke, najbolju efikasnost daje algoritam: {najbolji[0]}")


def siguran_unos_int(poruka, min_vrijednost=0):
    """Pomoćna funkcija koja sprečava rušenje programa pri pogrešnom unosu brojeva."""
    while True:
        try:
            vrijednost = int(input(poruka))
            if vrijednost < min_vrijednost:
                print(f"Vrijednost ne može biti manja od {min_vrijednost}.")
                continue
            return vrijednost
        except ValueError:
            print("❌ Greška! Molimo unesite ispravan cijeli broj.")


def glavni_program():
    """Glavna upravljačka petlja aplikacije."""
    sve_narudzbe = []

    while True:
        print("\n" + "="*40)
        print(" AUTOMATIZIRANI RESTORANSKI SISTEM ".center(40, '='))
        print("="*40)
        print("[1] Shortest Job First (SJF - Non-Preemptive)")
        print("[2] Shortest Remaining Time First (SRTF)")
        print("[3] Priority Scheduling")
        print("[4] POGLEDAJ KOMPARATIVNU ANALIZU (Sve odjednom)")
        print("[5] Unesi / Resetuj podatke o narudžbama")
        print("[6] Izlaz iz aplikacije")
        print("-" * 40)
        
        if sve_narudzbe:
            print(f"Status: U sistemu trenutno ima učitanih narudžbi: {len(sve_narudzbe)}")
        else:
            print("Status: Sistem nema učitanih podataka. Molimo idite na opciju [5].")

        izbor = input("Izaberite opciju (1-6): ")

        if izbor == '6':
            print("\nHvala na korištenju sistema. Prijatno!")
            break

        if izbor not in ['1', '2', '3', '4', '5']:
            print("❌ Pogrešan izbor! Pokušajte ponovo.")
            continue

        # Opcija za unos podataka
        if izbor == '5':
            broj = siguran_unos_int("\nUnesite ukupan broj narudžbi: ", min_vrijednost=1)
            sve_narudzbe = []

            for i in range(broj):
                print(f"\n--- Unos za narudžbu #{i + 1} ---")
                dolazak = siguran_unos_int("Vrijeme dolaska narudžbe (u kojoj minuti): ")
                burst = siguran_unos_int("Vrijeme pripreme/dostave (u minutama): ", min_vrijednost=1)

                # Definisanje prioriteta prema realnom opisu zadatka
                print("Tip kupca:")
                print(" 1) Hrana za ponijeti (Najviši prioritet)")
                print(" 2) Konzumacija u restoranu (Srednji prioritet)")
                print(" 3) Dostava na kućnu adresu (Najniži prioritet)")
                
                tip_kupca = siguran_unos_int("Izaberite tip kupca (1-3): ", min_vrijednost=1)
                while tip_kupca > 3:
                    print("Nepostojeći tip. Izaberite 1, 2 ili 3.")
                    tip_kupca = siguran_unos_int("Izaberite tip kupca (1-3): ")

                # Mapiranje: Tip 1 -> Prioritet 0, Tip 2 -> Prioritet 1, Tip 3 -> Prioritet 2
                prioritet = tip_kupca - 1

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
            print("\n✅ Podaci uspješno učitani u sistem!")
            input("\nPritisnite Enter za nastavak...")
            continue

        # Za izvršavanje algoritama (1-4) preduslov je da imamo podatke
        if not sve_narudzbe:
            print("\n⚠️ Greška: Morate prvo unijeti podatke (Opcija [5]) prije pokretanja simulacije!")
            input("\nPritisnite Enter za nastavak...")
            continue

        # Izvršavanje na osnovu izabrane opcije
        if izbor == '1':
            izracunaj_sjf_non_preemptive(sve_narudzbe)
        elif izbor == '2':
            izracunaj_srtf(sve_narudzbe)
        elif izbor == '3':
            izracunaj_priority(sve_narudzbe)
        elif izbor == '4':
            pokreni_komparativnu_analizu(sve_narudzbe)

        input("\nPritisnite Enter za povratak na glavni meni...")


if __name__ == "__main__":
    glavni_program()