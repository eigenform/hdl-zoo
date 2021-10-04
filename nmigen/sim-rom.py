#!/usr/bin/python3

from nmigen import *
from nmigen.sim import *

class MyROM(Elaboratable):
    """ Simple ROM wrapper around nMigen memories.

        word_width: The width of storage locations (in bits).
        num_words:  The number of storage locations.
        data:       The initial values of storage locations.
    """
    def __init__(self, word_width: int, num_words: int, data: list):
        from math import ceil, log2
        self.rom = Memory(width=word_width, depth=num_words, init=data)
        self.i_addr = Signal(ceil(log2(num_words)))
        self.o_data = Signal(word_width)

    def elaborate(self, platform):
        m = Module()
        m.submodules.rdport = rdport = self.rom.read_port()
        m.d.comb += [
            rdport.addr.eq(self.i_addr),
            self.o_data.eq(rdport.data),
        ]
        return m

ROM_TEST_DATA = [
    0x00000000, 0x11111111, 0x22222222, 0x33333333,
    0x44444444, 0x55555555, 0x66666666, 0x77777777,
    0x88888888, 0x99999999, 0xaaaaaaaa, 0xbbbbbbbb,
    0xcccccccc, 0xdddddddd, 0xeeeeeeee, 0xffffffff,
]

def do_rom_read(rom: MyROM, addr: int, val: int):
    yield rom.i_addr.eq(addr)
    yield Tick()
    yield Settle()
    data = yield rom.o_data
    sts  = "NG" if data != val else "OK"
    print(f"{sts} addr={addr:08x} data={data:08x} expected={val:08x}")

def test_rom_proc():
    for (addr, val) in enumerate(ROM_TEST_DATA):
        yield from do_rom_read(dut, addr, val)

dut = MyROM(32, 16, ROM_TEST_DATA)
sim = Simulator(dut)
sim.add_clock(1e-6)

sim.add_sync_process(test_rom_proc)
with sim.write_vcd("/tmp/test_rom_proc.vcd", "/tmp/test_rom_proc.gtkw"):
    sim.run()

