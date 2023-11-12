from amaranth.sim import Simulator
from splat.uart import UARTReceiver
from splat.utils import *
from random import sample


uart_rx = UARTReceiver(clocks_per_baud=10)


def simulate(testbench, export_vcd=False):
    sim = Simulator(uart_rx)
    sim.add_clock(1e-6)  # 1 MHz
    sim.add_sync_process(testbench)

    if not export_vcd:
        sim.run()

    else:
        with sim.write_vcd("uart_rx.vcd"):
            sim.run()


def verify_receive(data):
    # 8N1 serial, LSB sent first
    data_bits = "0" + f"{data:08b}"[::-1] + "1"
    data_bits = [int(bit) for bit in data_bits]

    valid_asserted_before = False

    for i in range(10 * uart_rx.clocks_per_baud):
        bit_index = i // uart_rx.clocks_per_baud

        # Every cycle, run checks on uart_rx:
        if (yield uart_rx.valid_o):
            if (yield uart_rx.data_o) != data:
                a = yield uart_rx.data_o
                print(data_bits)
                raise ValueError(
                    f"Incorrect byte presented - gave {hex(a)} instead of {hex(data)}!"
                )

            if bit_index != 9:
                print(bit_index)
                raise ValueError("Byte presented before it is complete!")

            if not valid_asserted_before:
                valid_asserted_before = True

            else:
                raise ValueError("Valid asserted more than once!")

        yield uart_rx.rx.eq(data_bits[bit_index])
        yield

    # if not valid_asserted_before:
    #     raise ValueError("Failed to assert valid!")


def test_all_possible_bytes():
    def testbench():
        yield uart_rx.rx.eq(1)
        yield

        for i in range(0xFF):
            yield from verify_receive(i)

    simulate(testbench)


def test_bytes_random_sample():
    def testbench():
        yield uart_rx.rx.eq(1)
        yield

        for i in sample(range(0xFF), k=0xFF):
            yield from verify_receive(i)

    simulate(testbench)
