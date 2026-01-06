@app.route("/api/companies/<company_id>/alerts/low-stock", methods=["GET"])
def get_low_stock_alerts(company_id):
    alerts = []

    # Fetch inventory joined with product and warehouse
    records = (
        db.session.query(Inventory, Product, Warehouse)
        .join(Product, Inventory.product_id == Product.id)
        .join(Warehouse, Inventory.warehouse_id == Warehouse.id)
        .filter(Product.company_id == company_id)
        .all()
    )

    for inventory, product, warehouse in records:
        # Check recent sales activity
        avg_daily_sales = get_average_daily_sales(
            product_id=product.id,
            days=30
        )

        # Skip products with no recent sales
        if avg_daily_sales <= 0:
            continue

        threshold = get_low_stock_threshold(product.product_type)

        # Skip if stock is not low
        if inventory.quantity >= threshold:
            continue

        # Calculate days until stockout
        days_until_stockout = int(inventory.quantity / avg_daily_sales)

        # Fetch supplier information
        supplier = (
            db.session.query(Supplier)
            .join(ProductSupplier)
            .filter(ProductSupplier.product_id == product.id)
            .first()
        )

        alerts.append({
            "product_id": product.id,
            "product_name": product.name,
            "sku": product.sku,
            "warehouse_id": warehouse.id,
            "warehouse_name": warehouse.name,
            "current_stock": inventory.quantity,
            "threshold": threshold,
            "days_until_stockout": days_until_stockout,
            "supplier": {
                "id": supplier.id if supplier else None,
                "name": supplier.name if supplier else None,
                "contact_email": supplier.contact_email if supplier else None
            }
        })

    return {
        "alerts": alerts,
        "total_alerts": len(alerts)
    }
