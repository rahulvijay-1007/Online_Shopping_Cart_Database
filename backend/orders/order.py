from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from auth.dependencies import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/checkout")
def checkout(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    user_id = current_user["user_id"]
    cursor = db.cursor(dictionary=True, buffered=True)

    try:
        # 1️⃣ Fetch cart items
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
            """,
            (user_id,)
        )
        cart_items = cursor.fetchall()

        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        # 2️⃣ Validate stock + calculate total
        total_amount = 0
        for item in cart_items:
            if item["quantity"] > item["stock"]:
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
            "message": "Order created successfully",
            "order_id": order_id,
            "total_amount": total_amount
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
