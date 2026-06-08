import copy
import sys

# ---------------------------------------------------------------
# Pomoćna funkcija za čekanje na pritisak bilo koje tipke
# Radi na Windows (msvcrt) i Linux/macOS (termios) sistemima
# ---------------------------------------------------------------
def pritisni_bilo_koju_tipku():
    """Čeka pritisak bilo koje tipke prije nastavka."""
    print("\nPritisnite bilo koju tipku za nastavak...")
    if sys.platform == "win32":
        import msvcrt
        msvcrt.getch()
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        stare_postavke = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, stare_postavke)


def prikazi_rezultate(narudzbe, naziv):
    """
    Funkcija za tabelarni prikaz rezultata izvrsavanja algoritma.
    Izracunava i prikazuje prosjecna vremena, kao i uspjesnost isporuke unutar SLA (20 min).
    """
    print(f"\n" + "="*80)
    print(f" REZULTATI ZA ALGORITAM: {naziv} ".center(80, '#'))
    print(f"="*80)
    print(f"{'ID':<4} | {'Dolazak':<8} | {'Burst':<6} | {'Prioritet':<9} | {'Komplet':<8} | {'TAT':<5} | {'Cekanje':<8} | {'Status (<20m)'}")
    print("-" * 80)

    ukupno_cekanje = 0
    ukupno_tat = 0
    usluzeno_na_vrijeme = 0

    # Sortiranje po ID-u radi konzistentnosti prikaza
    narudzbe.sort(key=lambda x: x['id'])

    for n in narudzbe:
        ukupno_cekanje += n['cekanje']
        ukupno_tat += n['tat']

        # Provjera da li je narudzba izvrsena unutar kriticnih 20 minuta od dolaska
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
    print(f"Prosjecno vrijeme cekanja: {prosjek_cekanja:.2f} min")
    print(f"Prosjecno ukupno vrijeme izvrsavanja (TAT): {prosjek_tat:.2f} min")
    print(f"Procenat zadovoljstva kupaca (SLA <= 20min): {procenat_uspjesnosti:.2f}%")
    print("=" * 80)

    # Vracamo vrijednosti za potrebe komparativne analize
    return prosjek_cekanja, prosjek_tat, procenat_uspjesnosti


