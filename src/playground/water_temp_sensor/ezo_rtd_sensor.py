import logging
import time
from typing import Tuple

import board
from busio import I2C

from modules.atlas import AtlasI2C


class AtlasEzoRtdSensor:
    """Represents an Atlas Scientific RTD (Resistance Temperature Detector) water temperature probe.

    The sensor uses the I2C communication protocol and provides water temperature readings.
    """

    SENSOR_NAME = "Atlas EZO RTD Water Temperature Probe"
    PROCESSING_DELAY = 1.1  # seconds
    INVALID_TEMPERATURE = -99.9
    DEFAULT_ADDRESS = 0x66

    def __init__(self, address: int = DEFAULT_ADDRESS) -> None:
        """Initializes the RTD sensor with the provided I2C address.

        Args:
            address (int): The I2C address of the temperature sensor.
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
            error_message = (
                f"Error detecting {self.SENSOR_NAME} (0x{self._address:02X})"
            )
            return True, error_message

        return False, ""

    def _configure_sensor(self) -> Tuple[bool, str]:
        """Configures the Atlas Scientific RTD sensor.

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
            self._sensor = AtlasI2C(address=self._address, moduletype="RTD")
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

    def read(self) -> Tuple[bool, str, float]:
        """Reads the temperature from the water temperature probe.

        Returns:
            Tuple[bool, str, float]: A tuple containing:

                - error (bool): True if an error occurred, False otherwise.
                - message (str): Error message if an error occurred, empty otherwise.
                - temperature (float): The temperature value read by the probe.
        """
        error, message = self._check_i2c_and_sensor()
        if error:
            return True, message, self.INVALID_TEMPERATURE

        if not self._sensor_configured:
            error, message = self._configure_sensor()
            if error:
                return True, message, self.INVALID_TEMPERATURE

        try:
            self._sensor.write("R")
            time.sleep(self.PROCESSING_DELAY)
            temperature = float(self._sensor.read())
            return False, "", temperature
        except Exception as e:
            error_message = (
                f"Error reading {self.SENSOR_NAME} (0x{self._address:02X}): {e}"
            )
            self._logger.error(error_message)
            return True, error_message, self.INVALID_TEMPERATURE


def main() -> None:
    """Main entry point of the program. Continuously reads data from the sensor."""
    logging.basicConfig(level=logging.INFO)
    sensor = AtlasEzoRtdSensor()  # Default address = 0x66

    while True:
        error, message, temperature = sensor.read()
        if error:
            logging.error(f"Error: {message}")
        else:
            logging.info(f"Sensor reading: {temperature}°C")
        time.sleep(5)


if __name__ == "__main__":
    main()