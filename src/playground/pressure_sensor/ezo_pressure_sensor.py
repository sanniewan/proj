import time
import board
from busio import I2C
from modules.atlas import AtlasI2C


class AtlasEzoPressureSensor:
    """Represents an Atlas Scientific Pressure Sensor using the I2C communication protocol."""

    PROCESSING_DELAY = 0.3  # seconds
    LONG_PROC_DELAY = 0.9  # seconds

    def __init__(self, address: int) -> None:
        """Initializes the pressure sensor.

        Args:
            address (int): The I2C address of the pressure sensor.
        """
        self._sensor_name = "Atlas EZO Pressure Sensor"
        self._address = address
        self._sensor = None
        self._sensor_configured = False
        self.error, self.message = self._configure_sensor()

    def _check_i2c_and_sensor(self) -> tuple[bool, str]:
        """Checks if the I2C bus and sensor are detected.

        Returns:
            tuple[bool, str]: A tuple containing:
                - error flag: True if an error occurred, False otherwise.
                - message: Error message if an error occurred, empty otherwise.
        """
        try:
            i2c = I2C(board.SCL, board.SDA)
            detected_i2c_devices = i2c.scan()
        except Exception as e:
            msg = f"Error scanning I2C bus: {e}"
            return True, msg

        if self._address not in detected_i2c_devices:
            msg = f"Error detecting {self._sensor_name} ({hex(self._address)})"
            return True, msg

        return False, ""

    def _configure_sensor(self) -> tuple[bool, str]:
        """Configures the pressure sensor.

        Returns:
            tuple[bool, str]: A tuple containing an error flag and a message.
        """
        self._sensor_configured = False

        err, msg = self._check_i2c_and_sensor()
        if err:
            return True, msg

        try:
            self._sensor = AtlasI2C(address=self._address, moduletype="PRES")

            # Set pressure units to cmH2O
            self._sensor.write("U,cmh2o")
            time.sleep(self.LONG_PROC_DELAY)

            # Set output to 1 decimal
            self._sensor.write("Dec,1")
            time.sleep(self.LONG_PROC_DELAY)

            self._sensor_configured = True
        except Exception as e:
            self._sensor = None
            msg = f"Error configuring {self._sensor_name} ({hex(self._address)}): {e}"
            return True, msg

        msg = f"Successfully configured {self._sensor_name} ({hex(self._address)})"
        return False, msg

    def read(self) -> tuple[bool, str, float]:
        """Reads the pressure value from the sensor.

        Returns:
            tuple[bool, str, float]: A tuple containing:
                - error flag: True if an error occurred, False otherwise.
                - error message: Description of the error, empty if no error.
                - pressure value: The pressure value in cmH2O.
        """
        err, msg = self._check_i2c_and_sensor()
        if err:
            return True, msg, -99.9

        if not self._sensor_configured:
            err, msg = self._configure_sensor()
            if err:
                return True, msg, -99.9

        try:
            self._sensor.write("R")
            time.sleep(self.PROCESSING_DELAY)
            pressure = float(self._sensor.read())
        except Exception as e:
            err_msg = f"Error reading {self._sensor_name} ({hex(self._address)}): {e}"
            return True, err_msg, -99.9

        return False, "", pressure

    def set_zero_point(self) -> tuple[bool, str]:
        """Sets the zero point calibration for the pressure sensor.

        Returns:
            tuple[bool, str]: A tuple containing an error flag and a message.
        """
        try:
            self._sensor.write("Cal,0")
            time.sleep(self.LONG_PROC_DELAY)
            return False, ""
        except Exception as e:
            msg = f"Error setting zero point for {self._sensor_name} ({hex(self._address)}): {e}"
            return True, msg

    def set_i2c_address(self, new_address: int) -> tuple[bool, str]:
        """Changes the I2C address of the sensor.

        Args:
            new_address (int): The new I2C address.

        Returns:
            tuple[bool, str]: A tuple containing an error flag and a message.
        """
        try:
            self._sensor.write(f"I2C,{new_address}")
            time.sleep(self.LONG_PROC_DELAY)
            self._address = new_address
            msg = f"I2C address changed to {hex(new_address)}"
            return False, msg
        except Exception as e:
            msg = f"Error changing I2C address to {hex(new_address)}: {e}"
            return True, msg


def main():
    address = 0x6A
    sensor = AtlasEzoPressureSensor(address)

    # Uncomment to set zero point
    # err, msg = sensor.set_zero_point()
    # if err:
    #     print(f"Error: {msg}")
    # else:
    #     print("Zero point calibration successful")
    # exit(0)

    while True:
        err, message, pressure = sensor.read()
        if err:
            print(f"Error: {message}")
        else:
            print(f"Pressure: {pressure} cmH2O")
        time.sleep(2)

    # Uncomment to change I2C address
    # new_address = 0x6B
    # err, msg = sensor.set_i2c_address(new_address)
    # if err:
    #     print(f"Error: {msg}")
    # else:
    #     print(msg)
    # exit(0)


if __name__ == '__main__':
    main()