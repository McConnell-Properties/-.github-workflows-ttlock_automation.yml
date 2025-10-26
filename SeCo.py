import requests
import csv
import os
import time
from datetime import datetime, timedelta

# TTLock OAuth / API config
CLIENT_ID = '3a5eb18b49bc4df0b85703071f9e96a5'
CLIENT_SECRET = '19e2a1afb5bfada46f6559c346777017'
OAUTH_HOST = 'https://api.sciener.com'
TTLOCK_API_BASE = 'https://euapi.ttlock.com'
TOKEN_FILE = 'ttlock_token.json'

def _load_token():
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_token(d):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(d, f, indent=2)

def _now():
    return time.time()

def _token_valid(tok):
    return tok and tok.get('access_token') and tok.get('expires_at', 0) > _now()

def _refresh_with_refresh_token(tok):
    r = requests.post(f'{OAUTH_HOST}/oauth2/token', data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': tok['refresh_token'],
    }, timeout=30)
    r.raise_for_status()
    data = r.json()
    data['expires_at'] = _now() + data.get('expires_in', 7200) - 60
    _save_token(data)
    return data

def get_access_token():
    tok = _load_token()
    if _token_valid(tok):
        return tok['access_token']
    if tok.get('refresh_token'):
        data = _refresh_with_refresh_token(tok)
        return data['access_token']
    raise RuntimeError("No valid TTLock token. Run your token helper to create ttlock_token.json first.")

def to_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)

def create_lock_code_simple(lock_id, code, name, start, end, code_type="Room", booking_id=""):
    payload = {
        "clientId": CLIENT_ID,
        "accessToken": get_access_token(),
        "lockId": lock_id,
        "keyboardPwd": code,
        "keyboardPwdName": f"{name} - {code_type} - {booking_id}",
        "keyboardPwdType": 3,
        "startDate": to_ms(start),
        "endDate": to_ms(end),
        "addType": 2,
        "date": int(time.time() * 1000),
    }

    print(f"Creating {code_type} code '{code}' for {name}")
    try:
        api_res = requests.post(f"{TTLOCK_API_BASE}/v3/keyboardPwd/add", data=payload, timeout=30)
        result = api_res.json()
        if result.get("errcode") in (10003, 10004, -2010):
            print("Token invalid; refreshing and retrying…")
            tok = _load_token()
            if not tok.get("refresh_token"):
                print("No refresh_token available. Run token helper first.")
                return False
            newtok = _refresh_with_refresh_token(tok)
            payload["accessToken"] = newtok["access_token"]
            api_res = requests.post(f"{TTLOCK_API_BASE}/v3/keyboardPwd/add", data=payload, timeout=30)
            result = api_res.json()

        if result.get("errcode") == 0:
            print(f"Code {code} created successfully")
            return True
        elif result.get("errcode") == -3007:
            print(f"Code {code} already exists for {name} - might be OK if same booking")
            return True
        else:
            print(f"API error: {result.get('errcode')} - {result.get('errmsg', 'Unknown error')}")
            return False
    except requests.exceptions.Timeout:
        print("TTLock API timeout")
    except Exception as e:
        print(f"TTLock API error: {e}")
    return False

# ---- Main CSV logic ----

# Example mapping (customize/expand for your properties/locks):
LOCK_IDS = {
    "Tooting": 20641052,
    "Streatham": 16273050,
    "Norwich": 17503964,
    # add more as needed
}

def parse_date(date_str):
    # Adjust as needed based on Google Sheets export format, e.g. '%d/%m/%Y'
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unknown date format: {date_str}")

def process_bookings_from_csv(csvfile):
    with open(csvfile, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            property_name = row.get("Property") or "Tooting"  # Update as appropriate
            lock_id = LOCK_IDS.get(property_name)
            if not lock_id:
                print(f"Property {property_name} not configured!")
                continue

            code = row.get("ReservationCode")
            name = row.get("GuestName")
            check_in = parse_date(row.get("CheckIn") or "")
            check_out = parse_date(row.get("CheckOut") or "")
            # Add hours if needed
            check_in = check_in.replace(hour=15, minute=0, second=0)
            check_out = check_out.replace(hour=11, minute=0, second=0)
            create_lock_code_simple(
                lock_id, code, name, check_in, check_out, code_type="Front Door", booking_id=code
            )
            time.sleep(1)

if __name__ == "__main__":
    process_bookings_from_csv("bookings.csv")
