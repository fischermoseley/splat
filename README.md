## SPLAT: Simplest Possible Logic Analysis Tool

![run_tests](https://github.com/fischermoseley/splat/actions/workflows/run_tests.yaml/badge.svg)

A FPGA debugging tool named after the sound bugs make they're squashed. Depending on your opinion of the code, the first letter of the acryonym may be easily substituted for _Spiffiest_, _Swankiest_, _Silliest_ or _Stupidest_. I'll also put a logo here when the time comes.

Right now this is mostly just a rewrite of [Manta](https://github.com/fischermoseley/manta) in [Amaranth HDL](https://github.com/amaranth-lang/amaranth) as opposed to vanilla Verilog-2001. This was done for a few reasons, the most significant being extensibility, quality of life for developers, and portability to more FPGA toolchains.

