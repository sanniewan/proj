from mcp23017_boards.high_power_board import MCP23017_RelayBoard
import time

def main():
    # set all ports to low 
    board = MCP23017_RelayBoard(0x26)  # Replace with your actual I2C address
    for port in range(board.port_count):
        # err_open, message_open, _ = board.open(port)
        # if err_open:
        #     print(f'Error closing port {port}: {message_open}')
        # else:
        #     print(f'Port {port} closed successfully.')

        # time.sleep(1)
        if port == 0:
            err, message, _ = board.close(port)
            if err:
                print(f'Error checking port {port}: {message}')
            else:
                print(f'Port {port} is {"closed" if _ else "open"}.')
        else: 
            err, message, _ = board.open(port)
            if err:
                print(f'Error close port {port}: {message}')
            else:
                print(f'Port {port} closed successfully.')

        # time.sleep(1)


if __name__ == "__main__":
    main()