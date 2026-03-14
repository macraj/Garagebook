CREATE TABLE IF NOT EXISTS vehicles (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    name                    TEXT NOT NULL,
    make                    TEXT,
    model                   TEXT,
    vin                     TEXT,
    year                    INTEGER,
    fuel_type               TEXT,
    first_registration_date TEXT,
    initial_odometer        INTEGER,
    created_at              TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS insurance (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id     INTEGER NOT NULL,
    policy_number  TEXT,
    company        TEXT,
    date_from      TEXT,
    date_to        TEXT,
    cost           REAL DEFAULT 0,
    notes          TEXT,
    created_at     TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS technical_inspection (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id  INTEGER NOT NULL,
    date        TEXT,
    valid_until TEXT,
    cost        REAL DEFAULT 0,
    notes       TEXT,
    created_at  TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cost_entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id  INTEGER NOT NULL,
    date        TEXT NOT NULL,
    category    TEXT NOT NULL,
    quantity    REAL DEFAULT 0,
    amount      REAL DEFAULT 0,
    odometer    INTEGER,
    description TEXT,
    user_code   TEXT,
    full_tank   INTEGER DEFAULT 0,
    oil_change  INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);
