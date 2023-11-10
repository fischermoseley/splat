from amaranth_boards.test.blinky import *
from amaranth_boards.arty_a7 import *
from amaranth_boards.icestick import *
from amaranth import *
import os


def test_arty_a7_tools():
    # Only test the toolchain if the VIVADO environment variable is defined.
    # This variable should point to the binary itself, not just the folder it's located in
    # (ie, /tools/Xilinx/Vivado/2023.1/bin/vivado, not /tools/Xilinx/Vivado/2023.1/bin)
    if "VIVADO" in os.environ:
        ArtyA7_100Platform().build(Blinky(), do_program=False)


def test_ice40_tools():
    # Only test the toolchain if the environment variables for the ice40 tools are defined.
    # These variables should point to the binaries themselves, not just the folder it's located in
    # (ie, /tools/oss-cad-suite/bin/yosys, not /tools/oss-cad-suite/bin/)
    tools = ["YOSYS", "NEXTPNR_ICE40", "ICEPACK", "ICEPROG"]
    if all(tool in os.environ for tool in tools):
        ICEStickPlatform().build(Blinky(), do_program=False)
