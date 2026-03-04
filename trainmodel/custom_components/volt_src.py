import math

from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentCircle, SegmentText

gap = (math.nan, math.nan)


class VoltageSourceCustom(Element):
    """
    Voltage source: circle with + and -.
    """

    def __init__(self, length=2.2, radius=0.35, lw=1.5):
        super().__init__()
        self.segments.append(Segment([(0, 0), (0, 0), gap, (1, 0), (1, 0)]))
        self.segments.append(
            SegmentCircle(
                (0.5, 0),
                0.5,
            )
        )
        self.elmparams["theta"] = 90
        plus_len = 0.2
        self.segments.append(
            Segment([(0.25, -plus_len / 2), (0.25, plus_len / 2)])
        )  # '-' sign
        self.segments.append(
            Segment([(0.75 - plus_len / 2, 0), (0.75 + plus_len / 2, 0)])
        )  # '+' sign
        self.segments.append(Segment([(0.75, -plus_len / 2), (0.75, plus_len / 2)]))
