from amaranth.sim import Simulator
from splat.logic_analyzer_core import LogicAnalyzerCore
from splat.utils import *
from random import sample

config = {
    "type": "logic_analyzer",
    "sample_depth": 4096,
    "trigger_loc": 1000,
    "probes": {
        "larry": 1,
        "curly": 3,
        "moe": 9
    },
    "triggers": ["moe RISING"]
}


la = LogicAnalyzerCore(config, base_addr=0, interface=None)

def test_do_you_fucking_work():
    def testbench():
        for _ in range(100):
            yield


    simulate(la, testbench, "la_core.vcd")
