from amaranth import *
from warnings import warn
from .utils import *
from .io_core import IOCore
from .memory_core import ReadOnlyMemoryCore
from math import ceil, log2

class LogicAnalyzerCore(Elaboratable):
    """
    """

    def __init__(self, config, base_addr, interface):
        self.config = config
        self.base_addr = base_addr
        self.interface = interface

        self.check_config(config)

        # State Machine Values
        self.states = {
            "IDLE": 0,
            "MOVE_TO_POSITION": 1,
            "IN_POSITION" : 2,
            "CAPTURING" : 3,
            "CAPTURED" : 4
        }

        # Trigger operations
        self.operations = {
            "DISABLE" : 0,
            "RISING" : 1,
            "FALLING" : 2,
            "CHANGING" : 3,
            "GT" : 4,
            "LT" : 5,
            "GEQ" : 6,
            "LEQ" : 7,
            "EQ" : 8,
            "NEQ" : 9
        }

        self.registers = self.make_registers(self.base_addr)
        self.sample_mem = self.make_sample_mem(self.registers.max_addr)
        self.define_signals()

    def check_config(self, config):
        # Check for unrecognized options
        valid_options = ["type", "sample_depth", "probes", "triggers", "trigger_loc", "trigger_mode"]
        for option in config:
            if option not in valid_options:
                warn(f"Ignoring unrecognized option '{option}' in Logic Analyzer.")

        # Check sample depth is provided and positive
        if "sample_depth" not in config:
            raise ValueError("Logic Analyzer must have sample_depth specified.")

        if not isinstance(config["sample_depth"], int):
            raise ValueError("Logic Analyzer sample_depth must be an integer.")

        if config["sample_depth"] <= 0:
            raise ValueError("Logic Analyzer sample_depth must be positive.")

        # Check probes
        if "probes" not in config:
            raise ValueError("Logic Analyzer must have at least one probe specified.")

        if len(config["probes"]) == 0:
            raise ValueError("Logic Analyzer must have at least one probe specified.")

        for name, width in config["probes"].items():
            if width < 0:
                raise ValueError(f"Width of probe {name} must be positive.")

        # Check triggers
        if "triggers" not in config:
            raise ValueError("Logic Analyzer must have at least one trigger specified.")

        if len(config["triggers"]) == 0:
            raise ValueError("Logic Analyzer must have at least one trigger specified.")

        # Check trigger location
        if "trigger_loc" in config:
            if not isinstance(config["trigger_loc"], int):
                raise ValueError("Trigger location must be an integer.")

            if config["trigger_loc"] < 0:
                raise ValueError("Trigger location must be positive.")

            if config["trigger_loc"] > config["sample_depth"]:
                raise ValueError("Trigger location cannot exceed sample depth.")

        # Check trigger mode
        if "trigger_mode" in config:
            valid_modes = ["single_shot", "incremental", "immediate"]
            if config["trigger_mode"] not in valid_modes:
                raise ValueError(f"Unrecognized trigger mode {config['trigger_mode']} provided.")

    def define_signals(self):
        # Bus Input
        self.addr_i = Signal(16)
        self.data_i = Signal(16)
        self.rw_i = Signal(1)
        self.valid_i = Signal(1)

        # Bus Output
        self.addr_o = Signal(16)
        self.data_o = Signal(16)
        self.rw_o= Signal(1)
        self.valid_o = Signal(1)

        # Probes
        self.probe_signals = {}
        for name, width in self.config["probes"].items():
            self.probe_signals[name] = {
                "top_level" : Signal(width),
                "prev" : Signal(width),
                "trigger_arg" : getattr(self.registers, f"{name}_arg"),
                "trigger_op" : getattr(self.registers, f"{name}_op"),
                "triggered" : Signal(1)
            }

        # Global trigger. High if any probe is triggered.
        self.trig = Signal(1)

    def make_registers(self, base_addr):
        # The logic analyzer uses an IO core to handle inputs to the FSM and trigger comparators
        register_config = {
            "inputs": {
                "state" : 4,
                "read_pointer" : ceil(log2(self.config["sample_depth"])),
                "write_pointer" : ceil(log2(self.config["sample_depth"]))
            },

            "outputs": {
                "trigger_loc" : ceil(log2(self.config["sample_depth"])),
                "trigger_mode" : 2,
                "request_start" : 1,
                "request_stop" : 1
            }
        }

        for name, width in self.config["probes"].items():
            register_config["outputs"][name + "_arg"] = width
            register_config["outputs"][name + "_op"] = 4

        return IOCore(register_config, base_addr, self.interface)

    def make_sample_mem(self, base_addr):

        sample_mem_config = {
            "width": sum(self.config["probes"].values()),
            "depth": self.config["sample_depth"]
        }

        return ReadOnlyMemoryCore(sample_mem_config, base_addr, self.interface)

    def run_triggers(self, m):
        # Run the trigger for each individual probe
        for name, attrs in self.probe_signals.items():
            top_level = attrs["top_level"]
            prev = attrs["prev"]
            trigger_arg = attrs["trigger_arg"]
            trigger_op = attrs["trigger_op"]
            triggered = attrs["triggered"]


            # Save the previous value to a register so we can do rising/falling edge detection later!
            m.d.sync += prev.eq(top_level)

            with m.If(trigger_op == self.operations["DISABLE"]):
                m.d.comb += triggered.eq(0)

            with m.Elif(trigger_op == self.operations["RISING"]):
                m.d.comb += triggered.eq( (top_level) & (~prev) )

            with m.Elif(trigger_op == self.operations["FALLING"]):
                m.d.comb += triggered.eq( (~top_level)  & (prev) )

            with m.Elif(trigger_op == self.operations["CHANGING"]):
                m.d.comb += triggered.eq(top_level != prev)

            with m.Elif(trigger_op == self.operations["GT"]):
                m.d.comb += triggered.eq(top_level > trigger_arg)

            with m.Elif(trigger_op == self.operations["LT"]):
                m.d.comb += triggered.eq(top_level < trigger_arg)

            with m.Elif(trigger_op == self.operations["GEQ"]):
                m.d.comb += triggered.eq(top_level >= trigger_arg)

            with m.Elif(trigger_op == self.operations["LEQ"]):
                m.d.comb += triggered.eq(top_level <= trigger_arg)

            with m.Elif(trigger_op == self.operations["EQ"]):
                m.d.comb += triggered.eq(top_level == trigger_arg)

            with m.Elif(trigger_op == self.operations["NEQ"]):
                m.d.comb += triggered.eq(top_level != trigger_arg)

            with m.Else():
                m.d.comb += triggered.eq(0)

        # Combine all the triggers
        m.d.comb += self.trig.eq(0)
        for name, attrs in self.probe_signals.items():
            m.d.comb += self.trig.eq( (self.trig) & (attrs["triggered"]) )

    def run_state_machine(self, m):
        self.prev_request_start = Signal(1)
        self.prev_request_stop = Signal(1)

        # Rising edge detection for start/stop requests
        m.d.sync += self.prev_request_start.eq(self.registers.request_start)
        m.d.sync += self.prev_request_stop.eq(self.registers.request_stop)

        m.d.comb += self.sample_mem.user_addr.eq(self.registers.write_pointer)

        with m.If(self.registers.state == self.states["IDLE"]):
            m.d.sync += self.registers.write_pointer.eq(0)
            m.d.sync += self.registers.read_pointer.eq(0)
            m.d.sync += self.sample_mem.user_we.eq(0) # or something like this

            with m.If( (self.registers.request_start) & (~self.prev_request_start) ):
                m.d.sync += self.registers.state.eq(self.states["MOVE_TO_POSITION"])

        with m.Elif(self.registers.state == self.states["MOVE_TO_POSITION"]):
            m.d.sync += self.registers.write_pointer.eq(self.registers.write_pointer + 1)
            m.d.sync += self.sample_mem.user_we.eq(1)

            with m.If(self.registers.write_pointer == self.registers.trigger_loc):
                with m.If(self.trig):
                    m.d.sync += self.registers.state.eq(self.states["CAPTURING"])

                with m.Elif(self.trig):
                    m.d.sync += self.registers.state.eq(self.states["IN_POSITION"])

        with m.Elif(self.registers.state == self.states["IN_POSITION"]):
            m.d.sync += self.registers.write_pointer.eq((self.registers.write_pointer + 1) % self.config["sample_depth"])
            m.d.sync += self.registers.read_pointer.eq((self.registers.read_pointer + 1) % self.config["sample_depth"])
            m.d.sync += self.sample_mem.user_we.eq(1)

            with m.If(self.trig):
                m.d.sync += self.registers.state.eq(self.states["CAPTURING"])

        with m.Elif(self.registers.state == self.states["CAPTURING"]):
            with m.If(self.registers.write_pointer == self.registers.read_pointer):
                m.d.sync += self.sample_mem.user_we.eq(0)
                m.d.sync += self.registers.state.eq(self.states["CAPTURED"])

            with m.Else():
                m.d.sync += self.registers.write_pointer.eq((self.registers.write_pointer + 1) % self.config["sample_depth"])

        with m.If( (self.registers.request_stop) & (~self.prev_request_stop) ):
            m.d.sync += self.registers.state.eq(self.states["IDLE"])

    def elaborate(self, platform):
        m = Module()

        # Add registers and sample memory as submodules
        m.submodules["registers"] = self.registers
        m.submodules["sample_mem"] = self.sample_mem

        # Concat all the probes together, and feed to input of sample memory
        # (it is necessary to reverse the order such that first probe occupies
        # the lowest location in memory)
        m.d.comb += self.sample_mem.user_data.eq(Cat( [p["top_level"] for p in self.probe_signals.values()][::-1] ))

        self.run_state_machine(m)
        self.run_triggers(m)

        # Wire internal modules
        m.d.comb += [
            self.registers.addr_i.eq(self.addr_i),
            self.registers.data_i.eq(self.data_i),
            self.registers.rw_i.eq(self.rw_i),
            self.registers.valid_i.eq(self.valid_i),

            self.sample_mem.addr_i.eq(self.registers.addr_o),
            self.sample_mem.data_i.eq(self.registers.data_o),
            self.sample_mem.rw_i.eq(self.registers.rw_o),
            self.sample_mem.valid_i.eq(self.registers.valid_o),

            self.addr_o.eq(self.sample_mem.addr_o),
            self.data_o.eq(self.sample_mem.data_o),
            self.rw_o.eq(self.sample_mem.rw_o),
            self.valid_o.eq(self.sample_mem.valid_o)
        ]

        return m

    def get_top_level_ports(self):
        return [p["top_level"] for p in self.probe_signals.values()]

    def get_max_addr(self):
        return self.sample_mem.get_max_addr()