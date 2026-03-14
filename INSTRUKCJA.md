# Garagebook — Instrukcja użytkownika

Aplikacja do śledzenia kosztów eksploatacji pojazdów. Działa jako program desktopowy (okno natywne).

---

## Uruchomienie

```bash
./start.sh
```

Przy pierwszym uruchomieniu zostaje automatycznie utworzona baza danych `garagebook.db`.

---

## Nawigacja

Pasek u góry ekranu zawiera przyciski:

| Przycisk | Opis |
|---|---|
| **Dashboard** | Widok główny — przegląd całej floty |
| **Pojazdy** | Zarządzanie listą pojazdów |
| **Ustawienia** | Waluta, kopia zapasowa bazy danych |

Kliknięcie karty pojazdu na dashboardzie otwiera szczegóły pojazdu.

---

## Dashboard

Wyświetla karty wszystkich pojazdów. Na każdej karcie widoczne są:

- **Nazwa, marka, model**
- **Ostatni stan licznika** (km)
- **Status OC** — ile dni pozostało do końca ubezpieczenia
- **Status przeglądu technicznego** — ile dni pozostało do wygaśnięcia

### Kolory alertów

| Kolor | Znaczenie |
|---|---|
| 🟢 Zielony | Ponad 30 dni do końca ważności |
| 🟡 Żółty | 30 dni lub mniej — zbliża się termin |
| 🔴 Czerwony | Termin minął |

---

## Pojazdy

### Dodawanie pojazdu

1. Kliknij **Pojazdy** w pasku nawigacji
2. Kliknij przycisk **Dodaj pojazd**
3. Wypełnij formularz:

| Pole | Opis |
|---|---|
| Nazwa * | Wymagana — np. „Boxer służbowy" |
| Marka / Model | np. Peugeot / Boxer |
| VIN | Numer identyfikacyjny pojazdu |
| Rok produkcji | Rok fabryczny |
| Rodzaj paliwa | Benzyna / Diesel / LPG / Elektryczny / Hybryda / CNG |
| Data 1. rejestracji | Data pierwszej rejestracji pojazdu |
| Startowy licznik (km) | Aktualny przebieg w chwili dodania — stanowi minimalną wartość licznika dla nowych wpisów |

4. Kliknij **Zapisz**

### Edycja i usuwanie

Na liście pojazdów przy każdym wierszu dostępne są przyciski:
- ✏️ **Edytuj** — zmiana danych pojazdu
- 🗑️ **Usuń** — trwałe usunięcie pojazdu wraz ze wszystkimi wpisami, ubezpieczeniami i przeglądami

> ⚠️ Usunięcia nie można cofnąć.

---

## Szczegóły pojazdu

Kliknięcie karty na dashboardzie (lub ikony 🔗 na liście pojazdów) otwiera widok szczegółów z trzema zakładkami:

- **Wpisy kosztów**
- **Dokumenty i terminy**
- **Paliwo / Spalanie**

Pod nagłówkiem widoczny jest wskaźnik **ostatniej wymiany oleju** (data, liczba dni i kilometrów od wymiany).

### Kolory wskaźnika oleju

| Kolor | Dni | Kilometry |
|---|---|---|
| 🟢 Zielony | < 270 dni | < 10 000 km |
| 🟡 Żółty | 270–365 dni | 10 000–15 000 km |
| 🔴 Czerwony | > 365 dni | > 15 000 km |

---

## Zakładka: Wpisy kosztów

Tabela wszystkich wydatków związanych z pojazdem.

### Kategorie

| Kategoria | Przykłady | Jednostka |
|---|---|---|
| **Paliwo** | Tankowanie benzyny, diesel, LPG, AdBlue | L |
| **Ładowanie** | Ładowanie EV lub hybrydy plug-in | kWh |
| **Części** | Klocki, żarówki, filtry, opony | szt |
| **Obsługa** | Wymiana oleju, kontrola ciśnienia, mycie | szt |
| **Usterka** | Awaria, naprawa nieplanowana | szt |
| **Serwis** | Wizyta w warsztacie, przegląd | szt |

