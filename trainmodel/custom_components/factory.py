import schemdraw

from resistor import ResistorCustom
from ac_src import ACSourceCustom
from battery import BatteryCustom
from cap import CapacitorCustom
from curr_src import CurrentSourceCustom
from diode import DiodeCustom
from inductor import InductorCustom
from swi_real import NMosCustom
from swi_ideal import SwitchIdealCustom
from xformer import TransformerCustom
from volt_src import VoltageSourceCustom

import inspect
from schemdraw.segments import SegmentArc, SegmentBezier, SegmentCircle


def make_component(cls: str):
    if cls == "ac_src":
        return ACSourceCustom()
    if cls == "volt_src":
        return VoltageSourceCustom()
    if cls == "curr_src":
        return CurrentSourceCustom()
    if cls == "battery":
        return BatteryCustom()
    if cls == "cap":
        return CapacitorCustom()
    if cls == "diode":
        return DiodeCustom()
    if cls == "inductor":
        return InductorCustom()
    if cls == "resistor":
        return ResistorCustom()
    if cls == "swi_ideal":
        return SwitchIdealCustom()
    if cls == "swi_real":
        return NMosCustom()
    if cls == "xformer":
        return TransformerCustom()
    raise ValueError(f"Unknown component class: {cls}")


# =========================
# DRAW TEST SECTION
# =========================

if __name__ == "__main__":

    # print("SegmentArc:", inspect.signature(SegmentArc.__init__))
    # print("SegmentBezier:", inspect.signature(SegmentBezier.__init__))
    # print("SegmentCircle:", inspect.signature(SegmentCircle.__init__))

    component_list = [
        "ac_src",
        "volt_src",
        "curr_src",
        "battery",
        "cap",
        "diode",
        "inductor",
        "resistor",
        "swi_ideal",
        "swi_real",
        "xformer",
    ]

    dx = 4.0
    dy = 3.0
    cols = 4

    with schemdraw.Drawing() as d:

        for i, name in enumerate(component_list):
            r = i // cols
            c = i % cols

            x = c * dx
            y = -r * dy

            elem = make_component(name)
            print("drawing", name)

            d += elem.at((x, y))
            elem.label(name, loc="bottom")

        d.draw()
