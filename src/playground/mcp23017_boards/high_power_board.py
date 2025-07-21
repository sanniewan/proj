import board
from busio import I2C
from adafruit_mcp230xx.mcp23017 import MCP23017
from time import sleep

class MCP23017_RelayBoard:
    """MCP23017-based relay board.

    This class provides an interface to the MCP23017 relay board.
    The board has 16 ports that can be used to control relays.
    """

    def __init__(self, address: int):
        """Initialize the MCP23017 Relay Board.

        Args:
            address (int): The I2C address of the relay board.
        """
        i2c = I2C(board.SCL, board.SDA)
        self._board = MCP23017(i2c, address=address)
        self.port_count = 16  # number of ports on the board
        err, message = self._set_ports_as_output()
        if err:
            print(message)

    def close(self, port: int) -> tuple[bool, str]:
        """Close the relay at the specified port.

        Args:
            port (int): The port number to close.

        Returns:
            tuple:
                - (bool) Returns True if error, False otherwise
                - (str) Error message or empty string
                - (bool) Returns True if the relay is closed, False otherwise
        """
        err, message = self._set_bit(port, False)
        if err:
            return True, f'Unable to execute close() relay at port {port}' + message
        
        return False, ''

    def open(self, port: int) -> tuple[bool, str]:
        """Open the relay at the specified port.

        Args:
            port (int): The port number to open.

        Returns:
            tuple:
                - (bool) Returns True if error, False otherwise
                - (str) Error message or empty string
                - (bool) Returns True if the relay is closed, False otherwise
        """
        err, message = self._set_bit(port, True)
        if err:
            return True, f'Unable to execute open() relay at port {port}' + message
        
        return False, ''

    def is_closed(self, port: int) -> tuple[bool, str, bool]:
        """Check if the relay at the specified port is closed.

        Args:
            port (int): The port number to check.

        Returns:
            tuple:
                - (bool) Returns True if error, False otherwise
                - (str) Error message or empty string
                - (bool) Returns True if the relay is closed, False otherwise
        """
        err, message, bit = self._get_bit(port)
        if err:
            return True, f'Unable to execute is_closed() relay at port {port}\n' + message, False
        
        return False, '', bit

    def is_open(self, port: int) -> tuple[bool, str, bool]:
        """Check if the relay at the specified port is open.

        Args:
            port (int): The port number to check.

        Returns:
            tuple:
                - (bool) Returns True if error, False otherwise
                - (str) Error message or empty string
                - (bool) Returns True if the relay is open, False otherwise
        """
        err, message, bit = self._get_bit(port)
        if err:
            return True, f'Unable to execute is_open() relay at port {port}\n' + message, False
        
        return False, '', not bit

    def _set_bit(self, port: int, bit: bool) -> tuple[bool, str]:
        """Set the bit at the specified port to the given value.

        Args:
            port (int): The port number to set.
            bit (bool): The bit value to set (False or True).

        Returns:
            tuple:
                (int) error flag,
                (str) error message.
        """
        err, message, bits = self._read_gpio()
        if err:
            return True, f'Unable to execute set_bit()\n' + message

        if bit:  # Set the bit
            bits = bits | (0x0001 << port)
        else:  # Clear the bit
            bits = bits & ~(0x0001 << port)

        err, message = self._write_gpio(bits)
        if err:
            return True, f'Unable to execute set_bit()\n' + message

        return False, ''

    def _get_bit(self, port: int) -> tuple[bool, str, bool]:
        """Get the bit value at the specified port.

        Args:
            port (int): The port number to get the value from.

        Returns:
            tuple: (int, bool or str) Returns (0, bit) if successful, otherwise returns (1, error message).
        """
        err, message, bits = self._read_gpio()
        if err:
            return True, f'Unable to execute get_bit()\n' + message, False
        
        bit = bool((bits >> port) & 0x0001)
        
        return False, '', bit

    def _write_gpio(self, bits: int) -> tuple[bool, str]:
        """Write the given bits to the GPIO register.

        Args:
            bits (int): The bits to write to the GPIO register.

        Returns:
            tuple: (int, str or None) Returns (0, None) if successful, otherwise returns (1, error message).
        """
        try:
            self._board.gpio = bits
            
        except Exception as e:
            return True, f'Unable to execute write_gpio(bits): {str(e)}'

        return False, ''

    def _read_gpio(self) -> tuple[bool, str, int]:
        """Read the current bits from the GPIO register.

        Returns:
            tuple: (int, int or str) Returns (0, bits) if successful, otherwise returns (1, error message).
        """
        try:
            bits = self._board.gpio
            
        except Exception as e:
            return True, f'Unable to execute read_gpio(): {str(e)}', 0x0000

        return False, '', bits

    def _set_ports_as_output(self) -> tuple[bool, str]:
        """Set all ports as output.

        Returns:
            tuple: (int, str or None) Returns (0, None) if successful, otherwise returns (1, error message).
        """
        try:
            self._board.iodir = 0x0000
        
        except Exception as e:
            return True, f'Unable to execute set_ports_as_output(): {str(e)}'
        
        return False, ''


def main(args=None) -> None:
    """Main entry point for the script."""
    board = MCP23017_RelayBoard(0x26)
    
    sleep(1)
    
    while True:
        for i in range(16):
            err, msg = board.open(i)
            if err:
                print(msg)
        sleep(5)
        
        # for port in range(16):
        #     err, msg = board.close(port)
        #     if err:
        #         print(msg)
        # sleep(5)
        
if __name__ == '__main__':
    main()