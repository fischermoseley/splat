from amaranth import *
from amaranth.lib.data import ArrayLayout
from warnings import warn
from math import ceil, log2


class ReadOnlyMemoryCore(Elaboratable):
    def __init__(self, config, base_addr, interface):
        self.config = config
        self.base_addr = base_addr
        self.interface = interface

        self.check_config(config)
        self.define_signals()

        self.depth = self.config['depth']
        self.width = self.config['width']
        self.addr_width = ceil(log2(self.depth))
        self.n_mems = ceil(self.width / 16)
        self.max_addr = self.base_addr + (self.depth * self.n_mems)

    def check_config(self, config):
        # Check for unrecognized options
        valid_options = ["type", "depth", "width", "disable_user_port"]
        for option in config:
            if option not in valid_options:
                warn(f"Ignoring unrecognized option '{option}' in memory core.")

        # Check depth is provided and positive
        if "depth" not in config:
            raise ValueError("Depth of memory core must be specified.")

        if not isinstance(config["depth"], int):
            raise ValueError("Depth of memory core must be an integer.")

        if config["depth"] <= 0:
            raise ValueError("Depth of memory core must be positive. ")


        # Check width is provided and positive
        if "width" not in config:
            raise ValueError("Width of memory core must be specified.")

        if not isinstance(config["width"], int):
            raise ValueError("Width of memory core must be an integer.")

        if config["width"] <= 0:
            raise ValueError("Width of memory core must be positive. ")

    def define_signals(self):
        self.addr_i = Signal(16)
        self.data_i = Signal(16)
        self.rw_i = Signal(1)
        self.valid_i = Signal(1)

        self.addr_o = Signal(16, reset=0)
        self.data_o = Signal(16, reset=0)
        self.rw_o = Signal(1, reset=0)
        self.valid_o = Signal(1, reset=0)

        # self.addr_pipe = ArrayLayout(16, 3)
        # self.data_pipe = ArrayLayout(16, 3)
        # self.rw_pipe = ArrayLayout(1, 3)
        # self.valid_pipe = ArrayLayout(1, 3)

        self.addr_pipe = [Signal(16) for _ in range(3)]
        self.data_pipe = [Signal(16) for _ in range(3)]
        self.rw_pipe = [Signal(1) for _ in range(3)]
        self.valid_pipe = [Signal(1) for _ in range(3)]

    def in_range(addr, start, stop):
        return (addr >= start) & (addr <= stop)

    def elaborate(self, platform):
        # ok so we just instantiate n_brams worth of memories, with the appropriate widths
        # and then we put them all on the bus?

        m = Module()

        # Set up memory
        self.mem = Memory(width = 16, depth=self.depth, init= [i for i in range(self.depth)])
        m.submodules["mem"] = self.mem
        read_port = self.mem.read_port()
        m.d.sync += read_port.en.eq(1)


        # Pipelining
        m.d.sync += self.addr_pipe[0].eq(self.addr_i)
        m.d.sync += self.data_pipe[0].eq(self.data_i)
        m.d.sync += self.rw_pipe[0].eq(self.rw_i)
        m.d.sync += self.valid_pipe[0].eq(self.valid_i)

        for i in range(1, 3):
            m.d.sync += self.addr_pipe[i].eq(self.addr_pipe[i-1])
            m.d.sync += self.data_pipe[i].eq(self.data_pipe[i-1])
            m.d.sync += self.rw_pipe[i].eq(self.rw_pipe[i-1])
            m.d.sync += self.valid_pipe[i].eq(self.valid_pipe[i-1])

        m.d.sync += self.addr_o.eq(self.addr_pipe[2])
        m.d.sync += self.data_o.eq(self.data_pipe[2])
        m.d.sync += self.rw_o.eq(self.rw_pipe[2])
        m.d.sync += self.valid_o.eq(self.valid_pipe[2])


        # Perform memory reads/writes
        start_addr = self.base_addr
        stop_addr = start_addr + self.depth

        # Throw BRAM operations into the front of the pipeline
        with m.If( (self.addr_i >= start_addr) & (self.addr_i <= stop_addr) ):
            with m.If(~self.rw_i):
                m.d.sync += read_port.addr.eq(self.addr_i - start_addr)

        # Pull BRAM reads from the back of the pipeline
        with m.If(self.valid_pipe[2] & (self.addr_pipe[2] >= start_addr) & (self.addr_pipe[2] <= stop_addr)):
            m.d.sync += self.data_o.eq(read_port.data)

        return m





        # for i, mem in self.mems:
        #     m.submodules[f"mem_{i}"] = mem
        #     start_addr = self.base_addr + (i * self.depth)
        #     stop_addr = start_addr + self.depth

        #     with m.If( (self.addr_i >= start_addr) & (self.addr_i <= stop_addr) ):
        #         with m.If(self.rw_i):
        #             mem.porta.addr.eq(self.addr_i - start_addr)
        #             mem.porta.data.eq(self.data_i)
        #             mem.porta.we.eq(1)

        #         with m.Else():
        #             mem[i].porta.addr.eq(self.addr_i - start_addr)
        #             self.data_o.eq(self.mems[i].porta.data)

        # m.d.comb += self.user.dout(Cat( [mem[i].portb.dout] for i in ...))

        # self.user_clk
        # self.user_addr
        # self.user_din
        # self.user_dout
        # self.user_we








    # I'm not sure either of these are correct - shouldn't we be reading from more than one
    # address if we're reading from something that's greater than 16-bits wide?

    # def write(self, addrs, datas):
    #     if isinstance(addrs, list):
    #         self.interface.write( ([a - self.base_addr] for a in addrs) , datas)

    #     else:
    #         self.interface.write(addrs - self.base_addr, datas)

    # def read(self, addrs):
    #     if isinstance(addrs, list):
    #         self.interface.read([a - self.base_addr] for a in addrs)

    #     else:
    #         self.interface.read(addrs - self.base_addr)


