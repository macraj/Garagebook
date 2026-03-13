from nicegui import ui
from db import database as db
from ui.layout import page_header

FUEL_TYPES = ['Benzyna', 'Diesel', 'LPG', 'Elektryczny', 'Hybryda', 'CNG']


def vehicles_page() -> None:
    page_header('Pojazdy')

    @ui.refreshable
    def content() -> None:
        vehicles = db.get_all_vehicles()

        with ui.column().classes('q-pa-md w-full gap-4'):
            with ui.row().classes('items-center'):
                ui.label('Zarządzanie pojazdami').classes('text-h5')
                ui.space()
                ui.button('Dodaj pojazd', icon='add', color='primary', on_click=open_add)

            if not vehicles:
                with ui.column().classes('items-center w-full q-mt-xl gap-2'):
                    ui.icon('directions_car', size='64px').classes('text-grey-3')
                    ui.label('Brak pojazdów').classes('text-grey-5')
                return

            columns = [
                {'name': 'name', 'label': 'Nazwa', 'field': 'name', 'sortable': True, 'align': 'left'},
                {'name': 'make', 'label': 'Marka', 'field': 'make', 'sortable': True, 'align': 'left'},
                {'name': 'model', 'label': 'Model', 'field': 'model', 'sortable': True, 'align': 'left'},
                {'name': 'vin', 'label': 'VIN', 'field': 'vin', 'align': 'left'},
                {'name': 'year', 'label': 'Rok', 'field': 'year', 'sortable': True},
                {'name': 'fuel_type', 'label': 'Paliwo', 'field': 'fuel_type'},
                {'name': 'first_registration_date', 'label': '1. rejestracja', 'field': 'first_registration_date'},
                {'name': 'actions', 'label': '', 'field': 'actions'},
            ]

            table = ui.table(columns=columns, rows=vehicles, row_key='id').classes('w-full')
            table.add_slot('body-cell-actions', '''
                <q-td :props="props" auto-width>
                    <q-btn flat round dense icon="open_in_new" color="primary" size="sm"
                           title="Otwórz" @click="$parent.$emit('open', props.row)" />
                    <q-btn flat round dense icon="edit" color="secondary" size="sm"
                           title="Edytuj" @click="$parent.$emit('edit', props.row)" />
                    <q-btn flat round dense icon="delete" color="negative" size="sm"
                           title="Usuń" @click="$parent.$emit('delete', props.row)" />
                </q-td>
            ''')
            table.on('open', lambda e: ui.navigate.to(f'/pojazd/{e.args["id"]}'))
            table.on('edit', lambda e: open_edit(e.args))
            table.on('delete', lambda e: open_delete(e.args))

    def _vehicle_dialog(on_save, vehicle: dict | None = None) -> ui.dialog:
        is_edit = vehicle is not None
        with ui.dialog() as dialog, ui.card().classes('w-[480px]'):
            ui.label('Edytuj pojazd' if is_edit else 'Nowy pojazd').classes('text-h6 q-mb-sm')

            with ui.column().classes('w-full gap-2'):
                name = ui.input('Nazwa *', value=vehicle.get('name', '') if is_edit else '').classes('w-full')
                with ui.row().classes('w-full gap-2'):
                    make = ui.input('Marka', value=vehicle.get('make', '') if is_edit else '').classes('flex-1')
                    model = ui.input('Model', value=vehicle.get('model', '') if is_edit else '').classes('flex-1')
                vin = ui.input('VIN', value=vehicle.get('vin', '') if is_edit else '').classes('w-full')
                with ui.row().classes('w-full gap-2'):
                    year = ui.number(
                        'Rok produkcji',
                        value=vehicle.get('year') if is_edit else None,
                        min=1900, max=2100, precision=0,
                    ).classes('flex-1')
                    fuel = ui.select(
                        FUEL_TYPES,
                        label='Rodzaj paliwa',
                        value=vehicle.get('fuel_type') if is_edit else None,
                    ).classes('flex-1')
                reg_date = ui.input(
                    'Data 1. rejestracji',
                    value=vehicle.get('first_registration_date', '') if is_edit else '',
                ).props('type=date').classes('w-full')
                initial_odo = ui.number(
                    'Startowy licznik (km)',
                    value=vehicle.get('initial_odometer') if is_edit else None,
                    min=0, precision=0,
                ).classes('w-full')
                if not is_edit:
                    ui.label('Aktualny przebieg przy dodawaniu pojazdu — będzie minimalną wartością licznika.') \
                        .classes('text-caption text-grey-5')

            def save():
                if not name.value.strip():
                    ui.notify('Nazwa jest wymagana', type='warning')
                    return
                data = {
                    'name': name.value.strip(),
                    'make': make.value.strip() or None,
                    'model': model.value.strip() or None,
                    'vin': vin.value.strip() or None,
                    'year': int(year.value) if year.value else None,
                    'fuel_type': fuel.value,
                    'first_registration_date': reg_date.value or None,
                    'initial_odometer': int(initial_odo.value) if initial_odo.value else None,
                }
                on_save(data)
                dialog.close()

            with ui.row().classes('justify-end gap-2 q-mt-md'):
                ui.button('Anuluj', on_click=dialog.close).props('flat')
                ui.button('Zapisz', on_click=save, color='primary')

        return dialog

    def open_add():
        def save(data):
            db.create_vehicle(data)
            ui.notify('Pojazd dodany', type='positive')
            content.refresh()
        _vehicle_dialog(save).open()

    def open_edit(vehicle_data: dict):
        def save(data):
            db.update_vehicle(vehicle_data['id'], data)
            ui.notify('Pojazd zaktualizowany', type='positive')
            content.refresh()
        _vehicle_dialog(save, vehicle_data).open()

    def open_delete(vehicle_data: dict):
        with ui.dialog() as d, ui.card():
            ui.label(f'Usunąć pojazd „{vehicle_data["name"]}"?').classes('text-body1')
            ui.label('Zostaną usunięte wszystkie powiązane wpisy, ubezpieczenia i przeglądy.').\
                classes('text-caption text-grey-6 q-mt-xs')
            with ui.row().classes('justify-end gap-2 q-mt-md'):
                ui.button('Anuluj', on_click=d.close).props('flat')
                def confirm():
                    db.delete_vehicle(vehicle_data['id'])
                    ui.notify('Pojazd usunięty', type='negative')
                    content.refresh()
                    d.close()
                ui.button('Usuń', on_click=confirm, color='negative')
        d.open()

    content()
