import sqlite3
from pathlib import Path
from datetime import date as date_type

DB_PATH = Path('garagebook.db')
BACKUPS_DIR = Path('backups')
SCHEMA_PATH = Path(__file__).parent / 'schema.sql'

CURRENCY_SYMBOLS: dict[str, str] = {
    'PLN': 'zł', 'EUR': '€', 'USD': '$', 'GBP': '£',
    'CHF': 'CHF', 'CZK': 'Kč', 'NOK': 'kr', 'SEK': 'kr',
}


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA_PATH.read_text())
        _migrate(conn)


def _migrate(conn: sqlite3.Connection) -> None:
    """Dodaje kolumny dodane po pierwszym uruchomieniu — bezpieczne przy ponownym init."""
    for sql in [
        'ALTER TABLE vehicles ADD COLUMN initial_odometer INTEGER',
        'ALTER TABLE cost_entries ADD COLUMN oil_change INTEGER DEFAULT 0',
    ]:
        try:
            conn.execute(sql)
        except sqlite3.OperationalError:
            pass  # kolumna już istnieje


def days_until(date_str: str | None) -> int | None:
    if not date_str:
        return None
    try:
        d = date_type.fromisoformat(date_str)
        return (d - date_type.today()).days
    except ValueError:
        return None


# ─── Settings ───────────────────────────────────────────────────────────────

def get_setting(key: str, default: str = '') -> str:
    with get_connection() as conn:
        row = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
        return row['value'] if row else default


def set_setting(key: str, value: str) -> None:
    with get_connection() as conn:
        conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))


def get_currency_symbol() -> str:
    return CURRENCY_SYMBOLS.get(get_setting('currency', 'PLN'), 'zł')


# ─── Vehicles ───────────────────────────────────────────────────────────────

def get_all_vehicles() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute('SELECT * FROM vehicles ORDER BY name').fetchall()
        return [dict(r) for r in rows]


