# multi_property_all_in_one.py  (replace your file with this)
import requests
import re
import time
import json
import csv
import os
from datetime import datetime, timedelta

# ===============================
# TTLock OAuth / API config
# ===============================
CLIENT_ID = '3a5eb18b49bc4df0b85703071f9e96a5'
CLIENT_SECRET = '19e2a1afb5bfada46f6559c346777017'  # required for refresh flow
OAUTH_HOST = 'https://api.sciener.com'              # OAuth tokens come from here
TTLOCK_API_BASE = 'https://euapi.ttlock.com'        # Lock control API base

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
    data['expires_at'] = _now() + data.get('expires_in', 7200) - 60  # small buffer
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

# ===============================
# ALL PROPERTIES IN ONE PLACE
# ===============================
PROPERTIES = {
    "tooting": {
        "FRONT_DOOR_LOCK_ID": 20641052,
        "ROOM_LOCK_IDS": {
            'Room 1': 21318606,
            'Room 2': 21321678,
            'Room 3': 21319208,
            'Room 4': 21321180,
            'Room 5': 21321314,
            'Room 6': 21973872,
        },
        "ICAL_URLS": {
            'Room 1': "https://io.eviivo.com/pms/v2/open/property/TooStaysSW17/rooms/7c131bbd-8e63-48bd-a60e-c46cbdd5ea86/ical.ics",
            'Room 2': "https://io.eviivo.com/pms/v2/open/property/TooStaysSW17/rooms/85d5035f-18fa-4f44-a9ae-05a67e068a04/ical.ics",
            'Room 3': "https://io.eviivo.com/pms/v2/open/property/TooStaysSW17/rooms/365e28a8-b6a9-4497-b286-58b6eebf6cec/ical.ics",
            'Room 4': "https://io.eviivo.com/pms/v2/open/property/TooStaysSW17/rooms/231e6d4a-9d9f-4a3f-bd89-701fb017d52f/ical.ics",
            'Room 5': "https://io.eviivo.com/pms/v2/open/property/TooStaysSW17/rooms/a20cdff1-f242-4d2c-8b4c-30d891e95460/ical.ics",
            'Room 6': "https://io.eviivo.com/pms/v2/open/property/TooStaysSW17/rooms/7919787f-89bd-4e25-97aa-6147cf490fe9/ical.ics"
        },
    },
    "streatham": {
        "FRONT_DOOR_LOCK_ID": 16273050,   # UPDATED front door
        "ROOM_LOCK_IDS": {
            'Room 1': 24719576,
            'Room 2': 24641840,
            'Room 3': 24719570,
            'Room 4': 24746950,           # UPDATED room 4
            'Room 5': 24717236,
            'Room 6': 24717242,
            'Room 7': None,
            'Room 8': None,
            'Room 9': 24692300,
            'Room 10': 24717964,
            'Room 11': None,
        },
        "ICAL_URLS": {
            'Room 1': "https://io.eviivo.com/pms/v2/open/property/StreathamRoomsCR4/rooms/913d99b1-2eef-4c92-878d-732407d458dd/ical.ics",
            'Room 2': "https://io.eviivo.com/pms/v2/open/property/StreathamRoomsCR4/rooms/859bbdad-ed8b-401c-b1c6-15eadad7035f/ical.ics",
            'Room 3': "https://io.eviivo.com/pms/v2/open/property/StreathamRoomsCR4/rooms/0484521e-b98b-46f8-b71a-50adeea7cc23/ical.ics",
            'Room 4': "https://io.eviivo.com/pms/v2/open/property/StreathamRoomsCR4/rooms/e2e623fd-b7d4-4580-bb63-4a0f7ddeb1a5/ical.ics",
            'Room 5': "https://io.eviivo.com/pms/v2/open/property/StreathamRoomsCR4/rooms/880b9a67-fe17-4d6f-8c3e-bb194dcc1eeb/ical.ics",
            'Room 6': "https://io.eviivo.com/pms/v2/open/property/StreathamRoomsCR4/rooms/b1c750b8-0c22-4fa1-b113-322fca48c20b/ical.ics",
            'Room 7': "https://io.eviivo.com/pms/v2/open/property/StreathamRoomsCR4/rooms/e5b80ef1-5d72-4546-b6dc-62d3d5a426be/ical.ics",
            'Room 8': "https://io.eviivo.com/pms/v2/open/property/StreathamRoomsCR4/rooms/1102b319-9da1-4f75-aced-020129964a3e/ical.ics",
            'Room 9': "https://io.eviivo.com/pms/v2/open/property/StreathamRoomsCR4/rooms/d772f9c8-f1d8-4bb4-9234-8c46c747400f/ical.ics",
            'Room 10': "https://io.eviivo.com/pms/v2/open/property/StreathamRoomsCR4/rooms/29fea56a-c6ba-42d9-9d89-e20094c8b2bb/ical.ics",
            'Room 11': "https://io.eviivo.com/pms/v2/open/property/StreathamRoomsCR4/rooms/cd990a37-0e27-4f1c-8664-ad3cad3fa845/ical.ics",
        },
    },
    "norwich": {
        "FRONT_DOOR_LOCK_ID": 17503964,  # front door only
        "ROOM_LOCK_IDS": {
            'Room 1': None,
            'Room 2': None,
            'Room 3': None,
            'Room 4': None,
            'Room 5': None,
        },
        "ICAL_URLS": {
            'Room 1': "https://io.eviivo.com/pms/v2/open/property/SeamStaysNR2/rooms/25bcbb93-cab7-4b1a-9d1c-967f797fa034/ical.ics",
            'Room 2': "https://io.eviivo.com/pms/v2/open/property/SeamStaysNR2/rooms/9e8ac4e3-8965-4c9f-bea0-e592865ee7f1/ical.ics",
            'Room 3': "https://io.eviivo.com/pms/v2/open/property/SeamStaysNR2/rooms/f5bca5de-5b4b-49de-9b44-522c9f691e91/ical.ics",
            'Room 4': "https://io.eviivo.com/pms/v2/open/property/SeamStaysNR2/rooms/28fc46c9-2ba6-4bcf-9978-367c3b7f20e8/ical.ics",
            'Room 5': "https://io.eviivo.com/pms/v2/open/property/SeamStaysNR2/rooms/a8d9c366-8e93-467d-a421-e2b6da60bc3c/ical.ics",
        },
    },
}

