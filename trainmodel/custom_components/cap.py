import math

from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentArc, SegmentText

# height = 0.25  # original Resistor height

gap = (math.nan, math.nan)


class CapacitorCustom(Element):
    """
    Two-plate capacitor.
    """

    _element_defaults = {"polar": False}

    def __init__(
        self,
        *,
        polar: bool = False,  # 是否加正负极符号
        type: int = 2,  # 型号
        height=0.25,  # cap高度
        capgap=0.2,  # cap中间的间隙
        caplw=2,  # cap的画线宽度
        # textlw=1,  # 正负极符号的画线宽度
        **kwargs
    ):
        super().__init__(**kwargs)

        if type == 1:
            self.segments.append(
                Segment(
                    [
                        (0, 0),
                        gap,
                        (0, height),
                        (0, -height),
                        gap,
                        (capgap, height),
                        (capgap, -height),
                        gap,
                        (capgap, 0),
                    ],
                    lw=caplw,
                )
            )
        if type == 2:
            self.segments.append(
                Segment(
                    [(0, 0), gap, (0, height), (0, -height), gap, (capgap, 0)], lw=caplw
                )
            )
            self.segments.append(
                SegmentArc(
                    (capgap * 1.5, 0),
                    width=capgap * 1.5,
                    height=height * 2.5,
                    theta1=105,
                    theta2=-105,
                    lw=caplw,
                )
            )
        if self.params["polar"]:
            self.segments.append(SegmentText((-capgap * 1.2, capgap), "+"))
