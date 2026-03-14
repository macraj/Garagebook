# Garagebook

Desktopowa aplikacja do śledzenia kosztów eksploatacji pojazdów.

**Stack:** Python · NiceGUI · PyWebView · SQLite

---

## Funkcje

- Wiele pojazdów (dane, VIN, rok, paliwo, 1. rejestracja)
- Wpisy kosztów z kategoriami: Paliwo, Ładowanie (EV/hybryda), Części, Obsługa, Usterka, Serwis
- Ubezpieczenia i przeglądy techniczne z alertami o zbliżających się terminach
- Zużycie paliwa (L/100km) i energii (kWh/100km) — obliczane z tankowań/ładowań do pełna
- Wskaźnik wymiany oleju (dni i km od ostatniej wymiany)
- Koszt eksploatacji i średni koszt/km
- Wybór waluty (PLN, EUR, USD, GBP, CHF, CZK, NOK, SEK)
- Kopia zapasowa bazy danych
- Eksport wpisów do CSV (Excel)

---

## Uruchomienie

### macOS
Kliknij dwukrotnie `Garagebook.command`

### Windows
Kliknij dwukrotnie `Garagebook.bat`

### Linux
```bash
bash Garagebook.sh
```

Przy pierwszym uruchomieniu instalator automatycznie tworzy środowisko `.venv` i instaluje zależności.

---

## Wymagania

- Python 3.10+
- macOS / Windows / Linux (Debian, Fedora, Arch)

---

## Struktura projektu

```
Garagebook/
├── main.py              # uruchomienie, strona pojazdu
├── db/
│   ├── schema.sql       # schemat SQLite
│   └── database.py      # operacje na bazie
├── ui/
│   ├── dashboard.py     # widok główny
│   ├── vehicles.py      # zarządzanie pojazdami
│   ├── entries.py       # wpisy kosztów
│   ├── documents.py     # ubezpieczenia i przeglądy
│   ├── settings.py      # ustawienia i backup
│   ├── export.py        # eksport CSV
│   └── layout.py        # nagłówek, alerty
├── scripts/
│   ├── macos/install.sh
│   ├── linux/install.sh
│   └── windows/install.bat
└── dev/
    └── build_dist.py    # builder ZIP do dystrybucji
```

---

## Budowanie dystrybucji

```bash
python3 dev/build_dist.py macos
python3 dev/build_dist.py windows
python3 dev/build_dist.py linux
python3 dev/build_dist.py all
```

Wynik trafia do katalogu `dist/`.
