-- backend/db/db_init/init.sql

CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    unit_weight FLOAT,
    unit_volume FLOAT,
    buy_price FLOAT,
    sell_price FLOAT
);

CREATE TABLE IF NOT EXISTS warehouses (
    id SERIAL PRIMARY KEY,
    location GEOGRAPHY(Point, 4326)
);

CREATE TABLE IF NOT EXISTS warehouse_items (
    warehouse_id INTEGER REFERENCES warehouses(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
    quantity FLOAT
);