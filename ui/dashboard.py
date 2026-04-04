from nicegui import ui
from db import database as db
from ui.layout import page_header, alert_color, alert_label


def dashboard_page() -> None:
    page_header()

    @ui.refreshable
    def content() -> None:
        vehicles = db.get_dashboard_data()
        cur = db.get_currency_symbol()

        # ── Fleet summary cards ─────────────────────────────────────────
        if vehicles:
            fleet = db.get_fleet_summary()
            with ui.row().classes('flex-wrap gap-4 q-pa-md q-pb-none'):
                with ui.card().classes('bg-indigo-50 q-pa-sm'):
                    ui.label(str(fleet['vehicle_count'])).classes('text-h5 text-indigo-900')
                    ui.label('Pojazdy').classes('text-caption text-grey-7')
                with ui.card().classes('bg-indigo-50 q-pa-sm'):
                    ui.label(f'{fleet["total_cost"]:,.2f} {cur}'.replace(',', '\u202f')).classes('text-h5 text-indigo-900')
                    ui.label('Łączne koszty').classes('text-caption text-grey-7')
                with ui.card().classes('bg-indigo-50 q-pa-sm'):
                    ui.label(f'{fleet["cost_this_month"]:,.2f} {cur}'.replace(',', '\u202f')).classes('text-h5 text-indigo-900')
                    ui.label('Koszty w tym miesiącu').classes('text-caption text-grey-7')

        # ── Reminders ───────────────────────────────────────────────────
        if vehicles:
            deadlines = []
            for v in vehicles:
                ins = v.get('insurance')
                if ins and ins.get('days_until') is not None:
                    deadlines.append({
                        'vehicle': v['name'], 'type': 'OC',
                        'days': ins['days_until'],
                        'date': ins.get('date_to', ''),
                        'vid': v['id'],
                    })
                insp = v.get('inspection')
                if insp and insp.get('days_until') is not None:
                    deadlines.append({
                        'vehicle': v['name'], 'type': 'Przegląd',
                        'days': insp['days_until'],
                        'date': insp.get('valid_until', ''),
                        'vid': v['id'],
                    })
            deadlines.sort(key=lambda d: d['days'])
            urgent = [d for d in deadlines if d['days'] <= 60]

            if urgent:
                with ui.column().classes('q-px-md q-pt-md q-pb-none gap-1'):
                    ui.label('Nadchodzące terminy').classes('text-h6')
                    with ui.element('div').classes('w-full'):
                        for d in urgent:
                            with ui.row().classes('items-center gap-2 q-py-xs cursor-pointer').on(
                                'click', lambda _, vid=d['vid']: ui.navigate.to(f'/pojazd/{vid}')
                            ):
                                ui.badge(alert_label(d['days']), color=alert_color(d['days'])).classes('text-caption')
                                ui.label(f'{d["vehicle"]} — {d["type"]}').classes('text-body2')
                                if d['date']:
                                    ui.label(f'({d["date"]})').classes('text-caption text-grey-5')

        # ── Vehicle cards ───────────────────────────────────────────────
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