# ===============================
# Helpers
# ===============================
def unfold_ical_lines(text: str) -> str:
    return re.sub(r'\r?\n[ \t]', '', text)

def parse_ical_events(text: str):
    events = []
    matches = re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", unfold_ical_lines(text), re.DOTALL)
    for block in matches:
        event = {}
        for field in ["DESCRIPTION", "DTSTART", "DTEND", "UID", "SUMMARY"]:
            m = re.search(rf"{field}(?:;[^:]*)?:(.+)", block)
            event[field] = m.group(1).strip() if m else ""
        events.append(event)
    return events

def parse_datetime(raw):
    try:
        return datetime.strptime(raw, "%Y%m%dT%H%M%S") if "T" in raw else datetime.strptime(raw, "%Y%m%d")
    except Exception:
        return None

def extract_summary_code(summary: str) -> str:
    """
    Extract 4-digit code from SUMMARY:
    • Preferred: match at start like '123-4...' -> '1234'
    • Fallback: first 3 chars + 5th char if length>=5
    """
    if not summary:
        print("❌ No SUMMARY present")
        return None
    m = re.match(r'^\s*(\d{3})-(\d)\b', summary)
    if m:
        code = m.group(1) + m.group(2)
        print(f"✅ Using SUMMARY {summary!r} -> Code: {code}")
        return code
    if len(summary) >= 5:
        code = summary[0:3] + summary[4]
        print(f"✅ Using SUMMARY (fallback) {summary!r} -> Code: {code}")
        return code
    print("❌ SUMMARY too short to extract code:", summary)
    return None

def extract_booking_id(uid: str) -> str:
    m = re.search(r'eviivo-booking-(.+)', uid)
    return m.group(1) if m else uid

def to_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)

def is_weekend(date) -> bool:
    return date.weekday() >= 5

# ===============================
# TTLock create code (with token refresh + retry)
# ===============================
def _ttlock_add_keyboard_pwd(payload):
    url = f"{TTLOCK_API_BASE}/v3/keyboardPwd/add"
    return requests.post(url, data=payload, timeout=30)

