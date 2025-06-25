import time
from atlas_ezo import AtlasEzoPhSensor

def main():
    address = 0x63  # I2C address of the sensor
    temperature = 20.0  # Example temperature for compensation
    sensor = AtlasEzoPhSensor(address)

    while True:
        err, message, ph_value = sensor.read(temperature)
        if err:
            print(f"Error: {message}")
        else:
            print(f"pH: {ph_value} @ {temperature}°C")
        time.sleep(1)

if __name__ == "__main__":
    main()