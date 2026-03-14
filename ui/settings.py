from pathlib import Path
from datetime import datetime
from nicegui import ui
from db import database as db
from ui.layout import page_header


def settings_page() -> None:
    page_header('Ustawienia')

    with ui.column().classes('q-pa-md w-full gap-6 max-w-xl'):

        # ── Waluta ──────────────────────────────────────────────────────────
        ui.label('Waluta').classes('text-h5')
        ui.separator()
        ui.label(
            'Wybierz walutę wyświetlaną przy kwotach. '
            'Zmiana dotyczy tylko oznaczenia — przeliczenie wartości należy do użytkownika.'
        ).classes('text-body2 text-grey-7')

        current_currency = db.get_setting('currency', 'PLN')
        currency_select = ui.select(
            options={k: f'{k}  ({v})' for k, v in db.CURRENCY_SYMBOLS.items()},
            value=current_currency,
            label='Waluta',
        ).classes('w-52')

        def save_currency():
            db.set_setting('currency', currency_select.value)
            ui.notify(f'Waluta zmieniona na {currency_select.value}', type='positive')

        ui.button('Zapisz', icon='save', on_click=save_currency, color='primary')

        ui.separator().classes('q-my-sm')

        # ── Kopia zapasowa ──────────────────────────────────────────────────
        ui.label('Kopia zapasowa').classes('text-h5')
        ui.separator()
        ui.label(
            'Pobierz plik bazy danych. Przechowuj kopię w bezpiecznym miejscu.'
        ).classes('text-body2 text-grey-7')

        def do_backup():
            db_path = Path('garagebook.db')
            if not db_path.exists():
                ui.notify('Baza danych nie istnieje', type='warning')
                return
            data = db_path.read_bytes()
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            ui.download(data, f'garagebook_backup_{ts}.db')
            ui.notify('Kopia zapasowa pobrana', type='positive')

        ui.button('Pobierz kopię zapasową', icon='backup', on_click=do_backup, color='secondary')
        ui.label(
            'Aby przywrócić: zastąp plik garagebook.db pobraną kopią (przy wyłączonej aplikacji).'
        ).classes('text-caption text-grey-5 q-mt-xs')
