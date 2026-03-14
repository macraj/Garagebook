from nicegui import ui
from db import database as db
from ui.layout import page_header
from ui.dashboard import dashboard_page
from ui.vehicles import vehicles_page
from ui.entries import entries_tab
from ui.documents import documents_tab
from ui.export import export_csv_button


@ui.page('/')
def index() -> None:
    dashboard_page()


@ui.page('/pojazdy')
def vehicles() -> None:
    vehicles_page()


@ui.page('/pojazd/{vehicle_id}')
def vehicle_detail(vehicle_id: int) -> None:
    vehicle = db.get_vehicle(vehicle_id)
    if not vehicle:
        ui.notify('Pojazd nie istnieje', type='negative')
        ui.navigate.to('/')
        return

    page_header(vehicle['name'])

    with ui.column().classes('q-pa-md w-full gap-2'):
        # Info bar under header
        info_parts = list(filter(None, [
            vehicle.get('make'),
            vehicle.get('model'),
            str(vehicle.get('year') or ''),
            vehicle.get('fuel_type'),
        ]))
        if info_parts:
            ui.label(' · '.join(info_parts)).classes('text-subtitle2 text-grey-7')
        if vehicle.get('vin'):
            ui.label(f'VIN: {vehicle["vin"]}').classes('text-caption text-grey-5')
        if vehicle.get('first_registration_date'):
            ui.label(f'1. rejestracja: {vehicle["first_registration_date"]}').classes('text-caption text-grey-5')

        # Wskaźnik ostatniej wymiany oleju
        oil = db.get_last_oil_change(vehicle_id)
        with ui.row().classes('items-center gap-3 q-mt-xs flex-wrap'):
            ui.icon('oil_barrel', size='18px').classes('text-grey-5')
            if oil:
                ui.label(f'Ostatnia wymiana oleju: {oil["date"]}').classes('text-caption text-grey-7')
                if oil.get('days_since') is not None:
                    color = 'text-negative' if oil['days_since'] > 365 else 'text-warning' if oil['days_since'] > 270 else 'text-positive'
                    ui.label(f'{oil["days_since"]} dni').classes(f'text-caption text-bold {color}')
                if oil.get('km_since') is not None:
                    color = 'text-negative' if oil['km_since'] > 15000 else 'text-warning' if oil['km_since'] > 10000 else 'text-positive'
                    ui.label(f'{oil["km_since"]:,} km'.replace(',', '\u202f')).classes(f'text-caption text-bold {color}')
            else:
                ui.label('Brak zarejestrowanej wymiany oleju').classes('text-caption text-grey-4')

        ui.separator().classes('q-my-xs')

        with ui.tabs().classes('w-full') as tabs:
            tab_entries = ui.tab('Wpisy kosztów',       icon='receipt_long')
            tab_docs    = ui.tab('Dokumenty i terminy', icon='assignment')
            tab_fuel    = ui.tab('Paliwo / Spalanie',   icon='local_gas_station')

        with ui.tab_panels(tabs, value=tab_entries).classes('w-full'):
            with ui.tab_panel(tab_entries):
                entries_tab(vehicle_id)

            with ui.tab_panel(tab_docs):
                documents_tab(vehicle_id)

            with ui.tab_panel(tab_fuel):
                _fuel_stats_tab(vehicle_id)

        ui.separator().classes('q-mt-lg')
        with ui.row().classes('q-mt-sm'):
            export_csv_button(vehicle_id, vehicle['name'])


