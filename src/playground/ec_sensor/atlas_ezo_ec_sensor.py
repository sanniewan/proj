import logging
import time
from typing import Tuple

import board
from busio import I2C

from modules.atlas import AtlasI2C


class AtlasEzoEcSensor:
    """Represents an Atlas Scientific EC (Electrical Conductivity) probe.

    The sensor uses the I2C communication protocol and provides EC readings.
    """

    SENSOR_NAME = "Atlas EZO Electrical Conductivity Probe"
    PROCESSING_DELAY = 1.4  # seconds (1.0 was too fast)
    PROCESSING_DELAY_TEMP = 0.3  # seconds
    INVALID_EC = -99.9
    DEFAULT_ADDRESS = 0x64  # I2C address of the EC sensor

    def __init__(self, address: int = DEFAULT_ADDRESS) -> None:
        """Initializes the EC sensor with the specified I2C address.

        Args:
            address (int): The I2C address of the EC sensor.
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
        """Configures the EC probe.

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
            self._sensor = AtlasI2C(address=self._address, moduletype="EC")
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

    def read(self, temperature: float) -> Tuple[bool, str, float]:
        """Reads the electrical conductivity (EC) value from the probe.

        Args:
            temperature (float): The water temperature used for EC compensation.

        Returns:
            Tuple[bool, str, float]: A tuple containing:

                - error (bool): True if an error occurred, False otherwise.
                - message (str): Error message if an error occurred, empty otherwise.
                - ec_value (float): The EC value read by the probe.
        """
        error, message = self._check_i2c_and_sensor()
        if error:
            return True, message, self.INVALID_EC

        if not self._sensor_configured:
            error, message = self._configure_sensor()
            if error:
                return True, message, self.INVALID_EC

        try:
            # Set the temperature compensation
            self._sensor.write(f"T,{temperature}")
            time.sleep(self.PROCESSING_DELAY_TEMP)

            # Request an EC reading
            self._sensor.write("R")
            time.sleep(self.PROCESSING_DELAY)

            # Read the EC value
            ec_value = float(self._sensor.read())
            return False, "", ec_value
        except Exception as e:
            error_message = (
                f"Error reading {self.SENSOR_NAME} (0x{self._address:02X}): {e}"
            )
            self._logger.error(error_message)
            return True, error_message, self.INVALID_EC


def main() -> None:
    """Main function demonstrating the usage of the EC sensor."""
    logging.basicConfig(level=logging.INFO)
    temperature = 20.0  # Example temperature for compensation
    sensor = AtlasEzoEcSensor()

    while True:
        error, message, ec_value = sensor.read(temperature)
        if error:
            logging.error(f"Error: {message}")
        else:
            logging.info(f"EC Reading: {ec_value} μS/cm")
        time.sleep(5)


if __name__ == "__main__":
    main()