### Dodawanie wpisu

1. Kliknij **Dodaj wpis**
2. Wypełnij pola:

| Pole | Opis |
|---|---|
| Data * | Wymagana |
| Rodzaj * | Kategoria wydatku |
| Ilość | Litry (Paliwo), kWh (Ładowanie) lub sztuki — label zmienia się automatycznie |
| Kwota | Koszt w wybranej walucie |
| Licznik (km) | Stan licznika — nie może być niższy od poprzedniego wpisu |
| Opis | Dowolny opis, można wpisać wiele pozycji w osobnych liniach |
| ID kierowcy | Kod osoby np. MR, TK |
| **Do pełna** | Widoczne dla Paliwo i Ładowanie — zaznacz przy pełnym tankowaniu lub ładowaniu (potrzebne do obliczania zużycia) |
| **Wymiana oleju** | Widoczne dla pozostałych kategorii — zaznacz przy każdej wymianie oleju |

> **Wskazówka:** W polu Opis możesz wpisać listę wykonanych czynności, każdą w nowej linii, np.:
> ```
> - wymiana oleju 5W30
> - wymiana filtra oleju
> - wymiana filtra powietrza
> ```

### Filtrowanie wpisów

Nad tabelą dostępne filtry:
- **Kategoria** — pokaż tylko wybrany rodzaj
- **Od / Do** — zakres dat

Po ustawieniu filtrów kliknij **Filtruj**. Aby wrócić do wszystkich wpisów — **Wyczyść**.

### Podsumowanie

Nad tabelą wyświetlane są karty z łącznym kosztem, łączną ilością paliwa (L) i łączną energią ładowania (kWh) dla aktywnych filtrów.

### Eksport CSV

Przycisk **Eksport CSV** (pod zakładkami) pobiera plik z wpisami bieżącego pojazdu, kompatybilny z Microsoft Excel.

---

## Zakładka: Dokumenty i terminy

Dwie sekcje na jednej stronie:

### Ubezpieczenia (OC / AC)

Dla każdej polisy przechowywane są:
- Numer polisy
- Firma ubezpieczeniowa
- Okres ważności (data od → data do)
- Koszt polisy
- Uwagi

Przy dodawaniu **data ważności domyślnie ustawiana jest na rok od dziś**.

> ⚠️ Data ważności nie może być wcześniejsza niż data początku.

### Przeglądy techniczne

Dla każdego przeglądu:
- Data wykonania
- Data ważności
- Koszt
- Uwagi

Przy dodawaniu **data ważności domyślnie ustawiana jest na rok od dziś**.

### Wybór daty

Kliknij pole daty lub ikonę 📅 — otworzy się kalendarz. Nawigacja po miesiącach i latach odbywa się strzałkami w kalendarzu.

---

## Zakładka: Energia / Spalanie

### Koszt eksploatacji

Karty z podsumowaniem wszystkich kosztów:

| Karta | Co zawiera |
|---|---|
| **Łączne koszty** | Suma wszystkich wpisów + ubezpieczenia + przeglądy |
| **Przebieg** | Km od startowego licznika do ostatniego wpisu |
| **Średni koszt / km** | Łączne koszty ÷ przebieg |
| **Ubezpieczenia** | Suma kosztów polis |
| **Przeglądy techniczne** | Suma kosztów przeglądów |
| Per kategoria | Paliwo, Ładowanie, Części, Obsługa itd. |

### Zużycie paliwa (L/100km)