def _fuel_stats_tab(vehicle_id: int) -> None:
    stats    = db.get_fuel_stats(vehicle_id)
    vstats   = db.get_vehicle_stats(vehicle_id)
    summary  = db.get_cost_summary(vehicle_id)

    with ui.column().classes('w-full gap-4'):

        # ── Koszt eksploatacji ──────────────────────────────────────────────
        ui.label('Koszt eksploatacji').classes('text-subtitle1 text-grey-7')
        with ui.row().classes('flex-wrap gap-3'):
            with ui.card().classes('bg-indigo-50 q-pa-sm'):
                total = vstats['total_cost']
                ui.label(f'{total:,.2f} PLN'.replace(',', '\u202f')).classes('text-h6 text-indigo-900')
                ui.label('Łączne koszty').classes('text-caption text-grey-6')

            if vstats.get('total_km'):
                with ui.card().classes('bg-purple-50 q-pa-sm'):
                    ui.label(f'{vstats["total_km"]:,} km'.replace(',', '\u202f')).classes('text-h6 text-purple-900')
                    ui.label(f'Przebieg ({vstats["start_odo"]:,} → {vstats["end_odo"]:,} km)'.replace(',', '\u202f')).classes('text-caption text-grey-6')

            if vstats.get('cost_per_km'):
                with ui.card().classes('bg-teal-50 q-pa-sm'):
                    ui.label(f'{vstats["cost_per_km"]:.2f} PLN/km').classes('text-h6 text-teal-900')
                    ui.label('Średni koszt / km').classes('text-caption text-grey-6')

            for s in summary:
                colors = {'Paliwo': 'green', 'Części': 'blue', 'Obsługa': 'teal', 'Usterka': 'red', 'Serwis': 'orange'}
                bg = {'Paliwo': 'bg-green-50', 'Części': 'bg-blue-50', 'Obsługa': 'bg-teal-50',
                      'Usterka': 'bg-red-50', 'Serwis': 'bg-orange-50'}.get(s['category'], 'bg-grey-1')
                with ui.card().classes(f'{bg} q-pa-sm'):
                    ui.label(f'{s["total"]:,.2f} PLN'.replace(',', '\u202f')).classes('text-h6')
                    ui.label(f'{s["category"]} ({s["count"]} wpisów)').classes('text-caption text-grey-6')

        ui.separator()

        # ── Zużycie paliwa ─────────────────────────────────────────────────
        ui.label('Zużycie paliwa (tankowania do pełna)').classes('text-subtitle1 text-grey-7')

        if not stats:
            with ui.column().classes('items-center q-mt-md gap-2'):
                ui.icon('local_gas_station', size='48px').classes('text-grey-3')
                ui.label('Brak danych. Dodaj wpisy paliwa z zaznaczonym „Do pełna".').classes('text-grey-5')
            return

        consumptions = [s['consumption_l100km'] for s in stats if s.get('consumption_l100km') is not None]

        if consumptions:
            avg_c = sum(consumptions) / len(consumptions)
            with ui.row().classes('flex-wrap gap-3 q-mb-sm'):
                with ui.card().classes('bg-green-50 q-pa-sm'):
                    ui.label(f'{avg_c:.2f} L/100km').classes('text-h6 text-green-900')
                    ui.label('Średnie spalanie').classes('text-caption text-grey-6')
                with ui.card().classes('bg-blue-50 q-pa-sm'):
                    ui.label(f'{min(consumptions):.2f} L/100km').classes('text-h6 text-blue-900')
                    ui.label('Najniższe').classes('text-caption text-grey-6')
                with ui.card().classes('bg-orange-50 q-pa-sm'):
                    ui.label(f'{max(consumptions):.2f} L/100km').classes('text-h6 text-orange-900')
                    ui.label('Najwyższe').classes('text-caption text-grey-6')

            chart_rows = [s for s in reversed(stats) if s.get('consumption_l100km') is not None]
            if chart_rows:
                ui.echart({
                    'tooltip': {'trigger': 'axis'},
                    'xAxis': {
                        'type': 'category',
                        'data': [r['date'] for r in chart_rows],
                        'axisLabel': {'rotate': 30, 'fontSize': 11},
                    },
                    'yAxis': {'type': 'value', 'name': 'L/100km'},
                    'series': [{
                        'type': 'line',
                        'data': [r['consumption_l100km'] for r in chart_rows],
                        'smooth': True,
                        'areaStyle': {'opacity': 0.15},
                        'markLine': {
                            'data': [{'type': 'average', 'name': 'Średnia'}],
                            'label': {'formatter': '{c:.1f}'},
                        },
                    }],
                    'grid': {'left': '8%', 'right': '4%', 'bottom': '15%'},
                }).classes('w-full h-56')

        # Tylko tankowania do pełna
        columns = [
            {'name': 'date',              'label': 'Data',         'field': 'date',              'sortable': True, 'align': 'left'},
            {'name': 'odometer',          'label': 'Licznik (km)', 'field': 'odometer',          'sortable': True, 'align': 'right'},
            {'name': 'distance_km',       'label': 'Trasa (km)',   'field': 'distance_km',       'align': 'right'},
            {'name': 'quantity',          'label': 'Litry (L)',    'field': 'quantity',          'align': 'right'},
            {'name': 'consumption_l100km','label': 'L/100km',      'field': 'consumption_l100km','sortable': True, 'align': 'right'},
            {'name': 'amount',            'label': 'Koszt (PLN)',  'field': 'amount',            'align': 'right'},
        ]
        rows = []
        for s in stats:
            rows.append({
                **s,
                'odometer':           f"{s['odometer']:,}".replace(',', '\u202f')   if s.get('odometer')           else '—',
                'distance_km':        f"{s['distance_km']:,}".replace(',', '\u202f') if s.get('distance_km')        else '—',
                'quantity':           f"{s['quantity']:.2f}"                         if s.get('quantity')           else '—',
                'consumption_l100km': f"{s['consumption_l100km']:.2f}"               if s.get('consumption_l100km') else '—',
                'amount':             f"{s['amount']:.2f}"                           if s.get('amount')             else '—',
            })
        ui.table(columns=columns, rows=rows, row_key='id',
                 pagination={'rowsPerPage': 20}).classes('w-full')


if __name__ in {'__main__', '__mp_main__'}:
    db.init_db()
    ui.run(
        native=True,
        title='Garagebook',
        window_size=(1280, 820),
        reload=False,
    )