def izracunaj_sjf_non_preemptive(narudzbe, tihi_mod=False):
    """
    Implementacija Shortest Job First (SJF - Non-Preemptive) algoritma.
    Procesi se ne prekidaju jednom kada zapocne njihova priprema.
    Primjenjuje se za dostavu - kupac sa najkracom udaljenoscu biva usluzeni prvi.
    """
    radne_narudzbe = copy.deepcopy(narudzbe)
    vrijeme = 0
    zavrsene = []

    while len(zavrsene) < len(radne_narudzbe):
        # Filtriranje narudzbi koje su stigle do trenutnog vremena, a nisu zavrsene
        spremne = [n for n in radne_narudzbe if n not in zavrsene and n['dolazak'] <= vrijeme]

        if not spremne:
            # Ako nema spremnih narudzbi, pomjeri vrijeme na dolazak sljedece najranije
            sljedeci_dolazak = min([n['dolazak'] for n in radne_narudzbe if n not in zavrsene])
            vrijeme = sljedeci_dolazak
            continue

        # Sortiranje po duzini trajanja pripreme (Burst Time) - najkraci prvi
        spremne.sort(key=lambda x: x['burst'])
        trenutna = spremne[0]

        # Buduci da je Non-Preemptive, radimo obradu do kraja bez prekidanja
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
    Ako stigne narudzba sa kracim preostalim vremenom, trenutna priprema se prekida.
    """
    radne_narudzbe = copy.deepcopy(narudzbe)
    for n in radne_narudzbe:
        n['preostalo'] = n['burst']

    vrijeme = 0
    zavrsene_brojac = 0
    ukupno_narudzbi = len(radne_narudzbe)
    zavrsene = []

    while zavrsene_brojac < ukupno_narudzbi:
        # Trazenje narudzbi koje su stigle i jos uvijek imaju posla za pripremu
        spremne = [n for n in radne_narudzbe if n['dolazak'] <= vrijeme and n['preostalo'] > 0]

        if not spremne:
            vrijeme += 1
            continue

        # Sortiranje prema PREOSTALOM vremenu pripreme - kljucni princip SRTF algoritma
        spremne.sort(key=lambda x: x['preostalo'])
        trenutna = spremne[0]

        # Izvrsavanje za 1 vremensku jedinicu (minutu) - omogucava preempciju
        vrijeme += 1
        trenutna['preostalo'] -= 1

        # Ako je priprema zavrsena, izracunaj metrike
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
    Narudzbe sa manjim brojem prioriteta (0 = najvisi) imaju prednost.
    Redoslijed: hrana za ponijeti (0) > konzumacija u restoranu (1) > dostava (2).
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

        # Sortiranje primarno po prioritetu, a sekundarno po vremenu dolaska (FCFS tie-break)
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
    Pokrece sva tri algoritma nad istim podacima i prikazuje
    uporedni izvjestaj za menadzment restorana.
    """
    if not narudzbe:
        print("\nNema unesenih narudzbi za analizu.")
        return

    print("\n" + "="*80)
    print(" REZIME KOMPARATIVNE ANALIZE ".center(80, '*'))
    print("="*80)

    # Pokretanje u "tihom" modu kako se ne bi ispisivale pojedinacne tabele ponovo
    sjf_zavrsene = izracunaj_sjf_non_preemptive(narudzbe, tihi_mod=True)
    srtf_zavrsene = izracunaj_srtf(narudzbe, tihi_mod=True)
    prio_zavrsene = izracunaj_priority(narudzbe, tihi_mod=True)

    def kalkulisi_prosjeke(liste_narudzbi):
        """Izracunava prosjecno cekanje, TAT i SLA procenat za listu narudzbi."""
        wc = sum(n['cekanje'] for n in liste_narudzbi) / len(liste_narudzbi)
        wtat = sum(n['tat'] for n in liste_narudzbi) / len(liste_narudzbi)
        wsla = (sum(1 for n in liste_narudzbi if n['tat'] <= 20) / len(liste_narudzbi)) * 100
        return wc, wtat, wsla

    sjf_c, sjf_t, sjf_s = kalkulisi_prosjeke(sjf_zavrsene)
    srtf_c, srtf_t, srtf_s = kalkulisi_prosjeke(srtf_zavrsene)
    prio_c, prio_t, prio_s = kalkulisi_prosjeke(prio_zavrsene)

    print(f"{'Algoritam':<30} | {'Prosjecno Cekanje':<18} | {'Prosjecni TAT':<15} | {'Zadovoljstvo (SLA)'}")
    print("-" * 80)
    print(f"{'[1] SJF (Non-Preemptive)':<30} | {sjf_c:<18.2f} | {sjf_t:<15.2f} | {sjf_s:.2f}%")
    print(f"{'[2] SRTF (Preemptive)':<30} | {srtf_c:<18.2f} | {srtf_t:<15.2f} | {srtf_s:.2f}%")
    print(f"{'[3] Priority Scheduling':<30} | {prio_c:<18.2f} | {prio_t:<15.2f} | {prio_s:.2f}%")
    print("=" * 80)

    # Preporuka sistema na osnovu minimalnog prosjecnog vremena cekanja
    najbolji = min(
        [("[1] SJF", sjf_c), ("[2] SRTF", srtf_c), ("[3] Priority", prio_c)],
        key=lambda x: x[1]
    )
    print(f"PREPORUKA SISTEMA: Za unesene podatke, najbolju efikasnost daje algoritam: {najbolji[0]}")


