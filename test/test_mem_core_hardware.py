from amaranth import *
from amaranth_boards.nexys4ddr import Nexys4DDRPlatform
from amaranth_boards.icestick import ICEStickPlatform
from splat import Splat
from splat.utils import *
import pytest
from random import sample

config_file = "test/test_mem_core_hardware.yaml"
s = Splat(config_file)
mem_core = s.cores["mem_core"]
io_core = s.cores["io_core"]


class ReadOnlyMemoryCoreLoopback(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        m.submodules["splat"] = s
        uart_pins = platform.request("uart")

        m.d.comb += [
            mem_core.user_addr.eq(io_core.addr),
            mem_core.user_data.eq(io_core.data),
            mem_core.user_we.eq(io_core.we),
            s.interface.rx.eq(uart_pins.rx.i),
            uart_pins.tx.o.eq(s.interface.tx),
        ]

        return m


def verify_mem_core(platform):
    """
    Test that all output probes take their expected initial values.
    We can't really test for the same of input probes, since the
    strobe register pulses every time the get_probe() method is called.
    """

    # Build and program board
    # platform.build(ReadOnlyMemoryCoreLoopback(), do_program=True)

    # Fill up memory from the user side
    for i in range(1024):
        io_core.set_probe("we", 0)
        io_core.set_probe("addr", i)
        io_core.set_probe("data", i)
        io_core.set_probe("we", 1)
        io_core.set_probe("we", 0)

    # Read it back out sequentially from the bus side
    for i in range(1024):
        data = mem_core.read_from_user_addr(i)
        if data != i:
            raise ValueError(
                f"Memory read from {hex(i)} returned {hex(data)} instead of {hex(i)}."
            )

    for i in sample(range(0x1024), k=1024):
        data = mem_core.read_from_user_addr(i)
        if data != i:
            raise ValueError(
                f"Memory read from {hex(i)} returned {hex(data)} instead of {hex(i)}."
            )


@pytest.mark.skipif(not xilinx_tools_installed(), reason="no toolchain installed")
def test_mem_core_xilinx():
    verify_mem_core(Nexys4DDRPlatform())


@pytest.mark.skipif(not ice40_tools_installed(), reason="no toolchain installed")
def test_mem_core_ice40():
    verify_mem_core(ICEStickPlatform())
