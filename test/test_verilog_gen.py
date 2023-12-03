from splat.cli import gen
from splat import Splat
import tempfile
import os


def test_verilog_gen():
    with tempfile.TemporaryDirectory() as tmp_dir:
        print("Created temporary directory at", tmp_dir)

        gen("test/test_verilog_gen.yaml", tmp_dir + "/splat.v")

        if not os.path.isfile(tmp_dir + "/splat.v"):
            raise ValueError("No Verilog file generated!")
