import time
import logging
from typing import Tuple

import board
from busio import I2C
from adafruit_ahtx0 import AHTx0


class DHT20Sensor:
    """Represents an Adafruit DHT20 (AHT20) sensor using the I2C communication protocol.

    The DHT20 measures temperature in degrees Celsius and relative humidity in percentage.
    """

    SENSOR_NAME = "DHT20 Air T-RH Sensor"
    INVALID_TEMPERATURE = -99.9
    INVALID_HUMIDITY = -9
    INVALID_CO2 = -9
    DEFAULT_ADDRESS = 0x38

    def __init__(self, address: int) -> None:
        """Initializes the DHT20 sensor.

        Args:
            address (int): The I2C address of the sensor.
        """
        self._address = address
        self._sensor = None
        self._sensor_configured = False
        self._logger = logging.getLogger(__name__)
        self.error, self.message = self._configure_sensor()

    def _check_i2c_and_sensor(self) -> Tuple[bool, str]:
        """Checks if the I2C bus and sensor are detected.

        Returns:
            Tuple[bool, str]: A tuple containing:
                error (bool): True if an error occurred, False otherwise.
                message (str): Error message if an error occurred, empty otherwise.
        """
        try:
            i2c = I2C(board.SCL, board.SDA)
            detected_devices = i2c.scan()
        except Exception as e:
            error_message = f"Error scanning I2C bus: {e}"
            return True, error_message

        if self._address not in detected_devices:
            error_message = f"Error detecting {self.SENSOR_NAME} (0x{self._address:02X})"
            return True, error_message

        return False, ""

    def _configure_sensor(self) -> Tuple[bool, str]:
        """Configures the DHT20 sensor.

        Returns:
            Tuple[bool, str]: A tuple containing:
                error (bool): True if an error occurred, False otherwise.
                message (str): Success or error message.
        """
        self._sensor_configured = False

        error, message = self._check_i2c_and_sensor()
        if error:
            return True, message

        try:
            i2c = I2C(board.SCL, board.SDA)
            self._sensor = AHTx0(i2c, address=self._address)
            self._sensor.calibrate()
            self._sensor_configured = True
            success_message = (
                f"Successfully configured {self.SENSOR_NAME} (0x{self._address:02X})"
            )
            self._logger.info(success_message)
            return False, success_message
        except Exception as e:
            self._sensor = None
            error_message = (
                f"Error configuring {self.SENSOR_NAME} (0x{self._address:02X}): {e}"
            )
            self._logger.error(error_message)
            return True, error_message

    def read(self) -> Tuple[bool, str, float, int]:
        """Reads temperature and relative humidity from the sensor.

        Returns:
            Tuple[bool, str, float, int]: A tuple containing:
                error (bool): True if an error occurred, False otherwise.
                message (str): Error message if an error occurred, empty otherwise.
                temperature (float): Temperature in degrees Celsius.
                humidity (int): Relative humidity in percentage.
        """
        error, message = self._check_i2c_and_sensor()
        if error:
            return True, message, self.INVALID_TEMPERATURE, self.INVALID_HUMIDITY, self.INVALID_CO2

        if not self._sensor_configured:
            error, message = self._configure_sensor()
            if error:
                return True, message, self.INVALID_TEMPERATURE, self.INVALID_HUMIDITY, self.INVALID_CO2

        try:
            temperature = float(self._sensor.temperature)
            humidity = int(self._sensor.relative_humidity)
            co2_concentration = int(0)
            return False, "", temperature, humidity, co2_concentration
        except Exception as e:
            error_message = (
                f"Error reading {self.SENSOR_NAME} (0x{self._address:02X}): {e}"
            )
            self._logger.error(error_message)
            return True, error_message, self.INVALID_TEMPERATURE, self.INVALID_HUMIDITY, self.INVALID_CO2


def main():
    """Main function to initialize the sensor and read data periodically."""
    address = DHT20Sensor.DEFAULT_ADDRESS
    sensor = DHT20Sensor(address)

    while True:
        error, message, temperature, humidity, co2_concentration = sensor.read()
        if error:
            print(f"Error: {message}")
        else:
            msg1 = f"Temperature: {temperature}°C\tRelative Humidity: {humidity}%"
            msg2 = f"\tCO2 Concentration: {co2_concentration} ppm"
        time.sleep(5)


if __name__ == "__main__":
    main()