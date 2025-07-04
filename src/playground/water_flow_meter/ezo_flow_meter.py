import time
import board
from busio import I2C
from modules.atlas import AtlasI2C


class AtlasEzoFlowMeter:
    """Represents an Atlas Scientific Flow Meter using the I2C communication protocol."""

    PROCESSING_DELAY = 0.3  # seconds

    def __init__(self, address: int, meter_type: str) -> None:
        """Initializes the Flow Meter with the given address and meter type.

        Args:
            address (int): The I2C address of the flow meter.
            meter_type (str): The type of the flow meter (e.g., '3/8', '1/4', '1/2', '3/4').
        """
        self._sensor_name = "Atlas EZO Flow Meter"
        self._address = address
        self._meter_type = meter_type
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
        """Configures the flow meter.

        Returns:
            tuple[bool, str]: A tuple containing:
                - error flag: True if an error occurred, False otherwise.
                - message: Success or error message.
        """
        self._sensor_configured = False

        err, msg = self._check_i2c_and_sensor()
        if err:
            return True, msg

        try:
            self._sensor = AtlasI2C(address=self._address, moduletype="FLO")

            # Configure meter type
            self._sensor.write(f"Set,{self._meter_type}")
            time.sleep(self.PROCESSING_DELAY)

            # Configure units to L and per L/minute
            self._sensor.write("CF,1")  # Liter
            time.sleep(self.PROCESSING_DELAY)
            self._sensor.write("Frp,m")  # per minute
            time.sleep(self.PROCESSING_DELAY)

            # Configure output
            self._sensor.write("O,TV,1")  # Enable total volume
            time.sleep(self.PROCESSING_DELAY)
            self._sensor.write("O,FR,1")  # Enable flow rate
            time.sleep(self.PROCESSING_DELAY)

            self._sensor_configured = True
        except Exception as e:
            self._sensor = None
            msg = f"Error configuring {self._sensor_name} ({hex(self._address)}): {e}"
            return True, msg

        msg = f"Successfully configured {self._sensor_name} ({hex(self._address)})"
        return False, msg

    def read(self) -> tuple[bool, str, float, float]:
        """Reads the current volume and flow rate from the flow meter.

        Returns:
            tuple[bool, str, float, float]: A tuple containing:
                - error flag: True if an error occurred, False otherwise.
                - error message: Description of the error, empty if no error.
                - volume: The total volume in liters.
                - flow rate: The flow rate in liters per minute.
        """
        err, msg = self._check_i2c_and_sensor()
        if err:
            return True, msg, -99.9, -99.9

        if not self._sensor_configured:
            err, msg = self._configure_sensor()
            if err:
                return True, msg, -99.9, -99.9

        try:
            self._sensor.write("R")
            time.sleep(self.PROCESSING_DELAY * 2)
            result = self._sensor.read().split(",")
            volume, rate = float(result[0]), float(result[1])
        except Exception as e:
            err_msg = f"Error reading {self._sensor_name} ({hex(self._address)}): {e}"
            return True, err_msg, -99.9, -99.9

        return False, "", volume, rate

    def clear(self) -> tuple[bool, str]:
        """Clears the flow meter's data.

        Returns:
            tuple[bool, str]: A tuple containing:
                - error flag: True if an error occurred, False otherwise.
                - message: Success or error message.
        """
        err, msg = self._check_i2c_and_sensor()
        if err:
            return True, msg

        if not self._sensor_configured:
            err, msg = self._configure_sensor()
            if err:
                return True, msg

        try:
            self._sensor.write("Clear")
            time.sleep(self.PROCESSING_DELAY)
        except Exception as e:
            err_msg = f"Error clearing {self._sensor_name} ({hex(self._address)}): {e}"
            return True, err_msg

        msg = f"Successfully cleared {self._sensor_name} ({hex(self._address)})"
        return False, msg


def main() -> None:
    """Main function to demonstrate the usage of the AtlasEzoFlowMeter class."""
    address = 0x68  # I2C address of the flow meter
    meter_type = "3/8"
    sensor = AtlasEzoFlowMeter(address, meter_type)

    while True:
        err, message, volume, rate = sensor.read()
        if err:
            print(f"Error: {message}")
        else:
            print(f"Total Volume (L): {volume}\nFlow Rate (L/min): {rate}")
        time.sleep(5)


if __name__ == '__main__':
    main()