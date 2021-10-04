#!/usr/bin/python3

from nmigen.sim import *
from nmigen import *

class FFProp:
    SYNC_RESET = 0

class DFlipFlop(Elaboratable):
    def __init__(self, prop=[]):
        self.prop  = prop
        self.input  = Signal()
        self.output = Signal()
        self.reset  = Signal()

    def elaborate(self, platform):
        m = Module()
        if FFProp.SYNC_RESET in self.prop:
            with m.If(self.reset):
                m.d.sync += self.output.eq(0)
            with m.Else():
                m.d.sync += self.output.eq(self.input)
        else:
            m.d.sync += self.output.eq(self.input)
        return m

    def sim_drive(self):
        """ Drive input for 16 cycles """
        for i in range(0,15):
            yield dut.input.eq(1)
            yield Tick()
            yield Settle()
            yield dut.input.eq(0)
            yield Tick()
            yield Settle()
        return

    def sim_drive_sr(self):
        """ Drive/reset for 16 cycles """
        def hold_rst(ticks: int):
            yield dut.reset.eq(1)
            for i in range(0, ticks):
                yield Tick()
        def drive(ticks: int):
            for i in range(0, ticks):
                yield dut.input.eq(1)
                yield Tick()
                yield dut.input.eq(0)
                yield Tick()
        yield from hold_rst(4)
        yield from drive(4)
        yield from hold_rst(4)
        yield from drive(4)
        return

def proc_ff():
    yield from DFlipFlop.sim_drive(dut)
def proc_ff_sr():
    yield from DFlipFlop.sim_drive_sr(dut)


tests = [
    { 'name': "ff",    'proc': proc_ff,    'prop': [] },
    { 'name': "ff_sr", 'proc': proc_ff_sr, 'prop': [FFProp.SYNC_RESET] },
]

for test in tests:
    dut = DFlipFlop(prop=test['prop'])
    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(test['proc'])
    gtkw_fn = "/tmp/{}.gtkw".format(test['name'])
    vcd_fn = "/tmp/{}.vcd".format(test['name'])
    with sim.write_vcd(vcd_fn, gtkw_fn):
        sim.run()
    print("Ran sim for '{}'".format(test['name']))