def create_lock_code_simple(lock_id, code, name, start, end, code_type="Room", booking_id=""):
    payload = {
        "clientId": CLIENT_ID,
        "accessToken": get_access_token(),
        "lockId": lock_id,
        "keyboardPwd": code,
        "keyboardPwdName": f"{name} - {code_type} - {booking_id}",
        "keyboardPwdType": 3,              # period
        "startDate": to_ms(start),
        "endDate": to_ms(end),
        "addType": 2,                      # cloud/app
        "date": int(time.time() * 1000),
    }

    print(f"📤 Creating {code_type} code '{code}' for {name}")
    try:
        api_res = _ttlock_add_keyboard_pwd(payload)
        try:
            result = api_res.json()
        except json.JSONDecodeError:
            print("❌ Invalid JSON response from TTLock")
            return False

        # If token invalid, refresh and retry once
        if result.get("errcode") in (10003, 10004, -2010):  # invalid token / invalid grant
            print("🔁 Token invalid; refreshing and retrying…")
            tok = _load_token()
            if not tok.get("refresh_token"):
                print("❌ No refresh_token available. Run token helper first.")
                return False
            try:
                newtok = _refresh_with_refresh_token(tok)
                payload["accessToken"] = newtok["access_token"]
                api_res = _ttlock_add_keyboard_pwd(payload)
                result = api_res.json()
            except Exception as e:
                print(f"❌ Refresh failed: {e}")
                return False

        if result.get("errcode") == 0:
            print(f"✅ {code_type} code {code} created successfully")
            return True
        elif result.get("errcode") == -3007:
            print(f"⚠️ Code {code} already exists on {code_type} - might be OK if same booking")
            return True
        elif result.get("errcode"):
            print(f"❌ API error {result.get('errcode')} - {result.get('errmsg', 'Unknown error')}")
            return False
        else:
            print(f"✅ {code_type} code {code} created successfully")
            return True

    except requests.exceptions.Timeout:
        print("❌ TTLock API timeout")
        return False
    except Exception as e:
        print(f"❌ TTLock API error: {e}")
        return False

# ===============================
# Booking collection / processing
# ===============================
def collect_bookings_for_property(ICAL_URLS):
    all_bookings = []
    print("📊 COLLECTING ALL BOOKINGS")
    print("="*60)

    now = datetime.now()
    cutoff_date = now - timedelta(days=1)

    for room_name, url in ICAL_URLS.items():
        print(f"\n📅 Collecting bookings for {room_name}...")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            events = parse_ical_events(response.text)

            room_bookings = 0
            for event in events:
                start = parse_datetime(event.get("DTSTART", ""))
                end = parse_datetime(event.get("DTEND", ""))
                if not start or not end:
                    continue

                if end.date() >= cutoff_date.date():
                    summary_code = extract_summary_code(event.get("SUMMARY", ""))
                    booking = {
                        'room': room_name,
                        'name': event["DESCRIPTION"].split()[0] if event.get("DESCRIPTION") else "Guest",
                        'start_date': start.date(),
                        'end_date': end.date(),
                        'check_in': start.replace(hour=15, minute=0, second=0),
                        'check_out': end.replace(hour=11, minute=0, second=0),
                        'booking_id': extract_booking_id(event.get("UID", "")),
                        'access_code': summary_code,  # from SUMMARY
                        'description': event.get("DESCRIPTION", ""),
                        'summary': event.get("SUMMARY", ""),
                        'spans_weekend': any(is_weekend((start + timedelta(days=i)).date()) for i in range((end - start).days + 1))
                    }
                    all_bookings.append(booking)
                    room_bookings += 1
                    print(f"  ➡️ {booking['name']}: {booking['start_date']} to {booking['end_date']} | Code: {summary_code or 'NONE'} | SUMMARY: {booking['summary']!r}")

            print(f"   Found {room_bookings} upcoming bookings")
        except Exception as e:
            print(f"❌ Error collecting bookings for {room_name}: {e}")

    print(f"\n📋 TOTAL BOOKINGS COLLECTED: {len(all_bookings)}")
    with_code = [b for b in all_bookings if b['access_code']]
    without_code = [b for b in all_bookings if not b['access_code']]
    print(f"✅ Bookings WITH summary codes: {len(with_code)}")
    print(f"❌ Bookings WITHOUT summary codes: {len(without_code)}")
    if without_code:
        print(f"\n⚠️ Bookings missing SUMMARY-derived codes (showing up to 5):")
        for b in without_code[:5]:
            print(f"   • {b['name']} - {b['room']} - {b['start_date']}")
            print(f"     SUMMARY: {b.get('summary','')[:80]}...")

    return all_bookings

