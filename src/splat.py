from amaranth import *
from warnings import warn
from sys import argv

from io_core import IOCore
from logo import logo

class Splat(Elaboratable):
    def __init__(self, config_path):
        # load config
        self.config = self.read_config_file(config_path)
        self.check_config()

        self.m = Module()
        self.interface = self.get_interface()
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
        if 'cores' not in config:
            raise ValueError('No cores specified in configuration file.')

        if not len(config["cores"]) > 0:
            raise ValueError('Must specify at least one core.')

    def get_interface(self):
        if 'uart' in config:
            from .uart import UARTInterface
            return UARTInterface(config['uart'])

        elif 'ethernet' in config:
            from .ethernet import EthernetInterface
            return EthernetInterface(config['ethernet'])

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

def main():
    if len(argv) == 1:
        help()

    elif argv[1] in ['help', '-h', '-help', '--help']:
        help()

    elif argv[1] == 'gen':
        if len(argv) != 4: wrong_args()
        gen(argv[2], argv[3])

    elif argv[1] == 'capture':
        if len(argv) < 5: wrong_args()
        capture(argv[2], argv[3], argv[4])

    elif argv[1] == 'playback':
        if len(argv) != 5: wrong_args()
        playback(argv[2], argv[3], argv[4])

    elif argv[1] == 'mmap':
        if len(argv) != 3: wrong_args()
        mmap(argv[2])

    elif argv[1] == 'ports':
        ports()

    else:
        wrong_args()

def help():
    print(logo)

def wrong_args():
    raise ValueError('Wrong number of arguments, run "splat help" for usage.')

def gen(config_path, output_path):
    s = Splat(config_path)

    from amaranth.back import verilog
    with open(output_path, 'w') as f:
        f.write(verilog.convert(s, ports=s.ports, strip_internal_attrs=True))

def capture(config_path, logic_analyzer_name, export_paths):
    s = Splat(config_path)
    la = getattr(s, logic_analyzer_name)
    data = la.capture()

    for path in export_paths:
        if '.vcd' in path: la.export_vcd(data, path)
        elif '.mem' in path: la.export_mem(data, path)
        else: warn(f'Unrecognized file type, skipping {path}.')

def playback(config_path, logic_analyzer_name, export_path):
    s = Splat(config_path)
    la = getattr(s, logic_analyzer_name)
    la.export_playback_module(export_path)

def mmap(config_path):
    print(Splat(config_path).mmap())

def ports():
    import serial.tools.list_ports
    for port in serial.tools.list_ports.comports():
        print(port)

        # sometimes macOS will enumerate non-serial devices as serial ports,
        # in which case the PID/VID/serial/location/etc are all None
        pid = f"0x{port.vid:04X}" if port.pid is not None else "None"
        vid = f"0x{port.vid:04X}" if port.vid is not None else "None"

        print(f" ->  pid: {pid}")
        print(f" ->  vid: {vid}")
        print(f" ->  ser: {port.serial_number}")
        print(f" ->  loc: {port.location}")
        print(f" -> mftr: {port.manufacturer}")
        print(f" -> prod: {port.product}")
        print(f" -> desc: {port.description}\n")

if __name__ == "__main__":
    main()