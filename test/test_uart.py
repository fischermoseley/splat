from amaranth.sim import Simulator
from splat.uart import UARTInterface
from splat.utils import *
from random import randint
import yaml

with open("splat.yaml", "r") as file:
    config = yaml.safe_load(file)["uart"]

uart = UARTInterface(config)


def simulate(testbench):
    sim = Simulator(uart)
    sim.add_clock(1e-6)  # 1 MHz
    sim.add_sync_process(testbench)

    with sim.write_vcd("uart.vcd"):
        sim.run()


def test_do_you_run_lol():
    def testbench():
        for _ in range(1000):
            yield

    simulate(testbench)


test_do_you_run_lol()