def process_bookings_for_property(property_name, config, bookings, writer):
    FRONT_DOOR_LOCK_ID = config["FRONT_DOOR_LOCK_ID"]
    ROOM_LOCK_IDS = config["ROOM_LOCK_IDS"]

    print("\n🔄 PROCESSING BOOKINGS - SUMMARY-BASED CODE")
    print("="*60)
    print("🔢 Will create codes using SUMMARY pattern: first 3 chars + 5th char (e.g., '123-4' → '1234')")
    print("🔧 No conflict checking - just attempt to create codes")

    now = datetime.now()

    for booking in bookings:
        if booking['end_date'] < now.date():
            continue

        print("\n" + "="*50)
        print(f"👤 Processing: {booking['name']} - {booking['room']}")
        print(f"📅 {booking['start_date']} to {booking['end_date']}")
        print(f"📝 SUMMARY: {booking.get('summary','')}")

        access_code = booking['access_code']
        if not access_code:
            print("❌ SKIPPING: No SUMMARY-derived code found")
            writer.writerow([property_name, booking['booking_id'], booking['name'], booking['room'],
                             booking['start_date'], booking['end_date'], 'None', 'NO', 'NO', 'NO',
                             'YES' if booking['spans_weekend'] else 'NO', 'No SUMMARY-derived code'])
            continue

        print(f"🔑 Using Summary Code: {access_code}")

        # Front door
        front_success = False
        if FRONT_DOOR_LOCK_ID:
            print("🚪 Creating front door code...")
            front_success = create_lock_code_simple(
                FRONT_DOOR_LOCK_ID, access_code, booking['name'],
                booking['check_in'], booking['check_out'],
                "Front Door", booking['booking_id']
            )
            time.sleep(1)
        else:
            print("🚪 Skipping front door (no lock ID set)")

        # Room
        room_success = False
        room_lock_id = ROOM_LOCK_IDS.get(booking['room'])
        print(f"🏠 Creating {booking['room']} code...")
        if room_lock_id:
            room_success = create_lock_code_simple(
                room_lock_id, access_code, booking['name'],
                booking['check_in'], booking['check_out'],
                booking['room'], booking['booking_id']
            )
        else:
            print(f"🏠 Skipping {booking['room']} (no room lock configured)")

        overall_success = front_success or room_success

        writer.writerow([
            property_name,
            booking['booking_id'],
            booking['name'],
            booking['room'],
            booking['start_date'],
            booking['end_date'],
            access_code,
            'YES' if front_success else 'NO',
            'YES' if room_success else 'NO',
            'YES' if overall_success else 'NO',
            'YES' if booking['spans_weekend'] else 'NO',
            '' if overall_success else ('No lock ID configured' if (not FRONT_DOOR_LOCK_ID and not room_lock_id) else 'Failed to create code')
        ])

        time.sleep(2)

def run_all_properties(selected=None):
    """
    selected: list like ['tooting','norwich'] to limit scope. If None, runs all.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_name = f"simple_phone_report_ALL_{timestamp}.csv"
    with open(csv_name, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Property','Booking_ID','Guest_Name','Room','Check_In','Check_Out',
                         'Access_Code','Front_Success','Room_Success','Overall_Success','Is_Weekend','Failure_Reason'])

        targets = selected or list(PROPERTIES.keys())
        for prop in targets:
            cfg = PROPERTIES[prop]
            print("\n" + "="*80)
            print(f"🏨 {prop.upper()} LOCK CODE GENERATOR - SUMMARY-BASED")
            print("="*80)
            print("🔢 Codes derived from SUMMARY (first 3 chars + 5th char, e.g., '123-4' → '1234')")
            print("🔧 Simple approach - attempts to create codes directly")

            bookings = collect_bookings_for_property(cfg["ICAL_URLS"])
            process_bookings_for_property(prop, cfg, bookings, writer)

    print(f"\n💾 Combined CSV saved: {csv_name}")
    print("🎯 ALL PROPERTIES COMPLETE!")

if __name__ == "__main__":
    run_all_properties()
