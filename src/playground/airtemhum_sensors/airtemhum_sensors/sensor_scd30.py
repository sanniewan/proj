import logging
import time
from typing import Tuple

import board
from busio import I2C
from adafruit_scd30 import SCD30


class SCD30Sensor:
    """Represents an Adafruit SCD30 NDIR sensor using the I2C communication protocol.

    The SCD30 measures CO2 concentration in ppm, temperature in degrees Celsius,
    and relative humidity in percentage.
    """

    SENSOR_NAME = "SCD30 Air CO2-T-RH Sensor"
    INVALID_TEMPERATURE = -99.9
    INVALID_HUMIDITY = -99
    INVALID_CO2 = -99
    DEFAULT_ADDRESS = 0x61

    def __init__(self, address: int = DEFAULT_ADDRESS) -> None:
        """Initializes the SCD30 sensor.

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

                - error (bool): True if an error occurred, False otherwise.
                - message (str): Error message if an error occurred, empty otherwise.
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
        """Configures the SCD30 sensor.

        Returns:
            Tuple[bool, str]: A tuple containing:

                - error (bool): True if an error occurred, False otherwise.
                - message (str): Success or error message.
        """
        self._sensor_configured = False

        error, message = self._check_i2c_and_sensor()
        if error:
            return True, message

        try:
            i2c = I2C(board.SCL, board.SDA)
            self._sensor = SCD30(i2c, address=self._address)
            self._sensor.measurement_interval = 5  # seconds
            self._sensor.ambient_pressure = 1013  # mbar
            self._sensor.altitude = 0  # meters
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

    def read(self) -> Tuple[bool, str, float, int, int]:
        """Reads CO2 concentration, temperature, and relative humidity from the sensor.

        Returns:
            Tuple[bool, str, float, int, int]: A tuple containing:

                - error (bool): True if an error occurred, False otherwise.
                - message (str): Error message if an error occurred, empty otherwise.
                - temperature (float): Temperature in degrees Celsius.
                - humidity (int): Relative humidity in percentage.
                - co2_concentration (int): CO2 concentration in parts per million (ppm).
        """
        error, message = self._check_i2c_and_sensor()
        if error:
            return True, message, self.INVALID_TEMPERATURE, \
                self.INVALID_HUMIDITY, self.INVALID_CO2

        if not self._sensor_configured:
            error, message = self._configure_sensor()
            if error:
                return True, message, self.INVALID_TEMPERATURE, \
                    self.INVALID_HUMIDITY,self.INVALID_CO2

        try:
            if self._sensor.data_available:
                temperature = float(self._sensor.temperature)
                humidity = int(self._sensor.relative_humidity)
                co2_concentration = int(self._sensor.CO2)
                return False, "", temperature, humidity, co2_concentration
            else:
                message = (
                    f"{self.SENSOR_NAME} (0x{self._address:02X}) has no data available"
                )
                self._logger.warning(message)
                return True, message, self.INVALID_TEMPERATURE, \
                    self.INVALID_HUMIDITY,self.INVALID_CO2

        except Exception as e:
            message = (
                f"Error reading {self.SENSOR_NAME} (0x{self._address:02X}): {e}"
            )
            self._logger.error(message)
            return True, message, self.INVALID_TEMPERATURE, \
                    self.INVALID_HUMIDITY,self.INVALID_CO2


def main() -> None:
    """Main function to continuously read data from the SCD30 sensor."""
    address = SCD30Sensor.DEFAULT_ADDRESS
    sensor = SCD30Sensor()

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