from .splat import Splat
from warnings import warn
from sys import argv

logo = """
  ╱|、
(˚ˎ 。7
 |、˜〵
じしˍ,)ノ ...nyah?
"""


def help():
    print(logo)


def wrong_args():
    raise ValueError('Wrong number of arguments, run "splat help" for usage.')


def gen(config_path, output_path):
    s = Splat(config_path)

    from amaranth.back import verilog

    with open(output_path, "w") as f:
        f.write(verilog.convert(s, ports=s.ports, strip_internal_attrs=True))


def capture(config_path, logic_analyzer_name, export_paths):
    s = Splat(config_path)
    la = getattr(s, logic_analyzer_name)
    data = la.capture()

    for path in export_paths:
        if ".vcd" in path:
            la.export_vcd(data, path)
        elif ".mem" in path:
            la.export_mem(data, path)
        else:
            warn(f"Unrecognized file type, skipping {path}.")


def playback(config_path, logic_analyzer_name, export_path):
    s = Splat(config_path)
    la = getattr(s, logic_analyzer_name)
    la.export_playback_module(export_path)


def mmap(config_path):
    print(Splat(config_path).mmap())


def ports():
    import serial.tools.list_ports

    for port in serial.tools.list_ports.comports():
        print(port)

        # sometimes macOS will enumerate non-serial devices as serial ports,
        # in which case the PID/VID/serial/location/etc are all None
        pid = f"0x{port.vid:04X}" if port.pid is not None else "None"
        vid = f"0x{port.vid:04X}" if port.vid is not None else "None"

        print(f" ->  pid: {pid}")
        print(f" ->  vid: {vid}")
        print(f" ->  ser: {port.serial_number}")
        print(f" ->  loc: {port.location}")
        print(f" -> mftr: {port.manufacturer}")
        print(f" -> prod: {port.product}")
        print(f" -> desc: {port.description}\n")


def main():
    if len(argv) == 1:
        help()

    elif argv[1] in ["help", "-h", "-help", "--help"]:
        help()

    elif argv[1] == "gen":
        if len(argv) != 4:
            wrong_args()
        gen(argv[2], argv[3])

    elif argv[1] == "capture":
        if len(argv) < 5:
            wrong_args()
        capture(argv[2], argv[3], argv[4])

    elif argv[1] == "playback":
        if len(argv) != 5:
            wrong_args()
        playback(argv[2], argv[3], argv[4])

    elif argv[1] == "mmap":
        if len(argv) != 3:
            wrong_args()
        mmap(argv[2])

    elif argv[1] == "ports":
        ports()

    else:
        wrong_args()


if __name__ == "__main__":
    main()
