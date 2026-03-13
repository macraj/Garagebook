from nicegui import ui
from db import database as db
from ui.layout import page_header, alert_color, alert_label


def dashboard_page() -> None:
    page_header()

    @ui.refreshable
    def content() -> None:
        vehicles = db.get_dashboard_data()

        with ui.row().classes('items-center q-pa-md q-pb-sm'):
            ui.label('Flota pojazdów').classes('text-h5')
            ui.space()
            ui.button('Zarządzaj pojazdami', icon='settings', on_click=lambda: ui.navigate.to('/pojazdy')).props('outline')

        if not vehicles:
            with ui.column().classes('items-center w-full q-mt-xl gap-2'):
                ui.icon('directions_car', size='72px').classes('text-grey-3')
                ui.label('Brak pojazdów').classes('text-h6 text-grey-5')
                ui.button('Dodaj pierwszy pojazd', icon='add', color='primary',
                          on_click=lambda: ui.navigate.to('/pojazdy'))
            return

        with ui.row().classes('flex-wrap gap-4 q-px-md'):
            for v in vehicles:
                _vehicle_card(v)

    content()


def _vehicle_card(v: dict) -> None:
    with (ui.card()
          .classes('w-72 cursor-pointer hover:shadow-md transition-shadow')
          .on('click', lambda vid=v['id']: ui.navigate.to(f'/pojazd/{vid}'))):

        with ui.card_section().classes('bg-indigo-50 q-py-sm'):
            ui.label(v['name'] or '—').classes('text-h6 text-indigo-900')
            sub = ' '.join(filter(None, [
                v.get('make') or '',
                v.get('model') or '',
                str(v.get('year') or ''),
            ])).strip()
            if sub:
                ui.label(sub).classes('text-caption text-grey-7')

        with ui.card_section().classes('q-py-sm'):
            odo = v.get('last_odometer')
            with ui.row().classes('items-center gap-1 q-mb-xs'):
                ui.icon('speed', size='16px').classes('text-grey-5')
                odo_text = f'{odo:,} km'.replace(',', '\u202f') if odo else '—'
                ui.label(f'Licznik: {odo_text}').classes('text-body2')

            ui.separator().classes('q-my-xs')

            # Insurance row
            ins = v.get('insurance')
            with ui.row().classes('items-center gap-2 q-mb-xs'):
                ui.icon('verified_user', size='16px').classes('text-grey-5')
                if ins:
                    days = ins.get('days_until')
                    ui.label('OC:').classes('text-body2 text-grey-7')
                    ui.badge(alert_label(days), color=alert_color(days)).classes('text-caption')
                else:
                    ui.label('OC: brak danych').classes('text-body2 text-grey-5')

            # Inspection row
            insp = v.get('inspection')
            with ui.row().classes('items-center gap-2'):
                ui.icon('build_circle', size='16px').classes('text-grey-5')
                if insp:
                    days = insp.get('days_until')
                    ui.label('Przegląd:').classes('text-body2 text-grey-7')
                    ui.badge(alert_label(days), color=alert_color(days)).classes('text-caption')
                else:
                    ui.label('Przegląd: brak danych').classes('text-body2 text-grey-5')
