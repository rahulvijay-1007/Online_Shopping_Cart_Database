from fastapi import APIRouter, Depends, HTTPException, Query
from auth.dependencies import require_admin
from database import get_db
from pydantic import BaseModel, conint, condecimal
from decimal import Decimal

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# ----------------------------
# SAFETY PING (DO NOT REMOVE)
# ----------------------------
@router.get("/ping", dependencies=[Depends(require_admin)])
def admin_ping():
    return {"status": "admin alive"}

# ----------------------------
# SCHEMA
# ----------------------------
class ProductCreate(BaseModel):
    name: str
    price: condecimal(max_digits=10, decimal_places=2)  # MONEY ≠ float
    stock: conint(ge=0)  # no negative stock

# ----------------------------
# CREATE PRODUCT (ADMIN ONLY)
# ----------------------------
@router.post("/products", dependencies=[Depends(require_admin)])
def create_product(
    product: ProductCreate,
    db=Depends(get_db)
):
    cursor = db.cursor(dictionary=True, buffered=True)

    try:
        cursor.execute(
            """
            INSERT INTO products (name, price, stock)
            VALUES (%s, %s, %s)
            """,
            (product.name, product.price, product.stock)
        )
        db.commit()

        return {
            "message": "Product created",
            "product_id": cursor.lastrowid
        }

    finally:
        cursor.close()

# ----------------------------
# UPDATE STOCK (ADMIN ONLY)
# ----------------------------
@router.put("/products/{product_id}/stock", dependencies=[Depends(require_admin)])
def update_stock(
    product_id: int,
    stock: int = Query(..., ge=0),
    db=Depends(get_db)
):
    cursor = db.cursor(dictionary=True, buffered=True)

    try:
        cursor.execute(
            "UPDATE products SET stock = %s WHERE product_id = %s",
            (stock, product_id)
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        db.commit()

        return {
            "message": "Stock updated",
            "product_id": product_id,
            "stock": stock
        }

    finally:
        cursor.close()
