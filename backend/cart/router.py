from fastapi import APIRouter, Depends, HTTPException
from cart.schemas import CartCreate
from database import get_db
from auth.dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


# =========================================================
# ADD / UPDATE CART ( +1 / -1 ONLY )
# =========================================================
@router.post("")
def update_cart(
    cart: CartCreate,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    user_id = current_user["user_id"]
    cursor = db.cursor(dictionary=True)

    # 1️⃣ Validate product
    cursor.execute(
        "SELECT stock FROM products WHERE product_id = %s",
        (cart.product_id,)
    )
    product = cursor.fetchone()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 2️⃣ Check cart
    cursor.execute(
        """
        SELECT quantity FROM cart
        WHERE user_id = %s AND product_id = %s
        """,
        (user_id, cart.product_id)
    )
    existing = cursor.fetchone()

    # 🔒 Clamp delta to ±1 ONLY
    delta = 1 if cart.quantity > 0 else -1

    # =====================================================
    # ITEM EXISTS
    # =====================================================
    if existing:
        new_qty = existing["quantity"] + delta

        # Remove item if qty <= 0
        if new_qty <= 0:
            cursor.execute(
                "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
                (user_id, cart.product_id)
            )
            db.commit()
            return {"message": "Item removed"}

        # Stock check
        if new_qty > product["stock"]:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        cursor.execute(
            """
            UPDATE cart
            SET quantity = %s
            WHERE user_id = %s AND product_id = %s
            """,
            (new_qty, user_id, cart.product_id)
        )

    # =====================================================
    # NEW ITEM → ONLY +1 ALLOWED
    # =====================================================
    else:
        if delta < 0:
            raise HTTPException(status_code=400, detail="Invalid operation")

        if product["stock"] < 1:
            raise HTTPException(status_code=400, detail="Out of stock")

        cursor.execute(
            """
            INSERT INTO cart (user_id, product_id, quantity)
            VALUES (%s, %s, 1)
            """,
            (user_id, cart.product_id)
        )

    db.commit()
    return {"message": "Cart updated"}


# =========================================================
# GET CART
# =========================================================
@router.get("")
def get_cart(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    user_id = current_user["user_id"]
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            c.product_id,
            p.name,
            p.price,
            c.quantity,
            (p.price * c.quantity) AS subtotal
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
        """,
        (user_id,)
    )

    items = cursor.fetchall()
    total = sum(item["subtotal"] for item in items) if items else 0

    return {"items": items, "total": total}

