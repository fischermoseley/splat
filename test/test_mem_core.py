from splat.memory_core import ReadOnlyMemoryCore
from splat.utils import *
from random import randint, sample

config = {"type": "memory", "width": 16, "depth": 1024}
mem_core = ReadOnlyMemoryCore(config, base_addr=0, interface=None)


def test_bus_read_sequential():
    def testbench():
        for i in range(1024):
            yield from verify_register(mem_core, i, i)

    simulate(mem_core, testbench)


def test_bus_read_random():
    def testbench():
        for i in sample(range(1024), k=1024):
            yield from verify_register(mem_core, i, i)

    simulate(mem_core, testbench, vcd_path="mem_core.vcd")

