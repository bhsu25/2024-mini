import requests
import json
from machine import Pin
import time
import random

N: int = 10
sample_ms = 10.0
on_ms = 500

firebase_url = "https://firestore.googleapis.com/v1/projects/mini-f8aad/databases/(default)/documents/response_times"

def upload_to_firebase(data: dict, id_token: str = '') -> None:
    headers = {
        "Content-Type": "application/json",
    }
    if id_token:
        headers["Authorization"] = f"Bearer {id_token}"
    
    json_data = json.dumps(data)
    
    firestore_data = {
        "GameTimesJson": json_data  
    }
    
    response = requests.post(firebase_url, data=json.dumps(firestore_data), headers=headers)
    print(response.text)

def random_time_interval(tmin: float, tmax: float) -> float:
    """return a random time interval between max and min"""
    return random.uniform(tmin, tmax)

def blinker(N: int, led: Pin) -> None:
    for _ in range(N):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)

def write_json(json_filename: str, data: dict) -> None:
    """Writes data to a JSON file."""
    with open(json_filename, "w") as f:
        json.dump(data, f)

def scorer(t: list[int | None]) -> dict:
    misses = t.count(None)

    # Print the statement with the formatted average
    t_good = [x for x in t if x is not None]

    if len(t_good) == 0:
        average = 0
    else:
        average = sum(t_good) / len(t_good)

    print(f"You missed the light {misses} / {len(t)} times, avg: {average:.2f}, min: {min(t_good)}, max: {max(t_good)}")
    print(t_good)

    # Prepare the data to upload to Firebase
    data = {
        "misses": misses,
        "average": average,
        "min": min(t_good) if t_good else None,
        "max": max(t_good) if t_good else None,
        "score": (len(t_good) / len(t)) if len(t) > 0 else 0,
    }

    return data

if __name__ == "__main__":
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

    upload_to_firebase(scores)
