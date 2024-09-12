import requests
import json
import firebase_admin
from firebase_admin import auth, credentials
from machine import Pin
import time
import random

# Initialize the Firebase app with your credentials
cred = credentials.Certificate("/Users/dev/Desktop/mini-f8aad-firebase-adminsdk-r6nm9-167cb44e80.json")
firebase_admin.initialize_app(cred)

N = 10
sample_ms = 10.0
on_ms = 500

firebase_url_template = "https://firestore.googleapis.com/v1/projects/mini-f8aad/databases/(default)/documents/users/{user_id}/data/response_times"

def random_time_interval(tmin: float, tmax: float) -> float:
    return random.uniform(tmin, tmax)

def blinker(N: int, led: Pin) -> None:
    for _ in range(N):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)

def scorer(t: list[int | None]) -> dict:
    misses = t.count(None)
    t_good = [x for x in t if x is not None]
    average = sum(t_good) / len(t_good) if t_good else 0

    print(f"You missed the light {misses} / {len(t)} times, avg: {average:.2f}, min: {min(t_good)}, max: {max(t_good)}")
    print(t_good)

    return {
        "misses": misses,
        "average": average,
        "min": min(t_good) if t_good else None,
        "max": max(t_good) if t_good else None,
        "score": (len(t_good) / len(t)) if len(t) > 0 else 0,
    }

def upload_to_firebase(data: dict, id_token: str, user_id: str) -> None:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {id_token}"  # Secure the request with the user's idToken
    }

    firebase_url = firebase_url_template.format(user_id=user_id)
    firestore_data = {
        "fields": {
            "GameTimesJson": {"stringValue": json.dumps(data)}
        }
    }
    
    response = requests.post(firebase_url, data=json.dumps(firestore_data), headers=headers)
    if response.status_code == 200:
        print("Data successfully uploaded.")
    else:
        print(f"Failed to upload data: {response.text}")

def authenticate_user(email: str):
    ALLOWED_EMAILS = ["trieut415@gmail.com", "bhsu25@bu.edu"]

    if email not in ALLOWED_EMAILS:
        raise ValueError("This email is not allowed to sign in.")

    user = auth.get_user_by_email(email)
    id_token = auth.create_custom_token(user.uid)
    return id_token, user.uid

if __name__ == "__main__":
    try:
        email = 'trieut415@gmail.com'
        id_token, user_id = authenticate_user(email)
    except ValueError as e:
        print(e)
        exit(1)

    led = Pin(0, Pin.OUT)
    button = Pin(15, Pin.IN, Pin.PULL_UP)

    t: list[int | None] = []

    blinker(3, led)

    for i in range(N):
        time.sleep(random_time_interval(0.5, 5.0))

        led.high()

        tic = time.ticks_ms()
        t0 = None
        while time.ticks_diff(time.ticks_ms(), tic) < on_ms:
            if button.value() == 0:
                t0 = time.ticks_diff(time.ticks_ms(), tic)
                led.low()
                break
        t.append(t0)

        led.low()

    blinker(5, led)

    scores = scorer(t)
    upload_to_firebase(scores, id_token, user_id)
