from amaranth.sim import Simulator
from splat.uart import TransmitBridge
from splat.utils import *
from random import randint, sample


bridge_tx = TransmitBridge()


def simulate(testbench, export_vcd=False):
    sim = Simulator(bridge_tx)
    sim.add_clock(1e-6)  # 1 MHz
    sim.add_sync_process(testbench)

    if not export_vcd:
        sim.run()

    else:
        with sim.write_vcd("bridge_tx.vcd"):
            sim.run()

def verify_encoding(data, bytes):
    """
    Send a series of bytes to the receive bridge, and verify that the bridge places
    a read request with the appropriate address on the internal bus.
    """

    yield bridge_tx.data_i.eq(data)
    yield bridge_tx.valid_i.eq(1)
    yield bridge_tx.rw_i.eq(0)
    yield bridge_tx.done_i.eq(1)

    yield

    yield bridge_tx.data_i.eq(0)
    yield bridge_tx.valid_i.eq(0)
    yield bridge_tx.rw_i.eq(0)

    yield

    # Model the uart_tx module
    # - by waiting for the module to assert start_o, and then
    #   taking an arbitrary amount of time to deassert done_i

    bytes_transmitted = b""
    iters = 0
    while((len(bytes_transmitted) < len(bytes)) and (iters < 15)):
        # check if start_o is asserted
        # if so, set done_i to zero, then delay for some amount of time, then set it to oen
        # delay for
        iters += 1

        if (yield bridge_tx.start_o):
            yield bridge_tx.done_i.eq(0)
            bytes_transmitted += (yield bridge_tx.data_o).to_bytes(1, 'big')

            yield bridge_tx.done_i.eq(0)
            for _ in range(10):
                yield

            yield bridge_tx.done_i.eq(1)
            yield


    if bytes_transmitted != bytes:
        print('oh no')
        print(bytes)
        print(bytes_transmitted)

def test_some_random_values():
    def testbench():
        for i in sample(range(0xFFFF), k=5000):
            expected = f"D{i:04X}\r\n".encode("ascii")
            print(i)
            yield from verify_encoding(i, expected)

    simulate(testbench, export_vcd=False)
    sample(range(10000000), k=60)


test_some_random_values()