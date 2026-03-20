# Garagebook

Desktopowa aplikacja do śledzenia kosztów eksploatacji pojazdów.

**Stack:** Python 3.13 · NiceGUI · PyWebView · SQLite · uv

---

## Funkcje

- Wiele pojazdów (dane, VIN, rok, paliwo, 1. rejestracja)
- Wpisy kosztów z kategoriami: Paliwo, Ładowanie (EV/hybryda), Części, Obsługa, Usterka, Serwis
- Ubezpieczenia i przeglądy techniczne z alertami o zbliżających się terminach
- Zużycie paliwa (L/100km) i energii (kWh/100km) — obliczane z tankowań/ładowań do pełna
- Wskaźnik wymiany oleju (dni i km od ostatniej wymiany)
- Koszt eksploatacji i średni koszt/km
- Wybór waluty (PLN, EUR, USD, GBP, CHF, CZK, NOK, SEK)
- Kopia zapasowa bazy danych (backup / restore / usuwanie)
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

Przy pierwszym uruchomieniu automatycznie instalowany jest `uv`, Python 3.13 oraz zależności.

---

## Wymagania

- Połączenie z internetem (przy pierwszym uruchomieniu)
- macOS / Windows / Linux (Debian, Fedora, Arch)

---

## Struktura projektu

```
Garagebook/
├── main.py              # uruchomienie, strona pojazdu
├── pyproject.toml       # zależności i wersja
├── uv.lock              # lockfile
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
uv run dev/build_dist.py macos
uv run dev/build_dist.py windows
uv run dev/build_dist.py linux
uv run dev/build_dist.py all
```

Wynik trafia do katalogu `dist/`.
