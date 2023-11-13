from amaranth import *
from amaranth_boards.nexys4ddr import Nexys4DDRPlatform
from amaranth_boards.icestick import ICEStickPlatform
from splat import Splat
from splat.utils import *
import pytest
import yaml

config_file = "test/splat.yaml"
s = Splat(config_file)


class IOCoreLoopback(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.submodules["splat"] = s
        io_core = s.cores["io_core"]

        uart_pins = platform.request("uart")

        m.d.comb += [
            io_core.probe0.eq(io_core.probe4),
            io_core.probe1.eq(io_core.probe5),
            io_core.probe2.eq(io_core.probe6),
            io_core.probe3.eq(io_core.probe7),
            s.interface.rx.eq(uart_pins.rx.i),
            uart_pins.tx.o.eq(s.interface.tx),
        ]

        return m


def verify_output_probe_initial_values(platform):
    """
    Test that all output probes take their expected initial values.
    We can't really test for the same of input probes, since the
    strobe register pulses every time the get_probe() method is called.
    """

    # Build and program board
    platform.build(IOCoreLoopback(), do_program=True)

    # Test that all output probes take their initial values
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
        inputs = config["cores"]["io_core"]["inputs"]
        outputs = config["cores"]["io_core"]["outputs"]

    for name, attrs in outputs.items():
        actual = s.cores["io_core"].get_probe(name)

        if isinstance(attrs, dict):
            if "initial_value" in attrs:
                expected = attrs["initial_value"]

        else:
            expected = 0

        if actual != expected:
            raise ValueError(
                f"Output probe {name} took initial value of {actual} instead of {expected}."
            )


@pytest.mark.skipif(not xilinx_tools_installed(), reason="no toolchain installed")
def test_output_probe_initial_values_xilinx():
    verify_output_probe_initial_values(Nexys4DDRPlatform())


@pytest.mark.skipif(not ice40_tools_installed(), reason="no toolchain installed")
def test_output_probe_initial_values_ice40():
    verify_output_probe_initial_values(ICEStickPlatform())
