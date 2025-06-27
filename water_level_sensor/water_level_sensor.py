# Agrowtek water level sensor module
import time
import board
import digitalio

# Use board pin reference for GPIO17
SENSOR_PIN = board.D17

def setup_sensor():
    sensor = digitalio.DigitalInOut(SENSOR_PIN)
    sensor.direction = digitalio.Direction.INPUT
    sensor.pull = digitalio.Pull.UP  # Use pull-up if needed, else set to None
    return sensor

def read_water_level(sensor):
    """
    Returns True if water is not detected (HIGH), False otherwise (LOW).
    """
    return sensor.value  # True = HIGH, False = LOW

if __name__ == "__main__":
    sensor = setup_sensor()
    try:
        while True:
            if read_water_level(sensor):
                print("No water detected.")
            else:
                print("Water detected!")
            time.sleep(1)
    except KeyboardInterrupt:
        pass