from splat.memory_core import ReadOnlyMemoryCore
from splat.utils import *
from random import randint, sample

config = {"type": "memory", "width": 16, "depth": 1024}
mem_core = ReadOnlyMemoryCore(config, base_addr=0, interface=None)


def fill_mem_from_user_port(mem_core):
    for i in range(1024):
        yield mem_core.user_addr.eq(i)
        yield mem_core.user_data.eq(i)
        yield mem_core.user_we.eq(1)
        yield


def test_bus_read_sequential():
    def testbench():
        yield from fill_mem_from_user_port(mem_core)
        for i in range(1024):
            yield from verify_register(mem_core, i, i)

    simulate(mem_core, testbench, vcd_path="mem_core.vcd")


def test_bus_read_random():
    def testbench():
        yield from fill_mem_from_user_port(mem_core)
        for i in sample(range(1024), k=1024):
            yield from verify_register(mem_core, i, i)

    simulate(mem_core, testbench, vcd_path="mem_core.vcd")


def test_random_base_addr():
    base_addr = randint(0, 2**16 - 1 - 1024)
    random_mem_core = ReadOnlyMemoryCore(config, base_addr, interface=None)

    def testbench():
        yield from fill_mem_from_user_port(random_mem_core)

        for i in range(1024):
            yield from verify_register(random_mem_core, i + base_addr, i)

    simulate(random_mem_core, testbench, vcd_path="mem_core.vcd")
