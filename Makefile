all:
	python3 test.py
	iverilog -g2012 -o sim.out io_core_tb.sv io_core.v
	vvp sim.out
	rm sim.out