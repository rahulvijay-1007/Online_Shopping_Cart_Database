import mysql.connector

def get_db():
    db = mysql.connector.connect(
        host="mysql",
        user="boss",
        password="boss123",
        database="shopping_cart_db",
        autocommit=True   # 🔥 THIS IS THE FIX
    )
    try:
        yield db
    finally:
        db.close()
