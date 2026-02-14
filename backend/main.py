from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from cart.router import router as cart_router
from orders.router import router as orders_router
from analytics.router import router as analytics_router
from auth.router import router as auth_router
from auth.dependencies import get_current_user
from admin.router import router as admin_router
from database import get_db
from fastapi.middleware.cors import CORSMiddleware
import hashlib

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # OK for demo/internship
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- ROUTERS ----------------
app.include_router(auth_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(analytics_router)
app.include_router(admin_router)

# ---------------- HEALTH ----------------
@app.get("/")
def root():
    return {"status": "shopping cart backend running"}

# ---------------- AUTH SANITY ----------------
@app.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# ---------------- PRODUCTS ----------------
@app.get("/products")
def get_products(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    return products

# ---------------- USERS ----------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


@app.post("/users")
def create_user(user: UserCreate, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True, buffered=True)

    password_hash = hashlib.sha256(user.password.encode()).hexdigest()

    cursor.execute(
        "SELECT user_id FROM users WHERE email = %s",
        (user.email,),
    )
    if cursor.fetchone():
        cursor.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    cursor.execute(
        """
        INSERT INTO users (name, email, password_hash)
        VALUES (%s, %s, %s)
        """,
        (user.name, user.email, password_hash),
    )
    db.commit()

    user_id = cursor.lastrowid
    cursor.close()

    return {
        "user_id": user_id,
        "name": user.name,
        "email": user.email,
    }

