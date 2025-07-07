from playground.mcp23017_boards.mid_power_board import MCP23017_GpioBoard
import time

def main() -> tuple[int, int]:

    board = MCP23017_GpioBoard(0x20)  # i2c address of gpio board

    """
    Set all ports as OUTPUTS (iodir 0)
    """
    err_out, msg_out = board._set_all_ports_as_output()
    err_is_out, msg_is_out, result = board._read_iodir()
    all_out = result==0x0000
    print(f"All ports are outputs? {all_out}")  # should print True
    five_on = 0x1F
    time.sleep(0.5)

    ports_to_test = 5
    err, passed, failed = test_port_combinations(board, ports_to_test)
    if err:
        print("test_port_combos ERROR")
    else:
        print(f"Passed {passed} tests and failed {failed} tests.")

def test_port_combinations(board, ports_to_test: int) -> tuple[bool, int, int]:
    total_tests = 0
    passed = 0
    failed = 0

    # Binary representation, bottom (ports_to_test) bits are 1, the rest are 0
    ports_b_ones = (1<<ports_to_test)-1

    for val in range(0x00, ports_b_ones+1):
        # Write value to the lower 5 bits; upper bits zero
        bits_to_write = val & ports_b_ones

        # Write to GPIO
        err_write, msg_write = board._write_gpio(bits_to_write)
        if err_write:
            print(f"[ERROR] Write failed: {msg_write}")
            continue

        # Read GPIO
        err_read, msg_read, gpio_status = board._read_gpio()
        if err_read:
            print(f"[ERROR] Read failed: {msg_read}")
            continue

        # Compare
        masked_status = gpio_status & ports_b_ones
        match = (masked_status == bits_to_write)
        if match:
            passed += 1
        else:
            failed += 1
        
        time.sleep (0.1)

        print(f"Written:  {format(bits_to_write, '016b')} "
              f"Read: {format(masked_status, '016b')} "
              f"{'✅ PASS' if match else '❌ FAIL'}")

        total_tests += 1

    print(f"\nCompleted {total_tests} tests.")
    return False, passed, failed


if __name__ == "__main__":
    main()



    # for port in range(ports):
    #     """ clear all (set to 0)
    #         turn one on
    #         chck if only that one is on by comparing gpio_status (actual) with concactenated bits (expected)
    #     """
    #     print("done sleeping")
    #     all_zero = True
    #     if(is_individual):
    #         err_erase, msg_erase = board._write_gpio(0x0000)
    #         err_is_in, msg_is_in, result = board._read_gpio()
    #         all_zero = result==0x0000
    #         print(f"Erased? {all_zero}: result = {result}")

    #         old_concat_bits = 0x1000

    #     if all_zero:
    #         err_write, msg_write = board.write(port,1)  # turn one on (set to 1)
    #         if err_write:
    #             print(f"Error at {board} : {msg_write}")
    #             return True
    #         else:
    #             print(msg_write)

    #         err_gpio, msg_gpio, gpio_status = board._read_gpio()  # read current gpio status
    #         if err_gpio:
    #             print(f"Error at {board} : {msg_gpio}")
    #             return True
    #         else:
    #             print(msg_gpio)

    #         concatenated_bits = (1 << port) or old_concat_bits
    #         old_concat_bits = concatenated_bits

    #         actual_is_expected = (concatenated_bits==gpio_status)
    #         print(f"Is expected input statuses the same as actual statues? "
    #                 f"Expected: {format(concatenated_bits, '016b')} Actual: {format(gpio_status, '016b')}")

    #         if (not actual_is_expected):
    #             print(f"ERROR: not actual_is_expected: actual: {format(gpio_status, '016b')} expected: {format(concatenated_bits, '016b')}")
    #             return True

    #         print("sleeping two seconds\n")

    #     time.sleep(2)

