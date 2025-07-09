from playground.ph_sensor.ezo_ph_sensor import AtlasEzoPhSensor
from playground.peristaltic_pump.ezo_peristaltic_pump import PeristalticPumpI2cAddressChanger

class Controller:
    """
    A simple proportional controller.

    This class is independent of ROS and can be unit-tested.
    """

    def __init__(self, unit_name: str, target_low: float=5.5, target_high: float=6.5, crit_low: float=4, crit_high: float=8.5, kp: float = 0.01):
        self.target_low = target_low  # pH value
        self.target_high = target_high
        self.crit_low = crit_low
        self.crit_high = crit_high
        self.unit_name = unit_name
        self.kp = kp

    def compute(self, measurement: float) -> tuple[bool, str, float]:
        """
        Compute the control effort based on the error between the target and the measurement, if the measurement is out of range.

        Args:
            measurement (float): Current sensor reading.

        Returns:
            Tuple[bool, str, float]: A tuple containing:
                - Error/Warning flag: True if an error or warning occurred, False otherwise.
                - Error/Warning message: Description of the error or warning, empty if no error or warning.
                - float: Control output (proportional term only).
        """
        if (self.target_low <= measurement <= self.target_high):
            return False, "", 0
        elif (self.crit_low > measurement or self.crit_high < measurement):
            msg = f"Warning: {self.unit_name} value has reached a critical {"low." if (self.crit_low > measurement) else "high."}"
            return True, msg, 0
        else:
            error = self.target - measurement
            control = self.kp * error
            return False, "", control


def ph_sensor_read(sensor: AtlasEzoPhSensor) -> tuple[bool, str, float]:
    # Read pH value and print
    temperature = 20 #  temperature compensation
    err, message, ph_value = sensor.read(temperature)

    return err, message, ph_value
    
    
def actuator_controller(pump: PeristalticPumpI2cAddressChanger, volume: float) -> tuple[bool, str]:
    err, message = pump.dispense_volume(volume)
    if err:
        return True, message
    else:
        return False, f"Successfully dispensed {volume} mL of solution"


def main() -> None:
    
    """Initialize the sensor input"""
    address = 0x63  # I2C address of the pH sensor
    sensor = AtlasEzoPhSensor(address)

    """Initialize the Controller"""
    kp = 0.01  # P value
    controller = Controller(unit_name="pH", kp=float(kp))

    """Initialize the peristaltic pump"""
    pump_ph_up = PeristalticPumpI2cAddressChanger(0x5a)
    pump_ph_down = PeristalticPumpI2cAddressChanger(0x5a)
    

    LOOP_DELAY = 1
    
    """Initial test"""
    err_ph, msg_ph, ph_reading = ph_sensor_read(sensor)
    if err_ph:
        print (msg_ph)
        return None
    pump.dispense_volume(15)
    warning, msg, to_dispense = controller.compute(ph_reading)
    if warning:
        print(msg)
    else:
        print(f"Sensor reads {ph_reading} pH. Computed to dispense {to_dispense} mL pH-UP")
    
    
    """ Control loop
        Read sensor
        Compute control output (volume to dispense)
        Send command for pump to dispense volume 
    """
    while True:
        err_ph, msg_ph, ph_reading = ph_sensor_read(sensor)
        if err_ph:
            print (msg_ph)
            return None
        else:
            print(f"ph_reading: {ph_reading}")
            
        warning, msg, to_dispense = controller.compute(ph_reading)
        pump = None
        if warning:
            print(msg)
        else:
            pump = pump_ph_up if to_dispense>=0 else pump_ph_down
            print(f"Sensor reads {ph_reading} pH. Computed to dispense {abs(to_dispense)} mL pH-{"UP" if pump == pump_ph_up else "DOWN"}")
        
        """Dispense whatever volume depending on the right pump"""
        # err_pump, msg_pump = pump.dispense_volume(to_dispense)
        # if err_pump:
        #     print(msg_pump)
        #     return None
        
        


if __name__ == "__main__":
    main()