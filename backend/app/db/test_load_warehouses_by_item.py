from app.db.queries import load_warehouses_by_item

def main():

    # Example test parameters
    params = dict(
        src_lat=12.9716,
        src_lon=77.5946,
        dest_lat=28.7041,
        dest_lon=77.1025,
        max_detour_meters=500000,        # 500 km
        max_load_capacity=50000,
        cost_per_km=12
    )

    print("Fetching warehouses...")
    warehouses = load_warehouses_by_item( **params)

    print(f"\nFound {len(warehouses)} warehouses:\n")

    for i, wh in enumerate(warehouses, 1):
        print(f"{i:02d}. Warehouse ID: {wh['warehouse_id']}")
        print(f"    Quantity: {wh['quantity']}")
        print(f"    Location: ({wh['lat']:.4f}, {wh['lon']:.4f})")
        print(f"    Item ID: {wh['item_id']}")
        print(f"    Unit Weight: {wh['unit_weight']}")
        print(f"    Unit Volume: {wh['unit_volume']}")
        print(f"    Sell Price: {wh['sell_price']}")
        print(f"    Buy Price: {wh['buy_price']}")
        print(f"    Demand Metric: {wh['demand_metric']}\n")

if __name__ == "__main__":
    main()
