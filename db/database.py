import sqlite3
from pathlib import Path
from datetime import date as date_type

DB_PATH = Path('garagebook.db')
SCHEMA_PATH = Path(__file__).parent / 'schema.sql'


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
               (vehicle_id, date, category, quantity, amount, odometer, description, user_code, full_tank)
               VALUES (:vehicle_id, :date, :category, :quantity, :amount, :odometer, :description, :user_code, :full_tank)''',
            data,
        )
        return cur.lastrowid


def update_entry(entry_id: int, data: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            '''UPDATE cost_entries
               SET date=:date, category=:category, quantity=:quantity, amount=:amount,
                   odometer=:odometer, description=:description, user_code=:user_code, full_tank=:full_tank
               WHERE id=:id''',
            {**data, 'id': entry_id},
        )


def delete_entry(entry_id: int) -> None:
    with get_connection() as conn:
        conn.execute('DELETE FROM cost_entries WHERE id = ?', (entry_id,))


def get_fuel_stats(vehicle_id: int) -> list[dict]:
    """Full-tank fuel entries with L/100km consumption via window function."""
    with get_connection() as conn:
        rows = conn.execute(
            '''WITH ranked AS (
                   SELECT id, date, quantity, odometer, amount,
                          LAG(odometer) OVER (ORDER BY odometer ASC) AS prev_odometer
                   FROM cost_entries
                   WHERE vehicle_id = ?
                     AND category = 'Paliwo'
                     AND full_tank = 1
                     AND odometer IS NOT NULL
               )
               SELECT
                   id, date, quantity, odometer, amount,
                   CASE WHEN prev_odometer IS NOT NULL AND odometer > prev_odometer
                        THEN ROUND(CAST(quantity AS REAL) / (odometer - prev_odometer) * 100, 2)
                        ELSE NULL END AS consumption_l100km,
                   CASE WHEN prev_odometer IS NOT NULL
                        THEN odometer - prev_odometer
                        ELSE NULL END AS distance_km
               FROM ranked
               ORDER BY odometer DESC''',
            (vehicle_id,),
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
