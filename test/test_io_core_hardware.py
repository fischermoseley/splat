from amaranth import *
from splat import Splat

class IOCoreLoopback(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        # probe0 = Signal()
        # probe1 = Signal(2)
        # probe2 = Signal(8)
        # probe3 = Signal(20)

        s = Splat('test/splat.yaml')
        m.submodules['splat'] = s
        io_core = s.cores['io_core']

        uart = platform.request("uart")

        m.d.comb += [
            io_core.probe0.eq(io_core.probe4),
            io_core.probe1.eq(io_core.probe5),
            io_core.probe2.eq(io_core.probe6),
            io_core.probe3.eq(io_core.probe7),
            s.interface.rx.eq(uart.rx),
            s.interface.tx.eq(uart.tx)
        ]

        return m

from amaranth_boards.arty_a7 import ArtyA7_100Platform
ArtyA7_100Platform().build(IOCoreLoopback(), do_program=True)