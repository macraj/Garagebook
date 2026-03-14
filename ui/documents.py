from datetime import date
from nicegui import ui
from db import database as db
from ui.layout import alert_color, alert_label


def _next_year() -> str:
    today = date.today()
    try:
        return today.replace(year=today.year + 1).isoformat()
    except ValueError:  # 29 lutego
        return today.replace(year=today.year + 1, day=28).isoformat()


def _date_picker(label: str, value: str = '') -> ui.input:
    """Pole tekstowe YYYY-MM-DD z kalendarzem Quasar jako popup — bez problemów z edycją roku."""
    with ui.input(label, value=value).props('readonly') as inp:
        with inp.add_slot('append'):
            ui.icon('event').classes('cursor-pointer').on('click', lambda: menu.open())
        with ui.menu().props('no-parent-event') as menu:
            picker = ui.date(value=value or None).props('mask="YYYY-MM-DD"')
            picker.on_value_change(lambda e: inp.set_value(e.value or ''))
            with ui.row().classes('justify-end q-pa-xs'):
                ui.button('Zamknij', on_click=menu.close).props('flat dense')
    inp.on('focus', menu.open)
    return inp


def documents_tab(vehicle_id: int) -> None:

    # ─── Insurance ──────────────────────────────────────────────────────────

    @ui.refreshable
    def insurance_section() -> None:
        records = db.get_vehicle_insurance(vehicle_id)
        with ui.column().classes('w-full gap-2'):
            with ui.row().classes('items-center'):
                ui.label('Ubezpieczenia (OC / AC)').classes('text-h6')
                ui.space()
                ui.button('Dodaj', icon='add', on_click=_open_add_insurance).props('outline dense')

            if not records:
                ui.label('Brak danych ubezpieczeniowych.').classes('text-grey-5')
                return

            for r in records:
                _insurance_card(r)

    def _insurance_card(r: dict) -> None:
        days = r.get('days_until')
        with ui.card().classes('w-full'):
            with ui.row().classes('items-center justify-between no-wrap'):
                with ui.column().classes('gap-0'):
                    ui.label(
                        f'{r.get("company") or "—"}  ·  Nr polisy: {r.get("policy_number") or "—"}'
                    ).classes('text-body1 text-bold')
                    ui.label(
                        f'{r.get("date_from") or "?"}  →  {r.get("date_to") or "?"}'
                    ).classes('text-caption text-grey-7')
                    if r.get('cost'):
                        ui.label(f'Koszt: {r["cost"]:.2f} {db.get_currency_symbol()}').classes('text-caption text-grey-6')
                    if r.get('notes'):
                        ui.label(r['notes']).classes('text-caption text-grey-5')
                with ui.row().classes('items-center gap-2 no-wrap'):
                    ui.badge(alert_label(days), color=alert_color(days))
                    ui.button(icon='edit',   on_click=lambda _, rec=r: _open_edit_insurance(rec)).props('flat round dense')
                    ui.button(icon='delete', on_click=lambda _, rec=r: _open_delete_insurance(rec)).props('flat round dense color=negative')

    def _insurance_dialog(on_save, record: dict | None = None) -> ui.dialog:
        is_edit = record is not None
        default_to = record.get('date_to', '') if is_edit else _next_year()

        with ui.dialog() as dialog, ui.card().classes('w-[440px]'):
            ui.label('Ubezpieczenie').classes('text-h6 q-mb-sm')
            with ui.column().classes('w-full gap-2'):
                policy  = ui.input('Nr polisy',             value=record.get('policy_number', '') if is_edit else '').classes('w-full')
                company = ui.input('Firma ubezpieczeniowa', value=record.get('company', '')        if is_edit else '').classes('w-full')
                with ui.row().classes('w-full gap-2'):
                    d_from = _date_picker('Data od',    value=record.get('date_from', '') if is_edit else date.today().isoformat())
                    d_from.classes('flex-1')
                    d_to   = _date_picker('Ważne do',   value=default_to)
                    d_to.classes('flex-1')
                cost  = ui.number(f'Koszt ({db.get_currency_symbol()})', value=record.get('cost', 0) if is_edit else 0, min=0, format='%.2f').classes('w-full')
                notes = ui.input('Uwagi',        value=record.get('notes', '') if is_edit else '').classes('w-full')

            def save():
                if d_from.value and d_to.value and d_to.value < d_from.value:
                    ui.notify('Data ważności nie może być wcześniejsza niż data początku', type='negative')
                    return
                on_save({
                    'vehicle_id':    vehicle_id,
                    'policy_number': (policy.value or "").strip()  or None,
                    'company':       (company.value or "").strip() or None,
                    'date_from':     d_from.value or None,
                    'date_to':       d_to.value   or None,
                    'cost':          cost.value   or 0,
                    'notes':         (notes.value or "").strip() or None,
                })
                dialog.close()

            with ui.row().classes('justify-end gap-2 q-mt-md'):
                ui.button('Anuluj', on_click=dialog.close).props('flat')
                ui.button('Zapisz', on_click=save, color='primary')
        return dialog

    def _open_add_insurance():
        def save(data):
            db.create_insurance(data)
            ui.notify('Ubezpieczenie dodane', type='positive')
            insurance_section.refresh()
        _insurance_dialog(save).open()

    def _open_edit_insurance(record: dict):
        def save(data):
            db.update_insurance(record['id'], data)
            ui.notify('Ubezpieczenie zaktualizowane', type='positive')
            insurance_section.refresh()
        _insurance_dialog(save, record).open()

    def _open_delete_insurance(record: dict):
        with ui.dialog() as d, ui.card():
            ui.label('Usunąć to ubezpieczenie?').classes('text-body1')
            with ui.row().classes('justify-end gap-2 q-mt-md'):
                ui.button('Anuluj', on_click=d.close).props('flat')
                def confirm():
                    db.delete_insurance(record['id'])
                    ui.notify('Ubezpieczenie usunięte', type='negative')
                    insurance_section.refresh()
                    d.close()
                ui.button('Usuń', on_click=confirm, color='negative')
        d.open()

    # ─── Technical Inspections ──────────────────────────────────────────────

    @ui.refreshable
    def inspections_section() -> None:
        records = db.get_vehicle_inspections(vehicle_id)
        with ui.column().classes('w-full gap-2'):
            with ui.row().classes('items-center'):
                ui.label('Przeglądy techniczne').classes('text-h6')
                ui.space()
                ui.button('Dodaj', icon='add', on_click=_open_add_inspection).props('outline dense')

            if not records:
                ui.label('Brak przeglądów technicznych.').classes('text-grey-5')
                return

            for r in records:
                _inspection_card(r)

    def _inspection_card(r: dict) -> None:
        days = r.get('days_until')
        with ui.card().classes('w-full'):
            with ui.row().classes('items-center justify-between no-wrap'):
                with ui.column().classes('gap-0'):
                    ui.label(
                        f'Data przeglądu: {r.get("date") or "?"}  ·  Ważny do: {r.get("valid_until") or "?"}'
                    ).classes('text-body1 text-bold')
                    if r.get('cost'):
                        ui.label(f'Koszt: {r["cost"]:.2f} {db.get_currency_symbol()}').classes('text-caption text-grey-6')
                    if r.get('notes'):
                        ui.label(r['notes']).classes('text-caption text-grey-5')
                with ui.row().classes('items-center gap-2 no-wrap'):
                    ui.badge(alert_label(days), color=alert_color(days))
                    ui.button(icon='edit',   on_click=lambda _, rec=r: _open_edit_inspection(rec)).props('flat round dense')
                    ui.button(icon='delete', on_click=lambda _, rec=r: _open_delete_inspection(rec)).props('flat round dense color=negative')

    def _inspection_dialog(on_save, record: dict | None = None) -> ui.dialog:
        is_edit = record is not None
        default_valid = record.get('valid_until', '') if is_edit else _next_year()

        with ui.dialog() as dialog, ui.card().classes('w-[440px]'):
            ui.label('Przegląd techniczny').classes('text-h6 q-mb-sm')
            with ui.column().classes('w-full gap-2'):
                with ui.row().classes('w-full gap-2'):
                    insp_date   = _date_picker('Data przeglądu', value=record.get('date', '') if is_edit else date.today().isoformat())
                    insp_date.classes('flex-1')
                    valid_until = _date_picker('Ważny do', value=default_valid)
                    valid_until.classes('flex-1')
                cost  = ui.number(f'Koszt ({db.get_currency_symbol()})', value=record.get('cost', 0) if is_edit else 0, min=0, format='%.2f').classes('w-full')
                notes = ui.input('Uwagi',        value=record.get('notes', '') if is_edit else '').classes('w-full')

            def save():
                if insp_date.value and valid_until.value and valid_until.value < insp_date.value:
                    ui.notify('Data ważności nie może być wcześniejsza niż data przeglądu', type='negative')
                    return
                on_save({
                    'vehicle_id':  vehicle_id,
                    'date':        insp_date.value   or None,
                    'valid_until': valid_until.value or None,
                    'cost':        cost.value        or 0,
                    'notes':       (notes.value or "").strip() or None,
                })
                dialog.close()

            with ui.row().classes('justify-end gap-2 q-mt-md'):
                ui.button('Anuluj', on_click=dialog.close).props('flat')
                ui.button('Zapisz', on_click=save, color='primary')
        return dialog

    def _open_add_inspection():
        def save(data):
            db.create_inspection(data)
            ui.notify('Przegląd dodany', type='positive')
            inspections_section.refresh()
        _inspection_dialog(save).open()

    def _open_edit_inspection(record: dict):
        def save(data):
            db.update_inspection(record['id'], data)
            ui.notify('Przegląd zaktualizowany', type='positive')
            inspections_section.refresh()
        _inspection_dialog(save, record).open()

    def _open_delete_inspection(record: dict):
        with ui.dialog() as d, ui.card():
            ui.label('Usunąć ten przegląd?').classes('text-body1')
            with ui.row().classes('justify-end gap-2 q-mt-md'):
                ui.button('Anuluj', on_click=d.close).props('flat')
                def confirm():
                    db.delete_inspection(record['id'])
                    ui.notify('Przegląd usunięty', type='negative')
                    inspections_section.refresh()
                    d.close()
                ui.button('Usuń', on_click=confirm, color='negative')
        d.open()

    # ─── Render ─────────────────────────────────────────────────────────────
    insurance_section()
    ui.separator().classes('q-my-lg')
    inspections_section()
