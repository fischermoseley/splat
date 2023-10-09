from amaranth.sim import Simulator
from src.io_core import IOCore
import yaml

with open('manta.yaml', 'r') as file:
    config = yaml.safe_load(file)['cores']['io_core']

io_core = IOCore(config, 0)

def bench():
    # Should be able to read all register values
    for i in range(11):
        yield io_core.addr_i.eq(i)
        yield io_core.data_i.eq(0)
        yield io_core.rw_i.eq(0)
        yield io_core.valid_i.eq(1)
        yield
        yield io_core.valid_i.eq(0)

        while not (yield io_core.valid_o):
            yield

        addr = yield (io_core.addr_o)
        data = yield (io_core.data_o)
        print(f'addr: {addr} data: {data}')



sim = Simulator(io_core)
sim.add_clock(1e-6) # 1 MHz
sim.add_sync_process(bench)
with sim.write_vcd("io_core.vcd"):
    sim.run()