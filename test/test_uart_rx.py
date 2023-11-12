from amaranth.sim import Simulator
from splat.uart import UARTReceiver
from splat.utils import *


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


def verify_receive(data, clocks_per_baud):
    # 8N1 serial, LSB sent first
    buffer = "0" + f"{data:08b}"[::1] + "1"
    buffer = [int(bit) for bit in buffer]
    # valid_has_been_asserted = False

    for bit in buffer:
        print(bit)
        yield uart_rx.rx.eq(bit)

        for _ in range(clocks_per_baud):
            yield

        # # Every cycle, run checks on uart_rx:
        # if(data_bit < 9):
        #     if(yield uart_rx.valid_o != 0):
        #         raise ValueError("Valid asserted before end of byte!")

        # if(yield uart_rx.valid_o):
        #     if data_bit != 9:
        #         raise ValueError("Byte presented before it is complete!")

        #     if not valid_has_been_asserted:
        #         valid_has_been_asserted = True

        #     else:
        #         raise ValueError("Valid asserted more than once!")

        # # Clock out next data bit
        # if bit_index == 0:
        #     yield uart_rx.rx.eq(0)

        # elif ((bit_index > 0) & (bit_index < 9)):
        #     int(f"data:08b")
        #     yield uart_rx.rx.eq(data[data_bit-1])

        # else:
        #     yield uart_rx.rx.eq(1)


def test_do_you_run_lol():
    def testbench():
        yield uart_rx.rx.eq(1)
        yield
        yield
        yield
        yield
        yield from verify_receive(0x00, 10)
        yield from verify_receive(0xA3, 10)

    simulate(testbench, export_vcd=True)


test_do_you_run_lol()
