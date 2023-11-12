from amaranth.sim import Simulator
from splat.uart import UARTTransmitter
from splat.utils import *
from random import sample


uart_tx = UARTTransmitter(clocks_per_baud=10)


def simulate(testbench, export_vcd=False):
    sim = Simulator(uart_tx)
    sim.add_clock(1e-6)  # 1 MHz
    sim.add_sync_process(testbench)

    if not export_vcd:
        sim.run()

    else:
        with sim.write_vcd("uart_tx.vcd"):
            sim.run()


def verify_bit_sequence(byte):
    """
    Request a byte to be transmitted, and verify that the sequence of bits is correct.
    """

    # Request byte to be transmitted
    yield uart_tx.data_i.eq(byte)
    yield uart_tx.start_i.eq(1)
    yield
    yield uart_tx.data_i.eq(0)
    yield uart_tx.start_i.eq(0)
    yield

    # Check that data bit is correct on every clock baud period

    # 8N1 serial, LSB sent first
    data_bits = "0" + f"{byte:08b}"[::-1] + "1"
    data_bits = [int(bit) for bit in data_bits]

    for i in range(10 * uart_tx.clocks_per_baud):
        bit_index = i // uart_tx.clocks_per_baud

        if (yield uart_tx.tx) != data_bits[bit_index]:
            raise ValueError("Wrong bit in sequence!")

        if (yield uart_tx.done_o) and (bit_index != 9):
            raise ValueError("Done asserted too early!")

        yield

    if not (yield uart_tx.done_o):
        raise ValueError("Done not asserted at end of transmission!")


def test_all_possible_bytes():
    def testbench():
        for i in range(0xFF):
            yield from verify_bit_sequence(i)

    simulate(testbench, export_vcd=True)


def test_bytes_random_sample():
    def testbench():
        for i in sample(range(0xFF), k=0xFF):
            yield from verify_bit_sequence(i)

    simulate(testbench, export_vcd=True)
