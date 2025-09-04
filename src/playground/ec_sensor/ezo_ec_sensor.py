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
    PROCESSING_DELAY = 0.6  # seconds
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

    def calibrate(self, command: str, ec: float=7.00) -> tuple[bool, str, str]:
        """Calibrates the EC at the EC value and scale specified
        
        Args:
            EC (float): current EC for the device to be calibrated against
            command (str): mid, low, high, clear; mid, low and high specify rank of current EC
                Cal,dry - single point calibration in air
                Cal,low,n - two point calibration at lowpoint
                Cal,high,n - three point calibration at highpoint
                Cal,clear - delete calibration data

        Returns:
            Tuple[bool, str, str]: A tuple containing:
                - error flag: True if an error occurred, False otherwise.
                - error message: Description of the error, empty if no error.
                - calibration level: ?CAL,0 or ?CAL,1 or ?CAL,2 calibration
                    where 0 is uncalibrated and three point is fully calibrated
        """
        err, msg = self._check_i2c_and_sensor()
        if err:
            return True, msg, ""

        if not self._sensor_configured:
            err, msg = self._configure_sensor()
            if err:
                return True, msg, ""
            
        # Send calibration command        ISSUING THE "Cal,mid" COMMAND WILL CLEAR ALL OTHER CALIBRATION POINTS.
        if (command == "low" or command == "high"):
            print(f"Command issued: {command}")
            print(f"EC value issued: {ec}")
            self._sensor.write(f"Cal,{command},{ec}")
            time.sleep(self.PROCESSING_DELAY)
            print("Calibrated")
        # Send dry calibration command
        elif (command == "dry"):
            self._sensor.write(f"Cal,{command}")
            time.sleep(self.PROCESSING_DELAY)
        # Delete calibration data
        elif (command == "clear"):
            self._sensor.write(f"Cal,{command}")
            time.sleep(self.PROCESSING_DELAY)
        # Command given is not valid
        else:
            err_msg = f"Command is not valid: input \"dry, low, high, or clear\". at {self._sensor_name} ({hex(self._address)})"
            return True, err_msg, "0"
        
        try: 
            # Check status of calibration
            self._sensor.write("Cal,?")
            time.sleep(self.PROCESSING_DELAY_TEMP)

            # Read response back
            cal_status = str(self._sensor.read())
        except Exception as e:
            err_msg = f"Error reading {self._sensor_name} ({hex(self._address)}): {e}"
            return True, err_msg, "0"

        return False, "", cal_status
    
    def check_calibration_status(self) -> tuple[bool, str, str]:
        """Checks the calibration status of the EC probe
        
        Returns:
            Tuple[bool, str, str]: A tuple containing:
                - error flag: True if an error occurred, False otherwise.
                - error message: Description of the error, empty if no error.
                - calibration level: ?CAL,0 or ?CAL,1 or ?CAL,2 calibration
                    where 0 is uncalibrated and 2 is fully calibrated
        """
        err, msg = self._check_i2c_and_sensor()
        if err:
            return True, msg, ""

        if not self._sensor_configured:
            err, msg = self._configure_sensor()
            if err:
                return True, msg, ""
        
        try: 
            # Check status of calibration
            self._sensor.write("Cal,?")
            time.sleep(self.PROCESSING_DELAY)

            # Read response back
            cal_status = str(self._sensor.read())
        except Exception as e:
            err_msg = f"Error reading {self._sensor_name} ({hex(self._address)}): {e}"
            return True, err_msg, "0"

        return False, "", cal_status


def main() -> None:
    """Main function demonstrating the usage of the EC sensor."""
    # logging.basicConfig(level=logging.INFO)
    temperature = 20.0  # Example temperature for compensation
    sensor = AtlasEzoEcSensor(0x64)

    while True:
        error, message, ec_value = sensor.read(temperature)
        if error:
            print(f"Error: {message}")
        else:
            print(f"EC Reading: {ec_value} μS/cm")
            
        print("Enter parameters for calibration solution your EC probe is currently submerged in:")
        
        # # Provide option for calibrating midpoint, lowpoint, or highpoint.
        # dry_low_hi = input("    Enter dry , low, or high to calibrate respective point:")
        
        # # Enter the EC value of the calibration solution
        # ec_val_cal = input(f"    Enter the EC value of the {dry_low_hi}point solution:")
        
        # print("Calibrating now:")
        # # Calibrate EC probe with user-entered parameters and print status
        # err1, message1, cal_status = sensor.calibrate(dry_low_hi,ec_val_cal)
        # if err1:
        #     print(f"    Error: {message1}")
        # else:
        #     print(f"    Cal level: {cal_status}")
            
        # Print calibration status of pH probe
        print("Calibration Status:")
        err2, message2, cal_status2 = sensor.check_calibration_status()
        if err2:
            print(f"    Error: {message2}")
        else:
            print(f"    cal level: {cal_status2}")
        
        time.sleep(1)


if __name__ == "__main__":
    main()