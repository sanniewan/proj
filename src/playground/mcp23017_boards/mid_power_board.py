import board
from busio import I2C
from adafruit_mcp230xx.mcp23017 import MCP23017

class MCP23017_GpioBoard:
    """MCP23017-based expander board for GPIO.

    This class provides an interface to the MCP23017
    GPIO expander board. The board has 16 GPIO pins
    that can be used as input or output.

    Note: hardware does not support "input, pull down"
    so all pins set as input are "input, pull up".
    """
    
    def __init__(self, address: int):
        """Initialize the MCP23017 GPIO Board.

        Args:
            address (int): The I2C address of the GPIO board.
        """
        i2c = I2C(board.SCL, board.SDA)
        self._board = MCP23017(i2c, address=address)
        self.port_count = 16  # number of ports on the board
        
    def set_as_input(self, port: int) -> tuple[bool, str]:
        """Set the specified port as input.

        Args:
            port (int): The port number to set as input.

        Returns:
            tuple: (int, str or None) Returns (0, None) if successful, otherwise returns (1, error message).
        """
        err, message = self._set_bit(port, True)
        if err:
            return True, f'Unable to execute set_as_input() at port {port}\n' + message

        return False, ''

    def set_as_output(self, port: int) -> tuple[bool, str]:
        """Set the specified port as output.

        Args:
            port (int): The port number to set as output.

        Returns:
            tuple: (int, str or None) Returns (0, None) if successful, otherwise returns (1, error message).
        """
        err, message = self._set_bit(port, False)
        if err:
            return True, f'Unable to execute set_as_output() at port {port}\n' + message

        return False, ''

    def read(self, port: int) -> tuple[bool, str, bool]:
        """Read the value from the specified port.

        Args:
            port (int): The port number to read from.

        Returns:
            tuple: (int, bool or str) Returns (0, bit) if successful, otherwise returns (1, error message).
        """
        err, message, bit = self._get_bit(port)
        if err:
            return True, f'Unable to execute read() at port {port}\n' + message, False

        return False, '', bit

    def write(self, port: int, bit: int) -> tuple[bool, str]:
        """Write the specified value to the port.

        Args:
            port (int): The port number to write to.
            value (int): The bit value to write (0 or 1).

        Returns:
            tuple: (int, str or None) Returns (0, None) if successful, otherwise returns (1, error message).
        """
        err, message = self._set_bit(port, bit)
        if err:
            return True, f'Unable to execute write() at port {port}\n' + message

        return False, ''

    def is_high(self, port: int) -> tuple[bool, str, bool]:
        """Check if the specified port is high.

        Args:
            port (int): The port number to check.

        Returns:
            tuple: (int, bool or str) Returns (0, True) if high, otherwise returns (1, error message).
        """
        err, message, bit = self._get_bit(port)
        if err:
            return True, f'Unable to execute is_high() at port {port}\n' + message, False

        return False, '', bit

    def is_low(self, port: int) -> tuple[bool, str, bool]:
        """Check if the specified port is low.

        Args:
            port (int): The port number to check.

        Returns:
            tuple: (int, bool or str) Returns (0, True) if low, otherwise returns (1, error message).
        """
        err, message, bit = self._get_bit(port)
        if err:
            return True, f'Unable to execute is_low() at port {port}\n' + message, False

        return False, '', not bit

    def flip(self, port: int) -> tuple[bool, str]:
        """Flip the value at the specified port.
        """
        err, message, current_bit = self._get_bit(port)
        if err:
            return True, f'Unable to execute flip() at port {port}\n' + message

        flipped_bit = not current_bit

        err, message = self._set_bit(port, flipped_bit)
        if err:
            return True, f'Unable to execute flip() at port {port}\n' + message

        return False, ''

    def _set_bit(self, port: int, bit: bool) -> tuple[bool, str]:
        """Set the bit value at the port"""
        err, message, bits = self._read_gpio()
        if err:
            return True, f'Unable to execute set_bit().\n' + message

        if bit: 
            bits = bits | (0x0001 << port) # set the bit
        else:
            bits = bits & ~(0x0001 << port) # clear the bit

        err, message = self._write_gpio(bits)
        if err:
            return True, f'Unable to execute set_bit().\n' + message

        return False, ''

    def _get_bit(self, port: int) -> tuple[bool, str, bool]:
        """Get the bit at the port"""
        err, message, bits = self._read_gpio()
        if err:
            return True, f'Unable to execute get_bit().\n', False

        bit = bool((bits >> port) & 1)

        return False, '', bit

    def _set_all_ports_as_input(self) -> tuple[bool, str]:
        """Set all ports as input.

        Returns:
            tuple: (int, str or None) Returns (0, None) if successful, otherwise returns (1, error message).
        """
        try:
            self._board.iodir = 0xFFFF

        except Exception as e:
            return True, f'Unable to execute set_all_ports_as_input(): \n{str(e)}'
        
        return False, ''

    def _set_all_ports_as_output(self) -> tuple[bool, str]:
        """Set all ports as output.

        Returns:
            tuple: (int, str or None) Returns (0, None) if successful, otherwise returns (1, error message).
        """
        try:
            self._board.iodir = 0x0000

        except Exception as e:
            return True, f'Unable to execute set_all_ports_as_output(): \n{str(e)}'

        return False, ''

    ##################################


    def _get_bit_from_int(self, port:int) -> bool:
        """Get a specific bit"""
        bit = bool((bits >> port) & 1)
        return bit

    def _set_bit_in_int(self, bits: int, port:int, bit:bool) -> int:
        """Set a specific bit"""
        if bit: 
            bits = bits | (1 << port) # set the bit
        else:
            bits = bits & ~(1 << port) # clear the bit
        return bits

    def _read_gpio(self) -> tuple[bool, str, int]:
        """Read the current bits from the GPIO register.
            

        Returns:
            Returns:
            tuple:
                (bool): True if there was an error, otherwise False.
                (str): The error message if there was an error.
                (int): The bits from the IODIR register: 0 = low, 1 = high
        """
        try:
            bits = int(self._board.gpio)

        except Exception as e:
            return True, f'Unable to execute read_gpio(): \n{str(e)}', 0x0000
        
        return False, '', bits

    def _write_gpio(self, bits) -> tuple[bool, str]:
        """Write the bits to the GPIO register.
            Only use if all ports as set at input.
            

        Args:
            bits (int): The bits to write to the GPIO register: 0 = low, 1 = high
        Returns:
            tuple:
                (bool): True if there was an error, otherwise False.
                (str): The error message if there was an error.
        """
        try:
            self._board.gpio = bits

        except Exception as e:
            return True, f'Unable to execute write_gpio(): \n{str(e)}'
        
        return False, ''

    def _read_iodir(self) -> tuple[bool, str, int]:
        """Read the current bits from the IODIR register.
            

        Returns:
            tuple:
                (bool): True if there was an error, otherwise False.
                (str): The error message if there was an error.
                (int): The bits from the IODIR register: 0 = output, 1 = input.
        """
        try:
            bits = int(self._board.iodir)

        except Exception as e:
            return True, f'Unable to execute read_iodir(): \n{str(e)}', 0x0000
        
        return False, '', bits

    def _write_iodir(self, bits: int) -> tuple[bool, str]:
        """Write the given bits to the IODIR register.

        Args:
            bits (int): The bits to write to the IODIR register. 0 = output, 1 = input.

        Returns:
            tuple:
                (bool): True if there was an error, otherwise False.
                (str): The error message if there was an error.
        """
        try:
            self._board.iodir = bits

        except Exception as e:
            return True, f'Unable to execute write_iodir(): \n{str(e)}'
        
        return False, ''

    def _read_gppu(self) -> tuple[bool, str, int]:
        """Read the current bits from the GPPU register.

        Returns:
            tuple:
                (bool): True if there was an error, otherwise False.
                (str): The error message if there was an error.
                (int): The bits from the GPPU register: 0 = pull-up disabled, 1 = pull-up enabled.
        """
        try:
            bits = int(self._board.gppu)

        except Exception as e:
            return True, f'Unable to execute read_gppu(): \n{str(e)}', 0x0000
        
        return False, '', bits

    def _write_gppu(self, bits: int) -> tuple[bool, str]:
        """Write the given bits to the GPPU register.

        Args:
            bits (int): The bits to write to the GPPU register: 0 = pull-up disabled, 1 = pull-up enabled.

        Returns:
            tuple:
                (bool): True if there was an error, otherwise False.
                (str): The error message if there was an error.
        """
        try:
            self._board.gppu = bits

        except Exception as e:
            return True, f'Unable to execute write_gppu(): \n{str(e)}'
        
        return False, ''

    

def main(args=None) -> None:
    """Main entry point for the script."""
    board = MCP23017_GpioBoard(0x20)
    err, message = board.set_as_input(0)
    if err:
        print(f'Error setting port 0 as input: {message}')
    else:
        print('Port 0 set as input')
        err, message, bit = board.read(0)
        if err:
            print(f'Error reading port 0: {message}')
        else:
            print(f'Port 0 value: {bit}')
    

    err, message = board.set_as_output(1)
    if err:
        print(f'Error setting port 1 as output: {message}')
    else:
        print('Port 1 set as output')
    
        err, message = board.write(1, 1)
        if err:
            print(f'Error writing to port 1: {message}')
        else:
            print('Port 1 written')
        
        err, message, bit = board.read(1)
        if err:
            print(f'Error reading port 1: {message}')
        else:
            print(f'Port 1 is set to value: {bit}')
        
        err, message = board.flip(1)
        if err:
            print(f'Error flipping port 1: {message}')
        else:
            print('Port 1 flipped')

        err, message, bit = board.read(1)
        if err:
            print(f'Error reading port 1: {message}')
        else:
            print(f'Port 1 is set to value: {bit}')


if __name__ == '__main__':
    main()