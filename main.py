from nicegui import ui
from db import database as db
from ui.layout import page_header
from ui.dashboard import dashboard_page
from ui.vehicles import vehicles_page
from ui.entries import entries_tab
from ui.documents import documents_tab
from ui.export import export_csv_button
from ui.settings import settings_page


@ui.page('/')
def index() -> None:
    dashboard_page()


@ui.page('/pojazdy')
def vehicles() -> None:
    vehicles_page()


@ui.page('/ustawienia')
def ustawienia() -> None:
    settings_page()


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
            tab_entries = ui.tab('Wpisy kosztów',        icon='receipt_long')
            tab_docs    = ui.tab('Dokumenty i terminy',  icon='assignment')
            tab_fuel    = ui.tab('Energia / Spalanie',   icon='local_gas_station')

        @ui.refreshable
        def fuel_stats_content():
            _fuel_stats_tab(vehicle_id)

        with ui.tab_panels(tabs, value=tab_entries).classes('w-full'):
            with ui.tab_panel(tab_entries):
                entries_tab(vehicle_id, on_change=fuel_stats_content.refresh)

            with ui.tab_panel(tab_docs):
                documents_tab(vehicle_id)

            with ui.tab_panel(tab_fuel):
                fuel_stats_content()

        ui.separator().classes('q-mt-lg')
        with ui.row().classes('q-mt-sm'):
            export_csv_button(vehicle_id, vehicle['name'])


