from fastapi import APIRouter, Depends
from auth.dependencies import require_admin
from database import get_db

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/top-products")
def top_products(
    _: dict = Depends(require_admin),
    db = Depends(get_db)
):
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            p.product_id,
            p.name AS product_name,
            SUM(oi.quantity) AS total_quantity_sold,
            SUM(oi.quantity * oi.price_at_purchase) AS total_revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_id, p.name
        ORDER BY total_quantity_sold DESC
        LIMIT 5;
    """)
    data = cursor.fetchall()
    cursor.close()
    return data