def siguran_unos_int(poruka, min_vrijednost=0):
    """
    Pomocna funkcija koja sprecava rusenje programa pri pogresnom unosu brojeva.
    Ponavlja unos sve dok korisnik ne unese ispravan cijeli broj >= min_vrijednost.
    """
    while True:
        try:
            vrijednost = int(input(poruka))
            if vrijednost < min_vrijednost:
                print(f"Vrijednost ne moze biti manja od {min_vrijednost}.")
                continue
            return vrijednost
        except ValueError:
            print("Greska! Molimo unesite ispravan cijeli broj.")


def glavni_program():
    """Glavna upravljacka petlja aplikacije."""
    sve_narudzbe = []

    while True:
        print("\n" + "="*40)
        print(" AUTOMATIZIRANI RESTORANSKI SISTEM ".center(40, '='))
        print("="*40)
        print("[1] Shortest Job First (SJF - Non-Preemptive)")
        print("[2] Shortest Remaining Time First (SRTF)")
        print("[3] Priority Scheduling")
        print("[4] POGLEDAJ KOMPARATIVNU ANALIZU (Sve odjednom)")
        print("[5] Unesi / Resetuj podatke o narudzbama")
        print("[6] Izlaz iz aplikacije")
        print("-" * 40)

        if sve_narudzbe:
            print(f"Status: U sistemu trenutno ima ucitanih narudzbi: {len(sve_narudzbe)}")
        else:
            print("Status: Sistem nema ucitanih podataka. Molimo idite na opciju [5].")

        izbor = input("Izaberite opciju (1-6): ")

        if izbor == '6':
            print("\nHvala na koristenju sistema. Prijatno!")
            break

        if izbor not in ['1', '2', '3', '4', '5']:
            print("Pogresan izbor! Pokusajte ponovo.")
            continue

        # Opcija za unos ili resetovanje podataka o narudzbama
        if izbor == '5':
            broj = siguran_unos_int("\nUnesite ukupan broj narudzbi: ", min_vrijednost=1)
            sve_narudzbe = []

            for i in range(broj):
                print(f"\n--- Unos za narudzbu #{i + 1} ---")
                dolazak = siguran_unos_int("Vrijeme dolaska narudzbe (u kojoj minuti): ")
                burst = siguran_unos_int("Vrijeme pripreme/dostave (u minutama): ", min_vrijednost=1)

                # Definisanje prioriteta prema realnom opisu zadatka
                print("Tip kupca:")
                print(" 1) Hrana za ponijeti  (Najvisi prioritet)")
                print(" 2) Konzumacija u restoranu  (Srednji prioritet)")
                print(" 3) Dostava na kucnu adresu  (Najnizi prioritet)")

                tip_kupca = siguran_unos_int("Izaberite tip kupca (1-3): ", min_vrijednost=1)
                while tip_kupca > 3:
                    print("Nepostojeci tip. Izaberite 1, 2 ili 3.")
                    tip_kupca = siguran_unos_int("Izaberite tip kupca (1-3): ")

                # Mapiranje tipa kupca na prioritet: Tip 1 -> 0, Tip 2 -> 1, Tip 3 -> 2
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

            print("\nPodaci uspjesno ucitani u sistem!")
            pritisni_bilo_koju_tipku()
            continue

        # Za izvrsavanje algoritama (1-4) preduslov je da imamo podatke u sistemu
        if not sve_narudzbe:
            print("\nGreska: Morate prvo unijeti podatke (Opcija [5]) prije pokretanja simulacije!")
            pritisni_bilo_koju_tipku()
            continue

        # Izvrsavanje algoritma na osnovu izabrane opcije
        if izbor == '1':
            izracunaj_sjf_non_preemptive(sve_narudzbe)
        elif izbor == '2':
            izracunaj_srtf(sve_narudzbe)
        elif izbor == '3':
            izracunaj_priority(sve_narudzbe)
        elif izbor == '4':
            pokreni_komparativnu_analizu(sve_narudzbe)

        pritisni_bilo_koju_tipku()


if __name__ == "__main__":
    glavni_program()