# Agrowtek water level sensor module
import time
import board
import digitalio

class AgrowtekWaterLevelSensor:
    """
    Agrowtek water level sensor module.
    This module reads the water level sensor with a digital i/o pin.
    """
    DEFAULT_SENSOR_PIN = 17 # IO17 pin on rpi

    def __init__(self, pin: int = DEFAULT_SENSOR_PIN) -> None:
        """Initializes sensor with default pin number.

        Args:
            pin (int): The I/O pin number of the optical level sensor.
        """
        self._pin = pin
        self._sensor_configured = False
        self._sensor = None
        self.error, self.message = self._configure_sensor()

    def _configure_sensor(self) -> tuple[bool, str]:
        """Configure the water level sensor.

        Returns:
            Tuple[bool, str]: A tuple of (error, message). If error is False, configuration succeeded.
        """
        try:
            pin_name = f"D{self._pin}"
            pin = getattr(board, pin_name)  # Convert integer to pin object

            self._sensor = digitalio.DigitalInOut(pin)
            self._sensor.direction = digitalio.Direction.INPUT
            self._sensor.pull = digitalio.Pull.UP  # Prevents floating input

            self._sensor_configured = True
            return False, f"Sensor configured successfully on GPIO {self._pin}."

        except AttributeError:
            return True, f"Invalid GPIO pin: D{self._pin} is not defined in `board`."

        except ValueError as e:
            return True, f"ValueError configuring pin D{self._pin}: {e}"

        except Exception as e:
            return True, f"Unexpected error configuring sensor on D{self._pin}: {e}"
            
    def read(self) -> bool:
        """Reads whether or not sensor detects water
        Returns:
            Boolean:
                True if water is not detected (HIGH), False otherwise (LOW).
        """
        return self._sensor.value

def main() -> None:
    """Main function to demonstrate the usage of the AgrowtekWaterLevelSensor class."""
    pin = 17
    vatsensor = AgrowtekWaterLevelSensor(pin)
    try:
        while True:
            if vatsensor.read():
                print("No water detected. Please refill the tank.")
            else:
                print("Water level is sufficient.")
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()