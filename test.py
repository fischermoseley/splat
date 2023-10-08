from amaranth import *
from amaranth.back import verilog
import yaml

class IOCore(Elaboratable):
    """
    Me just fucking around, mostly.

    """

    def __init__(self, config, base_addr):
        # Config
        self.base_addr = base_addr
        self.max_addr = self.base_addr + 10

        # Bus Ports
        self.addr_i = Signal(16)
        self.data_i = Signal(16)
        self.rw_i = Signal()
        self.valid_i = Signal()

        self.addr_o = Signal(16)
        self.data_o = Signal(16)
        self.rw_o = Signal()
        self.valid_o = Signal()

        # self.bus_in = Bus()
        # self.bus_out = Bus()

        # Input Probes (and buffers)
        for name, width in config['inputs'].items():
            setattr(self, name, Signal(width, name=name))
            setattr(self, name + '_buf', Signal(width, name=name+'_buf'))

        # Output Probes (and buffers)
        for name, attrs in config['outputs'].items():
            if isinstance(attrs, dict):
                width = attrs['width']
                initial_value = attrs['initial_value']
            else:
                width = attrs
                initial_value = 0

            setattr(self, name, Signal(width, name=name, reset=initial_value))
            setattr(self, name + '_buf', Signal(width, name=name+'_buf', reset=initial_value))

        # State
        self.strobe = Signal(reset = 0)

    def elaborate(self, platform):
        m = Module()

        # Shuffle bus transactions along
        # m.d.sync += self.bus_out.eq(self.bus_in)
        m.d.sync += self.addr_o.eq(self.addr_i)
        m.d.sync += self.data_o.eq(self.data_i)
        m.d.sync += self.rw_o.eq(self.rw_i)
        m.d.sync += self.valid_o.eq(self.valid_i)

        # Update buffers from probes
        with m.If(self.strobe):
            # Input buffers
            for name in config['inputs']:
                input_probe = getattr(self, name)
                input_probe_buf = getattr(self, name + '_buf')
                m.d.sync += input_probe_buf.eq(input_probe)

            # Output buffers
            for name in config['outputs']:
                output_probe = getattr(self, name)
                output_probe_buf = getattr(self, name + '_buf')
                m.d.sync += output_probe.eq(output_probe_buf)

        # Handle register reads and writes
        with m.If(  (self.addr_i >= self.base_addr) & \
                    (self.addr_o <= self.max_addr)):

            # writes
            with m.If(self.rw_i):
                with m.Switch(self.addr_i - self.base_addr):
                    with m.Case(0):
                        m.d.sync += self.strobe.eq(self.data_i)

                    with m.Case(6):
                        m.d.sync += self.probe4_buf.eq(self.data_i)
                    with m.Case(7):
                        m.d.sync += self.probe5_buf.eq(self.data_i)
                    with m.Case(8):
                        m.d.sync += self.probe6_buf.eq(self.data_i)
                    with m.Case(9):
                        m.d.sync += self.probe7_buf[0:15].eq(self.data_i)
                    with m.Case(10):
                        m.d.sync += self.probe7_buf[16:19].eq(self.data_i)

            # reads
            with m.Else():
                with m.Switch(self.addr_i - self.base_addr):
                    with m.Case(0):
                        m.d.sync += self.data_o.eq(self.strobe)

                    with m.Case(1):
                        m.d.sync += self.data_o.eq(self.probe0_buf)
                    with m.Case(2):
                        m.d.sync += self.data_o.eq(self.probe1_buf)
                    with m.Case(3):
                        m.d.sync += self.data_o.eq(self.probe2_buf)
                    with m.Case(4):
                        m.d.sync += self.data_o.eq(self.probe3_buf[0:15])
                    with m.Case(5):
                        m.d.sync += self.data_o.eq(self.probe3_buf[16:19])

                    with m.Case(6):
                        m.d.sync += self.data_o.eq(self.probe4_buf)
                    with m.Case(7):
                        m.d.sync += self.data_o.eq(self.probe5_buf)
                    with m.Case(8):
                        m.d.sync += self.data_o.eq(self.probe6_buf)
                    with m.Case(9):
                        m.d.sync += self.data_o.eq(self.probe7_buf[0:15])
                    with m.Case(10):
                        m.d.sync += self.data_o.eq(self.probe7_buf[16:19])
        return m





with open('manta.yaml', 'r') as file:
    config = yaml.safe_load(file)['cores']['io_core']
    print(config)

io_core = IOCore(config, 0)

ports = [
    io_core.addr_i,
    io_core.data_i,
    io_core.rw_i,
    io_core.valid_i,

    io_core.addr_o,
    io_core.data_o,
    io_core.rw_o,
    io_core.valid_o,

    io_core.probe0,
    io_core.probe1,
    io_core.probe2,
    io_core.probe3,

    io_core.probe4,
    io_core.probe5,
    io_core.probe6,
    io_core.probe7,

    io_core.probe0_buf,
    io_core.probe1_buf,
    io_core.probe2_buf,
    io_core.probe3_buf,

    io_core.probe4_buf,
    io_core.probe5_buf,
    io_core.probe6_buf,
    io_core.probe7_buf
]

with open("io_core.v", "w") as f:
    f.write(verilog.convert(io_core, ports=ports, strip_internal_attrs=True))