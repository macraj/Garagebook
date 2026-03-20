import platform
import subprocess
from pathlib import Path
from nicegui import ui
from db import database as db
from ui.layout import page_header


def _reveal_in_files(path: Path):
    system = platform.system()
    if system == 'Darwin':
        subprocess.Popen(['open', '-R', str(path)])
    elif system == 'Windows':
        subprocess.Popen(['explorer', '/select,', str(path)])
    else:
        subprocess.Popen(['xdg-open', str(path.parent)])


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
            'Backup to kopia pliku bazy danych. '
            'Przechowywany w podfolderze backups/ w katalogu aplikacji.'
        ).classes('text-body2 text-grey-7')

        # ── Dialog przywracania ─────────────────────────────────────────────
        restore_state: dict = {'path': None, 'name': ''}

        with ui.dialog() as restore_dialog, ui.card().classes('max-w-md'):
            ui.label('Przywróć kopię zapasową?').classes('text-lg text-bold')
            restore_info = ui.label('').classes('text-body2 text-grey-8 q-mt-xs')
            ui.label(
                'UWAGA: Bieżące dane zostaną nadpisane. '
                'Operacji nie można cofnąć.'
            ).classes('text-body2 text-red q-mt-sm')
            with ui.row().classes('justify-end gap-2 q-mt-md'):
                ui.button('Anuluj', on_click=restore_dialog.close).props('flat')

                def do_restore():
                    try:
                        db.restore_db(restore_state['path'])
                        restore_dialog.close()
                        ui.notify('Baza danych przywrócona. Przekierowuję...', type='positive')
                        ui.navigate.to('/')
                    except Exception as ex:
                        ui.notify(f'Błąd przywracania: {ex}', type='negative')

                ui.button('Przywróć', icon='restore', on_click=do_restore).props('color=red')

        # ── Lista backupów ──────────────────────────────────────────────────
        @ui.refreshable
        def backup_list():
            backups = db.list_backups()
            if not backups:
                ui.label('Brak kopii zapasowych.').classes('text-body2 text-grey-5 q-py-sm')
                return

            with ui.column().classes('w-full'):
                for bp in backups:
                    size_kb = bp.stat().st_size / 1024
                    size_str = f'{size_kb:.0f} KB' if size_kb < 1024 else f'{size_kb / 1024:.1f} MB'
                    with ui.row().classes('w-full items-center q-py-xs gap-2'):
                        ui.icon('storage').classes('text-grey-5')
                        ui.label(bp.name).classes('text-caption text-weight-medium').style('font-family: monospace; flex: 1')
                        ui.label(size_str).classes('text-caption text-grey-6')
                        ui.button(
                            icon='restore',
                            on_click=lambda _, p=bp: [
                                restore_state.update({'path': p, 'name': p.name}),
                                restore_info.set_text(f'Plik: {p.name}'),
                                restore_dialog.open(),
                            ],
                        ).props('flat dense color=orange size=sm').tooltip('Przywróć')
                        ui.button(
                            icon='delete',
                            on_click=lambda _, p=bp: [
                                db.delete_backup(p),
                                backup_list.refresh(),
                                ui.notify('Backup usunięty', type='warning'),
                            ],
                        ).props('flat dense color=red size=sm').tooltip('Usuń')

        # ── Przyciski akcji ─────────────────────────────────────────────────
        with ui.row().classes('gap-2 q-mb-sm'):
            def make_backup():
                try:
                    path = db.backup_db()
                    backup_list.refresh()
                    ui.notify(f'Backup utworzony: {path.name}', type='positive')
                except Exception as ex:
                    ui.notify(f'Błąd tworzenia backupu: {ex}', type='negative')

            ui.button('Utwórz backup', icon='backup', on_click=make_backup, color='primary')
            ui.button(
                'Otwórz folder backupów',
                icon='folder_open',
                on_click=lambda: (
                    db.BACKUPS_DIR.mkdir(exist_ok=True),
                    _reveal_in_files(db.BACKUPS_DIR),
                ),
            ).props('flat color=grey-7')

        backup_list()

        ui.label(
            'Aby przywrócić ręcznie: zastąp plik garagebook.db pobraną kopią (przy wyłączonej aplikacji).'
        ).classes('text-caption text-grey-5 q-mt-xs')
