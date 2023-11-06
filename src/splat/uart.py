from amaranth import *
from amaranth.lib.data import ArrayLayout
from warnings import warn
from .utils import *


class UARTInterface(Elaboratable):
    def __init__(self, config):
        self.config = config
        self.check_config(self.config)

        self.port = config["port"]
        self.clock_freq = config["clock_freq"]
        self.baudrate = config["baudrate"]
        self.clocks_per_baud = self.clock_freq // self.baudrate

        self.define_signals()

        # Set chunk_size, which is the max amount of bytes that the core will
        # dump to the OS driver at a time. Since the FPGA will return bytes
        # almost instantaneously, this prevents the OS's input buffer from
        # overflowing, and dropping bytes.
        self.chunk_size = 256  # in bytes
        if "chunk_size" in config:
            self.chunk_size = config["chunk_size"]

    def check_config(self, config):
        # Warn if unrecognized options have been given
        recognized_options = ["port", "clock_freq", "baudrate", "chunk_size"]
        for option in config:
            if option not in recognized_options:
                warn(
                    f"Ignoring unrecognized option '{option}' in UART interface config."
                )

        # Ensure a serial port has been given
        if "port" not in config:
            raise ValueError("No serial port provided to UART interface.")

        # Ensure clock frequency is provided and positive
        if "clock_freq" not in config:
            raise ValueError("No clock frequency provided to UART interface.")

        if config["clock_freq"] <= 0:
            raise ValueError("Non-positive clock frequency provided to UART interface.")

        # Check that baudrate is provided and positive
        if "baudrate" not in config:
            raise ValueError("No baudrate provided to UART interface.")

        if config["baudrate"] <= 0:
            raise ValueError("Non-positive baudrate provided to UART interface.")

        # Confirm the actual baudrate is within 5% of the target baudrate
        clock_freq = config["clock_freq"]
        baudrate = config["baudrate"]
        clocks_per_baud = clock_freq // baudrate
        actual_baudrate = clock_freq / clocks_per_baud
        error = 100 * abs(actual_baudrate - baudrate) / baudrate

        if error > 5:
            raise ValueError(
                "UART interface is unable to match targeted baudrate with specified clock frequency."
            )

    def read(self, addrs):
        """
        Read the data stored in a set of address on Manta's internal memory. Addresses
        must be specified as either integers or a list of integers.
        """

        # Handle a single integer address
        if isinstance(addrs, int):
            return self.read([addrs])[0]

        # Make sure all list elements are integers
        if not all(isinstance(a, int) for a in addrs):
            raise ValueError("Read address must be an integer or list of integers.")

        # Send read requests, and get responses
        ser = self.get_port()
        addr_chunks = split_into_chunks(addrs, self.chunk_size)
        datas = []

        for addr_chunk in addr_chunks:
            # Encode addrs into read requests
            bytes_out = b"".join([f"R{a:04X}\r\n".encode("ascii") for a in addr_chunk])
            ser.write(bytes_out)

            # Read responses have the same length as read requests
            bytes_in = ser.read(len(bytes_out))

            # Split received bytes into individual responses and decode
            responses = split_into_chunks(bytes_in, 7)
            data_chunk = self.decode_read_response(responses)
            datas += data_chunk

        return datas

    def write(self, addrs, datas):
        """
        Write the provided data into the provided addresses in Manta's internal memory.
        Addresses and data must be specified as either integers or a list of integers.
        """

        # Handle a single integer address and data
        if isinstance(addrs, int) and isinstance(datas, int):
            self.write([addrs], [datas])

        # Make sure address and datas are all integers
        if not isinstance(addrs, list) or not isinstance(datas, list):
            raise ValueError(
                "Write addresses and data must be an integer or list of integers."
            )

        if not all(isinstance(a, int) for a in addrs):
            raise ValueError("Write addresses must be all be integers.")

        if not all(isinstance(d, int) for d in datas):
            raise ValueError("Write data must all be integers.")

        # I'm not sure if it's necessary to split outputs into chunks
        # I think the output buffer doesn't really drop stuff, just the input buffer

        # Encode addrs and datas into write requests
        bytes_out = "".join([f"W{a:04X}{d:04X}\r\n" for a, d in zip(addrs, datas)])
        ser = self.get_port()
        ser.write(bytes_out)

    def decode_read_response(self, response_bytes):
        """
        Check that read response is formatted properly, and extract the encoded data if so.
        """

        # Make sure response is not empty
        if response_bytes is None:
            raise ValueError("Unable to decode read response - no bytes received.")

        # Make sure response is properly encoded
        response_ascii = response_bytes.decode("ascii")

        if len(response_ascii) != 7:
            raise ValueError(
                "Unable to decode read response - wrong number of bytes received."
            )

        if response_ascii[0] != "D":
            raise ValueError("Unable to decode read response - incorrect preamble.")

        for i in range(1, 5):
            if response_ascii[i] not in "0123456789ABCDEF":
                raise ValueError("Unable to decode read response - invalid data byte.")

        if response_ascii[5] != "\r":
            raise ValueError("Unable to decode read response - incorrect EOL.")

        if response_ascii[6] != "\n":
            raise ValueError("Unable to decode read response - incorrect EOL.")

        return int(response_ascii[1:5], 16)

    def define_signals(self):
        self.rx = Signal()
        self.tx = Signal()

        self.addr_o = Signal(16)
        self.data_o = Signal(16)
        self.rw_o = Signal()
        self.valid_o = Signal()

        self.addr_i = Signal(16)
        self.data_i = Signal(16)
        self.rw_i = Signal()
        self.valid_i = Signal()

    def elaborate(self, platform):
        # fancy submoduling and such goes in here
        m = Module()

        m.submodules["uart_rx"] = uart_rx = UARTReceiver(self.clocks_per_baud)
        m.submodules["bridge_rx"] = bridge_rx = RecieveBridge()
        m.submodules["bridge_tx"] = bridge_tx = TransmitBridge()
        m.submodules["uart_tx"] = uart_tx = UARTTransmitter(self.clocks_per_baud)

        m.d.comb += [
            # UART RX -> Internal Bus
            uart_rx.rx.eq(self.rx),
            bridge_rx.data_i.eq(uart_rx.data_o),
            bridge_rx.valid_i.eq(uart_rx.valid_o),
            self.data_o.eq(bridge_rx.data_o),
            self.addr_o.eq(bridge_rx.addr_o),
            self.rw_o.eq(bridge_rx.rw_o),
            self.valid_o.eq(bridge_rx.valid_o),
            # Internal Bus -> UART TX
            bridge_tx.data_i.eq(self.data_i),
            bridge_tx.rw_i.eq(self.rw_i),
            bridge_tx.valid_i.eq(self.valid_i),
            uart_tx.data_i.eq(bridge_tx.data_o),
            uart_tx.start_i.eq(bridge_tx.start_o),
            bridge_tx.done_i.eq(uart_tx.done_o),
            self.tx.eq(uart_tx.tx),
        ]
        return m


