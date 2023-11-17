from amaranth.sim import Simulator
from splat.memory_core import ReadOnlyMemoryCore
from splat.utils import *
from random import randint

config = {
    'type':'memory',
    'width':16,
    'depth':4096
}

mem_core = ReadOnlyMemoryCore(config, base_addr=0, interface=None)


def simulate(testbench, export_vcd=False):
    sim = Simulator(mem_core)
    sim.add_clock(1e-6)  # 1 MHz
    sim.add_sync_process(testbench)

    if not export_vcd:
        sim.run()

    else:
        with sim.write_vcd("mem_core.vcd"):
            sim.run()

def test_bus_read_write():
    def testbench():
        for i in range(config['depth']):
            yield mem_core.addr_i.eq(i)
            yield mem_core.data_i.eq(0)
            yield mem_core.rw_i.eq(0)
            yield mem_core.valid_i.eq(1)

            while not (yield mem_core.valid_o):
                yield

            print((yield mem_core.data_o))
            yield


    simulate(testbench, export_vcd=True)

test_bus_read_write()