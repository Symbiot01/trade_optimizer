import os
import psycopg2
import random
from dotenv import load_dotenv

load_dotenv()

# Connect to the database
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cur = conn.cursor()

# Create tables if not exists
cur.execute("""
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
""")

# Define 10 standard items
ITEMS = [
    {"id": i + 1, "name": f"Item {i+1}", "unit_weight": random.uniform(0.5, 5.0),
     "unit_volume": random.uniform(0.01, 0.5),
     "buy_price": round(random.uniform(90, 120), 2),
     "sell_price": round(random.uniform(60, 89), 2)}
    for i in range(10)
]

# Insert items
cur.execute("DELETE FROM warehouse_items;")
cur.execute("DELETE FROM warehouses;")
cur.execute("DELETE FROM items;")

for item in ITEMS:
    cur.execute("""
        INSERT INTO items (id, name, unit_weight, unit_volume, buy_price, sell_price)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (item["id"], item["name"], item["unit_weight"], item["unit_volume"],
          item["buy_price"], item["sell_price"]))
print(" Seeded items table")

# Indian cities for spatial bias
cities = [
    ("Mumbai", 19.0760, 72.8777, 100),
    ("Delhi", 28.7041, 77.1025, 100),
    ("Bangalore", 12.9716, 77.5946, 90),
    ("Hyderabad", 17.3850, 78.4867, 85),
    ("Ahmedabad", 23.0225, 72.5714, 80),
    ("Chennai", 13.0827, 80.2707, 75),
    ("Kolkata", 22.5726, 88.3639, 70),
    ("Pune", 18.5204, 73.8567, 65),
    ("Surat", 21.1702, 72.8311, 60),
    ("Jaipur", 26.9124, 75.7873, 55),
    ("Lucknow", 26.8467, 80.9462, 55),
    ("Kanpur", 26.4499, 80.3319, 50),
    ("Nagpur", 21.1458, 79.0882, 50),
    ("Indore", 22.7196, 75.8577, 48),
    ("Thane", 19.2183, 72.9781, 45),
    ("Bhopal", 23.2599, 77.4126, 45),
    ("Visakhapatnam", 17.6868, 83.2185, 43),
    ("Patna", 25.5941, 85.1376, 43),
    ("Vadodara", 22.3072, 73.1812, 42),
    ("Ghaziabad", 28.6692, 77.4538, 40)
]

city_weights = [c[3] for c in cities]
city_coords = [(c[1], c[2]) for c in cities]
min_lat, max_lat = 8.0, 37.0
min_lon, max_lon = 68.0, 92.0

def random_point_near(lat, lon, max_km=30):
    delta_deg = max_km / 111.0
    return lat + random.uniform(-delta_deg, delta_deg), lon + random.uniform(-delta_deg, delta_deg)

print("Seeding warehouses...")

for i in range(100_000):
    if random.random() < 0.7:
        lat_c, lon_c = random.choices(city_coords, weights=city_weights, k=1)[0]
        lat, lon = random_point_near(lat_c, lon_c)
    else:
        lat = random.uniform(min_lat, max_lat)
        lon = random.uniform(min_lon, max_lon)

    cur.execute("""
        INSERT INTO warehouses (location)
        VALUES (ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography)
        RETURNING id
    """, (lon, lat))
    warehouse_id = cur.fetchone()[0]

    for item in ITEMS:
        if random.random() < 0.7:
            quantity = round(random.uniform(-5000, 5000), 2)
            if abs(quantity) < 100:
                continue
            cur.execute("""
                INSERT INTO warehouse_items (warehouse_id, item_id, quantity)
                VALUES (%s, %s, %s)
            """, (warehouse_id, item["id"], quantity))

    if i % 1000 == 0:
        print(f"Inserted {i} warehouses...")
        conn.commit()

conn.commit()
cur.close()
conn.close()
print(" Done seeding 100,000 warehouses with item-level data")