def _fuel_stats_tab(vehicle_id: int) -> None:
    fuel_stats   = db.get_fuel_stats(vehicle_id, 'Paliwo')
    charge_stats = db.get_fuel_stats(vehicle_id, 'Ładowanie')
    vstats       = db.get_vehicle_stats(vehicle_id)
    summary      = db.get_cost_summary(vehicle_id)
    cur          = db.get_currency_symbol()

    with ui.column().classes('w-full gap-4'):

        # ── Koszt eksploatacji ──────────────────────────────────────────────
        ui.label('Koszt eksploatacji').classes('text-subtitle1 text-grey-7')
        with ui.row().classes('flex-wrap gap-3'):
            with ui.card().classes('bg-indigo-50 q-pa-sm'):
                total = vstats['total_cost']
                ui.label(f'{total:,.2f} {cur}'.replace(',', '\u202f')).classes('text-h6 text-indigo-900')
                ui.label('Łączne koszty').classes('text-caption text-grey-6')

            if vstats.get('total_km'):
                with ui.card().classes('bg-purple-50 q-pa-sm'):
                    ui.label(f'{vstats["total_km"]:,} km'.replace(',', '\u202f')).classes('text-h6 text-purple-900')
                    ui.label(f'Przebieg ({vstats["start_odo"]:,} → {vstats["end_odo"]:,} km)'.replace(',', '\u202f')).classes('text-caption text-grey-6')

            if vstats.get('cost_per_km'):
                with ui.card().classes('bg-teal-50 q-pa-sm'):
                    ui.label(f'{vstats["cost_per_km"]:.2f} {cur}/km').classes('text-h6 text-teal-900')
                    ui.label('Średni koszt / km').classes('text-caption text-grey-6')

            if vstats['cost_insurance']:
                with ui.card().classes('bg-cyan-50 q-pa-sm'):
                    ui.label(f'{vstats["cost_insurance"]:,.2f} {cur}'.replace(',', '\u202f')).classes('text-h6 text-cyan-900')
                    ui.label('Ubezpieczenia').classes('text-caption text-grey-6')

            if vstats['cost_inspection']:
                with ui.card().classes('bg-lime-50 q-pa-sm'):
                    ui.label(f'{vstats["cost_inspection"]:,.2f} {cur}'.replace(',', '\u202f')).classes('text-h6 text-lime-900')
                    ui.label('Przeglądy techniczne').classes('text-caption text-grey-6')

            for s in summary:
                bg = {'Paliwo': 'bg-green-50', 'Ładowanie': 'bg-purple-50', 'Części': 'bg-blue-50',
                      'Obsługa': 'bg-teal-50', 'Usterka': 'bg-red-50', 'Serwis': 'bg-orange-50'}.get(s['category'], 'bg-grey-1')
                with ui.card().classes(f'{bg} q-pa-sm'):
                    ui.label(f'{s["total"]:,.2f} {cur}'.replace(',', '\u202f')).classes('text-h6')
                    ui.label(f'{s["category"]} ({s["count"]} wpisów)').classes('text-caption text-grey-6')

        # ── Struktura kosztów (donut chart) ─────────────────────────────
        if summary:
            COLOR_MAP = {
                'Paliwo': '#4caf50', 'Ładowanie': '#7e57c2', 'Części': '#2196f3',
                'Obsługa': '#009688', 'Usterka': '#f44336', 'Serwis': '#ff9800',
                'Ubezpieczenia': '#00bcd4', 'Przeglądy': '#cddc39',
            }
            pie_data = [{'name': s['category'], 'value': round(s['total'], 2)} for s in summary]
            if vstats['cost_insurance']:
                pie_data.append({'name': 'Ubezpieczenia', 'value': round(vstats['cost_insurance'], 2)})
            if vstats['cost_inspection']:
                pie_data.append({'name': 'Przeglądy', 'value': round(vstats['cost_inspection'], 2)})

            ui.label('Struktura kosztów').classes('text-subtitle1 text-grey-7')
            ui.echart({
                'tooltip': {'trigger': 'item', 'formatter': '{b}: {c} ' + cur + ' ({d}%)'},
                'series': [{
                    'type': 'pie',
                    'radius': ['40%', '70%'],
                    'data': pie_data,
                    'itemStyle': {'borderRadius': 6, 'borderColor': '#fff', 'borderWidth': 2},
                    'label': {'formatter': '{b}\n{d}%'},
                    'color': [COLOR_MAP.get(d['name'], '#9e9e9e') for d in pie_data],
                }],
            }).classes('w-full h-64')

        ui.separator()

        # ── Koszty i przebieg w czasie ──────────────────────────────────
        monthly = db.get_monthly_stats(vehicle_id)
        if monthly:
            view_state = {'mode': 'month'}

            @ui.refreshable
            def timeline_chart():
                mode = view_state['mode']
                if mode == 'year':
                    # aggregate by year
                    yearly: dict[str, dict] = {}
                    for m in monthly:
                        y = m['month'][:4]
                        if y not in yearly:
                            yearly[y] = {'total_cost': 0, 'km_driven': 0}
                        yearly[y]['total_cost'] += m['total_cost']
                        if m['km_driven']:
                            yearly[y]['km_driven'] += m['km_driven']
                    labels = list(yearly.keys())
                    costs = [round(yearly[y]['total_cost'], 2) for y in labels]
                    kms = [yearly[y]['km_driven'] or None for y in labels]
                else:
                    labels = [m['month'] for m in monthly]
                    costs = [round(m['total_cost'], 2) for m in monthly]
                    kms = [m['km_driven'] for m in monthly]

                series = [
                    {'name': f'Koszt ({cur})', 'type': 'bar', 'data': costs,
                     'itemStyle': {'color': '#5c6bc0', 'borderRadius': [4, 4, 0, 0]}},
                ]
                y_axes = [{'type': 'value', 'name': cur}]

                if any(k for k in kms):
                    series.append({
                        'name': 'Przebieg (km)', 'type': 'line', 'yAxisIndex': 1,
                        'data': kms, 'smooth': True,
                        'itemStyle': {'color': '#ab47bc'},
                    })
                    y_axes.append({'type': 'value', 'name': 'km', 'position': 'right'})

                ui.echart({
                    'tooltip': {'trigger': 'axis'},
                    'legend': {'data': [s['name'] for s in series], 'bottom': 0},
                    'xAxis': {
                        'type': 'category', 'data': labels,
                        'axisLabel': {'rotate': 30, 'fontSize': 11},
                    },
                    'yAxis': y_axes,
                    'series': series,
                    'grid': {'left': '8%', 'right': '8%', 'bottom': '18%'},
                }).classes('w-full h-64')

            ui.label('Koszty i przebieg w czasie').classes('text-subtitle1 text-grey-7')
            with ui.row().classes('gap-2 q-mb-sm'):
                def set_mode(m):
                    view_state['mode'] = m
                    timeline_chart.refresh()
                ui.button('Miesięcznie', on_click=lambda: set_mode('month')).props('outline dense')
                ui.button('Rocznie', on_click=lambda: set_mode('year')).props('outline dense')
            timeline_chart()

        ui.separator()

        # ── Zużycie paliwa (L) i ładowanie (kWh) ──────────────────────────
        has_fuel   = bool(fuel_stats)
        has_charge = bool(charge_stats)

        if not has_fuel and not has_charge:
            with ui.column().classes('items-center q-mt-md gap-2'):
                ui.icon('local_gas_station', size='48px').classes('text-grey-3')
                ui.label('Brak danych. Dodaj wpisy Paliwo lub Ładowanie z zaznaczonym „Do pełna".').classes('text-grey-5')
            return

        if has_fuel:
            _consumption_section(fuel_stats, unit='L', unit_per='L/100km', cur=cur,
                                 title='Zużycie paliwa (tankowania do pełna)',
                                 avg_class='bg-green-50 text-green-900')

        if has_fuel and has_charge:
            ui.separator()

        if has_charge:
            _consumption_section(charge_stats, unit='kWh', unit_per='kWh/100km', cur=cur,
                                 title='Zużycie energii (ładowania do pełna)',
                                 avg_class='bg-purple-50 text-purple-900')


