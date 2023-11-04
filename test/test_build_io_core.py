from amaranth_boards.arty_a7 import *
from amaranth import *


class ExampleLEDModule(Elaboratable):
    def __init__(self):
        self.count = Signal(32, reset=0)

    def elaborate(self, platform):
        m = Module()
        m.d.sync += self.count.eq(self.count + 1)
        if platform is not None:
            grn_led = platform.request("led_g", 0)
            blu_led = platform.request("led_b", 0)
            m.d.comb += [grn_led.o.eq(self.count[20]), blu_led.o.eq(~grn_led.o)]
        return m


if __name__ == "__main__":
    dut = ExampleLEDModule()
    ArtyA7_100Platform().build(dut, do_program=False)
