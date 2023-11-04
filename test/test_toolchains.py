from amaranth_boards.test.blinky import *
from amaranth_boards.arty_a7 import *
from amaranth_boards.icestick import *
from amaranth import *
import os


def test_arty_a7_tools():
    os.environ["VIVADO"] = "/tools/Xilinx/Vivado/2023.1/bin/vivado"
    ArtyA7_100Platform().build(Blinky(), do_program=True)


def test_ice40_tools():
    os.environ["YOSYS"] = "/tools/oss-cad-suite/bin/yosys"
    os.environ["NEXTPNR_ICE40"] = "/tools/oss-cad-suite/bin/nextpnr-ice40"
    os.environ["ICEPACK"] = "/tools/oss-cad-suite/bin/icepack"
    os.environ["ICEPROG"] = "/tools/oss-cad-suite/bin/iceprog"
    ICEStickPlatform().build(Blinky(), do_program=False)
