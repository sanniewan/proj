# works same as i2cdetect -y 1

from atlas import AtlasI2C


def main():
    # List all available I2C devices
    sensor = AtlasI2C()
    devices = AtlasI2C.list_i2c_devices(sensor)
    print("Available I2C devices:", devices)
if __name__ == "__main__":
    main()