class UARTReceiver(Elaboratable):
    def __init__(self, clocks_per_baud):
        self.clocks_per_baud = clocks_per_baud

        # Define Signals
        self.rx = Signal()
        self.data_o = Signal(8)
        self.valid_o = Signal(1, reset=0)

        self.IDLE = 0
        self.BIT_ZERO = 1
        self.STOP_BIT = 9

        self.state = Signal(4, reset=self.IDLE)
        self.baud_counter = Signal(16, reset=0)
        self.zero_baud_counter = Signal()

        self.ck_uart = Signal(reset=1)
        self.q_uart = Signal(reset=1)

    def elaborate(self, platform):
        m = Module()
        m.d.comb += self.zero_baud_counter.eq(self.baud_counter == 0)

        m.d.sync += self.ck_uart.eq(self.q_uart)
        m.d.sync += self.q_uart.eq(self.rx)

        with m.If(self.state == self.IDLE):
            m.d.sync += self.state.eq(self.IDLE)
            m.d.sync += self.baud_counter.eq(0)

            with m.If(self.ck_uart == 0):
                m.d.sync += self.state.eq(self.BIT_ZERO)
                m.d.sync += self.baud_counter.eq(
                    self.clocks_per_baud + self.clocks_per_baud // 2 - 1
                )

        with m.Elif(self.zero_baud_counter):
            m.d.sync += self.state.eq(self.state + 1)
            m.d.sync += self.baud_counter.eq(self.clocks_per_baud - 1)

            with m.If(self.state == self.STOP_BIT):
                m.d.sync += self.state.eq(self.IDLE)
                m.d.sync += self.baud_counter.eq(0)

        with m.Else():
            m.d.sync += self.baud_counter.eq(self.baud_counter - 1)

        with m.If(self.zero_baud_counter & self.state != self.STOP_BIT):
            m.d.sync += self.data_o.eq(Cat(self.data_o[1:7], self.ck_uart))

        m.d.sync += self.valid_o.eq(
            self.zero_baud_counter & (self.state == self.STOP_BIT)
        )
        return m


