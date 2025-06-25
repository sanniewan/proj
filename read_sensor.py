import time
from atlas import AtlasI2C

def main():
    PROCESSING_DELAY = 0.9  # seconds to wait for processing

    sensor = AtlasI2C()
    devices = AtlasI2C.list_i2c_devices(sensor)
    sensor_objects = []
    for i in range (0, len(devices)):
        sensor_objects.append(AtlasI2C(address=devices[i]))
        time.sleep(0.1)
    while True:
        for sensor in sensor_objects:
            try:
                sensor.write("R")
                time.sleep(2)
                reading = sensor.read()
                device_info = sensor.get_device_info()
                print(f"Sensor 0x{sensor.address:02X} ({device_info}): {reading}")
            except Exception as e:
                print(f"Error reading sensor {sensor.get_device_info()}: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()
    