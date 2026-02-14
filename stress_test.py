import requests
import threading
import sys

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/login"
CHECKOUT_URL = f"{BASE_URL}/orders/checkout"

USER_EMAIL = "user@test.com"
USER_PASSWORD = "user123"

# -----------------------------
# AUTO LOGIN — GET FRESH JWT
# -----------------------------
login_resp = requests.post(
    LOGIN_URL,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data=f"username={USER_EMAIL}&password={USER_PASSWORD}"
)

if login_resp.status_code != 200:
    print("❌ Login failed:", login_resp.text)
    sys.exit(1)

token = login_resp.json()["access_token"]

HEADERS = {
    "Authorization": f"Bearer {token}"
}

print("✅ Logged in, token acquired")

# -----------------------------
# CONCURRENT CHECKOUT TEST
# -----------------------------
results = []

def hit_checkout(i):
    try:
        r = requests.post(CHECKOUT_URL, headers=HEADERS)
        results.append((i, r.status_code, r.text))
    except Exception as e:
        results.append((i, "EXCEPTION", str(e)))

threads = []

for i in range(10):  # 10 concurrent requests
    t = threading.Thread(target=hit_checkout, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# -----------------------------
# RESULTS
# -----------------------------
print("\n==== STRESS TEST RESULTS ====")
for r in results:
    print(r)
