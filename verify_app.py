import requests
import os
import time

BASE_URL = "http://127.0.0.1:5000"
CACHE_FILE = "stock_data.csv"

def verify():
    session = requests.Session()
    
    print("1. Signing Up...")
    res = session.post(f"{BASE_URL}/sign-up", data={"username": "testuser", "password": "password"})
    if res.url == f"{BASE_URL}/dashboard":
        print("   Success: Signed up and redirected to dashboard.")
    else:
        print(f"   Failed: Redirected to {res.url}")

    print("2. Checking Dashboard Data (First Load)...")
    # Dashboard load triggers API call
    res = session.get(f"{BASE_URL}/dashboard")
    if "Mega 7 Dashboard" in res.text:
        print("   Success: Dashboard loaded.")
    else:
        print("   Failed: Dashboard content missing.")

    print("3. Checking Cache File Creation...")
    if os.path.exists(CACHE_FILE):
        print(f"   Success: {CACHE_FILE} created.")
        initial_mtime = os.path.getmtime(CACHE_FILE)
    else:
        print(f"   Failed: {CACHE_FILE} not found.")
        return

    print("4. Checking Cache Usage (Second Load)...")
    time.sleep(1) # Ensure time difference if file were to be touched (though we depend on date)
    
    res = session.get(f"{BASE_URL}/dashboard")
    current_mtime = os.path.getmtime(CACHE_FILE)
    
    if current_mtime == initial_mtime:
         print("   Success: Cache file NOT modified (Cached data used).")
    else:
         print("   Failed: Cache file modified (API called again?).")

    print("\nVerification Complete.")

if __name__ == "__main__":
    # Ensure fresh start
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    
    try:
        verify()
    except Exception as e:
        print(f"Verification failed with error: {e}")
