from schemdraw.elements import Element

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
from schemdraw.segments import Segment, SegmentArc, SegmentBezier, SegmentCircle


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
        return CapacitorCustom()  # customized
    if cls == "diode":
        return DiodeCustom()  # customized
    if cls == "inductor":
        return InductorCustom()  # customized
    if cls == "resistor":
        return ResistorCustom()  # customized
    if cls == "swi_ideal":
        return SwitchIdealCustom()  # customized
    if cls == "swi_real":
        return NMosCustom()  # 暂时用系统自带的
    if cls == "xformer":
        return TransformerCustom()  # customized
    raise ValueError(f"Unknown component class: {cls}")


class BBoxRect(Element):
    def __init__(self, xmin, ymin, xmax, ymax, lw=0.8):
        super().__init__()
        self.segments.append(Segment([(xmin, ymin), (xmax, ymin)], lw=lw))
        self.segments.append(Segment([(xmax, ymin), (xmax, ymax)], lw=lw))
        self.segments.append(Segment([(xmax, ymax), (xmin, ymax)], lw=lw))
        self.segments.append(Segment([(xmin, ymax), (xmin, ymin)], lw=lw))


# =========================
# DRAW TEST SECTION
# =========================

if __name__ == "__main__":

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
        "xformer",
        "swi_real",
    ]

    dx = 4.0
    dy = 3.0
    cols = 4
    d = schemdraw.Drawing()

    for i, name in enumerate(component_list):
        r, c = divmod(i, cols)
        x, y = c * dx, -r * dy

        elem = make_component(name)
        d += elem.at((x, y))
        elem.label(name, loc="bottom")

        # --- 1) 元件自身 bbox（未应用 transform） ---
        # bb_local = elem.get_bbox(transform=False, includetext=False)
        # print(name, "local bbox (no transform, no text):", bb_local)

        # # --- 2) 放到 drawing 里的 bbox（应用 transform） ---
        # bb_world = elem.get_bbox(transform=True, includetext=False)
        # print(name, "world bbox (transform, no text):", bb_world)

        # # 画 world bbox 框出来（你也可以画 local bbox，但要手动加偏移/变换，麻烦）
        # xmin, ymin, xmax, ymax = bb_world
        # d += BBoxRect(xmin, ymin, xmax, ymax, lw=0.8)

    d.draw(show=True)
    # d.save("bbox_debug.svg")
    # print("Saved bbox_debug.svg")