class RecieveBridge(Elaboratable):
    def __init__(self):
        # Top-Level Ports
        self.data_i = Signal(8)
        self.valid_i = Signal()

        self.addr_o = Signal(16, reset=0)
        self.data_o = Signal(16, reset=0)
        self.rw_o = Signal(1, reset=0)
        self.valid_o = Signal(1, reset=0)

        # State Machine
        self.IDLE_STATE = 0
        self.READ_STATE = 1
        self.WRITE_STATE = 2

        # Internal Signals
        self.buffer = Signal(ArrayLayout(8, 8), reset_less=True)
        self.state = Signal(2, reset=self.IDLE_STATE)
        self.byte_num = Signal(4, reset=0)

    def from_ascii_hex(self, m, char):
        """
        Convert an ASCII character encoding a hex digit to the
        corresponding numerical value.
        """

        # Decode 0-9
        with m.If((char >= 0x30) & (char <= 0x39)):
            yield char - 0x30

        # Decode A-F
        with m.Elif((char >= 0x41) & (char <= 0x46)):
            yield char - 0x41 + 10

        with m.Else():
            yield 0

    def is_ascii_hex(self, m, char):
        """
        Checks if a byte is an ASCII character that encodes a hex digit.
        """

        # Decode 0-9
        with m.If((char >= 0x30) & (char <= 0x39)):
            yield 1

        # Decode A-F
        with m.Elif((char >= 0x41) & (char <= 0x46)):
            yield 1

        with m.Else():
            yield 0

    def elaborate(self, platform):
        m = Module()

        m.d.sync += self.addr_o.eq(0)
        m.d.sync += self.data_o.eq(0)
        m.d.sync += self.rw_o.eq(0)
        m.d.sync += self.valid_o.eq(0)

        with m.If(self.state == self.IDLE_STATE):
            m.d.sync += self.byte_num.eq(0)
            with m.If(self.valid_i):
                with m.If(self.data_i == ord("R")):
                    m.d.sync += self.state.eq(self.READ_STATE)

                with m.If(self.data_i == ord("W")):
                    m.d.sync += self.state.eq(self.WRITE_STATE)

        with m.Else():
            with m.If(self.valid_i):
                # Buffer bytes regardless of if they're good
                self.byte_num.eq(self.byte_num + 1)
                self.buffer[self.byte_num].eq(self.data_i)

                # Current transaction specifies a read operation
                with m.If(self.state == self.READ_STATE):
                    # Go to IDLE if any bytes don't make sense.
                    with m.If(self.byte_num < 4):
                        with m.If(not self.is_ascii_hex(m, self.data_i)):
                            m.d.sync += self.state.eq(self.IDLE_STATE)

                    with m.Elif(self.byte_num == 4):
                        m.d.sync += self.state.eq(self.IDLE_STATE)

                        # Put data on teh bus if the last byte looks good
                        with m.If((self.data_i == 0x0D) | (self.data_i == 0x0A)):
                            m.d.sync += self.addr_o.eq(
                                # bleh
                                0
                            )

                            m.d.sync += self.data_o.eq(0)
                            m.d.sync += self.rw_o.eq(0)
                            m.d.sync += self.valid_o.eq(1)

                # Current transaction specifies a write transaction
                with m.Elif(self.state == self.WRITE_STATE):
                    # Go to IDLE if any bytes don't make sense.
                    with m.If(self.byte_num < 8):
                        if not self.is_ascii_hex(m, self.data_i):
                            m.d.sync += self.state.eq(self.IDLE)

                    with m.Elif(self.byte_num == 8):
                        m.d.sync += self.state.eq(self.IDLE_STATE)

                        # Put data on the bus if the last byte looks good
                        with m.If((self.data_i == 0x0D) | (self.data_i == 0x0A)):
                            m.d.sync += self.addr_o.eq(
                                # ew grossss
                                0
                            )

                            m.d.sync += self.data_o.eq(
                                # ew super gross
                                0
                            )

                            m.d.sync += self.rw_o.eq(1)
                            m.d.sync += self.valid_o.eq(1)
        return m


class UARTTransmitter(Elaboratable):
    def __init__(self, clocks_per_baud):
        self.data_i = Signal(8)
        self.start_i = Signal()
        self.done_o = Signal(reset=0)

        self.tx = Signal(reset=1)

    def elaborate(self, platform):
        m = Module()
        m.d.sync += self.done_o.eq(0)
        m.d.sync += self.tx.eq(1)
        return m


class TransmitBridge(Elaboratable):
    def __init__(self):
        self.data_i = Signal(16)
        self.rw_i = Signal()
        self.valid_i = Signal()

        self.data_o = Signal(8)
        self.start_o = Signal()
        self.done_i = Signal()

    def elaborate(self, platform):
        m = Module()
        m.d.sync += self.data_o.eq(0)
        m.d.sync += self.start_o.eq(0)
        return m
