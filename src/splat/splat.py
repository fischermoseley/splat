from amaranth import *
from warnings import warn
from .io_core import IOCore

class Splat(Elaboratable):
    def __init__(self, config_path):
        # load config
        self.config = self.read_config_file(config_path)
        self.check_config()

        self.m = Module()
        # self.interface = self.get_interface()
        self.add_cores()
        self.ports = self.get_top_level_ports()
        self.connect_cores()

    def read_config_file(self, path):
        """
        Take path to configuration file, and retun the configuration as a python list/dict object.
        """

        extension = path.split(".")[-1]

        if "json" in extension:
            with open(path, "r") as f:
                import json
                return json.load(f)

        elif "yaml" in extension or "yml" in extension:
            with open(path, "r") as f:
                import yaml
                return yaml.safe_load(f)

        else:
            raise ValueError("Unable to recognize configuration file extension.")

    def check_config(self):
        if 'cores' not in self.config:
            raise ValueError('No cores specified in configuration file.')

        if not len(self.config["cores"]) > 0:
            raise ValueError('Must specify at least one core.')

    def get_interface(self):
        if 'uart' in self.config:
            from .uart import UARTInterface
            return UARTInterface(self.config['uart'])

        elif 'ethernet' in self.config:
            from .ethernet import EthernetInterface
            return EthernetInterface(self.config['ethernet'])

        else:
            raise ValueError('Unrecognized interface specified.')

    def get_cores(self):
        """
        """

        self.m.submodules.io_core_0 = io_core_0 = IOCore(config, 0)
        self.m.submodules.io_core_1 = io_core_1 = IOCore(config, 0)
        return

        base_addr = 0
        for name, attrs in config['cores'].items():
            # make sure core type is specified
            if 'type' not in attrs:
                raise ValueError(f'No type specified for core {name}.')

            # make an instance of the core
            if attrs['type'] == 'logic_analyzer':
                new_core = LogicAnalyzerCore(attrs, name, base_addr, self.interface)

            elif attrs['type'] == 'io':
                new_core = IOCore(attrs, name, base_addr, self.interface)

            elif attrs['type'] == 'block_memory':
                new_core = BlockMemoryCore(attrs, name, base_addr, self.interface)

            else:
                raise ValueError(f"Unrecognized core type specified for {name}.")

            # make sure we're not out of address space
            if new_core.get_max_addr() > (2**16)-1:
                raise ValueError(f'Ran out of address space to allocate to core {name}.')

            # make the next core's base address start one address after the previous one's
            base_addr = new_core.get_max_addr() + 1

    def connect_cores(self):
        self.m.d.comb += [
            io_core_0.addr_i.eq(self.addr_i),
            io_core_0.data_i.eq(self.data_i),
            io_core_0.rw_i.eq(self.rw_i),
            io_core_0.valid_i.eq(self.valid_i),

            io_core_1.addr_i.eq(io_core_0.addr_o),
            io_core_1.data_i.eq(io_core_0.data_o),
            io_core_1.rw_i.eq(io_core_0.rw_o),
            io_core_1.valid_i.eq(io_core_0.valid_o),

            self.addr_o.eq(io_core_1.addr_o),
            self.data_o.eq(io_core_1.data_o),
            self.rw_o.eq(io_core_1.rw_o),
            self.valid_o.eq(io_core_1.valid_o)
        ]

    def elaborate(self, platform):
        return self.m