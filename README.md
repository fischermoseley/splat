## SPLAT: Simplest Possible Logic Analysis Tool

![run_tests](https://github.com/fischermoseley/splat/actions/workflows/run_tests.yaml/badge.svg)

A FPGA debugging tool named after the sound bugs make they're squashed. Depending on your opinion of the code, the first letter of the acryonym may be easily substituted for _Spiffiest_, _Swankiest_, _Silliest_ or _Stupidest_. I'll also put a logo here when the time comes.

Right now this is mostly just a rewrite of [Manta](https://github.com/fischermoseley/manta) in [Amaranth HDL](https://github.com/amaranth-lang/amaranth) as opposed to vanilla Verilog-2001. This was done for a few reasons, the most significant being extensibility, quality of life for developers, and portability to more FPGA toolchains.

### Installation
If you're on Ubuntu, you'll have to run `export DEB_PYTHON_INSTALL_LAYOUT=deb_system` thanks to a bug in the latest version of `setuptools`.

For a normal installation without all the extra development tools, just run `pip install git+https://github.com/fischermoseley/splat.git`

However if you're a developer, then you'll need the optional dependencies, installable with `pip install git+https://github.com/fischermoseley/splat.git[dev]`

### A Quick Example

At the time of writing (11/12/23), just the IO core is working. I haven't written proper docs yet, so for now here's a quick example for someone familiar with how Manta works:

Splat uses the same configuration file format as Manta does, and has the same command-line usage. An example `splat.yaml` file could look like the following:

```yaml
---
cores:
  io_core:
    type: io

    inputs:
      probe0: 1
      probe1: 2
      probe2: 8
      probe3: 20

    outputs:
      probe4:
        width: 1
        initial_value: 1
      probe5:
        width: 2
        initial_value: 2
      probe6: 8
      probe7:
        width: 20
        initial_value: 65538

uart:
  port: "/dev/ttyUSB1"
  baudrate: 115200
  clock_freq: 100000000
```

Which can then be turned into a Verilog file by running `splat gen splat.yaml splat.v`, which produces `splat.v`. You can include this file in your design, instantiate the `splat` module, and connect all your inputs and outputs accordingly.

Using Splat from Python is very similar to Manta. Here's quick Python snippet on how to use the configuration provided above:

```python
from splat import Splat
s = Splat('splat.yaml')

s.io_core.set_probe("probe6", 27)
foo = s.io_core.get_probe("probe2")
print(foo)
```

More docs soon to come!

