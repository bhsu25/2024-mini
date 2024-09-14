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

def connect_wifi(ssid):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid)
    
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('Waiting for connection...')
        time.sleep(1)
        
    if wlan.status() == 3:
        print('Connected successfully!')
        status = wlan.ifconfig()
        print(f'IP address: {status[0]}')
        return True
    else:
        print('Failed to connect to Wi-Fi')
        return False

N: int = 10
sample_ms = 10.0
on_ms = 500


def random_time_interval(tmin: float, tmax: float) -> float:
    """return a random time interval between max and min"""
    return random.uniform(tmin, tmax)


def blinker(N: int, led: Pin) -> None:
    # %% let user know game started / is over

    for _ in range(N):
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


def scorer(t: list[int | None]) -> None:
    # %% collate results
    misses = t.count(None)
    print(f"You missed the light {misses} / {len(t)} times")

    t_good = [x for x in t if x is not None]

    print(t_good)

    # add key, value to this dict to store the minimum, maximum, average response time
    # and score (non-misses / total flashes) i.e. the score a floating point number
    # is in range [0..1]
    
    if t_good:
        avg_time = sum(t_good)/len(t_good)
        min_time = min(t_good)
        max_time = max(t_good)
    else:
        avg_time = min_time = max_time = None
        
    
    print(f"Response Times: {t_good}")
    print(f"Avg: {avg_time}, min: {min_time}, max: {max_time}")
        
    data = {
        "average_time" : avg_time,
        "min_time" : min_time,
        "max_time" : max_time,
        "misses" : misses,
        "score" : (N - misses) / N 
        }

    # %% make dynamic filename and write JSON

    now: tuple[int] = time.localtime()

    now_str = "-".join(map(str, now[:3])) + "T" + "_".join(map(str, now[3:6]))
    filename = f"score-{now_str}.json"

    print("write", filename)

    
    response = requests.post(url + f"{filename}", data = json.dumps(data))
    print(response.text)

#if __name__ == "__main__":
    # using "if __name__" allows us to reuse functions in other script files

connect_wifi(SSID)
led = Pin("LED", Pin.OUT)
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

scorer(t)