Obliczane **tylko na podstawie tankowań do pełna** (wpisy Paliwo z zaznaczonym „Do pełna").

Wzór: `L/100km = litry / kilometry od poprzedniego pełnego tankowania × 100`

Wyświetlane są:
- Średnie, najniższe i najwyższe spalanie
- Wykres zmian spalania w czasie
- Tabela tankowań do pełna z kolumną L/100km i trasą (km)

### Zużycie energii (kWh/100km)

Widoczne tylko gdy pojazd ma wpisy w kategorii **Ładowanie** z zaznaczonym „Do pełna".

Wzór: `kWh/100km = kWh / kilometry od poprzedniego pełnego ładowania × 100`

Sekcja działa analogicznie do zużycia paliwa — wykres, statystyki i tabela.

### Hybryda plug-in

Dla hybryd obie sekcje są widoczne jednocześnie — paliwo (L/100km) i energia elektryczna (kWh/100km) — obliczane niezależnie na podstawie swoich wpisów.

> **Wskazówka:** Im więcej wpisów „Do pełna", tym dokładniejsze statystyki. Pierwszy wpis po dodaniu pojazdu nie ma obliczonego zużycia (brak punktu odniesienia).

---

## Często zadawane pytania

**Jak śledzić wymianę oleju?**
Dodaj wpis w kategorii Obsługa lub Serwis i zaznacz checkbox **Wymiana oleju**. Wskaźnik pojawi się automatycznie pod danymi pojazdu.

**Dlaczego licznik nie pozwala zapisać?**
Przy nowym wpisie licznik nie może być niższy od dotychczasowego maksimum. Sprawdź wartość wskazaną w komunikacie błędu. Przy edycji istniejącego wpisu nie ma tej blokady.

**Jak poprawić datę w kalendarzu gdy rok się nie zmienia?**
Użyj strzałek `‹` `›` do nawigacji po miesiącach lub kliknij nagłówek z miesiącem/rokiem w kalendarzu, aby przejść do widoku wyboru roku.

**Gdzie jest baza danych?**
Plik `garagebook.db` w katalogu aplikacji. Użyj funkcji kopii zapasowej w Ustawieniach lub skopiuj plik ręcznie.

---

## Ustawienia

Strona dostępna przez przycisk **Ustawienia** w pasku nawigacji.

### Waluta

Wybierz walutę wyświetlaną przy kwotach w całej aplikacji:

| Waluta | Symbol |
|---|---|
| PLN — złoty polski | zł |
| EUR — euro | € |
| USD — dolar amerykański | $ |
| GBP — funt brytyjski | £ |
| CHF — frank szwajcarski | CHF |
| CZK — korona czeska | Kč |
| NOK — korona norweska | kr |
| SEK — korona szwedzka | kr |

Po wybraniu waluty kliknij **Zapisz ustawienia**.

### Kopia zapasowa

Przycisk **Pobierz kopię zapasową** pobiera plik `garagebook_backup_YYYY-MM-DD_HH-MM-SS.db`.

Aby przywrócić dane z kopii: zastąp plik `garagebook.db` w katalogu aplikacji pobraną kopią (przed uruchomieniem aplikacji).

---

## Struktura projektu

```
Garagebook/
├── main.py              — uruchomienie aplikacji, strona pojazdu
├── Garagebook.command   — launcher macOS
├── Garagebook.sh        — launcher Linux
├── Garagebook.bat       — launcher Windows
├── start.sh             — skrypt startowy (tryb deweloperski)
├── requirements.txt     — zależności Python
├── INSTALACJA.txt       — instrukcja instalacji
├── scripts/
│   ├── macos/install.sh
│   ├── linux/install.sh
│   └── windows/install.bat
├── db/
│   ├── schema.sql       — schemat bazy danych
│   └── database.py      — wszystkie operacje na bazie
└── ui/
    ├── dashboard.py     — widok główny
    ├── vehicles.py      — zarządzanie pojazdami
    ├── entries.py       — wpisy kosztów
    ├── documents.py     — ubezpieczenia i przeglądy
    ├── settings.py      — ustawienia i kopia zapasowa
    ├── export.py        — eksport CSV
    └── layout.py        — wspólny nagłówek i kolory alertów
```
