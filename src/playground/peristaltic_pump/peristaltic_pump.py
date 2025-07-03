#!/usr/bin/env python3
"""Script to change the I2C address of a peristaltic pump."""

import argparse
import logging
from typing import Tuple

from busio import I2C
import board
from external.AtlasI2C import AtlasI2C


class PeristalticPumpI2cAddressChanger:
    """Class for changing the I2C address of a peristaltic pump."""

    def __init__(self, i2c_address: int):
        """Initialize the controller with the given I2C address."""
        self._i2c_address = i2c_address
        self._device = None
        self._name = "Peristatic Pump"
        self._detected_i2c_devices = []

    def change_i2c_address(self, new_i2c_address: int) -> None:
        """Change the I2C address of the device.

        Args:
            new_i2c_address (int): The new I2C address to set.
        """
        if not self._detect_i2c_bus():
            return

        if not self._detect_device():
            return

        if not self._configure_device():
            return

        self._set_i2c_address(new_i2c_address)

    def _detect_i2c_bus(self) -> bool:
        """Check if the I2C bus is detected.

        Returns:
            bool: True if the I2C bus was successfully scanned, False otherwise.
        """
        try:
            with I2C(board.SCL, board.SDA) as i2c:
                self._detected_i2c_devices = i2c.scan()
                return True
        except Exception as e:
            logging.error(f'I2C bus detection failed: {e}')
            self._detected_i2c_devices = []
            return False

    def _detect_device(self) -> bool:
        """Check if the device is detected.

        Returns:
            bool: True if the device is detected, False otherwise.
        """
        if self._i2c_address not in self._detected_i2c_devices:
            logging.error(f'Peristaltic pump ({hex(self._i2c_address)}) not detected')
            return False
        return True

    def _configure_device(self) -> bool:
        """Configure the device.

        Returns:
            bool: True if the device was successfully configured, False otherwise.
        """
        try:
            self._device = AtlasI2C(address=self._i2c_address)
        except Exception as e:
            logging.error(f'Peristaltic pump ({hex(self._i2c_address)}) configuration failed: {e}')
            return False
        return True

    def _set_i2c_address(self, new_address: int) -> bool:
        """Set the new I2C address.

        Args:
            new_address (int): New I2C address to set.

        Returns:
            bool: True if the address was successfully set, False otherwise.
        """
        try:
            self._device.query('Plock,0')
            self._device.query(f'I2C,{new_address}')
        except Exception as e:
            logging.error(f'Peristaltic pump (0x{self._i2c_address:x}): changing address to 0x{new_address:x} failed: {e}')
            return False
        return True
    def _dispense_volume(self, volume: float=0) -> tuple[bool,str]:
        """Dispense specified volume.

        Args:
            volume: in mL
        Returns: 
            bool: error flag - True if an error occured, False otherwise.
            str: dispense status ?D,-40.50,0
        """
        err = self._detect_i2c_bus and self._detect_device
        if err:
            return True, "Peristaltic pump or I2C bus detection failed"
        
        try:
            self._device.write(f"D,{volume}")
        except Exception as e:
            msg = f"Error configuring {self._name} {self._device} ({self._i2c_address})"
            return True, msg
        
        msg = f"Successfully configured {self._name} ({self._i2c_address})"
        return False, msg



def hex_int(value: str) -> int:
    """Convert a hex string to an integer. Supports both '0x67' and '67' formats.

    Args:
        value (str): Hex string to convert.

    Returns:
        int: Converted integer.
    """
    return int(value, 16)


def main() -> None:
    current_address = 0x68
    pump = PeristalticPumpI2cAddressChanger(current_address)
    
    time.sleep(15)
    volume_to_disp = 15
    err, msg = pump._dispense_volume(volume_to_disp)
    if err:
        print(f'Error at {pump._name} at address {pump._i2c_address}')
        print(msg)
    else: 
        print(f'Successfully pumped {volume_to_disp}')

if __name__ == "__main__":
    main()