from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from auth.dependencies import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


# =========================================================
# GET ORDERS — SUMMARY
# =========================================================
@router.get("")
def get_orders(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    user_id = current_user["user_id"]
    cursor = db.cursor(dictionary=True, buffered=True)

    try:
        cursor.execute(
            """
            SELECT
                order_id,
                total_amount,
                created_at
            FROM orders
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

        orders = cursor.fetchall()
        return {"orders": orders}

    finally:
        cursor.close()


# =========================================================
# CHECKOUT — TRANSACTION + STOCK LOCKING (CRITICAL)
# =========================================================
@router.post("/checkout")
def checkout(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    user_id = current_user["user_id"]
    cursor = db.cursor(dictionary=True, buffered=True)

    try:
        # 🔐 Explicit transaction
        cursor.execute("START TRANSACTION")

        # 1️⃣ Lock cart + product rows
        cursor.execute(
            """
            SELECT
                c.product_id,
                c.quantity,
                p.price,
                p.stock
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
            FOR UPDATE
            """,
            (user_id,)
        )

        cart_items = cursor.fetchall()

        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        # 2️⃣ Validate stock + calculate total
        total_amount = 0
        for item in cart_items:
            if item["stock"] < item["quantity"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product {item['product_id']}"
                )
            total_amount += item["price"] * item["quantity"]

        # 3️⃣ Create order
        cursor.execute(
            """
            INSERT INTO orders (user_id, total_amount)
            VALUES (%s, %s)
            """,
            (user_id, total_amount)
        )
        order_id = cursor.lastrowid

        # 4️⃣ Insert order_items + reduce stock
        for item in cart_items:
            cursor.execute(
                """
                INSERT INTO order_items
                (order_id, product_id, quantity, price_at_purchase)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    order_id,
                    item["product_id"],
                    item["quantity"],
                    item["price"]
                )
            )

            cursor.execute(
                """
                UPDATE products
                SET stock = stock - %s
                WHERE product_id = %s
                """,
                (item["quantity"], item["product_id"])
            )

        # 5️⃣ Clear cart
        cursor.execute(
            "DELETE FROM cart WHERE user_id = %s",
            (user_id,)
        )

        db.commit()

        return {
            "message": "Order placed successfully",
            "order_id": order_id,
            "total_amount": total_amount
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Checkout failed. Transaction rolled back."
        )

    finally:
        cursor.close()


# =========================================================
# ORDER HISTORY — GROUPED RESPONSE
# =========================================================
@router.get("/history")
def order_history(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    user_id = current_user["user_id"]
    cursor = db.cursor(dictionary=True, buffered=True)

    try:
        cursor.execute(
            """
            SELECT
                o.order_id,
                o.created_at,
                o.total_amount,

                oi.product_id,
                p.name AS product_name,
                oi.quantity,
                oi.price_at_purchase
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE o.user_id = %s
            ORDER BY o.created_at DESC
            """,
            (user_id,)
        )

        rows = cursor.fetchall()

        # -------- GROUPING LOGIC --------
        orders = {}
        for row in rows:
            oid = row["order_id"]

            if oid not in orders:
                orders[oid] = {
                    "order_id": oid,
                    "created_at": row["created_at"],
                    "total_amount": row["total_amount"],
                    "items": []
                }

            orders[oid]["items"].append({
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "quantity": row["quantity"],
                "price_at_purchase": row["price_at_purchase"]
            })

        return {"orders": list(orders.values())}

    finally:
        cursor.close()
