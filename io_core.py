from amaranth import *
from warnings import warn
from math import ceil

class IOCore(Elaboratable):
    """
    Me just fucking around, mostly.

    """

    def __init__(self, config, base_addr):
        # Config
        self.config = config
        self.check_config(self.config)

        # Bus Ports
        self.addr_i = Signal(16)
        self.data_i = Signal(16)
        self.rw_i = Signal()
        self.valid_i = Signal()

        self.addr_o = Signal(16)
        self.data_o = Signal(16)
        self.rw_o = Signal()
        self.valid_o = Signal()

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

        # Strobe Register
        self.strobe = Signal(reset = 0)

        # Memory Map
        self.base_addr = base_addr
        self.memory_map, self.max_addr = self.assign_memory()

    def elaborate(self, platform):
        m = Module()

        # Shuffle bus transactions along
        m.d.sync += self.addr_o.eq(self.addr_i)
        m.d.sync += self.data_o.eq(self.data_i)
        m.d.sync += self.rw_o.eq(self.rw_i)
        m.d.sync += self.valid_o.eq(self.valid_i)

        # Update buffers from probes
        with m.If(self.strobe):
            # Input buffers
            for name in self.config['inputs']:
                input_probe = getattr(self, name)
                input_probe_buf = getattr(self, name + '_buf')
                m.d.sync += input_probe_buf.eq(input_probe)

            # Output buffers
            for name in self.config['outputs']:
                output_probe = getattr(self, name)
                output_probe_buf = getattr(self, name + '_buf')
                m.d.sync += output_probe.eq(output_probe_buf)

        # Handle register reads and writes
        with m.If(  (self.addr_i >= self.base_addr) & \
                    (self.addr_o <= self.max_addr)):
            # writes
            with m.If(self.rw_i):
                with m.Switch(self.addr_i - self.base_addr):

                    # strobe register
                    with m.Case(0):
                        m.d.sync += self.strobe.eq(self.data_i)

                    # output probes
                    for name in self.config['outputs']:
                        probe = self.memory_map[name + '_buf']
                        addrs = probe['addrs']
                        signals = probe['signals']

                        for addr, signal in zip(addrs, signals):
                            with m.Case(addr):
                                m.d.sync += signal.eq(self.data_i)

            # reads
            with m.Else():
                with m.Switch(self.addr_i - self.base_addr):
                    with m.Case(0):
                        m.d.sync += self.data_o.eq(self.strobe)

                    # input probes
                    for name in self.config['inputs']:
                        probe = self.memory_map[name + '_buf']
                        addrs = probe['addrs']
                        signals = probe['signals']

                        for addr, signal in zip(addrs, signals):
                            with m.Case(addr):
                                m.d.sync += self.data_o.eq(signal)

                    # output probes
                    for name in self.config['outputs']:
                        probe = self.memory_map[name + '_buf']
                        addrs = probe['addrs']
                        signals = probe['signals']

                        for addr, signal in zip(addrs, signals):
                            with m.Case(addr):
                                m.d.sync += self.data_o.eq(signal)
        return m

    def check_config(self, config):
        # make sure ports are defined
        if 'inputs' not in config or 'outputs' not in config:
            raise ValueError('No input or output ports specified.')

        # check for unrecognized options
        valid_options = ["type", "inputs", "outputs", "user_clock"]
        for option in config:
            if option not in valid_options:
                warn(f"Ignoring unrecognized option '{option}' in IO core.'")

        # check that user_clock is a bool
        if 'user_clock' in config:
            if not isinstance(config['user_clock'], bool):
                raise ValueError('Option user_clock must be a boolean.')

        # check that inputs is only dicts of format name:width
        if 'inputs' in config:
            for name, attrs in config['inputs'].items():
                if not isinstance(name, str):
                    raise ValueError(f'Input probe "{name}" has invalid name, names must be strings.')

                if not isinstance(attrs, int):
                    raise ValueError(f'Input probe "{name}" must have integer width.')

                if not attrs > 0:
                    raise ValueError(f'Input probe "{name}" must have positive width.')

        if 'outputs' in config:
            for name, attrs in config['outputs'].items():
                if not isinstance(name, str):
                    raise ValueError(f'Output probe "{name}" has invalid name, names must be strings.')

                if not isinstance(attrs, int) and not isinstance(attrs, dict):
                    raise ValueError(f'Unrecognized format for output probe "{name}".')

                if isinstance(attrs, int):
                    if not attrs > 0:
                        raise ValueError(f'Output probe "{name}" must have positive width.')

                if isinstance(attrs, dict):
                    # check that each output probe has only recognized options
                    valid_options = ['width', 'initial_value']
                    for option in attrs:
                        if option not in valid_options:
                            warn(f'Ignoring unrecognized option "{option}" in IO core.')

                    # check that widths are appropriate
                    if 'width' not in attrs:
                        raise ValueError(f'No width specified for output probe {name}.')

                    if not isinstance(attrs['width'], int):
                        raise ValueError(f'Output probe "{name}" must have integer width.')

                    if not attrs['width'] > 0:
                        raise ValueError(f'Input probe "{name}" must have positive width.')

    def assign_memory(self):
        """
        the memory map is a dict that maps registers (in memory) to their locations (in memory)
        as well as their Signals (from Amaranth). This looks like the following:

        {
            strobe:
                addrs: [0x0000]
                signals: [self.strobe]
            probe0_buf:
                addrs: [0x0001]
                signals: [self.probe0_buf]
            probe1_buf:
                addrs: [0x0002]
                signals: [self.probe1_buf]
            probe2_buf:
                addrs: [0x0003]
                signals: [self.probe2_buf]
            probe3_buf:
                addrs: [0x0004, 0x0005]
                signals: [self.probe3_buf[0:15], self.probe3_buf[16:19]]
            ... and so on
        }

        let's try implementing this and we'll see if we like it
        """

        memory_map = {
            'strobe' : {
                'addrs': [self.base_addr],
                'signals': [self.strobe]
            },

            'probe0_buf' : {
                'addrs': [self.base_addr + 1],
                'signals': [self.probe0_buf]
            },

            'probe1_buf' : {
                'addrs': [self.base_addr + 2],
                'signals': [self.probe1_buf]
            },

            'probe2_buf' : {
                'addrs': [self.base_addr + 3],
                'signals': [self.probe2_buf]
            },

            'probe3_buf' : {
                'addrs': [self.base_addr + 4, self.base_addr + 5],
                'signals': [self.probe3_buf[0:16], self.probe3_buf[16:20]]
            },

            'probe4_buf' : {
                'addrs': [self.base_addr + 6],
                'signals': [self.probe4_buf]
            },

            'probe5_buf' : {
                'addrs': [self.base_addr + 7],
                'signals': [self.probe5_buf]
            },

            'probe6_buf' : {
                'addrs': [self.base_addr + 8],
                'signals': [self.probe6_buf]
            },

            'probe7_buf' : {
                'addrs': [self.base_addr + 9, self.base_addr + 10],
                'signals': [self.probe7_buf[0:16], self.probe7_buf[16:20]]
            }
        }

        return memory_map, self.base_addr + 10

    def set_probe(self, probe_name, value):
        # set value in buffer
        addrs = self.memory_map[probe_name+'_buf']['addrs']
        datas = value_to_words(value, len(addrs))
        self.interface.write(addrs, datas)

        # pulse strobe register
        strobe_addr = self.memory_map['strobe']['addrs'][0]
        self.interface.write(strobe_addr, 0)
        self.interface.write(strobe_addr, 1)
        self.interface.write(strobe_addr, 0)

    def get_probe(self, probe_name):
        # pulse strobe register
        strobe_addr = self.memory_map['strobe']['addrs'][0]
        self.interface.write(strobe_addr, 0)
        self.interface.write(strobe_addr, 1)
        self.interface.write(strobe_addr, 0)

        # get value from buffer
        addrs = self.memory_map[probe_name+'_buf']['addrs']
        return words_to_value(self.interface.read(addrs))
