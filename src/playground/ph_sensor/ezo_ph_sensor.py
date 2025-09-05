import time
import board
from busio import I2C
from modules.atlas import AtlasI2C


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

    def calibrate(self, command: str, pH: float=7.00) -> tuple[bool, str, str]:
        """Calibrates the pH at the pH value and scale specified
        
        Args:
            pH (float): current pH for the device to be calibrated against
            command (str): mid, low, high, clear; mid, low and high specify rank of current pH
                Cal,mid,n - single point calibration at midpoint
                Cal,low,n - two point calibration at lowpoint
                Cal,high,n - three point calibration at highpoint
                Cal,clear - delete calibration data

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
            if (command == "mid" or command == "low" or command == "high"):
                self._sensor.write(f"Cal,{command},{pH}")
                time.sleep(self.PROCESSING_DELAY)
            # Delete calibration data
            elif (command == "clear"):
                self._sensor.write(f"Cal,{command}")
                time.sleep(self.PROCESSING_DELAY)
            # Command given is not valid
            else:
                err_msg = f"Command is not valid: input \"mid, low, high, or clear\". at {self._sensor_name} ({hex(self._address)})"
                return True, err_msg, "0"

            # Check status of calibration
            self._sensor.write("Cal,?")
            time.sleep(self.PROCESSING_DELAY_CAL)

            # Read response back
            cal_status = str(self._sensor.read())
        except Exception as e:
            err_msg = f"Error reading {self._sensor_name} ({hex(self._address)}): {e}"
            return True, err_msg, "0"

        return False, "", cal_status
        
    def check_calibration_status(self) -> tuple[bool, str, str]:
        """Checks the calibration status of the pH probe
        
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
            # Check status of calibration
            self._sensor.write("Cal,?")
            time.sleep(self.PROCESSING_DELAY_CAL)

            # Read response back
            cal_status = str(self._sensor.read())
        except Exception as e:
            err_msg = f"Error reading {self._sensor_name} ({hex(self._address)}): {e}"
            return True, err_msg, "0"

        return False, "", cal_status

    def check_export(self) -> tuple[bool, str, str]:
        """Checks how many strings to export
        """
        err, msg = self._check_i2c_and_sensor()
        if err:
            return True, msg, "0"

        if not self._sensor_configured:
            err, msg = self._configure_sensor()
            if err:
                return True, msg, "0"
        
        try: 
            # Check status of calibration
            self._sensor.write("Export,?")
            time.sleep(self.PROCESSING_DELAY_CAL)

            # Read response back
            num_strings = str(self._sensor.read())
        except Exception as e:
            err_msg = f"Error checking export strings {self._sensor_name} ({hex(self._address)}): {e}"
            return True, err_msg, "0"

        return False, "", num_strings
    
    def export(self, raw_num_strings: str) -> tuple[bool, str, list[str]]:
        """Exports strings
        """
        err, msg = self._check_i2c_and_sensor()
        if err:
            return True, msg, "0"

        if not self._sensor_configured:
            err, msg = self._configure_sensor()
            if err:
                return True, msg, "0"
        
        try:
            # Split by commas
            parts = raw_num_strings.split(",")

            # Get the second value (index 1)
            num_strings = int(parts[1])   # "6" -> 6
            
            export_strings = []
            for i in range(num_strings):
                # Check status of calibration
                self._sensor.write("Export")
                time.sleep(self.PROCESSING_DELAY_CAL)

                # Read response back
                export_string = str(self._sensor.read())
                # print(f"Export string {i+1}: {export_string}")
                
                # Store export strings in a list
                export_strings.append(export_string)
            
        except Exception as e:
            err_msg = f"Error exporting strings {self._sensor_name} ({hex(self._address)}): {e}"
            return True, err_msg, "0"

        return False, "", export_strings
    
    def import_cal_string(self, import_strings: list[str]) -> tuple[bool, str, list[str]]:
            """Exports strings
            """
            err, msg = self._check_i2c_and_sensor()
            if err:
                return True, msg, "0"

            if not self._sensor_configured:
                err, msg = self._configure_sensor()
                if err:
                    return True, msg, "0"
            
            try:
                self._sensor.query(f"Import,{len(import_strings)+1}")
                time.sleep(self.PROCESSING_DELAY)
                
                for s in import_strings:
                    self._sensor.query(f"Import,{s}")
                    print(f"Import,{s}")
                    time.sleep(self.PROCESSING_DELAY_CAL)
                    
            except Exception as e:
                err_msg = f"Error importing strings {self._sensor_name} ({hex(self._address)}): {e}"
                return True, err_msg, "0"

            return False, "", import_strings


def main() -> None:
    """Main function to demonstrate the usage of the AtlasEzoPhSensor class."""
    address = 0x63  # I2C address of the pH sensor
    temperature = 24.0  # Water temperature for compensation
    sensor = AtlasEzoPhSensor(address)

    while True:
        # Read pH value and print
        time.sleep(1)
        
        err, message, ph_value = sensor.read(temperature)
        if err:
            print(f"Error: {message}\n")
        else:
            print(f"Current pH reading from sensor: pH: {ph_value} @ {temperature}°C\n")
        
        print("Enter parameters for calibration solution your pH probe is currently submerged in:")
        
        # Print calibration status of pH probe
        print("Calibration Status:")
        err2, message2, cal_status2 = sensor.check_calibration_status()
        if err2:
            print(f"    Error: {message2}")
        else:
            print(f"    cal level: {cal_status2}")
        
        ########## UNCOMMENT TO CALIBRATE ##########
        # # Provide option for calibrating midpoint, lowpoint, or highpoint.
        # mid_low_hi = input("    Enter low , mid, or high to calibrate respective point:")
        
        # # Enter the ph value of the calibration solution
        # ph_val_cal = input(f"    Enter the pH value of the {mid_low_hi}point solution:")
        
        # print("Calibrating now:")
        # # Calibrate pH probe with user-entered parameters and print status
        # err1, message1, cal_status = sensor.calibrate(mid_low_hi,ph_val_cal)
        # if err1:
        #     print(f"    Error: {message1}")
        # else:
        #     print(f"    Cal level: {cal_status}")

        
        ########## UNCOMMENT TO EXPORT STRINGS ##########
        # # Print number of strings to export
        # print("Exporting data:")
        # err3, msg3, num_strings = sensor.check_export()
        # if err3:
        #     print(f"    Error: {msg3}")
        # else:
        #     print(f"    Number of strings to export: {num_strings}")
        
        # # Export strings and print
        # err4, msg4, export_strings = sensor.export(num_strings)
        # if err4:
        #     print(f"    Error: {msg4}")
        # else:
        #     for i, string in enumerate(export_strings):
        #         print(f"    Export string {i+1}: {string}")

        ########## UNCOMMENT TO IMPORT STRINGS ##########
        # # Import strings and print
        # to_import = ['0024FFC683B2','41C3807044C3','010101000080','400000E04000','002041005DE7']
        # err5, msg5, import_strings = sensor.import_cal_string(to_import)
        # if err5:
        #     print(f"    Error: {msg5}")

if __name__ == '__main__':
    main()