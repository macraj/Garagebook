from nicegui import ui


def alert_color(days: int | None) -> str:
    if days is None:
        return 'grey'
    if days > 30:
        return 'positive'
    if days > 0:
        return 'warning'
    return 'negative'


def alert_label(days: int | None) -> str:
    if days is None:
        return 'brak danych'
    if days > 30:
        return f'za {days} dni'
    if days > 0:
        return f'⚠ za {days} dni'
    return f'✗ przeterminowane ({abs(days)} dni)'


def page_header(title: str = '') -> None:
    with ui.header().classes('bg-indigo-800 text-white items-center gap-6 px-6 py-2'):
        ui.link('🚗 Garagebook', '/').classes('text-h6 text-white no-underline')
        if title:
            ui.label('·').classes('text-grey-4')
            ui.label(title).classes('text-body1')
        ui.space()
        ui.link('Dashboard', '/').classes('text-white text-body2 no-underline')
        ui.link('Pojazdy', '/pojazdy').classes('text-white text-body2 no-underline')
        ui.link('Ustawienia', '/ustawienia').classes('text-white text-body2 no-underline')
