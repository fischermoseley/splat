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

        # Free-running counter
        self.counter = Signal(13)
        m.d.sync += self.counter.eq(self.counter + 1)

        m.submodules["splat"] = self.s
        uart_pins = platform.request("uart")


        m.d.comb += [
            self.s.larry.eq(self.counter[0]),
            self.s.curly.eq(self.counter[1:4]),
            self.s.moe.eq(self.counter[4:]),
            self.s.interface.rx.eq(uart_pins.rx.i),
            uart_pins.tx.o.eq(self.s.interface.tx),
        ]

        return m

    def build_and_program(self):
        self.platform.build(self, do_program=True)

    def verify(self):
        self.build_and_program()
        cap = self.capture()
        print(cap.capture_data)


@pytest.mark.skipif(not xilinx_tools_installed(), reason="no toolchain installed")
def test_mem_core_xilinx():
    LogicAnalyzerCounterTest(Nexys4DDRPlatform(), "/dev/ttyUSB2").verify()


@pytest.mark.skipif(not ice40_tools_installed(), reason="no toolchain installed")
def test_mem_core_ice40():
    LogicAnalyzerCounterTest(ICEStickPlatform(), "/dev/ttyUSB1").verify()
