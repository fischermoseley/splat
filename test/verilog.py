from src.io_core import IOCore
from amaranth.back import verilog
import yaml

with open("manta.yaml", "r") as file:
    config = yaml.safe_load(file)["cores"]["io_core"]
    # print(config)

io_core = IOCore(config, 0)

ports_sim = [
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
    io_core.probe7_buf,
]

ports_synth = [
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
]

with open("io_core.v", "w") as f:
    f.write(verilog.convert(io_core, ports=ports_synth, strip_internal_attrs=True))
