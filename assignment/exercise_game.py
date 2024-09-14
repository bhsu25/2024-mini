"""
Response time - single-threaded
"""

from machine import Pin
import time
import random
import json
import requests
import network

url = "https://mini-f8aad-default-rtdb.firebaseio.com/"
SSID = "BU Guest (unencrypted)"

def connect_to_wifi(ssid):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid)
    
    buffer_time = 10
    while buffer_time > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        buffer_time -= 1
        print('Connecting...')
        time.sleep(1)
        
    if wlan.status() == 3:
        print('Connected...')
        return True
    else:
        print('Not connected to Wi-Fi.')
        return False

total_flashes: int = 2
flash_duration_ms = 500

def random_time_interval(min_time: float, max_time: float) -> float:
    """Returns a random time interval between max_time and min_time"""
    return random.uniform(min_time, max_time)

def blinker(flash_count: int, led: Pin) -> None:
    """Blink the LED flash_count times."""
    for _ in range(flash_count):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)

def write_json(json_filename: str, data: dict) -> None:
    """Writes data to a JSON file.

    Parameters
    ----------

    json_filename: str
        The name of the file to write to. This will overwrite any existing file.

    data: dict
        Dictionary data to write to the file.
    """
    with open(json_filename, "w") as f:
        json.dump(data, f)

def scorer(response_times: list[int | None]) -> None:
    """Calculate and print the score and statistics from response times."""
    missed_responses = response_times.count(None)
    print(f"You missed the light {missed_responses} / {len(response_times)} times")

    t_good = [time for time in response_times if time is not None]
    print(t_good)

    if t_good:
        max_response_time = max(t_good)
        min_response_time = min(t_good)
        avg_response_time = sum(t_good) / len(t_good)
    else:
        avg_response_time = min_response_time = max_response_time = None

    print(f"Response Times: {t_good}, Avg: {avg_response_time}, Min: {min_response_time}, Max: {max_response_time}")

    metrics = {
        "average_response_time": avg_response_time,
        "min_response_time": min_response_time,
        "max_response_time": max_response_time,
        "missed_responses": missed_responses,
        "success_rate": (total_flashes - missed_responses) / total_flashes
    }

    now = time.localtime()
    now_str = "-".join(map(str, now[:3])) + "T" + "_".join(map(str, now[3:6]))
    filename = f"score-{now_str}.json"

    print("Writing", filename)

    response = requests.post(url + f"{filename}", data=json.dumps(metrics))
    print(response.text)

# Connect to Wi-Fi
connect_to_wifi(SSID)
led = Pin("LED", Pin.OUT)
button = Pin(15, Pin.IN, Pin.PULL_UP)

response_times: list[int | None] = []

blinker(3, led)

for _ in range(total_flashes):
    time.sleep(random_time_interval(0.5, 5.0))

    led.high()

    tic = time.ticks_ms()
    response_time = None
    while time.ticks_diff(time.ticks_ms(), tic) < flash_duration_ms:
        if button.value() == 0:
            response_time = time.ticks_diff(time.ticks_ms(), tic)
            led.low()
            break
    response_times.append(response_time)

    led.low()

blinker(5, led)

scorer(response_times)
