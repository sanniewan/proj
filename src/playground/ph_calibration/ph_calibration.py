import time
import board
from busio import I2C
from atlas import AtlasI2C


class AtlasEzoPhSensor:
    """Represents an Atlas Scientific pH probe.
    
    The sensor uses the I2C communication protocol and provides pH readings.
    """

    PROCESSING_DELAY = 0.9  # seconds
    PROCESSING_DELAY_TEMP = 0.3
    PROCESSING_DELAY_CAL = 0.3

    def __init__(self, address: int) -> None:
        """Initializes the pH sensor with the specified I2C address.

        Args:
            address (int): The I2C address of the pH sensor.
        """
        self._sensor_name = "Atlas EZO pH Probe"
        self._address = address
        self._sensor = None
        self._sensor_configured = False
        self.error, self.message = self._configure_sensor()

    def _check_i2c_and_sensor(self) -> tuple[bool, str]:
        """Checks if the I2C bus and sensor are detected.

        Returns:
            Tuple[bool, str]: A tuple containing:
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
        """Configures the pH probe.

        Returns:
            Tuple[bool, str]: A tuple containing:
                - error flag: True if an error occurred, False otherwise.
                - message: Success or error message.
        """
        self._sensor_configured = False

        err, msg = self._check_i2c_and_sensor()
        if err:
            return True, msg

        try:
            self._sensor = AtlasI2C(address=self._address, moduletype="PH")
            self._sensor_configured = True
        except Exception as e:
            self._sensor = None
            msg = f"Error configuring {self._sensor_name} ({hex(self._address)}): {e}"
            return True, msg

        msg = f"Successfully configured {self._sensor_name} ({hex(self._address)})"
        return False, msg

    def read(self, temperature: float) -> tuple[bool, str, float]:
        """Reads the pH value from the probe.

        Args:
            temperature (float): The water temperature for compensation.

        Returns:
            Tuple[bool, str, float]: A tuple containing:
                - error flag: True if an error occurred, False otherwise.
                - error message: Description of the error, empty if no error.
                - pH value: The pH value read by the probe.
        """
        err, msg = self._check_i2c_and_sensor()
        if err:
            return True, msg, -99.9

        if not self._sensor_configured:
            err, msg = self._configure_sensor()
            if err:
                return True, msg, -99.9

        try:
            # Set temperature compensation
            self._sensor.write(f"T,{temperature}")
            time.sleep(self.PROCESSING_DELAY_TEMP)

            # Request a pH reading
            self._sensor.write("R")
            time.sleep(self.PROCESSING_DELAY)

            # Read the pH value
            ph_value = float(self._sensor.read())
        except Exception as e:
            err_msg = f"Error reading {self._sensor_name} ({hex(self._address)}): {e}"
            return True, err_msg, -99.9

        return False, "", ph_value

    def calibrate(self, command: str, pH: float) -> tuple[bool, str, str]:
        """Calibrates the pH at the pH value and scale specified
        
        Args:
            pH (float): current pH for the device to be calibrated against
            command (str): mid, low, high, clear; mid, low and high specify rank of current pH
        
        Returns:
            Tuple[bool, str, str]: A tuple containing:
                - error flag: True if an error occurred, False otherwise.
                - error message: Description of the error, empty if no error.
                - calibration level: ?CAL,0 or ?CAL,1 or ?CAL,2 or ?CAL,3 calibration
                    where 0 is uncalibrated and three point is fully calibrated
        """
        err, msg = self._check_i2c_and_sensor()
        if err:
            return True, msg, ""

        if not self._sensor_configured:
            err, msg = self._configure_sensor()
            if err:
                return True, msg, ""
        
        try: 
            # Send calibration command        ISSUING THE "Cal,mid" COMMAND WILL CLEAR ALL OTHER CALIBRATION POINTS.
            # self._sensor.write(f"Cal,{command},{pH}")
            time.sleep(self.PROCESSING_DELAY)

            # Check status of calibration
            self._sensor.write("Cal,?")
            time.sleep(self.PROCESSING_DELAY_CAL)

            # Read response back
            cal_status = str(self._sensor.read())
        except Exception as e:
            err_msg = f"Error reading {self._sensor_name} ({hex(self._address)}): {e}"
            return True, err_msg, "0"

        return False, "", cal_status


def main() -> None:
    """Main function to demonstrate the usage of the AtlasEzoPhSensor class."""
    address = 0x63  # I2C address of the pH sensor
    temperature = 20.0  # Example temperature for compensation
    sensor = AtlasEzoPhSensor(address)

    while True:
        # Read pH value and print
        err, message, ph_value = sensor.read(temperature)
        if err:
            print(f"Error: {message}")
        else:
            print(f"pH: {ph_value} @ {temperature}°C")

        # Calibrate pH probe with known solutions and print status
        err1, message1, cal_status = sensor.calibrate("dim",7)  # CHANGE THIS
        if err1:
            print(f"Error: {message1}")
        else:
            print(f"cal level: {cal_status}")
        
        time.sleep(5)


if __name__ == '__main__':
    main()