def _consumption_section(
    stats: list[dict],
    unit: str,
    unit_per: str,
    cur: str,
    title: str,
    avg_class: str,
) -> None:
    ui.label(title).classes('text-subtitle1 text-grey-7')

    consumptions = [s['consumption_per_100km'] for s in stats if s.get('consumption_per_100km') is not None]

    if consumptions:
        avg_c = sum(consumptions) / len(consumptions)
        with ui.row().classes('flex-wrap gap-3 q-mb-sm'):
            with ui.card().classes(f'{avg_class} q-pa-sm'):
                ui.label(f'{avg_c:.2f} {unit_per}').classes('text-h6')
                ui.label('Średnie').classes('text-caption text-grey-6')
            with ui.card().classes('bg-blue-50 q-pa-sm'):
                ui.label(f'{min(consumptions):.2f} {unit_per}').classes('text-h6 text-blue-900')
                ui.label('Najniższe').classes('text-caption text-grey-6')
            with ui.card().classes('bg-orange-50 q-pa-sm'):
                ui.label(f'{max(consumptions):.2f} {unit_per}').classes('text-h6 text-orange-900')
                ui.label('Najwyższe').classes('text-caption text-grey-6')

        chart_rows = [s for s in reversed(stats) if s.get('consumption_per_100km') is not None]
        if chart_rows:
            ui.echart({
                'tooltip': {'trigger': 'axis'},
                'xAxis': {
                    'type': 'category',
                    'data': [r['date'] for r in chart_rows],
                    'axisLabel': {'rotate': 30, 'fontSize': 11},
                },
                'yAxis': {'type': 'value', 'name': unit_per},
                'series': [{
                    'type': 'line',
                    'data': [r['consumption_per_100km'] for r in chart_rows],
                    'smooth': True,
                    'areaStyle': {'opacity': 0.15},
                    'markLine': {
                        'data': [{'type': 'average', 'name': 'Średnia'}],
                        'label': {'formatter': '{c:.1f}'},
                    },
                }],
                'grid': {'left': '8%', 'right': '4%', 'bottom': '15%'},
            }).classes('w-full h-56')

    columns = [
        {'name': 'date',                 'label': 'Data',           'field': 'date',                 'sortable': True, 'align': 'left'},
        {'name': 'odometer',             'label': 'Licznik (km)',   'field': 'odometer',             'sortable': True, 'align': 'right'},
        {'name': 'distance_km',          'label': 'Trasa (km)',     'field': 'distance_km',          'align': 'right'},
        {'name': 'quantity',             'label': f'Ilość ({unit})', 'field': 'quantity',             'align': 'right'},
        {'name': 'consumption_per_100km','label': unit_per,          'field': 'consumption_per_100km','sortable': True, 'align': 'right'},
        {'name': 'amount',               'label': f'Koszt ({cur})', 'field': 'amount',               'align': 'right'},
    ]
    rows = []
    for s in stats:
        rows.append({
            **s,
            'odometer':              f"{s['odometer']:,}".replace(',', '\u202f')    if s.get('odometer')              else '—',
            'distance_km':           f"{s['distance_km']:,}".replace(',', '\u202f') if s.get('distance_km')           else '—',
            'quantity':              f"{s['quantity']:.3f}"                          if s.get('quantity')              else '—',
            'consumption_per_100km': f"{s['consumption_per_100km']:.2f}"             if s.get('consumption_per_100km') else '—',
            'amount':                f"{s['amount']:.2f}"                            if s.get('amount')                else '—',
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