def get_vehicle(vehicle_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute('SELECT * FROM vehicles WHERE id = ?', (vehicle_id,)).fetchone()
        return dict(row) if row else None


def create_vehicle(data: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            '''INSERT INTO vehicles (name, make, model, vin, year, fuel_type, first_registration_date, initial_odometer)
               VALUES (:name, :make, :model, :vin, :year, :fuel_type, :first_registration_date, :initial_odometer)''',
            data,
        )
        return cur.lastrowid


def update_vehicle(vehicle_id: int, data: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            '''UPDATE vehicles
               SET name=:name, make=:make, model=:model, vin=:vin,
                   year=:year, fuel_type=:fuel_type, first_registration_date=:first_registration_date,
                   initial_odometer=:initial_odometer
               WHERE id=:id''',
            {**data, 'id': vehicle_id},
        )


def delete_vehicle(vehicle_id: int) -> None:
    with get_connection() as conn:
        conn.execute('DELETE FROM vehicles WHERE id = ?', (vehicle_id,))


# ─── Insurance ──────────────────────────────────────────────────────────────

def get_vehicle_insurance(vehicle_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            'SELECT * FROM insurance WHERE vehicle_id = ? ORDER BY date_to DESC',
            (vehicle_id,),
        ).fetchall()
    result = [dict(r) for r in rows]
    for r in result:
        r['days_until'] = days_until(r['date_to'])
    return result


def create_insurance(data: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            '''INSERT INTO insurance (vehicle_id, policy_number, company, date_from, date_to, cost, notes)
               VALUES (:vehicle_id, :policy_number, :company, :date_from, :date_to, :cost, :notes)''',
            data,
        )
        return cur.lastrowid


def update_insurance(insurance_id: int, data: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            '''UPDATE insurance
               SET policy_number=:policy_number, company=:company,
                   date_from=:date_from, date_to=:date_to, cost=:cost, notes=:notes
               WHERE id=:id''',
            {**data, 'id': insurance_id},
        )


def delete_insurance(insurance_id: int) -> None:
    with get_connection() as conn:
        conn.execute('DELETE FROM insurance WHERE id = ?', (insurance_id,))


# ─── Technical Inspections ──────────────────────────────────────────────────

def get_vehicle_inspections(vehicle_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            'SELECT * FROM technical_inspection WHERE vehicle_id = ? ORDER BY valid_until DESC',
            (vehicle_id,),
        ).fetchall()
    result = [dict(r) for r in rows]
    for r in result:
        r['days_until'] = days_until(r['valid_until'])
    return result


def create_inspection(data: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            '''INSERT INTO technical_inspection (vehicle_id, date, valid_until, cost, notes)
               VALUES (:vehicle_id, :date, :valid_until, :cost, :notes)''',
            data,
        )
        return cur.lastrowid


def update_inspection(inspection_id: int, data: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            '''UPDATE technical_inspection
               SET date=:date, valid_until=:valid_until, cost=:cost, notes=:notes
               WHERE id=:id''',
            {**data, 'id': inspection_id},
        )


def delete_inspection(inspection_id: int) -> None:
    with get_connection() as conn:
        conn.execute('DELETE FROM technical_inspection WHERE id = ?', (inspection_id,))


# ─── Cost Entries ───────────────────────────────────────────────────────────

def get_vehicle_entries(
    vehicle_id: int,
    category: str = '',
    date_from: str = '',
    date_to: str = '',
) -> list[dict]:
    query = 'SELECT * FROM cost_entries WHERE vehicle_id = ?'
    params: list = [vehicle_id]
    if category:
        query += ' AND category = ?'
        params.append(category)
    if date_from:
        query += ' AND date >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND date <= ?'
        params.append(date_to)
    query += ' ORDER BY date DESC, id DESC'
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def create_entry(data: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            '''INSERT INTO cost_entries
               (vehicle_id, date, category, quantity, amount, odometer, description, user_code, full_tank, oil_change)
               VALUES (:vehicle_id, :date, :category, :quantity, :amount, :odometer, :description, :user_code, :full_tank, :oil_change)''',
            data,
        )
        return cur.lastrowid


def update_entry(entry_id: int, data: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            '''UPDATE cost_entries
               SET date=:date, category=:category, quantity=:quantity, amount=:amount,
                   odometer=:odometer, description=:description, user_code=:user_code,
                   full_tank=:full_tank, oil_change=:oil_change
               WHERE id=:id''',
            {**data, 'id': entry_id},
        )


def delete_entry(entry_id: int) -> None:
    with get_connection() as conn:
        conn.execute('DELETE FROM cost_entries WHERE id = ?', (entry_id,))


def get_last_oil_change(vehicle_id: int) -> dict | None:
    """Ostatnia wymiana oleju — data, licznik, ile dni i km minęło."""
    with get_connection() as conn:
        row = conn.execute(
            '''SELECT date, odometer FROM cost_entries
               WHERE vehicle_id = ? AND oil_change = 1
               ORDER BY date DESC, id DESC LIMIT 1''',
            (vehicle_id,),
        ).fetchone()
    if not row:
        return None
    result = dict(row)
    try:
        d = date_type.fromisoformat(row['date'])
        result['days_since'] = (date_type.today() - d).days
    except ValueError:
        result['days_since'] = None
    max_odo = get_max_odometer(vehicle_id)
    result['km_since'] = (max_odo - row['odometer']) if (max_odo and row['odometer'] is not None) else None
    return result


def get_fuel_stats(vehicle_id: int, category: str = 'Paliwo') -> list[dict]:
    """Full-tank/full-charge entries with consumption per 100 km via window function."""
    with get_connection() as conn:
        rows = conn.execute(
            '''WITH ranked AS (
                   SELECT id, date, quantity, odometer, amount,
                          LAG(odometer) OVER (ORDER BY odometer ASC) AS prev_odometer
                   FROM cost_entries
                   WHERE vehicle_id = ?
                     AND category = ?
                     AND full_tank = 1
                     AND odometer IS NOT NULL
               )
               SELECT
                   id, date, quantity, odometer, amount,
                   CASE WHEN prev_odometer IS NOT NULL AND odometer > prev_odometer
                        THEN ROUND(CAST(quantity AS REAL) / (odometer - prev_odometer) * 100, 2)
                        ELSE NULL END AS consumption_per_100km,
                   CASE WHEN prev_odometer IS NOT NULL
                        THEN odometer - prev_odometer
                        ELSE NULL END AS distance_km
               FROM ranked
               ORDER BY odometer DESC''',
            (vehicle_id, category),
        ).fetchall()
        return [dict(r) for r in rows]


def get_cost_summary(vehicle_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            '''SELECT category, SUM(amount) AS total, COUNT(*) AS count
               FROM cost_entries WHERE vehicle_id = ?
               GROUP BY category ORDER BY total DESC''',
            (vehicle_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_vehicle_stats(vehicle_id: int) -> dict:
    """Łączne koszty, przebieg i koszt na km dla pojazdu."""
    with get_connection() as conn:
        vrow = conn.execute(
            'SELECT initial_odometer FROM vehicles WHERE id = ?', (vehicle_id,)
        ).fetchone()
        initial_odo = (vrow['initial_odometer'] or 0) if vrow else 0

        odo_row = conn.execute(
            '''SELECT MIN(odometer) AS min_odo, MAX(odometer) AS max_odo
               FROM cost_entries WHERE vehicle_id = ? AND odometer IS NOT NULL''',
            (vehicle_id,),
        ).fetchone()
        min_odo = odo_row['min_odo'] if odo_row else None
        max_odo = odo_row['max_odo'] if odo_row else None

        start_odo = min(filter(None, [initial_odo or None, min_odo])) if any([initial_odo, min_odo]) else None

        entries_row = conn.execute(
            'SELECT SUM(amount) AS total FROM cost_entries WHERE vehicle_id = ?',
            (vehicle_id,),
        ).fetchone()
        insurance_row = conn.execute(
            'SELECT SUM(cost) AS total FROM insurance WHERE vehicle_id = ?',
            (vehicle_id,),
        ).fetchone()
        inspection_row = conn.execute(
            'SELECT SUM(cost) AS total FROM technical_inspection WHERE vehicle_id = ?',
            (vehicle_id,),
        ).fetchone()

        total_cost = (
            (entries_row['total']    or 0.0) +
            (insurance_row['total']  or 0.0) +
            (inspection_row['total'] or 0.0)
        )
        cost_insurance  = insurance_row['total']  or 0.0
        cost_inspection = inspection_row['total'] or 0.0

        total_km = (max_odo - start_odo) if (max_odo and start_odo is not None and max_odo > start_odo) else None
        cost_per_km = round(total_cost / total_km, 2) if total_km else None

        return {
            'total_cost':       total_cost,
            'cost_insurance':   cost_insurance,
            'cost_inspection':  cost_inspection,
            'start_odo':        start_odo,
            'end_odo':          max_odo,
            'total_km':         total_km,
            'cost_per_km':      cost_per_km,
        }


def get_max_odometer(vehicle_id: int, exclude_entry_id: int | None = None) -> int:
    """Najwyższy zarejestrowany licznik (uwzględnia initial_odometer pojazdu)."""
    with get_connection() as conn:
        vrow = conn.execute(
            'SELECT initial_odometer FROM vehicles WHERE id = ?', (vehicle_id,)
        ).fetchone()
        initial = (vrow['initial_odometer'] or 0) if vrow else 0

        query = 'SELECT MAX(odometer) AS v FROM cost_entries WHERE vehicle_id = ? AND odometer IS NOT NULL'
        params: list = [vehicle_id]
        if exclude_entry_id is not None:
            query += ' AND id != ?'
            params.append(exclude_entry_id)
        row = conn.execute(query, params).fetchone()
        entry_max = row['v'] or 0
        return max(initial, entry_max)


def get_last_odometer(vehicle_id: int) -> int | None:
    val = get_max_odometer(vehicle_id)
    return val if val > 0 else None


# ─── Dashboard ──────────────────────────────────────────────────────────────

def get_dashboard_data() -> list[dict]:
    vehicles = get_all_vehicles()
    for v in vehicles:
        vid = v['id']
        ins_list = get_vehicle_insurance(vid)
        v['insurance'] = ins_list[0] if ins_list else None
        insp_list = get_vehicle_inspections(vid)
        v['inspection'] = insp_list[0] if insp_list else None
        v['last_odometer'] = get_last_odometer(vid)
    return vehicles


# ─── Backup / Restore ────────────────────────────────────────────────────────

def backup_db() -> Path:
    from datetime import datetime
    BACKUPS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    dest = BACKUPS_DIR / f'garagebook_{ts}.db'
    src = sqlite3.connect(str(DB_PATH))
    dst = sqlite3.connect(str(dest))
    src.backup(dst)
    src.close()
    dst.close()
    return dest


def list_backups() -> list[Path]:
    if not BACKUPS_DIR.exists():
        return []
    return sorted(BACKUPS_DIR.glob('garagebook_*.db'), reverse=True)


def restore_db(backup_path: Path):
    import shutil
    shutil.copy2(str(backup_path), str(DB_PATH))


def delete_backup(backup_path: Path):
    backup_path.unlink(missing_ok=True)
