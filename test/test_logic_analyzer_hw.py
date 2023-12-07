from amaranth import *
from amaranth_boards.nexys4ddr import Nexys4DDRPlatform
from amaranth_boards.icestick import ICEStickPlatform
from splat import Splat
from splat.utils import *
import pytest

class LogicAnalyzerCounterTest(Elaboratable):
    def __init__(self, platform, port):
        self.platform = platform
        self.port = port

        self.config = self.platform_specific_config()
        self.s = Splat(self.config)

    def platform_specific_config(self):
        return {
            "cores": {
                "la": {
                    "type": "logic_analyzer",
                    "sample_depth": 1024,
                    "trigger_loc": 500,
                    "probes": {
                        "larry" : 1,
                        "curly" : 3,
                        "moe" : 9
                    },
                    "triggers": ["moe RISING"]
                },
            },
            "uart": {
                "port": self.port,
                "baudrate": 3e6,
                "clock_freq": self.platform.default_clk_frequency,
            },
        }

    def elaborate(self, platform):
        m = Module()
        m.submodules["splat"] = self.s
        uart_pins = platform.request("uart")

        larry = self.s.la.probe_signals["larry"]["top_level"]
        curly = self.s.la.probe_signals["curly"]["top_level"]
        moe = self.s.la.probe_signals["moe"]["top_level"]

        m.d.sync += larry.eq(larry + 1)
        m.d.sync += curly.eq(curly + 1)
        m.d.sync += moe.eq(moe + 1)

        m.d.comb += [
            self.s.interface.rx.eq(uart_pins.rx.i),
            uart_pins.tx.o.eq(self.s.interface.tx)
        ]

        return m

    def build_and_program(self):
        self.platform.build(self, do_program=True)

    def verify(self):
        self.build_and_program()
        cap = self.s.la.capture()

        # check that VCD export works
        cap.export_vcd("out.vcd")

        # verify that each signal is just a counter modulo the width of the signal
        for name, width in self.s.la.config["probes"].items():
            trace = cap.get_trace(name)

            for i in range(len(trace) - 1):
                if trace[i+1] != (trace[i] + 1) % (2**width):
                    raise ValueError("Bad counter!")


@pytest.mark.skipif(not xilinx_tools_installed(), reason="no toolchain installed")
def test_mem_core_xilinx():
    LogicAnalyzerCounterTest(Nexys4DDRPlatform(), "/dev/ttyUSB2").verify()


@pytest.mark.skipif(not ice40_tools_installed(), reason="no toolchain installed")
def test_mem_core_ice40():
    LogicAnalyzerCounterTest(ICEStickPlatform(), "/dev/ttyUSB1").verify()
