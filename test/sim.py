from amaranth.sim import Simulator
from splat.io_core import IOCore
from splat.utils import *
from random import randint
import yaml

with open('splat.yaml', 'r') as file:
    config = yaml.safe_load(file)['cores']['io_core']

io_core = IOCore(config, 0)

def verify_register(addr, expected_data):
    # place read transaction on the bus
    yield io_core.addr_i.eq(addr)
    yield io_core.data_i.eq(0)
    yield io_core.rw_i.eq(0)
    yield io_core.valid_i.eq(1)
    yield
    yield io_core.valid_i.eq(0)

    # wait for output to be valid
    while not (yield io_core.valid_o):
        yield

    # compare returned value with expected
    data = yield (io_core.data_o)
    if data != expected_data:
        raise ValueError(f"Read from {addr} yielded {data} instead of {expected_data}")

    else:
        print(f"Read from {addr} yielded {data} as expected")

def write_register(addr, data):
    yield io_core.addr_i.eq(addr)
    yield io_core.data_i.eq(data)
    yield io_core.rw_i.eq(1)
    yield io_core.valid_i.eq(1)
    yield
    yield io_core.valid_i.eq(0)
    yield

def pulse_strobe_register():
    strobe_addr = io_core.mmap['strobe']['addrs'][0]
    yield from write_register(strobe_addr, 0)
    yield from write_register(strobe_addr, 1)
    yield from write_register(strobe_addr, 0)

def verify_output_probe_initial_values():
    # Verify all output probes initialize to the values in the config
    for name, attrs in config['outputs'].items():

        initial_value = 0
        if isinstance(attrs, dict):
            if 'initial_value' in attrs:
                initial_value = attrs['initial_value']

        output_probe = getattr(io_core, name)
        value = yield output_probe

        if value != initial_value:
            raise ValueError(f"Output probe {name} initialized to {value} instead of {initial_value}")

        else:
            print(f"Output probe {name} initialized to {value} as expected.")

def verify_input_probe_buffer_initial_value():
    # Verify all input probe buffers initialize to zero
    for name, width in config['inputs'].items():
        addrs = io_core.mmap[name + '_buf']['addrs']

        for addr in addrs:
            yield from verify_register(addr, 0)

def verify_output_probe_buffer_initial_value():
    # Verify all output probe buffers initialize to the values in the config
    for name, attrs in config['outputs'].items():
        addrs = io_core.mmap[name + '_buf']['addrs']

        datas = [0] * len(addrs)
        if isinstance(attrs, dict):
            if 'initial_value' in attrs:
                datas = value_to_words(attrs['initial_value'], len(addrs))

        for addr, data in zip(addrs, datas):
            yield from verify_register(addr, data)

def verify_output_probes_are_writeable():
    for name, attrs in config['outputs'].items():
        if isinstance(attrs, dict):
            width = attrs['width']
        else:
            width = attrs

        addrs = io_core.mmap[name + '_buf']['addrs']
        test_value = randint(0, (2**width) - 1)
        datas = value_to_words(test_value, len(addrs))

        # write value to registers
        for addr, data in zip(addrs, datas):
            yield from write_register(addr, data)

        # read value back from registers
        for addr, data in zip(addrs, datas):
            yield from verify_register(addr, data)

def verify_output_probes_update():
    for name, attrs in config['outputs'].items():
        if isinstance(attrs, dict):
            width = attrs['width']
        else:
            width = attrs

        addrs = io_core.mmap[name + '_buf']['addrs']
        test_value = randint(0, (2**width) - 1)
        datas = value_to_words(test_value, len(addrs))

        # write value to registers
        for addr, data in zip(addrs, datas):
            yield from write_register(addr, data)

        # pulse strobe register
        yield from pulse_strobe_register()

        # check that outputs took updated value
        output_probe = getattr(io_core, name)
        value = yield (output_probe)

        if value != test_value:
            raise ValueError(f'Output probe {name} took value {value} instead of {test_value} after pulsing strobe.')

        else:
            print(f'Output probe {name} took value {value} after pulsing strobe.')

def verify_input_probes_update():
    for name, width in config['inputs'].items():
        test_value = randint(0, (2**width) - 1)

        # set input probe value
        input_probe = getattr(io_core, name)
        yield input_probe.eq(test_value)

        # pulse strobe register
        yield from pulse_strobe_register()

        # check that values are as expected once read back
        addrs = io_core.mmap[name + '_buf']['addrs']
        datas = value_to_words(test_value, len(addrs))

        for addr, data in zip(addrs, datas):
            yield from verify_register(addr, data)

def bench():
    # Should be able to read all register values
    yield from verify_output_probe_initial_values()
    yield from verify_output_probe_buffer_initial_value()
    yield from verify_input_probe_buffer_initial_value()
    yield from verify_output_probes_are_writeable()
    yield from verify_output_probes_update()
    yield from verify_input_probes_update()


sim = Simulator(io_core)
sim.add_clock(1e-6) # 1 MHz
sim.add_sync_process(bench)
with sim.write_vcd("io_core.vcd"):
    sim.run()