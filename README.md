# 🚀 Warehouse Trade Optimizer

---

## Running with Docker

### Prerequisites

* Docker
* Docker Compose

### Steps

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/trade_optimizer.git
cd trade_optimizer
```

2. **Create a `.env` file:**

```env
DB_HOST=warehouse_db
DB_PORT=5432
DB_NAME=warehouse_db
DB_USER=postgres
DB_PASS=1234
```

3. **Build and start services:**

```bash
docker compose up --build
```

This will:

* Start the PostgreSQL + PostGIS database
* Seed \~100,000 warehouse records with item-level data
* Launch the FastAPI backend on [http://localhost:8000/docs](http://localhost:8000/docs)

> **Note:** Seeding may take several minutes on first run.

4. **(Optional) Re-run seeding manually:**

```bash
docker exec -it trade_optimizer bash
PYTHONPATH=. python3 data/seed_warehouses.py
```

---

## Accessing the Database with Docker

### Prerequisites

* Docker
* Docker Compose

---

### Steps

1. **Ensure containers are running:**

```bash
docker compose up --build
```

---

2. **Open a shell inside the PostgreSQL container:**

```bash
docker exec -it trade_optimizer-warehouse_db-1 bash
```

---

3. **Start the PostgreSQL client:**

```bash
psql -U postgres -d warehouse_db
```

You will see a prompt like:

```
warehouse_db=#
```

From here, you can run any SQL commands.

---

4. **Exit the PostgreSQL client:**

```
\q
```

---

5. **Exit the container shell:**

```
exit
```

---

# Sustainable Trucking Optimizer – Backend

This backend system supports route planning and profitable warehouse trade matching based on location, item demand/supply, and truck constraints. It uses FastAPI, PostgreSQL, and PostGIS.

---

## Database Structure

### `warehouses`

Stores geographic locations of warehouses.

### `warehouse_items`

Stores per-warehouse item quantities (positive = supply, negative = demand).

### `items`

Stores global item properties: unit weight, volume, buy/sell prices.

---

## Directory Structure

```
backend/
├── app/
│   ├── api/                 # FastAPI routes
│   │   └── routes.py
│   ├── core/                # Core business logic
│   │   └── optimizer.py
│   ├── db/                  # Database session configuration
│   │   └── db_session.py
│   ├── geo_utils.py         # Geospatial helper functions
│   ├── main.py              # FastAPI app entry point
│   └── models/              # Pydantic and SQLAlchemy models
│       ├── db_models.py
│       └── schemas.py
├── data/
│   └── seed_warehouses.py   # Script to generate and insert synthetic data
├── Dockerfile               # Container setup for backend
├── requirements.txt         # Python dependencies
└── static/
    └── route_map.html       # (Optional) rendered route map output
docker-compose.yml           # Multi-service config for backend + PostGIS
README.md                    # Project documentation
```

---

## How It Works

1. **FastAPI** handles POST requests with pickup/drop tasks.
2. **PostgreSQL + PostGIS** stores and queries spatial warehouse data.
3. **Optimizer** evaluates possible trade routes with profit and feasibility logic.
4. **Geo utilities** assist with distance, filtering, and route planning.
5. **Seed script** populates 100,000 warehouse entries with city-biased distribution and item-level supply/demand.
6. **Docker Compose** sets up the backend and PostGIS database in containers.

---

# Database Schema: Sustainable Trucking Optimizer

This schema supports a logistics optimization system that identifies profitable warehouse trade routes under spatial and operational constraints.

## Tables

### 1. `warehouses`

Stores the geographic location of each warehouse.

```sql
CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    location GEOGRAPHY(Point, 4326)
);
```

* Used for spatial queries and proximity filtering.

### 2. `warehouse_items`

Stores item-level supply or demand for each warehouse.

```sql
CREATE TABLE warehouse_items (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER REFERENCES warehouses(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL CHECK (item_id BETWEEN 1 AND 10),
    quantity FLOAT NOT NULL,
    UNIQUE (warehouse_id, item_id)
);
```

* Positive `quantity` indicates supply.
* Negative `quantity` indicates demand.
* One row per item per warehouse.

### 3. `items`

Defines global attributes for each item type.

```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    unit_weight FLOAT NOT NULL,
    unit_volume FLOAT NOT NULL,
    buy_price FLOAT NOT NULL,
    sell_price FLOAT NOT NULL
);
```

* Prices and physical properties are uniform across all warehouses.

## .env file

Create a .env file in the project root with the following content:
```
DB_HOST=warehouse_db
DB_PORT=5432
DB_NAME=warehouse_db
DB_USER=postgres
DB_PASS=your_password
ORS_API_KEY=your_api_key_here
```

## Query Examples

**Warehouses near Delhi needing item 2:**

```sql
SELECT w.id, -wi.quantity AS demand_units
FROM warehouses w
JOIN warehouse_items wi ON wi.warehouse_id = w.id
WHERE wi.item_id = 2 AND wi.quantity < 0
  AND ST_DWithin(w.location, ST_MakePoint(77.1025, 28.7041)::geography, 30000);
```

**Warehouses within 100 km supplying item 5:**

```sql
SELECT w.id, wi.quantity AS supply_units
FROM warehouses w
JOIN warehouse_items wi ON wi.warehouse_id = w.id
WHERE wi.item_id = 5 AND wi.quantity > 0
  AND ST_DWithin(w.location, ST_MakePoint(72.8777, 19.0760)::geography, 100000);
```

## Notes

* The schema is normalized for scalability and efficiency.
* Spatial indexing and geography types support fast geospatial queries.
* Pricing and logistics calculations use item-level attributes from the `items` table.

---
