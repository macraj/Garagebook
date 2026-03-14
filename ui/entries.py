from datetime import date
from nicegui import ui
from db import database as db

CATEGORIES = ['Paliwo', 'Ładowanie', 'Części', 'Obsługa', 'Usterka', 'Serwis']


def entries_tab(vehicle_id: int) -> None:
    filter_state = {'category': '', 'date_from': '', 'date_to': ''}
    raw_cache: list[dict] = []

    @ui.refreshable
    def entries_content() -> None:
        cur = db.get_currency_symbol()
        entries = db.get_vehicle_entries(
            vehicle_id,
            filter_state['category'],
            filter_state['date_from'],
            filter_state['date_to'],
        )
        raw_cache.clear()
        raw_cache.extend(entries)

        # Summary cards
        total_amount = sum(e.get('amount') or 0 for e in entries)
        total_fuel_l   = sum(e.get('quantity') or 0 for e in entries if e['category'] == 'Paliwo')
        total_charge_kwh = sum(e.get('quantity') or 0 for e in entries if e['category'] == 'Ładowanie')

        with ui.row().classes('gap-3 q-mb-md flex-wrap'):
            with ui.card().classes('bg-blue-50 q-pa-sm'):
                ui.label(f'{total_amount:,.2f} {cur}'.replace(',', '\u202f')).classes('text-h6 text-blue-900')
                ui.label('Łączny koszt').classes('text-caption text-grey-6')
            if total_fuel_l > 0:
                with ui.card().classes('bg-green-50 q-pa-sm'):
                    ui.label(f'{total_fuel_l:.2f} L').classes('text-h6 text-green-900')
                    ui.label('Łącznie paliwo').classes('text-caption text-grey-6')
            if total_charge_kwh > 0:
                with ui.card().classes('bg-purple-50 q-pa-sm'):
                    ui.label(f'{total_charge_kwh:.2f} kWh').classes('text-h6 text-purple-900')
                    ui.label('Łącznie ładowanie').classes('text-caption text-grey-6')
            ui.label(f'{len(entries)} wpisów').classes('text-caption text-grey-5 self-end q-pb-xs')

        if not entries:
            ui.label('Brak wpisów dla wybranych filtrów.').classes('text-grey-5 q-mt-sm')
            return

        columns = [
            {'name': 'date',        'label': 'Data',          'field': 'date',        'sortable': True, 'align': 'left'},
            {'name': 'category',    'label': 'Rodzaj',         'field': 'category',    'sortable': True, 'align': 'left'},
            {'name': 'quantity',    'label': 'Ilość',          'field': 'quantity_fmt','align': 'right'},
            {'name': 'amount',      'label': f'Kwota ({cur})', 'field': 'amount_fmt',  'sortable': True, 'align': 'right'},
            {'name': 'odometer',    'label': 'Licznik (km)',   'field': 'odometer_fmt','sortable': True, 'align': 'right'},
            {'name': 'full_tank',   'label': 'Do pełna',       'field': 'full_tank_fmt'},
            {'name': 'oil_change',  'label': 'Olej',           'field': 'oil_change_fmt'},
            {'name': 'description', 'label': 'Opis',           'field': 'description', 'align': 'left'},
            {'name': 'user_code',   'label': 'ID',             'field': 'user_code'},
            {'name': 'actions',     'label': '',               'field': 'actions'},
        ]

        rows = []
        for e in entries:
            rows.append({
                **e,
                'quantity_fmt':  f"{e['quantity']:.2f}"               if e.get('quantity')  else '—',
                'amount_fmt':    f"{e['amount']:.2f}"                  if e.get('amount')    else '—',
                'odometer_fmt':  f"{e['odometer']:,}".replace(',', '\u202f') if e.get('odometer') else '—',
                'full_tank_fmt': '✓' if e.get('full_tank') else '',
                'oil_change_fmt': '🔧' if e.get('oil_change') else '',
            })

        table = ui.table(
            columns=columns, rows=rows, row_key='id',
            pagination={'rowsPerPage': 25, 'sortBy': 'date', 'descending': True},
        ).classes('w-full')

        table.add_slot('body-cell-category', '''
            <q-td :props="props">
                <q-badge :color="{'Paliwo':'green','Ładowanie':'deep-purple','Części':'blue',
                                   'Obsługa':'teal','Usterka':'red','Serwis':'orange'}[props.value] || 'grey'"
                         :label="props.value" />
            </q-td>
        ''')
        table.add_slot('body-cell-actions', '''
            <q-td :props="props" auto-width>
                <q-btn flat round dense icon="edit" color="secondary" size="sm"
                       @click="$parent.$emit('edit', props.row)" />
                <q-btn flat round dense icon="delete" color="negative" size="sm"
                       @click="$parent.$emit('delete', props.row)" />
            </q-td>
        ''')
        table.on('edit',   lambda e: _open_edit(e.args))
        table.on('delete', lambda e: _open_delete(e.args))

    def _entry_dialog(on_save, entry: dict | None = None) -> ui.dialog:
        is_edit = entry is not None
        with ui.dialog() as dialog, ui.card().classes('w-[440px]'):
            ui.label('Edytuj wpis' if is_edit else 'Nowy wpis').classes('text-h6 q-mb-sm')

            with ui.column().classes('w-full gap-2'):
                date_in = ui.input(
                    'Data *',
                    value=entry.get('date', str(date.today())) if is_edit else str(date.today()),
                ).props('type=date').classes('w-full')

                category = ui.select(
                    CATEGORIES, label='Rodzaj *',
                    value=entry.get('category', CATEGORIES[0]) if is_edit else CATEGORIES[0],
                ).classes('w-full')

                with ui.row().classes('w-full gap-2'):
                    quantity = ui.number(
                        'Ilość',
                        value=entry.get('quantity') if is_edit else None,
                        min=0, format='%.3f',
                    ).classes('flex-1')
                    amount = ui.number(
                        f'Kwota ({db.get_currency_symbol()})',
                        value=entry.get('amount') if is_edit else None,
                        min=0, format='%.2f',
                    ).classes('flex-1')

                odometer = ui.number(
                    'Licznik (km)',
                    value=entry.get('odometer') if is_edit else None,
                    min=0, precision=0,
                ).classes('w-full')

                description = ui.textarea(
                    'Opis',
                    value=entry.get('description', '') if is_edit else '',
                ).classes('w-full').props('rows=3 autogrow')

                user_code = ui.input(
                    'ID kierowcy (np. MR)',
                    value=entry.get('user_code', '') if is_edit else '',
                ).classes('w-full')

                full_tank_row = ui.row().classes('items-center')
                with full_tank_row:
                    full_tank = ui.checkbox(
                        'Do pełna',
                        value=bool(entry.get('full_tank')) if is_edit else False,
                    )

                oil_change_row = ui.row().classes('items-center')
                with oil_change_row:
                    oil_change = ui.checkbox(
                        'Wymiana oleju',
                        value=bool(entry.get('oil_change')) if is_edit else False,
                    )

                def _update_ui():
                    is_fuel   = category.value == 'Paliwo'
                    is_charge = category.value == 'Ładowanie'
                    full_tank_row.set_visibility(is_fuel or is_charge)
                    oil_change_row.set_visibility(not is_fuel and not is_charge)
                    if is_fuel:
                        quantity.props('label="Ilość (L)"')
                    elif is_charge:
                        quantity.props('label="Ilość (kWh)"')
                    else:
                        quantity.props('label="Ilość (szt)"')

                category.on_value_change(lambda _: _update_ui())
                _update_ui()

            def save():
                if not date_in.value:
                    ui.notify('Data jest wymagana', type='warning')
                    return
                if odometer.value and not is_edit:
                    new_odo = int(odometer.value)
                    max_odo = db.get_max_odometer(vehicle_id)
                    if new_odo < max_odo:
                        ui.notify(
                            f'Licznik nie może być niższy od poprzedniego wpisu ({max_odo:,} km)'.replace(',', '\u202f'),
                            type='negative',
                        )
                        return
                data = {
                    'vehicle_id':  vehicle_id,
                    'date':        date_in.value,
                    'category':    category.value,
                    'quantity':    quantity.value or 0,
                    'amount':      amount.value or 0,
                    'odometer':    int(odometer.value) if odometer.value else None,
                    'description': (description.value or "").strip() or None,
                    'user_code':   (user_code.value or "").strip() or None,
                    'full_tank':   1 if (category.value in ('Paliwo', 'Ładowanie') and full_tank.value) else 0,
                    'oil_change':  1 if (category.value not in ('Paliwo', 'Ładowanie') and oil_change.value) else 0,
                }
                on_save(data)
                dialog.close()

            with ui.row().classes('justify-end gap-2 q-mt-md'):
                ui.button('Anuluj', on_click=dialog.close).props('flat')
                ui.button('Zapisz', on_click=save, color='primary')

        return dialog

    def _open_add():
        def save(data):
            db.create_entry(data)
            ui.notify('Wpis dodany', type='positive')
            entries_content.refresh()
        _entry_dialog(save).open()

    def _open_edit(display_row: dict):
        raw = next((e for e in raw_cache if e['id'] == display_row['id']), None)
        if not raw:
            return
        def save(data):
            db.update_entry(raw['id'], data)
            ui.notify('Wpis zaktualizowany', type='positive')
            entries_content.refresh()
        _entry_dialog(save, raw).open()

    def _open_delete(display_row: dict):
        with ui.dialog() as d, ui.card():
            ui.label(f'Usunąć wpis z dnia {display_row.get("date", "?")}?').classes('text-body1')
            with ui.row().classes('justify-end gap-2 q-mt-md'):
                ui.button('Anuluj', on_click=d.close).props('flat')
                def confirm():
                    db.delete_entry(display_row['id'])
                    ui.notify('Wpis usunięty', type='negative')
                    entries_content.refresh()
                    d.close()
                ui.button('Usuń', on_click=confirm, color='negative')
        d.open()

    # Filter bar
    with ui.row().classes('items-end gap-3 q-mb-md flex-wrap'):
        cat_filter  = ui.select([''] + CATEGORIES, label='Kategoria', value='').classes('w-40')
        date_from   = ui.input('Od', placeholder='YYYY-MM-DD').props('type=date').classes('w-36')
        date_to     = ui.input('Do', placeholder='YYYY-MM-DD').props('type=date').classes('w-36')

        def apply_filters():
            filter_state['category']  = cat_filter.value or ''
            filter_state['date_from'] = date_from.value or ''
            filter_state['date_to']   = date_to.value or ''
            entries_content.refresh()

        def clear_filters():
            cat_filter.value = ''
            date_from.value  = ''
            date_to.value    = ''
            filter_state.update({'category': '', 'date_from': '', 'date_to': ''})
            entries_content.refresh()

        ui.button('Filtruj', icon='filter_list', on_click=apply_filters).props('outline')
        ui.button('Wyczyść', icon='clear', on_click=clear_filters).props('flat')
        ui.space()
        ui.button('Dodaj wpis', icon='add', color='primary', on_click=_open_add)

    entries_content()
