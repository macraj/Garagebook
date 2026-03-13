import csv
import io
from nicegui import ui
from db import database as db


def export_csv_button(vehicle_id: int, vehicle_name: str) -> None:
    """Renders an export-to-CSV button."""

    def do_export():
        entries = db.get_vehicle_entries(vehicle_id)
        if not entries:
            ui.notify('Brak wpisów do eksportu', type='warning')
            return

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(['Data', 'Rodzaj', 'Ilość', 'Kwota', 'Licznik', 'Opis', 'ID', 'Do pełna'])
        for e in entries:
            writer.writerow([
                e.get('date', ''),
                e.get('category', ''),
                e.get('quantity', ''),
                e.get('amount', ''),
                e.get('odometer', ''),
                e.get('description', ''),
                e.get('user_code', ''),
                'T' if e.get('full_tank') else 'N',
            ])

        # utf-8-sig adds BOM so Excel opens the file correctly
        csv_bytes = buf.getvalue().encode('utf-8-sig')
        safe_name = vehicle_name.replace(' ', '_')
        ui.download(csv_bytes, f'{safe_name}_wpisy.csv')
        ui.notify('Eksport CSV gotowy', type='positive')

    ui.button('Eksport CSV', icon='download', on_click=do_export).props('outline')
